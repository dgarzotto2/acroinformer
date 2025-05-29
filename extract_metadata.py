import fitz  # PyMuPDF
import hashlib
from PyPDF2 import PdfReader
from lxml import etree
import re

def extract_metadata(file_path, file_bytes):
    metadata = {
        "producer": None,
        "creator": None,
        "creation_date": None,
        "mod_date": None,
        "xmp_toolkit": None,
        "document_id": None,
        "instance_id": None,
        "has_acroform": False,
        "has_xfa": False,
        "has_valid_signature": False,
        "suspect_overlay": False,
    }

    try:
        reader = PdfReader(file_path)
        doc_info = reader.metadata or {}

        metadata["producer"] = doc_info.get("/Producer")
        metadata["creator"] = doc_info.get("/Creator")
        metadata["creation_date"] = doc_info.get("/CreationDate")
        metadata["mod_date"] = doc_info.get("/ModDate")

        # Check AcroForm presence
        if "/AcroForm" in reader.trailer["/Root"]:
            metadata["has_acroform"] = True
            acroform = reader.trailer["/Root"]["/AcroForm"]
            if "/XFA" in acroform:
                metadata["has_xfa"] = True

        # Check for digital signature field
        for page in reader.pages:
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    obj = annot.get_object()
                    if obj.get("/FT") == "/Sig":
                        metadata["has_valid_signature"] = True

        # Fallback signature or overlay detection (image paste check)
        if file_bytes:
            preview_score = file_bytes.count(b"Preview") + file_bytes.count(b"/Image")
            if preview_score > 5 and not metadata["has_valid_signature"]:
                metadata["suspect_overlay"] = True

    except Exception as e:
        raise RuntimeError(f"Metadata parsing error: {e}")

    # Try extracting embedded XMP
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        xrefs = [x for x in doc.xref_length()]
        for xref in xrefs:
            try:
                xobj = doc.xref_object(xref)
                if b"xpacket" in xobj:
                    xml_start = xobj.find(b"<?xpacket begin=")
                    xml_end = xobj.find(b"<?xpacket end=", xml_start)
                    xmp_raw = xobj[xml_start:xml_end]
                    tree = etree.fromstring(xmp_raw)
                    toolkit = tree.xpath("//*[local-name()='xmpToolkit']/text()")
                    docid = tree.xpath("//*[local-name()='DocumentID']/text()")
                    instid = tree.xpath("//*[local-name()='InstanceID']/text()")
                    if toolkit:
                        metadata["xmp_toolkit"] = toolkit[0]
                    if docid:
                        metadata["document_id"] = docid[0]
                    if instid:
                        metadata["instance_id"] = instid[0]
                    break
            except Exception:
                continue
    except Exception as e:
        pass

    return metadata