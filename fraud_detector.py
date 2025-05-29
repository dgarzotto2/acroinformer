# fraud_detector.py

import re
from collections import defaultdict
from typing import List, Dict, Any

def normalize_minute(creation_date: str) -> str:
    """
    Collapse a CreationDate to minute precision: YYYYMMDDHHMM.
    Supports PDF D:YYYYMMDDHHmmSS and ISO formats.
    """
    m = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})", creation_date or "")
    if m:
        return "".join(m.groups())         # YYYYMMDDHHMM
    m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})", creation_date or "")
    if m2:
        return "".join(m2.groups())       # YYYYMMDDHHMM
    return (creation_date or "").replace("-", "").replace(":", "")[:12]

def detect_mass_fraud(metadatas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify clusters of PDFs produced in the same minute_key but
    carrying differing XMP toolkit values.
    Returns list of { minute_key, toolkit_values, docs }.
    """
    groups = defaultdict(list)
    for md in metadatas:
        key = normalize_minute(md.get("creation_date", ""))
        groups[key].append(md)

    fraud = []
    for minute_key, docs in groups.items():
        if len(docs) < 2:
            continue
        tk_values = {doc.get("xmp_toolkit") for doc in docs}
        if len(tk_values) > 1:
            fraud.append({
                "minute_key": minute_key,
                "toolkit_values": sorted(tk_values),
                "docs": docs
            })
    return fraud

def detect_producer_override(metadatas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find cases where the same DocumentID appears under multiple Producer values.
    Returns list of { document_id, original_producer, override_producer }.
    """
    by_id = {}
    overrides = []
    for md in metadatas:
        docid = md.get("document_id")
        prod  = md.get("producer") or ""
        if not docid:
            continue
        if docid in by_id and by_id[docid] != prod:
            overrides.append({
                "document_id":      docid,
                "original_producer": by_id[docid],
                "override_producer": prod
            })
        else:
            by_id[docid] = prod
    return overrides