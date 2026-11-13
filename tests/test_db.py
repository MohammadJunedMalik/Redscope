from redscope.db import init_db, get_db, create_project, save_resource, save_scan, save_api_spec
from redscope.crawler import Crawl, crawl
from redscope.evidence import Evidence
import sqlite3
import pytest
from redscope.api import Apioperation, ApiSpec

# so this boy does the path selection by using a custom path if given otherwise defaults in redscope.db , it ensures the parent folder exists on disk , access database columns by name like dictionaries and it forces sqlite to enforce relational integrity and block orphaned records 

def test_init_db():
    in_db = init_db(":memory:")
    fetch_set = {row["name"] for row in in_db.execute("SELECT name FROM sqlite_master WHERE type='table';")}
    assert "projects" in fetch_set
    assert "scans" in fetch_set
    assert "resources" in fetch_set
    assert "scan_resources" in fetch_set
    assert "evidence" in fetch_set
    assert "edges" in fetch_set
    assert "api_spec" in fetch_set
    assert "api_operations" in fetch_set


def test_rowfactory():
    in_db = init_db(":memory:")
    fetch = in_db.execute("INSERT INTO projects (name) VALUES ('Redscope Test')")
    fetch_1 = in_db.execute("SELECT * FROM projects WHERE id = 1")
    take = fetch_1.fetchone()
    assert take["name"] == "Redscope Test"

def test_foreign_key():
    in_db = init_db(":memory:")
    with pytest.raises(sqlite3.IntegrityError):
        scan = in_db.execute("INSERT INTO scans (project_id, target_origin) VALUES(9999, 'http://example.com')")
        
def test_create_project():
    init = init_db(":memory:")
    p1 = create_project(init, "Alpha Target")
    p2 = create_project(init, "Beta Target")
    assert p1 == 1  
    assert p2 == 2
    fetch = init.execute("SELECT name FROM projects WHERE id = ?", (p1, )).fetchone()
    assert fetch["name"] == "Alpha Target"

def test_save_resource():
    init = init_db(":memory:")
    r1 = save_resource(init, "http://example.com/api", "page")
    r2 = save_resource(init, "http://example.com/api", "page")
    r3 = save_resource(init, "http://example.com/login", "page")
    assert r1 == r2
    assert r3 != r1
    count_r = init.execute("SELECT COUNT(*) as cnt FROM resources").fetchone()
    assert count_r["cnt"] == 2


def test_save_scan():
    init = init_db(":memory:")
    p_id = create_project(init, "E2E Target")
    res_crawl = Crawl( target_url = "http://example.com",
                      visited_urls = {"http://example.com/home"},
                      all_links = {"http://example.com/home", "http://example.com/about"},
                      all_scripts = {"http://example.com/app.js"},
                      all_stylesheets = set(),
                      all_forms = set(), )
    evi = [Evidence(target_url="http://example.com/about",
                    source_url = "http://example.com/home",
                    evidence_type = "referenced",
                    discovery_method = "href", )]

    scan_id = save_scan(init, p_id, "http://example.com", res_crawl, evi)
    assert scan_id == 1
    fetch_1 = init.execute("SELECT status FROM scans WHERE id = 1").fetchone()
    assert fetch_1["status"] == "completed"
    fetch_2 = init.execute("SELECT COUNT(*) as c FROM resources").fetchone()
    assert fetch_2["c"] >= 3
    fetch_3 = init.execute("SELECT * FROM evidence WHERE scan_id = 1").fetchone()
    assert fetch_3["source_url"] == "http://example.com/home"
    fetch_4 = init.execute("SELECT * FROM edges WHERE scan_id = 1").fetchone()
    assert fetch_4["relation_type"] == "href"


def test_save_api():
    init = init_db(":memory:")
    test = create_project(init, 'api_spec')
    api = ApiSpec(title = "Store API", version = "1.0", base_url = "https://api.test.com", operations = [Apioperation( path="/products", method = "GET", summary = "List products", parameters=["limit"], auth_required=False), Apioperation(path="/products", method="POST", summary="Add product", parameters=[], auth_required = True)])
    spec_id = save_api_spec(init, test, api)
    assert spec_id == 1
    fetch_1 = init.execute(" SELECT * FROM api_spec WHERE id = ?", (spec_id, )).fetchone()
    assert fetch_1["title"] == "Store API"
    assert fetch_1["version"] == "1.0"
    assert fetch_1["base_url"] == "https://api.test.com"
    assert fetch_1["project_id"] == test
    fetch_2 = init.execute("SELECT * FROM api_operations WHERE spec_id = ?", (spec_id, )).fetchall()
    assert len(fetch_2) == 2
    op_1_f2= fetch_2[0]
    op_2_f2 = fetch_2[1]
    assert op_1_f2['method'] == "GET"
    assert op_1_f2['auth_required'] == 0
    assert op_2_f2['method'] == 'POST'
    assert op_2_f2['auth_required'] == 1




