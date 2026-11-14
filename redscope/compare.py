# here this file performs differentials analysis between 2 scans(baseline scan and the other is current scan) to track changes in the attack surface over time 

from dataclasses import dataclass, field, asdict

Category_New = "new" # this is found in the current scan but not in baseline scan
Category_Unchanged = "unchanged" # this is found in both scan and with same http status code 
Category_Modified = "modified"  # this is found in both scans but http status code changed 
Category_not_rediscovered = "not_rediscovered" # and this is again found in both scans but missing in the latest scan


# this dataclass here represents the diff on an individual url in the following categories defined in this dataclass
@dataclass
class Resourcediff:
    url: str
    resource_type: str = ""
    category: str = Category_New
    old_status: int | None = None
    new_status: int | None = None
    details: str = ""


#here this is the summary container of the entire comparison here
@dataclass 
class Scancomparison:
    baseline_scan_id: int
    current_scan_id: int
    diffs: list[Resourcediff] = (field(default_factory=list))
    new_count: int = 0
    unchanged_count: int = 0
    modified_count: int = 0
    not_rediscovered_count: int = 0
    def to_dict(self) -> dict:
        return asdict(self)


#and here ( uhhhhhhhhhhhhh,,,,,,, it's gonna be big but i have to explain )this comparison function fetches resources and status code for both scans from SQlite into dictionaries keyed by normalized url, it takes the set of union of all urls to ensure every url seen across or either scan is evaluated, it also loops through each url to classify it into one of the four drift categories updates the counters  , it also resolves the resource type ( means it prefers current scan and falls back to baseline) and lastly here it assembles all Resourcediff items into a Scancomparison result 
def compare(conn, baseline_scan_id: int, current_scan_id: int) -> Scancomparison:
    fetch_1 = conn.execute(" SELECT * FROM resources r JOIN scan_resources sr ON r.id = sr.resource_id WHERE sr.scan_id = ?", (baseline_scan_id, )).fetchall()
    normal_1 = {r["normalized_url"]: r for r in fetch_1}
    fetch_2 = conn.execute("SELECT * FROM resources r JOIN scan_resources sr ON r.id = sr.resource_id WHERE sr.scan_id = ?", (current_scan_id, )).fetchall()
    normal_2 = {r["normalized_url"]: r for r in fetch_2}
    all_url = (set(normal_1.keys()) | set(normal_2.keys()))
    new_count = unchanged_count = modified_count = not_rediscovered_count = 0
    diffs = []
    for all in all_url:
        if all in normal_2 and all not in normal_1:
            old_status = None
            new_status = normal_2[all]["observed_status"]
            category = Category_New
            new_count += 1
            details = "newly discovered"

        elif all not in normal_2 and all in normal_1:
            old_status = normal_1[all]["observed_status"]
            new_status = None
            details = "Observed previouslt but not rediscovered"
            not_rediscovered_count += 1
            category = Category_not_rediscovered

        elif all in normal_2 and all in normal_1:
            old_status = normal_1[all]["observed_status"]
            new_status = normal_2[all]["observed_status"]
            details = "changed"
            if old_status != new_status:
                category = Category_Modified
                modified_count += 1
            if old_status == new_status:
                category = Category_Unchanged
                unchanged_count += 1 
        if all in normal_2:
            resource_type = normal_2[all]["resource_type"] 
        else: 
            resource_type = normal_1[all]["resource_type"]
        diff = Resourcediff(url=all, resource_type = resource_type, category = category , old_status = old_status, new_status = new_status, details = details)
        diffs.append(diff)
    return Scancomparison(baseline_scan_id, current_scan_id, diffs=diffs, new_count=new_count, unchanged_count = unchanged_count, modified_count = modified_count, not_rediscovered_count = not_rediscovered_count) 



