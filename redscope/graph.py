# so hello umm this one turns scan results into a direct graph structure for attack surface mapping and visualization
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse

#here this dataclass represents nodes in the graph, holds the database resource ID, url, a display label , resource type and the http status code
@dataclass
class Graphnode:
    id: int
    url: str
    label: str = ""
    resource_type: str = ""
    status: int = field(default=0)

# this class a drirected connection(edge) from a source resource id to target id with it's relationship also 
@dataclass
class Graphedge:
    source: int 
    target: int
    relation_type: str = ""


# this dataclass holds the list of all nodes and edges for a scan and the to dict function serealize the grapg into standard dictionary so it can be export as a json for fronted visualizers 
@dataclass
class Attackgraph:
    nodes: list[Graphnode] = field(default_factory=list)
    edges: list[Graphedge] = field(default_factory=list)
    def to_dict(self) -> dict:
        return asdict(self)

#  this function here helps to generates a clean, readable label for graph visualization
def label(url: str) -> str:
    parse = urlparse(url)
    if parse:
        if parse.path and parse.path != "/":
            return parse.path
        else:
            return parse.netloc or "/"

# and lastly this function here is the main builder function here so here are the queries of the resources joined with scan_resoources to build theblist of graphnode objects with the given scan_id, queries are distinct here from the edges so that scan construct the list of graphedge objects and it package them together and returns the complete Attack graph
def make_graph(conn, scan_id: int) -> Attackgraph:
    fetch_nodes = conn.execute("SELECT r.id, r.normalized_url, r.resource_type, sr.observed_status FROM resources r JOIN scan_resources sr ON  r.id = sr.resource_id WHERE sr.scan_id = ?", (scan_id, )).fetchall()
    nodes = []
    for r in fetch_nodes:
        graph_node = Graphnode(id = r["id"], url = r["normalized_url"], label = label(r["normalized_url"]), resource_type = r["resource_type"], status = r["observed_status"])
        nodes.append(graph_node)
    edges = []
    fetch_edges = conn.execute(" SELECT DISTINCT source_resource_id, target_resource_id, relation_type FROM edges where scan_id = ?", (scan_id, )).fetchall()
    for r in fetch_edges:
        graph_edge = Graphedge(r["source_resource_id"], r["target_resource_id"], r["relation_type"])
        edges.append(graph_edge)

    return Attackgraph(nodes=nodes, edges=edges)




