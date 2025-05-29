# pdf_utils.py

import fitz  # PyMuPDF
import hashlib
from PyPDF2 import PdfReader
from datetime import datetime

def extract_metadata(file_path):
    meta = {
        "creation_time": None,
        "modification_time": None,
        "xmp_document_id": None,
        "xmp_instance_id": None,
        "acroform_fields": [],
        "producer": None,
        "title": None,
        "author": None
    }

    try:
        reader = PdfReader(file_path)
        doc_info = reader.metadata

        meta["producer"] = doc_info.get('/Producer')
        meta["title"] = doc_info.get('/Title')
        meta["author"] = doc_info.get('/Author')

        # AcroForm fields
        if reader.trailer.get("/Root"):
            acro_form = reader.trailer["/Root"].get("/AcroForm")
            if acro_form and "/Fields" in acro_form:
                fields = acro_form["/Fields"]
                meta["acroform_fields"] = [str(f.get_object()) for f in fields]

        # Dates
        creation_date = doc_info.get('/CreationDate')
        mod_date = doc_info.get('/ModDate')
        if creation_date:
            meta["creation_time"] = parse_pdf_date(creation_date)
        if mod_date:
            meta["modification_time"] = parse_pdf_date(mod_date)

        # XMP metadata via PyMuPDF
        with fitz.open(file_path) as doc:
            xmp = doc.metadata
            meta["xmp_document_id"] = xmp.get("xmp:DocumentID")
            meta["xmp_instance_id"] = xmp.get("xmp:InstanceID")

    except Exception as e:
        meta["error"] = f"Metadata extraction failed: {str(e)}"

    return meta

def parse_pdf_date(d):
    try:
        if d.startswith("D:"):
            d = d[2:]
        return datetime.strptime(d[:14], "%Y%m%d%H%M%S").isoformat()
    except Exception:
        return d  # Fallback raw string

def compute_sha256(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None