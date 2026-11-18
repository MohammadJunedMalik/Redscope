from flask import Flask, render_template, jsonify, request, g
from redscope.db import init_db, get_db, create_project, save_scan, save_api_spec
from redscope.graph import make_graph
from redscope.compare import compare
from redscope.evidence import Evidence
from redscope.crawler import crawl
from redscope.config import ScanConfig
from redscope.scope import valid_target
from redscope.api import  parse_api

app = Flask(__name__)

@app.before_request
def app_db():
    g.db = get_db()
        

@app.teardown_appcontext
def close_db(error=None):
    pop = g.pop('db', None)
    if pop:
        pop.close()

@app.route("/")
def render():
    return render_template("index.html")

@app.route("/api/projects", methods=["GET"])
def jsonfile():
    db = g.db
    fetch = db.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    dic = []
    for f in fetch:
        d = dict(f)
        dic.append(d)
    return jsonify(dic)


@app.route("/api/projects", methods=["POST"])
def project():
    req = request.get_json()
    if not req or not req.get("name"):
        Json = jsonify({"error" : "Project name is required"}), 400
        return Json
    name = req.get("name", "").strip()
    if not name:
        error = jsonify({"error" : "Project name is required"}), 400
        return error
    pro = create_project(g.db, name)
    return jsonify({"id" : pro, "name" : name})

@app.route("/api/overview", methods=["GET"])
def query_db():
    db = g.db
    fetch_1 = db.execute("SELECT count(*) FROM projects").fetchone()[0]
    fetch_2 = db.execute("SELECT count(*) FROM scans").fetchone()[0]
    fetch_3 = db.execute("SELECT count(*) FROM resources").fetchone()[0]
    fetch_4 = db.execute("SELECT * FROM scans ORDER BY started_at  DESC LIMIT 5").fetchall()
    dic_4 = [dict(r) for r in fetch_4]
    return jsonify({"total_projects" : fetch_1, "total_scans" : fetch_2, "total_resources" : fetch_3, "recent_scans" : dic_4})

@app.route("/api/scans", methods=["GET"])
def project_scan():
    project_id = request.args.get("project_id", type=int)
    if project_id:
        pro = g.db.execute("SELECT * FROM scans WHERE project_id = ? ORDER BY started_at DESC", (project_id, )).fetchall()
    else:
        pro = g.db.execute("SELECT * FROM scans  ORDER BY started_at DESC").fetchall()
    l = [dict(r) for r in pro]
    return jsonify(l)




@app.route("/api/scans/<int:scan_id>/resources", methods=["GET"])
def scan_projects(scan_id):
    db = g.db
    fetch = db.execute(" SELECT r.id, r.normalized_url, r.resource_type, sr.observed_status, sr.first_seen_at FROM scan_resources sr JOIN resources r ON sr.resource_id = r.id WHERE sr.scan_id=?", (scan_id, )).fetchall()
    dic = [dict(f) for f in fetch]
    return jsonify(dic)

@app.route("/api/scans/<int:scan_id>/graph", methods = ["GET"])
def graph(scan_id):
    db = g.db
    fetch = db.execute(" SELECT * FROM scans WHERE id = ? ", (scan_id, )).fetchone()
    if not fetch :
        Json = jsonify({"error" : "scan not found here  "}), 404
        return Json
    else:
        build_graph = make_graph(g.db, scan_id)
        to_dict = build_graph.to_dict()
        Json = jsonify(to_dict), 200
        return Json

@app.route("/api/diff", methods = ["GET"])
def comp():
    baseline = request.args.get("baseline", type=int)
    current = request.args.get("current", type=int)
    if not baseline or not current:
        Json = jsonify({"error" : "baseline and current ids are required "}), 400
        return Json
    base_fetch = g.db.execute("SELECT id FROM scans WHERE id = ?", (baseline, )).fetchone()
    current_fetch = g.db.execute("SELECT id FROM scans WHERE id = ?", (current, )).fetchone()
    if not current_fetch  or not base_fetch:
        Json = jsonify({"error" : "current and baseline are not in the scans table"}), 404
        return Json
    com = compare(g.db, baseline, current)
    to_dict = com.to_dict()
    return jsonify(to_dict)

@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    Json = request.get_json()
    if not Json:
        error = jsonify({"error" : "json file isn't here"}), 400
        return error
    target = Json.get("target", "")
    valid  ,origin= valid_target(target)
    if not valid:
        error = jsonify({"error" :  origin}), 400
        return error
    project_id = Json.get("project_id", 1)
    max_pages = Json.get("max_pages", 10)
    max_depth = Json.get("max_depth", 2)
    scan = ScanConfig(max_depth, max_pages)
    cr = crawl(target, scan)
    evidence = []
    for l in cr.all_links:
        method = "href"
        evi = Evidence(target_url = l, source_url = target, discovery_method = method)
        evidence.append(evi)

    for s in cr.all_scripts:
        method = "script"
        evi = Evidence(target_url = s, source_url = target, discovery_method = method)
        evidence.append(evi)

    for f in cr.all_forms:
        method = "form"
        evi = Evidence(target_url = f, source_url = target, discovery_method = method)
        evidence.append(evi)

    for ss in cr.all_stylesheets:
        method = "stylesheet"
        evi = Evidence(target_url = ss, source_url = target, discovery_method = method)
        evidence.append(evi)
    save_s = save_scan(g.db, project_id, origin, cr, evidence)
    res = {"scan_id" : save_s, "status" : "completed", "pages_crawled" : cr.pages_crawled}
    Jsn = jsonify(res), 201
    return Jsn


@app.route("/api/scans/<int:scan_id>", methods=["GET"])
def query_scan_id(scan_id):
    fetch = g.db.execute("SELECT * FROM scans WHERE id = ?", (scan_id, )).fetchone()
    if not fetch:
        error = jsonify({"error" : "Scan not found"}), 404
        return error
    dic = dict(fetch)
    return jsonify(dic)

@app.route("/api/import-api", methods = ["POST"])
def query_import():
    Json = request.get_json()
    if not Json:       
        return jsonify({"error" : "json payload is required here "}), 400
    project_id = Json.get("project", 1)
    spec = Json.get("spec", Json)
    if not isinstance(spec, dict) or not spec.get("paths"):
        error = jsonify({"error" : "valid open api is required here "}), 400
        return error
    parse = parse_api(spec)
    api_spec = save_api_spec(g.db, project_id, parse)
    dic = {"spec_id" : api_spec, "title" : parse.title, "operation_count" : len(parse.operations)}
    return jsonify(dic), 201   
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)