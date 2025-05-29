from PyPDF2 import PdfReader
from lxml import etree

def extract_metadata(file_path: str, file_bytes: bytes) -> dict:
    """
    Extract basic PDF metadata, detect AcroForm and signature fields,
    parse XMP Toolkit, and detect stamp‐style signature overlays.
    """
    reader = PdfReader(file_path)
    info = reader.metadata or {}
    raw_xmp = reader.xmp_metadata

    # Parse XMP Toolkit
    xmp_toolkit = None
    if raw_xmp:
        try:
            root = etree.fromstring(raw_xmp)
            tk = root.find(".//{http://ns.adobe.com/xap/1.0/}Toolkit")
            if tk is not None:
                xmp_toolkit = tk.text
        except Exception:
            pass

    # Detect AcroForm & cryptographic signature fields
    has_acroform = "/AcroForm" in reader.trailer["/Root"]
    has_signature_field = False
    if has_acroform:
        acro = reader.trailer["/Root"]["/AcroForm"]
        for fld in acro.get("/Fields", []):
            try:
                if fld.get_object().get("/FT", "") == "/Sig":
                    has_signature_field = True
                    break
            except Exception:
                continue

    # Detect visible signature overlays (/Stamp annotations)
    signature_overlay_detected = False
    for page in reader.pages:
        annots = page.get("/Annots", [])
        for annot in annots:
            try:
                obj = annot.get_object()
                if obj.get("/Subtype") == "/Stamp":
                    signature_overlay_detected = True
                    break
            except Exception:
                continue
        if signature_overlay_detected:
            break

    # Core metadata
    producer      = info.get("/Producer")
    creation_date = info.get("/CreationDate")
    mod_date      = info.get("/ModDate")

    # Tamper‐risk heuristics
    tamper_risk = None
    if creation_date and mod_date and creation_date != mod_date:
        tamper_risk = "Timestamp mismatch"
    elif has_acroform and not has_signature_field:
        tamper_risk = "AcroForm without cryptographic signature"

    return {
        "producer": producer,
        "toolkit": producer,
        "xmp_toolkit": xmp_toolkit,
        "creation_date": creation_date,
        "mod_date": mod_date,
        "has_acroform": has_acroform,
        "has_signature_field": has_signature_field,
        "tamper_risk": tamper_risk,
        "signature_overlay_detected": signature_overlay_detected,
    }