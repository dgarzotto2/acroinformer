import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import hashlib
import re

def extract_metadata(file_path, file_bytes):
    metadata = {}

    # SHA256 Hash
    metadata["sha256"] = hashlib.sha256(file_bytes).hexdigest()

    try:
        reader = PdfReader(file_path)
        metadata["num_pages"] = len(reader.pages)
        metadata["pdf_version"] = reader.pdf_header_version

        # Document Info
        doc_info = reader.metadata or {}
        metadata["title"] = doc_info.get("/Title", "")
        metadata["author"] = doc_info.get("/Author", "")
        metadata["producer"] = doc_info.get("/Producer", "")
        metadata["creator"] = doc_info.get("/Creator", "")
        metadata["created"] = doc_info.get("/CreationDate", "")
        metadata["modified"] = doc_info.get("/ModDate", "")
        metadata["xmp_metadata"] = reader.xmp_metadata

        # Form fields
        try:
            metadata["has_acroform"] = "/AcroForm" in reader.trailer["/Root"]
            metadata["acroform_fields"] = list(reader.get_fields() or {}).keys()
        except:
            metadata["has_acroform"] = False
            metadata["acroform_fields"] = []
    except Exception as e:
        metadata["error"] = f"PyPDF2 failed: {str(e)}"

    # Render using MuPDF to double check fonts and stream content
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        metadata["fonts"] = list(set([
            x["font"] for page in doc for x in page.get_text("dict")["blocks"]
            if "lines" in x for line in x["lines"] for span in line["spans"]
        ]))
    except Exception as e:
        metadata["fonts"] = []
        metadata["fitz_error"] = str(e)

    return metadata