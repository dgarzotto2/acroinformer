# metadata.py

import fitz
from PyPDF2 import PdfReader

def extract_metadata(file_path):
    result = {
        "producer": None,
        "creator": None,
        "creation_date": None,
        "mod_date": None,
        "document_id": None,
        "xmp_toolkit": None,
        "fonts": [],
        "xfa_present": False,
        "acroform_present": False,
        "has_javascript": False,
        "notes": [],
    }

    try:
        reader = PdfReader(file_path)
        info = reader.metadata
        result["producer"] = getattr(info, "producer", None)
        result["creator"] = getattr(info, "creator", None)
        result["creation_date"] = getattr(info, "creation_date", None)
        result["mod_date"] = getattr(info, "modification_date", None)
        result["document_id"] = reader.trailer.get("/ID", [None])[0]

        try:
            root = reader.trailer["/Root"]
            if "/AcroForm" in root:
                result["acroform_present"] = True
            if "/XFA" in root.get("/AcroForm", {}):
                result["xfa_present"] = True
        except Exception:
            pass

    except Exception as e:
        result["notes"].append(f"Error reading PyPDF2 metadata: {e}")

    try:
        doc = fitz.open(file_path)
        fonts = set()
        js_found = False
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            if "font" in s:
                                fonts.add(s["font"])
        result["fonts"] = list(fonts)
        if doc.is_encrypted:
            result["notes"].append("Encrypted PDF – some metadata may be hidden.")

        js_found = any(doc.get_javascript())
        result["has_javascript"] = js_found

    except Exception as e:
        result["notes"].append(f"Error reading fonts or JS from fitz: {e}")

    return result