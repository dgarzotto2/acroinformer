import fitz  # PyMuPDF
import hashlib
import re

def validate_signatures(file_path: str) -> dict:
    result = {
        "signatures_found": False,
        "signature_fields": [],
        "xfa_present": False,
        "acroform_present": False,
        "visible_signature_images": [],
        "validation_notes": [],
        "signature_hashes": [],
    }

    try:
        doc = fitz.open(file_path)
        field_names = doc.get_form_fields()
        if field_names:
            result["acroform_present"] = True
            for name, field in field_names.items():
                if field.get("type") == "signature":
                    result["signatures_found"] = True
                    result["signature_fields"].append(name)
                    result["validation_notes"].append(f"Signature field '{name}' detected in AcroForm structure.")

        # Look for visual signatures (e.g. scanned or image overlays)
        for page in doc:
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                base_image = doc.extract_image(xref)
                if base_image:
                    img_bytes = base_image.get("image", b"")
                    sha256 = hashlib.sha256(img_bytes).hexdigest()
                    result["visible_signature_images"].append(f"xref {xref} SHA256 {sha256[:12]}...")
                    result["signature_hashes"].append(sha256)

        # Check for presence of XFA (common in synthetic workflows)
        xfa = doc.xfa
        if xfa:
            result["xfa_present"] = True
            result["validation_notes"].append("XFA stream present – may indicate synthetic or flattened form generation.")

        # Detect static signature overlays or fake fields
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        if re.search(r"signed by|approved by|signature of", full_text, re.I):
            result["validation_notes"].append("Text phrases suggest manual or static overlay signature.")

    except Exception as e:
        result["validation_notes"].append(f"Signature check failed: {str(e)}")

    return result