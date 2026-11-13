import redscope.config
import sqlite3 
from pathlib import Path
from redscope.crawler import Crawl
from redscope.evidence import Evidence
import json
from redscope.api import ApiSpec


# so this boy does the path selection by using a custom path if given otherwise defaults in redscope.db , it ensures the parent folder exists on disk , access database columns by name like dictionaries and it forces sqlite to enforce relational integrity and block orphaned records 

def get_db(db_file=None):
    if db_file :
        target_path = db_file
    else:
        target_path = redscope.config.db_path
    Path(target_path).parent.mkdir(parents=True, exist_ok = True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# tis boy executes scheme script to build the 6 core tables:- projects : does top level mean grouping target applications, scans: does individual crawl runs , resources: does the master catalog of unique urls and asset types, scan_resources: it maps which resources were seen in which scan  storing http status codes, evidence: it tracks where and how the an asset found source url, method, confidence tier, and lastly edges : does the source to target connections powering the attack surface relationship graph.
def init_db(db_file=None):
    schema = """CREATE TABLE IF NOT EXISTS projects ( id INTEGER PRIMARY KEY AUTOINCREMENT , name TEXT NOT NULL , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 
    CREATE TABLE IF NOT EXISTS scans ( id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, target_origin TEXT NOT NULL, started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, finished_at TIMESTAMP, status TEXT DEFAULT 'pending', config_json TEXT, FOREIGN KEY(project_id) REFERENCES projects(id));
    CREATE TABLE IF NOT EXISTS resources ( id INTEGER PRIMARY KEY AUTOINCREMENT, normalized_url TEXT UNIQUE NOT NULL, resource_type TEXT);
    CREATE TABLE IF NOT EXISTS scan_resources ( scan_id INTEGER, resource_id INTEGER, content_type TEXT, observed_status INTEGER, first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (scan_id, resource_id), FOREIGN KEY (scan_id) REFERENCES scans(id), FOREIGN KEY (resource_id) REFERENCES resources(id));
    CREATE TABLE IF NOT EXISTS evidence( id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, resource_id INTEGER, source_url TEXT, evidence_type TEXT, discovery_method TEXT, details_json TEXT, observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (scan_id) REFERENCES scans(id), FOREIGN KEY (resource_id) REFERENCES resources(id));
    CREATE TABLE IF NOT EXISTS edges( id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, source_resource_id INTEGER, target_resource_id INTEGER, relation_type TEXT, FOREIGN KEY (scan_id) REFERENCES  scans(id), FOREIGN KEY (source_resource_id) REFERENCES resources(id), FOREIGN KEY (target_resource_id) REFERENCES resources(id));
    CREATE TABLE IF NOT EXISTS api_spec( id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, title TEXT, version TEXT, base_url TEXT, imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (project_id) REFERENCES projects(id));
    CREATE TABLE IF NOT EXISTS api_operations( id INTEGER PRIMARY KEY AUTOINCREMENT, spec_id INTEGER, path TEXT NOT NULL, method TEXT NOT NULL, summary TEXT, parameters_json TEXT, auth_required INTEGER DEFAULT 0, FOREIGN KEY (spec_id) REFERENCES api_spec(id));


    """
    conn = get_db(db_file)
    conn.executescript(schema)
    conn.commit() 
    return conn


# it's an helper that creates an project container and gives it's primary key
def create_project(conn, name: str) -> int :
    cr = conn.execute("INSERT INTO projects (name) VALUES (?)", (name, ))
    conn.commit()
    return cr.lastrowid


# it work is a url is spotted multiple times , i don't want duplicates of 
def save_resource(conn, normalized_url: str, resource_type: str = "page") -> int:
    
    conn.execute("INSERT  OR IGNORE INTO resources (normalized_url, resource_type) VALUES (?, ?)", (normalized_url, resource_type))
    fetch = conn.execute("SELECT id FROM resources WHERE normalized_url = ?", (normalized_url, )).fetchone()

    return fetch["id"]

# here the function does , when my crawler finish exploring a site then it will persist the entire function  attact surface into sqlite
def save_scan(conn, project_id: int, target_origin: str, crawl_result: Crawl, evidence_list: list[Evidence] = None) -> int:
    cr = conn.execute("INSERT INTO scans (project_id, target_origin, status) VALUES (?, ?, ?)", (project_id, target_origin, "completed", ))
    scan_id = cr.lastrowid
    for u in crawl_result.visited_urls:
        res_id = save_resource(conn, u, "page")
        conn.execute("INSERT OR IGNORE INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (scan_id, res_id, 200, ))

    for l in crawl_result.all_links:
        if l not in crawl_result.visited_urls:
            res_id = save_resource(conn, l, "page")
            conn.execute("INSERT OR IGNORE INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (scan_id, res_id, 0, ))

    for s in crawl_result.all_scripts:
        res_id = save_resource(conn, s, "scripts")
        conn.execute("INSERT OR IGNORE INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (scan_id, res_id, 0))

    for st in crawl_result.all_stylesheets:
        res_id = save_resource(conn, st, "stylesheets")
        conn.execute("INSERT OR IGNORE INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (scan_id, res_id, 0))

    for f in crawl_result.all_forms:
        res_id = save_resource(conn, f, "form")
        conn.execute("INSERT OR IGNORE INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (scan_id, res_id, 0))

    if evidence_list:
        for i in evidence_list:
            target_id = save_resource(conn, i.target_url)
            conn.execute("INSERT OR IGNORE INTO evidence (scan_id, resource_id, source_url, evidence_type, discovery_method, details_json) VALUES (?,?,?,?,?,?)", (scan_id, target_id, i.source_url, i.evidence_type, i.discovery_method, json.dumps(i.details)))
            if i.source_url:
                source_id = save_resource(conn, i.source_url)
                conn.execute("INSERT OR IGNORE INTO edges (scan_id, source_resource_id, target_resource_id, relation_type) VALUES (?,?,?,?)", (scan_id, source_id, target_id, i.discovery_method))

    conn.commit()
    return scan_id


def save_api_spec(conn, project_id: int, spec: ApiSpec) -> int:
    cr = conn.execute(" INSERT INTO api_spec (project_id, title, version, base_url) VALUES (?,?,?,?)", (project_id, spec.title, spec.version, spec.base_url))
    spec_id = cr.lastrowid
    for s in spec.operations:
        parameter_json = json.dumps(s.parameters)
        auth_required = 1 if s.auth_required else 0
        path = s.path
        method = s.method
        summary = s.summary
        conn.execute(" INSERT INTO api_operations (spec_id, path, method, summary, parameters_json, auth_required) VALUES (?,?,?,?,?,?)", (spec_id, path, method, summary, parameter_json, auth_required))
    conn.commit()
    return spec_id




