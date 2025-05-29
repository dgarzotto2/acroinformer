import hashlib
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import re

def extract_metadata(file_path, file_bytes):
    sha256 = hashlib.sha256(file_bytes).hexdigest()

    # Fallback values
    creator = producer = creation_date = mod_date = xmp_toolkit = None
    signature_type = None
    form_fields = []

    # Primary PDF object parsing
    try:
        reader = PdfReader(file_path)
        doc_info = reader.metadata or reader.documentInfo or {}

        creator = doc_info.get("/Creator") or doc_info.get("Creator")
        producer = doc_info.get("/Producer") or doc_info.get("Producer")
        creation_date = doc_info.get("/CreationDate") or doc_info.get("CreationDate")
        mod_date = doc_info.get("/ModDate") or doc_info.get("ModDate")

        # AcroForm field extraction
        if "/AcroForm" in reader.trailer["/Root"]:
            acroform = reader.trailer["/Root"]["/AcroForm"]
            if "/Fields" in acroform:
                form_fields = [str(f.get_object()) for f in acroform["/Fields"]]

        # Signature check
        if "/AcroForm" in reader.trailer["/Root"]:
            sig_flags = acroform.get("/SigFlags")
            if sig_flags:
                signature_type = "Cryptographic Signature" if int(sig_flags) > 0 else "None"
    except Exception:
        pass

    # XMP parsing via PyMuPDF
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        xmp = doc.metadata
        xmp_toolkit = xmp.get("xmp:Toolkit")
    except Exception:
        pass

    return {
        "filename": file_path.split("/")[-1],
        "sha256": sha256,
        "creator": creator,
        "producer": producer,
        "creation_date": creation_date,
        "mod_date": mod_date,
        "xmp_toolkit": xmp_toolkit,
        "signature_type": signature_type,
        "form_fields": form_fields
    }