from dataclasses import dataclass, field
from redscope.extracter import Extracterpage

observed = "observed"
referenced = "referenced"
inferred = "inferred"
method_seed = "seed"
method_href = "href"
method_script = "script"
method_stylesheet = "stylesheet"
method_form = "form"
method_http_fetch = "http_fetch"

# this one holds evidence items
@dataclass
class Evidence:
    target_url: str
    source_url: str = ""
    evidence_type: str = referenced
    discovery_method: str = method_href
    details: dict = field(default_factory=dict)

# it's an helper  that returns a human-readable explanation specifyiing why this one is trusted
def explain_confidence(evidence_type: str) -> str:
    if evidence_type == "observed":
        return "directly confirmed via http response from the target server"
    elif evidence_type == "referenced":
        return "discovered as a reference inside application code or markup, but not requested directly though"
    elif evidence_type == "inferred" :
        return "deduced from structural convention or headers without explicit reference"
    else:
        return "there is unknown evidence having confidence level"
# and lastly this boy  converts the raw sets of discoveries of links, stylesheets, forms and scripts into structured evidence objects and also remember their source_url
def evi_from_page(source_url: str, page: Extracterpage) -> list[Evidence]:
    rec = []
    for l in page.links:
        rec.append(Evidence(target_url=l, source_url=source_url, evidence_type = referenced, discovery_method= method_href))

    for s in page.scripts :
        rec.append(Evidence(target_url=s, source_url=source_url, evidence_type= referenced, discovery_method=method_script))

    for st in page.stylesheets:
        rec.append(Evidence(target_url=st, source_url=source_url, evidence_type = referenced, discovery_method = method_stylesheet))

    for f in page.forms:
        rec.append(Evidence(target_url=f, source_url=source_url, evidence_type = referenced, discovery_method = method_form))

    return rec



