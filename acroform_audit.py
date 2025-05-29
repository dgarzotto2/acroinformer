def audit_acroform_fields(field_data):
    """
    Analyze AcroForm/XFA structure to detect signs of synthetic generation or reuse.
    Input:
        field_data: dict with AcroForm/XFA info from each PDF
            e.g., {
                "filename.pdf": {
                    "acroform_fields": [...],
                    "xfa_fields": [...],
                    "form_flags": {...}
                },
                ...
            }
    Returns:
        dict with summary audit findings
    """
    results = {
        "empty_forms": [],
        "identical_fieldsets": [],
        "suspicious_templates": [],
        "summary": [],
    }

    filenames = list(field_data.keys())

    for fname, data in field_data.items():
        afields = data.get("acroform_fields", [])
        xfields = data.get("xfa_fields", [])
        flags = data.get("form_flags", {})

        if not afields and not xfields:
            results["empty_forms"].append(fname)
            results["summary"].append(f"{fname}: No AcroForm or XFA fields — possible static/pasted signature or image overlay.")

        if flags.get("needs_appearance") == False and flags.get("sig_flags") == 0:
            results["suspicious_templates"].append(fname)
            results["summary"].append(f"{fname}: Form does not require appearances and has no signature flags — may be synthetic.")

    # Compare field sets across documents
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            f1 = filenames[i]
            f2 = filenames[j]
            af1 = set(field_data[f1].get("acroform_fields", []))
            af2 = set(field_data[f2].get("acroform_fields", []))
            if af1 == af2 and af1:
                pair = f"{f1} vs {f2}"
                results["identical_fieldsets"].append(pair)
                results["summary"].append(f"{pair}: Identical AcroForm fields — form may have been cloned or mass-reused.")

    return results