# pdf_utils.py

import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from lxml import etree
import hashlib

def extract_metadata(pdf_path):
    """
    Extracts metadata including XMP DocumentID, InstanceID, Producer, CreationDate,
    and any AcroForm field keys from the PDF.
    """
    metadata = {}
    try:
        reader = PdfReader(pdf_path)

        # PDF core metadata
        core = reader.metadata
        metadata["producer"] = core.get("/Producer", "")
        metadata["creation_date"] = core.get("/CreationDate", "").replace("D:", "")

        # AcroForm fields
        metadata["acroform_fields"] = []
        if "/AcroForm" in reader.trailer["/Root"]:
            form = reader.trailer["/Root"]["/AcroForm"]
            fields = form.get("/Fields", [])
            for f in fields:
                try:
                    obj = f.get_object()
                    if "/T" in obj:
                        metadata["acroform_fields"].append(obj["/T"])
                except Exception:
                    continue

        # XMP metadata (DocumentID and InstanceID)
        metadata["xmp:DocumentID"] = ""
        metadata["xmp:InstanceID"] = ""
        for page in reader.pages:
            if "/Metadata" in page:
                try:
                    xmp_raw = page["/Metadata"].get_data()
                    xml = etree.fromstring(xmp_raw)
                    for el in xml.iter():
                        tag = el.tag.lower()
                        if "documentid" in tag:
                            metadata["xmp:DocumentID"] = el.text
                        if "instanceid" in tag:
                            metadata["xmp:InstanceID"] = el.text
                except Exception:
                    continue
            break  # XMP found only once, usually on the first page

        return metadata

    except Exception as e:
        return {"error": str(e)}