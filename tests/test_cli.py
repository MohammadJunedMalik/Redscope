from redscope.db import init_db, create_project, save_resource
from redscope.cli import project, handle_graph, handle_diff, handle_api, handle_crawl
import argparse
import json
from pathlib import Path


def test_project():
    init = init_db(":memory:")
    pro1 = project(init, "Alpha")
    pro2 = project(init, "Alpha")
    pro3 = project(init, "Beta")
    assert pro1 == pro2
    assert pro3 != pro1

def test_diff():
    init = init_db(":memory:")
    pro = create_project(init, "Diff Test")
    init.execute(" INSERT INTO scans (project_id, target_origin, status) VALUES (?, ?, ?) ", (1, "http://test.com", 'completed', ))
    init.execute(" INSERT INTO scans (project_id, target_origin, status) VALUES (?, ? ,?) ", (1, "http://test.com", 'completed'))
    init.commit()
    parse = argparse.Namespace(baseline=1, current=2)
    diff = handle_diff(init, parse)

def test_graph(tmp_path):
    init = init_db(":memory:")
    pro = create_project(init, "Scan")
    init.execute("INSERT INTO scans (project_id, target_origin, status) VALUES (?, ?, ?)", (1, "http://test.com", "completed"))
    res = save_resource(init, "http://test.com/login", resource_type="page")
    init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (1, res, 200))
    init.commit()
    path = str(tmp_path / "out.json")
    parse = argparse.Namespace(scan=1, output=path)
    graph = handle_graph(init, parse)
    assert Path(path).exists() == True


def test_api(tmp_path):
    init = init_db(":memory:")
    dic = {"openapi" : "3.0.0", "info" : {"title" : "Test API", "version" : "1.0.0"}, "paths" : {"/api/users" : {"get" : {"summary" : "Get users"}}}}
    Json = json.dumps(dic)
    path = tmp_path / "spec.json"
    path.write_text(Json)
    paths = str(path)
    parse = argparse.Namespace(file=paths, project="API Test")
    handle_api(init, parse)
    fetch_1 = init.execute("SELECT count(*) FROM api_spec").fetchone()[0]
    assert fetch_1 == 1
    fetch_2 = init.execute("SELECT count(*) FROM api_operations").fetchone()[0]
    assert fetch_2 == 1   


def test_api_not_found(tmp_path):
    init = init_db(":memory:")
    path = tmp_path / "nonexistent.json"
    parse = argparse.Namespace(file=str(path))
    handle_api(init, parse)
    fetch = init.execute("SELECT count(*) FROM api_spec").fetchone()[0]
    assert fetch == 0

def test_crawl():
    init = init_db(":memory:")
    parse = argparse.Namespace(target="ftp://invalid.com", project="scan", max_pages=10, max_depth=2)
    result = handle_crawl(init, parse)
    assert result.startswith("[-] error")
    
