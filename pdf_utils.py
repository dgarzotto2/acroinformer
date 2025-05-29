# pdf_utils.py

import fitz  # PyMuPDF
import hashlib
import re

def compute_sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except:
        return ""

def extract_metadata(file_name, file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    metadata = doc.metadata
    xmp_block = None
    for xref in range(doc.xref_length()):
        try:
            obj = doc.xref_object(xref)
            if "<x:xmpmeta" in obj:
                xmp_block = obj
                break
        except:
            continue
    doc_id, inst_id = None, None
    if xmp_block:
        doc_id_match = re.search(r"xmpMM:DocumentID=\"uuid:([^\"]+)\"", xmp_block)
        inst_id_match = re.search(r"xmpMM:InstanceID=\"uuid:([^\"]+)\"", xmp_block)
        if doc_id_match:
            doc_id = f"uuid:{doc_id_match.group(1)}"
        if inst_id_match:
            inst_id = f"uuid:{inst_id_match.group(1)}"

    form_fields = []
    for xref in range(doc.xref_length()):
        try:
            obj = doc.xref_object(xref)
            if "/FT /Tx" in obj and "/T (" in obj and "/V (" in obj:
                name = extract_between(obj, "/T (", ")")
                value = extract_between(obj, "/V (", ")")
                form_fields.append({"name": name, "value": value})
        except:
            continue

    return {
        "filename": file_name,
        "sha256": compute_sha256(file_bytes),
        "creation_date": metadata.get("creationDate", "unknown"),
        "mod_date": metadata.get("modDate", "unknown"),
        "xmp_document_id": doc_id,
        "xmp_instance_id": inst_id,
        "form_fields": form_fields,
    }
