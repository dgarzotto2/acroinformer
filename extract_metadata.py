from PyPDF2 import PdfReader
from lxml import etree
import re

def extract_metadata(file_path, file_bytes):
    reader = PdfReader(file_path)
    info = reader.metadata or {}
    raw_xmp = reader.xmp_metadata
    xmp_toolkit = None

    # Attempt to parse XMP
    if raw_xmp:
        try:
            xml_root = etree.fromstring(raw_xmp)
            toolkit_el = xml_root.find(".//{adobe:ns:meta/}xmpmeta//{http://ns.adobe.com/xap/1.0/}Toolkit")
            if toolkit_el is not None:
                xmp_toolkit = toolkit_el.text
        except Exception:
            xmp_toolkit = None

    # Detect form fields and signature fields
    has_acroform = "/AcroForm" in reader.trailer["/Root"]
    has_signature_field = False
    if has_acroform:
        acroform = reader.trailer["/Root"]["/AcroForm"]
        fields = acroform.get("/Fields", [])
        for field in fields:
            try:
                if "/Sig" in field.get_object().get("/FT", ""):
                    has_signature_field = True
                    break
            except Exception:
                continue

    # Detect producer and creator
    producer = info.get("/Producer", None)
    creator = info.get("/Creator", None)
    toolkit = info.get("/PDFProducer", None)
    creation_date = info.get("/CreationDate", None)
    mod_date = info.get("/ModDate", None)

    # Flag possible tampering
    tamper_risk = None
    if creation_date and mod_date and creation_date != mod_date:
        tamper_risk = "Timestamp mismatch"
    if not has_signature_field and has_acroform:
        tamper_risk = "AcroForm with no cryptographic signature"

    return {
        "producer": producer,
        "creator": creator,
        "toolkit": toolkit,
        "xmp_toolkit": xmp_toolkit,
        "creation_date": creation_date,
        "mod_date": mod_date,
        "has_acroform": has_acroform,
        "has_signature_field": has_signature_field,
        "tamper_risk": tamper_risk,
    }