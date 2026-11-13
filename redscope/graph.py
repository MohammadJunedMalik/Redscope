from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse

@dataclass
class Graphnode:
    id: int
    url: str
    label: str = ""
    resource_type: str = ""
    status: int = field(default=0)


@dataclass
class Graphedge:
    source: int 
    target: int
    relation_type: str = ""


@dataclass
class Attackgraph:
    nodes: list[Graphnode] = field(default_factory=list)
    edges: list[Graphedge] = field(default_factory=list)
    def to_dict(self) -> dict:
        return asdict(self)


def label(url: str) -> str:
    parse = urlparse(url)
    if parse:
        if parse.path and parse.path != "/":
            return parse.path
        else:
            return parse.netloc or "/"

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


