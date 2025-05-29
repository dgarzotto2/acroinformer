import os
import fitz
import hashlib
import datetime
from modules.extract_metadata import extract_metadata
from modules.entity_extraction import extract_entities
from modules.ocr_fallback import run_ocr
from modules.geoip_resolver import resolve_geoip
from modules.gpt_fraud_summary import summarize_fraud
from modules.utils.utility import is_agpl_pdf

def decode_pdf(file_path):
    result = {
        "sha256": None,
        "metadata": {},
        "entities": [],
        "gps": [],
        "notes": [],
        "fraud_flags": [],
        "obfuscation_flags": [],
        "agpl_license_flag": False,
        "cid_font_usage": False,
    }

    with open(file_path, "rb") as f:
        file_bytes = f.read()
        result["sha256"] = hashlib.sha256(file_bytes).hexdigest()

    try:
        doc = fitz.open(file_path)
        metadata = extract_metadata(doc)
        result["metadata"] = metadata
        result["cid_font_usage"] = metadata.get("cid_fonts_detected", False)
        result["agpl_license_flag"] = is_agpl_pdf(metadata)
        if result["agpl_license_flag"]:
            result["fraud_flags"].append("PDF generated with AGPL/GPL-bound library")

        if metadata.get("byte_range_mismatch"):
            result["fraud_flags"].append("ByteRange tampering detected")

        result["entities"] = extract_entities(doc, metadata)
        result["gps"] = [e.get("gps") for e in result["entities"] if "gps" in e]
        if metadata.get("cid_fonts_detected"):
            result["obfuscation_flags"].append("CID font suppression likely")

    except Exception as e:
        result["notes"].append(f"PDF decoding error: {str(e)}")

    return result