from redscope.db import init_db, create_project, save_resource
from redscope.compare import compare, Category_New, Category_Unchanged, Category_Modified, Category_not_rediscovered

def test_compare():
    init = init_db(":memory:")
    project = create_project(init, "Diff Project")
    scan_1 = init.execute("INSERT INTO scans (project_id, target_origin, status) VALUES (1, 'http://test.com', 'completed')")
    scan_2 = init.execute("INSERT INTO scans (project_id, target_origin, status) VALUES (1, 'http://test.com', 'completed')")
    same = "http://test.com/same"
    mod = "http://test.com/mod"
    old = "http://test.com/old"
    new = "http://test.com/new"
    baseline_scan_same = save_resource(init, same)
    baseline_scan_mod = save_resource(init, mod)
    baseline_scan_old = save_resource(init, old)
    baseline_scan_new = save_resource(init, new)

    
    scan_id_1_same = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (1, baseline_scan_same, 200))
    scan_id_1_mod = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (1, baseline_scan_mod, 200))
    scan_id_1_old = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (1, baseline_scan_old, 200))
    scan_id_2_same = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (2, baseline_scan_same, 200))
    scan_id_2_mod = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (2, baseline_scan_mod, 500))
    scan_id_2_mod = init.execute("INSERT INTO scan_resources (scan_id, resource_id, observed_status) VALUES (?, ?, ?)", (2, baseline_scan_new, 200))
    init.commit()
    result = compare(init, baseline_scan_id=1, current_scan_id=2)
    assert result.new_count == 1
    assert result.unchanged_count == 1
    assert result.modified_count == 1
    assert result.not_rediscovered_count == 1
    assert len(result.diffs) == 4
    assert result.to_dict()["baseline_scan_id"] == 1



