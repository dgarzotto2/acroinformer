# fraud_detector.py

import re
from typing import List, Dict, Any
from collections import defaultdict

def normalize_minute(creation_date: str) -> str:
    """
    Collapse a PDF CreationDate to minute precision: YYYYMMDDHHMM
    Expects strings like 'D:20250529123000Z' or '2025-05-29T12:30:00'.
    """
    # Try PDF date format D:YYYYMMDDHHmmSS
    m = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})", creation_date)
    if m:
        return "".join(m.groups())  # YYYYMMDDHHMM
    # Fallback ISO-like
    m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})", creation_date)
    if m2:
        return "".join(m2.groups())  # YYYYMMDDHHMM
    # Last resort: take first 12 chars
    return creation_date.replace("-", "").replace(":", "")[:12]

def detect_mass_fraud(metadatas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify clusters of PDFs that share the same minute_key but have differing
    XMP toolkit values. Returns a list of groups:
      - minute_key
      - toolkit_values: list of distinct xmp_toolkit values
      - docs: the metadata dicts in that cluster
    """
    groups = defaultdict(list)
    for md in metadatas:
        cd = md.get("creation_date")
        if not cd:
            continue
        key = normalize_minute(cd)
        groups[key].append(md)

    fraud_clusters = []
    for minute_key, docs in groups.items():
        if len(docs) < 2:
            continue
        tk_values = {doc.get("xmp_toolkit") for doc in docs}
        if len(tk_values) > 1:
            fraud_clusters.append({
                "minute_key": minute_key,
                "toolkit_values": sorted(tk_values),
                "docs": docs
            })
    return fraud_clusters