from redscope.graph import Graphnode, Graphedge, Attackgraph, make_graph, label
from redscope.db import init_db, create_project, save_scan
from redscope.crawler import Crawl
from redscope.evidence import Evidence

def test_label():
    assert label("http://example.com/about") == "/about"
    assert label("http://example.com/api/v1/users") == "/api/v1/users"
    assert label("http://example.com") == "example.com"






def test_graph():

    init = init_db(":memory:")
    project_id = create_project(init, "Graph Project")
    crawl_res = Crawl(target_url = "http://example.com/about",
                  visited_urls = {"http://example.com"},
                  all_links = {"http://example.com", "http://example.com/about"},
                  all_scripts={"http://example.com/bundle.js"},
                  all_stylesheets=set(),
                  all_forms=set(),)
    evi = [Evidence(target_url= "http://example.com", source_url = "http://example.com/about", discovery_method = "script"), Evidence(target_url = "http://example.com", source_url= "http://example.com/bundle.js", discovery_method = "script")]
    scan_id = save_scan(init, project_id, "http://example.com", crawl_res, evi)
    graph = make_graph(init, scan_id)
    assert isinstance(graph, Attackgraph)
    assert len(graph.nodes) >= 3
    assert len(graph.edges) == 2
    edge_1 = graph.edges[0]
    assert edge_1.relation_type in ("href", "script")
    data = graph.to_dict() 
    assert "nodes" in data
    assert "edges" in data 







