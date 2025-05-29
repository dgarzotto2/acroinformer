import hashlib
import fitz  # PyMuPDF
import PyPDF2
import xml.etree.ElementTree as ET

def extract_metadata(file_path, file_bytes):
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    result = {
        "filename": file_path.split("/")[-1],
        "sha256": sha256,
        "producer": None,
        "creator": None,
        "creation_date": None,
        "mod_date": None,
        "xmp_toolkit": None,
        "xmp_instance_id": None,
        "xmp_document_id": None,
        "has_acroform": False,
        "has_signature": False,
        "signature_type": "none"
    }

    # --- Classic PDF Metadata ---
    try:
        reader = PyPDF2.PdfReader(file_path)
        info = reader.metadata or {}

        result["producer"] = info.get("/Producer")
        result["creator"] = info.get("/Creator")
        result["creation_date"] = info.get("/CreationDate")
        result["mod_date"] = info.get("/ModDate")

        if "/AcroForm" in reader.trailer["/Root"]:
            result["has_acroform"] = True
            acro = reader.trailer["/Root"]["/AcroForm"]
            if acro.get("/SigFlags") or acro.get("/Fields"):
                result["has_signature"] = True
                result["signature_type"] = "digital"
    except Exception as e:
        pass  # Allow fallback to PyMuPDF if PyPDF2 fails

    # --- Signature Check with PyMuPDF (for visible overlays) ---
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "image" in b.get("type", "") or "/Sig" in str(b):
                    result["has_signature"] = True
                    if result["signature_type"] == "none":
                        result["signature_type"] = "image"
    except Exception:
        pass

    # --- XMP Metadata Parsing ---
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        xmp = doc.metadata.get("xmp")
        if xmp:
            root = ET.fromstring(xmp)
            for elem in root.iter():
                tag = elem.tag.lower()
                text = elem.text
                if tag.endswith("xmp:creatortoolkit") or "xmptoolkit" in tag:
                    result["xmp_toolkit"] = text
                elif tag.endswith("instanceid"):
                    result["xmp_instance_id"] = text
                elif tag.endswith("documentid"):
                    result["xmp_document_id"] = text
    except Exception:
        pass

    return result