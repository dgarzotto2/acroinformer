from metadata_comparator import compare_metadata

def test_compare_identical():
    md = {"a": 1, "b": 2}
    rows = compare_metadata(md, md)
    assert all(not r["mismatch"] for r in rows)

def test_compare_diff():
    md1 = {"a": 1}
    md2 = {"a": 2}
    rows = compare_metadata(md1, md2)
    assert any(r["mismatch"] for r in rows)