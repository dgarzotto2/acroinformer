# pdf_utils.py

import hashlib
from PyPDF2 import PdfReader
from typing import Dict, Any

def extract_metadata(file_path: str, file_bytes: bytes) -> Dict[str, Any]:
    result = {
        "sha256": hashlib.sha256(file_bytes).hexdigest(),
        "file_size": len(file_bytes),
        "page_count": 0,
        "acroform_present": False,
        "xfa_present": False,
        "metadata": {},
        "errors": [],
    }

    try:
        reader = PdfReader(file_path)
        result["page_count"] = len(reader.pages)

        if "/AcroForm" in reader.trailer["/Root"]:
            result["acroform_present"] = True
            af = reader.trailer["/Root"]["/AcroForm"]
            if af.get("/XFA"):
                result["xfa_present"] = True

        doc_info = reader.metadata
        if doc_info:
            result["metadata"] = {
                k.replace("/", ""): v for k, v in doc_info.items() if isinstance(k, str)
            }

    except Exception as e:
        result["errors"].append(str(e))

    return result