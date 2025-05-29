import difflib

def compare_metadata(metadata_list):
    if len(metadata_list) < 2:
        return {"error": "At least two metadata records are required for comparison."}

    results = {
        "shared_xmp_ids": [],
        "identical_creation_times": [],
        "identical_modification_times": [],
        "shared_toolkits": [],
        "shared_acroform_flags": [],
        "warnings": [],
        "differences": {}
    }

    # Build pairwise comparisons
    for i in range(len(metadata_list)):
        for j in range(i + 1, len(metadata_list)):
            meta_a = metadata_list[i]
            meta_b = metadata_list[j]
            name_a = meta_a.get("filename", f"file_{i}")
            name_b = meta_b.get("filename", f"file_{j}")

            pair_name = f"{name_a} vs {name_b}"
            results["differences"][pair_name] = []

            # Check XMP IDs
            xmp_a = meta_a.get("xmp", {})
            xmp_b = meta_b.get("xmp", {})

            if xmp_a.get("xmpMM:DocumentID") == xmp_b.get("xmpMM:DocumentID"):
                if xmp_a.get("xmpMM:InstanceID") != xmp_b.get("xmpMM:InstanceID"):
                    results["shared_xmp_ids"].append(pair_name)
                    results["warnings"].append(
                        f"{pair_name}: Shared xmpMM:DocumentID but different InstanceIDs — likely duplication from template."
                    )

            # Check creation/mod times
            if meta_a.get("CreationDate") == meta_b.get("CreationDate"):
                results["identical_creation_times"].append(pair_name)
                results["warnings"].append(f"{pair_name}: Identical CreationDate — may be batch-generated.")
            if meta_a.get("ModDate") == meta_b.get("ModDate"):
                results["identical_modification_times"].append(pair_name)
                results["warnings"].append(f"{pair_name}: Identical ModDate — suggests simultaneous editing.")

            # Toolkit reuse
            if meta_a.get("xmp", {}).get("xmp:CreatorTool") == meta_b.get("xmp", {}).get("xmp:CreatorTool"):
                results["shared_toolkits"].append(pair_name)

            # AcroForm/XFA reuse
            if meta_a.get("acroform_flags") == meta_b.get("acroform_flags") and meta_a.get("acroform_flags") is not None:
                results["shared_acroform_flags"].append(pair_name)

            # Raw diff (truncated display)
            raw_a = str(meta_a)[:4000]
            raw_b = str(meta_b)[:4000]
            diff = list(difflib.unified_diff(raw_a.splitlines(), raw_b.splitlines()))
            results["differences"][pair_name] = diff[:50]  # limit for display

    return results