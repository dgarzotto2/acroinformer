import hashlib

def compare_metadata(pdf_reports):
    comparison_results = {
        "shared_ids": [],
        "timestamp_clones": [],
        "toolkit_matches": [],
        "hash_collisions": [],
        "warnings": []
    }

    seen_doc_ids = {}
    seen_instance_ids = {}
    seen_creation_dates = {}
    seen_mod_dates = {}
    seen_toolkits = {}

    for report in pdf_reports:
        filename = report.get("filename", "Unknown")
        meta = report.get("metadata", {})

        # Normalize
        doc_id = meta.get("xmpMM:DocumentID", "").strip()
        inst_id = meta.get("xmpMM:InstanceID", "").strip()
        cdate = meta.get("CreationDate", "").strip()
        mdate = meta.get("ModDate", "").strip()
        toolkit = meta.get("xmp:Toolkit", "").strip()
        creator_tool = meta.get("xmp:CreatorTool", "").strip()
        sha = report.get("sha256", "")

        # DocumentID checks
        if doc_id:
            if doc_id in seen_doc_ids:
                comparison_results["shared_ids"].append((doc_id, seen_doc_ids[doc_id], filename))
            else:
                seen_doc_ids[doc_id] = filename

        # InstanceID checks
        if inst_id:
            if inst_id in seen_instance_ids:
                comparison_results["shared_ids"].append((inst_id, seen_instance_ids[inst_id], filename))
            else:
                seen_instance_ids[inst_id] = filename

        # Timestamp checks
        if cdate:
            if cdate in seen_creation_dates:
                comparison_results["timestamp_clones"].append((cdate, seen_creation_dates[cdate], filename))
            else:
                seen_creation_dates[cdate] = filename

        if mdate:
            if mdate in seen_mod_dates:
                comparison_results["timestamp_clones"].append((mdate, seen_mod_dates[mdate], filename))
            else:
                seen_mod_dates[mdate] = filename

        # Toolkit checks
        if toolkit or creator_tool:
            key = (toolkit, creator_tool)
            if key in seen_toolkits:
                comparison_results["toolkit_matches"].append((key, seen_toolkits[key], filename))
            else:
                seen_toolkits[key] = filename

    # Hash collision check
    hashes = {}
    for report in pdf_reports:
        sha = report.get("sha256", "")
        fname = report.get("filename", "")
        if sha in hashes:
            comparison_results["hash_collisions"].append((sha, hashes[sha], fname))
        else:
            hashes[sha] = fname

    # Warnings
    if not comparison_results["shared_ids"] and not comparison_results["timestamp_clones"]:
        comparison_results["warnings"].append("No forensic indicators of duplication found.")
    else:
        comparison_results["warnings"].append("⚠️ Multiple signs of reused identifiers or cloned timestamps.")

    return comparison_results