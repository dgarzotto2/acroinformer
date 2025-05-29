import fitz  # PyMuPDF
import hashlib
import os
from PyPDF2 import PdfReader
from collections import defaultdict

def compute_sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def extract_basic_metadata(pdf_path):
    reader = PdfReader(pdf_path)
    metadata = reader.metadata or {}
    doc_id = reader.trailer.get("/ID", [None])[0]
    return {
        "title": metadata.get("/Title"),
        "author": metadata.get("/Author"),
        "producer": metadata.get("/Producer"),
        "creator": metadata.get("/Creator"),
        "creation_date": metadata.get("/CreationDate"),
        "mod_date": metadata.get("/ModDate"),
        "doc_id": doc_id,
        "custom_uuid": metadata.get("/UUID"),
    }

def extract_entities_and_fonts(pdf_path):
    entities = {"grantors": set(), "grantees": set()}
    cid_fonts_used = False
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        try:
            fonts = page.get("/Resources", {}).get("/Font", {})
            for font in fonts.values():
                font_obj = font.get_object()
                base_font = font_obj.get("/BaseFont", "")
                subtype = font_obj.get("/Subtype", "")
                if "CID" in subtype or "CID" in base_font:
                    cid_fonts_used = True
        except Exception:
            continue
    # Simple name matching example
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        if "grantor" in text.lower():
            entities["grantors"].add("Detected")
        if "grantee" in text.lower():
            entities["grantees"].add("Detected")
    except Exception:
        pass
    return entities, cid_fonts_used

def analyze_batch(pdf_paths):
    seen = defaultdict(set)
    results = []

    for path in pdf_paths:
        result = {}
        sha256 = compute_sha256(path)
        result["filename"] = os.path.basename(path)
        result["sha256"] = sha256
        meta = extract_basic_metadata(path)
        entities, cid_flag = extract_entities_and_fonts(path)

        result.update(meta)
        result["cid_font"] = cid_flag
        result["entities"] = entities
        result["fraud_flags"] = []

        # Cross-file duplication detection
        for field in ["title", "author", "producer", "creator", "creation_date", "doc_id", "custom_uuid"]:
            value = meta.get(field)
            if value and value in seen[field]:
                result["fraud_flags"].append(f"Duplicate {field}: {value}")
            if value:
                seen[field].add(value)

        for role in ["grantors", "grantees"]:
            for entity in entities[role]:
                if entity in seen[role]:
                    result["fraud_flags"].append(f"Repeated entity: {role[:-1]} {entity}")
                seen[role].add(entity)

        if cid_flag:
            result["fraud_flags"].append("CID font detected")

        results.append(result)

    return results