from typing import Dict, List

def compare_metadata(md1: Dict, md2: Dict) -> List[Dict]:
    """
    Returns a list of dicts for each key:
      - field, file1_value, file2_value, mismatch (bool)
    Avoids heavy pandas dependency.
    """
    keys = sorted(set(md1) | set(md2))
    rows = []
    for k in keys:
        v1 = md1.get(k)
        v2 = md2.get(k)
        rows.append({
            "field": k,
            "file1": str(v1),
            "file2": str(v2),
            "mismatch": v1 != v2
        })
    return rows