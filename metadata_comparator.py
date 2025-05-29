# metadata_comparator.py

from typing import Dict, List, Any

def compare_metadata(md1: Dict[str, Any], md2: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build a side-by-side comparison of two metadata dicts.
    Returns a list of { field, file1, file2, mismatch }.
    """
    keys = sorted(set(md1) | set(md2))
    rows: List[Dict[str, Any]] = []
    for k in keys:
        v1 = md1.get(k)
        v2 = md2.get(k)
        rows.append({
            "field":    k,
            "file1":    str(v1),
            "file2":    str(v2),
            "mismatch": v1 != v2
        })
    return rows