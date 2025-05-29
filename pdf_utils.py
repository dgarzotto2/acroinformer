# pdf_utils.py

import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from datetime import datetime

def extract_metadata(file_path, file_bytes):
    meta = {
        "file_path": file_path,
        "file_size": len(file_bytes),
        "acroform_present": False,
        "xfa_present": False,
        "flattened": None,
        "field_names": [],
        "field_count": 0,
        "metadata_fields": {},
        "creation_date": None,
        "mod_date": None,
        "pdf_version": None,
        "producer": None
    }

    try:
        reader = PdfReader(file_path)

        if "/AcroForm" in reader.trailer["/Root"]:
            meta["acroform_present"] = True
            form = reader.trailer["/Root"]["/AcroForm"]
            if "/Fields" in form:
                fields = form["/Fields"]
                meta["field_count"] = len(fields)
                for f in fields:
                    field_obj = f.get_object()
                    name = field_obj.get("/T", "")
                    if name:
                        meta["field_names"].append(str(name))

            if "/XFA" in form:
                meta["xfa_present"] = True

        doc_info = reader.metadata
        meta["metadata_fields"] = {k: str(v) for k, v in doc_info.items() if v is not None}

        meta["pdf_version"] = reader.pdf_header.replace("%PDF-", "") if hasattr(reader, "pdf_header") else None
        meta["producer"] = doc_info.get("/Producer", "")

        created = doc_info.get("/CreationDate", "")
        if created.startswith("D:"):
            try:
                meta["creation_date"] = parse_pdf_date(created)
            except:
                meta["creation_date"] = created

        modified = doc_info.get("/ModDate", "")
        if modified.startswith("D:"):
            try:
                meta["mod_date"] = parse_pdf_date(modified)
            except:
                meta["mod_date"] = modified

    except Exception as e:
        meta["error"] = f"PyPDF2 failed: {str(e)}"

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        flattened = True
        for page in doc:
            annots = page.annots()
            if annots:
                flattened = False
                break
        meta["flattened"] = flattened
    except Exception as e:
        meta["flattened"] = None
        meta["fitz_error"] = str(e)

    return meta


def parse_pdf_date(datestr):
    # Parses PDF date strings like D:20231206143000-08'00'
    try:
        clean = datestr.replace("D:", "").split("-")[0].split("+")[0]
        dt = datetime.strptime(clean[:14], "%Y%m%d%H%M%S")
        return dt.isoformat()
    except Exception:
        return datestr