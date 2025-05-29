# metadata.py

import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from typing import Dict
from pdf_license_fingerprint import detect_pdf_license_fingerprint


def extract_metadata(file_path: str) -> Dict:
    result = {
        "metadata": {},
        "flags": [],
        "notes": [],
        "xfa_present": False,
        "cid_font_detected": False,
        "byte_range_mismatch": False,
        "pdf_license_risk": "None",
        "licensing_flags": []
    }

    try:
        # Load basic metadata with PyMuPDF
        doc = fitz.open(file_path)
        result["metadata"] = doc.metadata or {}

        # CID font detection (manual scan)
        try:
            for page in doc:
                font_list = page.get_fonts(full=True)
                for font in font_list:
                    if "/CIDFont" in str(font):
                        result["cid_font_detected"] = True
                        result["flags"].append("CID font encoding detected")
                        result["notes"].append("Font uses /CIDFont – possible glyph suppression")
                        break
                if result["cid_font_detected"]:
                    break
        except Exception as e:
            result["notes"].append(f"Font parsing error: {e}")

    except Exception as e:
        result["notes"].append(f"Error loading with PyMuPDF: {e}")

    # Supplement with PyPDF2
    try:
        reader = PdfReader(file_path)

        # ByteRange mismatch
        try:
            b_range = reader.trailer.get("/ByteRange", None)
            if b_range and hasattr(b_range, "get_object"):
                b_range = b_range.get_object()
            if isinstance(b_range, list) and len(b_range) > 4:
                result["byte_range_mismatch"] = True
                result["flags"].append("ByteRange longer than expected")
                result["notes"].append("Suspicious ByteRange length – may indicate tampering")
        except Exception as e:
            result["notes"].append(f"ByteRange error: {e}")

        # Check for XFA (XML Forms Architecture) overlays
        try:
            if "/XFA" in str(reader.trailer):
                result["xfa_present"] = True
                result["flags"].append("XFA detected")
                result["notes"].append("XFA form structure detected – possible flattening layer")
        except Exception as e:
            result["notes"].append(f"XFA detection error: {e}")

        # Extract full metadata dict
        pdf_info = {}
        try:
            if reader.metadata:
                for key, value in reader.metadata.items():
                    clean_key = key.replace("/", "")
                    pdf_info[clean_key] = str(value)
                result["metadata"].update(pdf_info)
        except Exception as e:
            result["notes"].append(f"Metadata parse error: {e}")

        # Detect AGPL/GPL licensed PDF generators
        license_info = detect_pdf_license_fingerprint(result["metadata"])
        if license_info["licensing_flag"]:
            result["licensing_flags"].append(license_info["licensing_flag"])
            result["pdf_license_risk"] = license_info["license_type"]

    except Exception as e:
        result["notes"].append(f"PyPDF2 load error: {e}")

    return result