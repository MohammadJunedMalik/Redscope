import argparse 
import json
import sys
from pathlib import Path
from redscope.config import ScanConfig
from redscope.db import init_db, create_project, save_scan, save_api_spec
from redscope.crawler import crawl
from redscope.compare import compare
from redscope.graph import make_graph
from redscope.api import parse_api
from redscope.scope import valid_target
from redscope.evidence import Evidence



banner = """
        ██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗
        ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
        ██████╔╝█████╗  ██║  ██║███████╗██║     ██║   ██║██████╔╝█████╗  
        ██╔══██╗██╔══╝  ██║  ██║╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝  
        ██║  ██║███████╗██████╔╝███████║╚██████╗╚██████╔╝██║     ███████╗
        ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝
                 [+] Evidence-Driven Attack Surface Intelligence [+]
"""

def project(conn, name: str) -> int:
    fetch = conn.execute("SELECT id from projects WHERE name=?", (name, )).fetchone()
    if fetch:
        return fetch["id"]
    else:
        return create_project(conn, name)


def handle_crawl(conn, args):
    ok, origin = valid_target(args.target)
    if ok == False:
        return f"[-] error: {origin}"
    max_pages = ScanConfig(max_pages=args.max_pages, max_depth=args.max_depth)
    print("----now Crawling has started here-----")
    cr = crawl(args.target, max_pages)
    evi = []
    for c in cr.all_links:
        link = Evidence(target_url=c, source_url=args.target, discovery_method="href")
        evi.append(link)
    for s in cr.all_scripts:
        scripts = Evidence(target_url=s, source_url=args.target, discovery_method="script")
        evi.append(scripts)
    for f in cr.all_forms:
        forms = Evidence(target_url=f, source_url=args.target, discovery_method="form")
        evi.append(forms)
    for ss in cr.all_stylesheets:
        stylesheets = Evidence(target_url=ss, source_url=args.target, discovery_method="stylesheet")
        evi.append(stylesheets)
    project_id = project(conn, args.project)
    scan = save_scan(conn, project_id, origin, cr, evi)

    print("<------!scan!------->")
    print(f"scan id: {scan}")
    print(f"total pages crawled: {cr.pages_crawled}")
    print(len(cr.all_links))
    print(len(cr.all_scripts))
    print(len(cr.all_forms))
    if cr.errors:
        for e in cr.errors:
            print(e)


def handle_diff(conn, args):
    result = compare(conn, baseline_scan_id=args.baseline, current_scan_id=args.current)
    print("-"*30)
    print(f" [+] total new endspoints: {result.new_count}")
    print(f"[+] total modified endpoints: {result.modified_count}")
    print(f" [+] total unchanged endpoints: {result.unchanged_count}")
    print(f" [+] total endpont not rediscovered: {result.not_rediscovered_count}")

    for d in result.diffs:
        if d.category != "unchanged":
            print(f" endpoints url: {d.url}")
            print(f" classification category: {d.category}")
            print(f"http status, old: {d.old_status} | new: {d.new_status}")
            print(f" details: {d.details}")



def handle_graph(conn, args):
    graph = make_graph(conn, scan_id=args.scan)
    print(f"<------------Scan ID is being inspected here : {args.scan}------------------->")
    print(f" [+] total nodes: {len(graph.nodes)}")
    print(f" total edges: {len(graph.edges)}")

    for n in graph.nodes:
        print(f" {n.label}, {n.status}, {n.resource_type}")
    if args.output:
        dic = graph.to_dict()
        Json = json.dumps(dic, indent=2)
        path = Path(args.output).write_text(Json)
        print("------------! file is saved in json !---------------->")


def handle_api(conn, args):
    path = Path(args.file)
    if not path.exists():
        print("[-] Error: file not found")
        return 
    read = path.read_text()
    Json = json.loads(read)
    spec = parse_api(Json)
    project_id = project(conn, args.project)
    db = save_api_spec(conn, project_id, spec)
    print("<----------imported the api here--------->")
    print(f" {db} | {spec.title} | {spec.version} | {spec.operations}")
    print(f" total no. of operations imported: {len(spec.operations)}")
    for s in spec.operations:
        print(f" {s.method} | {s.path}")

    





