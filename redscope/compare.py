from dataclasses import dataclass, field, asdict


Category_New = "new"
Category_Unchanged = "unchanged"
Category_Modified = "modified"
Category_not_rediscovered = "not_rediscovered"


@dataclass
class Resourcediff:
    url: str
    resource_type: str = ""
    category = str = Category_New
    old_status: int | None = None
    new_status: int | None = None
    details: str = ""

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



def compare(conn, baseline_scan_id: int, current_scan_id: int) -> Scancomparison:
    fetch_1 = conn.execute(" SELECT * FROM resources r JOIN scan_resources sr ON WHERE scan_id = baseline_scan_id").fetchall()
    normal_1 = {r["normalized_url"]: r for r in fetch_1}
    fetch_2 = conn.execute("SELECT * FROM resources r JOIN scan_resources sr ON WHERE sr.scan_id = ?", (baseline_scan_id, current_scan_id, )).fetchall()
    normal_2 = {r["normalize_url"]: r for r in fetch_2}
    all_url = (set(normal_1.keys()) | set(normal_2.keys()))
    diffs = []
    for all in all_url:
        if all in normal_2 and all not in normal_1:
            old_status = None
            new_status = normal_2[all]["observed_status"]
            category = Category_New
            new_count += 1
            details = "newly discovered"

        if all not in normal_2 and all in normal_1:
            old_status = normal_1[all]["observed_status"]
            new_status = None
            details = "Observed previouslt but not rediscovered"
            not_rediscovered_count += 1
            category = Category_not_rediscovered

        if all in normal_2 and all in normal_1:
            old_status = normal_1[all]["observed_status"]
            new_status = normal_2[all]["observed_status"]
            details = "Unchanged"
            if old_status != new_status:
                category = Category_Modified
                modified_count += 1
            if old_status == new_status:
                category = Category_Unchanged
                unchanged_count += 1 
        resource_type =  normal_2[all]["resource_type"]  
        if resource_type:
            continue
        else:
            resource_type = normal_1[all]["resource_type"] 
        diff = Resourcediff(url=all, resource_type = resource_type, category = category , old_status = old_status, new_status = new_status, details = details)
        diffs.append(diff)
    return Scancomparison(baseline_scan_id, current_scan_id, diffs=diffs, new_count=new_count, unchanged_count = unchanged_count, modified_count = modified_count, not_rediscovered_count = not_rediscovered_count) 



