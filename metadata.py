# /mount/src/acroinformer/metadata.py

import fitz  # PyMuPDF
import re
import os

def extract_metadata(pdf_path):
    result = {
        "cid_font_detected": False,
        "xfa_found": False,
        "acroform_detected": False,
        "launch_action": False,
        "embedded_js": [],
        "hidden_lib_usage": False,
        "byte_range_mismatch": False,
        "overlay_detected": False,
        "xmp_toolkit": "Unknown",
        "pdf_producer": "Unknown",
        "risk_score": 0,
        "notes": []
    }

    try:
        doc = fitz.open(pdf_path)

        # Check for CID fonts
        for page in doc:
            fonts = page.get_fonts(full=True)
            for f in fonts:
                if "/CIDFont" in str(f):
                    result["cid_font_detected"] = True
                    result["notes"].append("CID font usage detected (may indicate glyph masking)")
                    break

        # Check AcroForm and XFA
        try:
            xfa_data = doc.xfa
            if xfa_data:
                result["xfa_found"] = True
                result["notes"].append("XFA form found (used for dynamic or hidden fields)")
        except Exception:
            pass

        if "AcroForm" in doc.pdf_catalog():
            result["acroform_detected"] = True
            result["notes"].append("AcroForm object detected")

        # Check for embedded JavaScript
        for i in range(len(doc)):
            js = doc.get_page_text("rawdict", i).get("js")
            if js:
                result["embedded_js"].append(js)
                result["notes"].append("Embedded JavaScript found on page")

        # LaunchAction
        for i in range(len(doc)):
            raw = doc.get_page_text("rawdict", i)
            if "Launch" in str(raw):
                result["launch_action"] = True
                result["notes"].append("LaunchAction trigger detected")
                break

        # Check overlay (preview-only)
        text_sample = "".join([doc[i].get_text() for i in range(min(len(doc), 3))])
        if text_sample.strip().lower() == "preview":
            result["overlay_detected"] = True
            result["notes"].append("Preview-only overlay detected (possible suppression)")

        # ByteRange mismatch
        if "/ByteRange" in doc.metadata:
            b_range = doc.metadata.get("/ByteRange")
            if isinstance(b_range, str) and len(b_range.split()) > 4:
                result["byte_range_mismatch"] = True
                result["notes"].append("Suspicious ByteRange length")

        # Extract metadata fields
        meta = doc.metadata or {}
        result["xmp_toolkit"] = meta.get("xmp:Toolkit", "Unknown")
        result["pdf_producer"] = meta.get("producer", "Unknown")

        # Hidden lib usage (BFO/iText/ABCpdf)
        if any(lib in result["pdf_producer"] for lib in ["iText", "BFO", "ABCpdf", "Appligent", "Prince", "jsPDF"]):
            result["hidden_lib_usage"] = True
            result["notes"].append(f"Known obfuscation toolkit: {result['pdf_producer']}")

        # Risk score
        risk = 0
        if result["cid_font_detected"]:
            risk += 20
        if result["xfa_found"]:
            risk += 15
        if result["launch_action"]:
            risk += 20
        if result["embedded_js"]:
            risk += 15
        if result["overlay_detected"]:
            risk += 20
        if result["hidden_lib_usage"]:
            risk += 10
        if result["byte_range_mismatch"]:
            risk += 10

        result["risk_score"] = risk

        doc.close()
        return result

    except Exception as e:
        return {"error": str(e), "risk_score": 100, "notes": ["Failed to analyze PDF. Possibly malformed or encrypted."]}