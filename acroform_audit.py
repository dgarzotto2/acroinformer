from PyPDF2 import PdfReader

def audit_acroform_fields(file_bytes, filename="Unknown"):
    results = {
        "filename": filename,
        "has_acroform": False,
        "field_names": [],
        "empty_fields": [],
        "signature_fields": [],
        "synthetic_warnings": [],
        "raw_acroform_data": {},
    }

    try:
        reader = PdfReader(file_bytes)
        if "/AcroForm" not in reader.trailer["/Root"]:
            return results  # No AcroForm present

        results["has_acroform"] = True
        acroform = reader.trailer["/Root"]["/AcroForm"]
        fields = acroform.get("/Fields", [])

        for field in fields:
            field_obj = field.get_object()
            name = field_obj.get("/T", "")
            value = field_obj.get("/V", "")
            ftype = field_obj.get("/FT", "")
            results["field_names"].append(name)
            results["raw_acroform_data"][name] = {
                "value": str(value),
                "type": str(ftype),
            }

            if ftype == "/Sig":
                results["signature_fields"].append(name)

            if not value:
                results["empty_fields"].append(name)

        # Warnings for synthetic use
        if results["signature_fields"] and results["empty_fields"]:
            results["synthetic_warnings"].append("Some signature fields are empty – likely form shell reuse.")
        if any(n.lower() in ["sig1", "signhere", "signature"] for n in results["field_names"]):
            results["synthetic_warnings"].append("Generic field names suggest auto-template form usage.")
        if len(results["field_names"]) > 0 and not results["signature_fields"]:
            results["synthetic_warnings"].append("AcroForm present with no digital signature field – check for pasted images.")

    except Exception as e:
        results["synthetic_warnings"].append(f"AcroForm audit failed: {str(e)}")

    return results