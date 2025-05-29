import hashlib
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import xml.etree.ElementTree as ET


def extract_metadata(file_path, file_bytes):
    # Compute SHA-256
    sha256 = hashlib.sha256(file_bytes).hexdigest()

    # Load PDF with PyMuPDF
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pdf_version = doc.pdf_version

    # Load PDF with PyPDF2 for metadata
    reader = PdfReader(file_path)
    info = reader.metadata

    # Basic metadata
    producer = info.get("/Producer", "")
    creator = info.get("/Creator", "")
    creation_date = info.get("/CreationDate", "")
    mod_date = info.get("/ModDate", "")

    # Check for signature
    has_signature = any("/Sig" in str(field.get_object()) for field in reader.trailer.get("/Root", {}).get("/AcroForm", {}).get("/Fields", []) if hasattr(field, "get_object"))

    # Check for AcroForm
    has_acroform = "/AcroForm" in reader.trailer.get("/Root", {})

    # Extract XMP Metadata
    xmp_toolkit = ""
    doc_id = ""
    instance_id = ""
    try:
        xmp_xml = reader.xmp_metadata
        if xmp_xml:
            root = ET.fromstring(xmp_xml.get_data())
            ns = {"x": "adobe:ns:meta/", "xmpMM": "http://ns.adobe.com/xap/1.0/mm/", "xmp": "http://ns.adobe.com/xap/1.0/"}
            xmp_toolkit = root.find(".//x:xmpmeta", ns).attrib.get("x:xmptk", "")
            doc_id_el = root.find(".//xmpMM:DocumentID", ns)
            instance_id_el = root.find(".//xmpMM:InstanceID", ns)
            if doc_id_el is not None:
                doc_id = doc_id_el.text
            if instance_id_el is not None:
                instance_id = instance_id_el.text
    except Exception:
        pass

    # Flag conditions
    flags = []
    if creation_date == mod_date:
        flags.append("identical_timestamps")
    if xmp_toolkit and "Adobe" in xmp_toolkit and not has_signature:
        flags.append("no_signature_in_adobe_xmp")
    if doc_id == instance_id:
        flags.append("same_doc_and_instance_id")
    if not has_acroform:
        flags.append("no_acroform")
    if has_signature:
        flags.append("digital_signature_detected")

    return {
        "filename": file_path.split("/")[-1],
        "sha256": sha256,
        "producer": producer,
        "creator": creator,
        "creation_date": creation_date,
        "mod_date": mod_date,
        "pdf_version": pdf_version,
        "xmp_toolkit": xmp_toolkit,
        "doc_id": doc_id,
        "instance_id": instance_id,
        "acroform": has_acroform,
        "has_signature": has_signature,
        "flags": flags
    }