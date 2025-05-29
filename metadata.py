import fitz  # PyMuPDF
import re
import os

def extract_metadata(pdf_path):
    result = {
        "metadata": {},
        "embedded_js": [],
        "has_cid_fonts": False,
        "hidden_lib_usage": False,
        "byte_range_mismatch": False,
        "notes": []
    }

    try:
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        result["metadata"] = meta

        # Scan fonts for CID usage
        for page in doc:
            fonts = page.get_fonts(full=True)
            for font in fonts:
                if "CID" in font[3] or "CID" in font[0]:
                    result["has_cid_fonts"] = True
                    result["notes"].append("CID fonts detected — possible glyph masking")

        # Check for embedded JavaScript (basic placeholder)
        if "/Names" in doc.pdf_catalog():
            js_obj = doc.pdf_catalog().get("/Names", {}).get("/JavaScript", {})
            if js_obj:
                result["embedded_js"].append(str(js_obj))

        # Check for hidden JS libraries (text-based search)
        text = ""
        for page in doc:
            text += page.get_text()
        if any(lib in text.lower() for lib in ["jspdf", "html2pdf", "nodecanvas"]):
            result["hidden_lib_usage"] = True
            result["notes"].append("Suspicious PDF JS library references found")

        doc.close()

    except Exception as e:
        result["notes"].append(f"PyMuPDF error: {str(e)}")

    # ByteRange check (tamper detection)
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        if b"/ByteRange" in pdf_bytes:
            matches = re.findall(rb'/ByteRange\s*\[(.*?)\]', pdf_bytes, re.DOTALL)
            for match in matches:
                if len(match.strip().split()) > 4:
                    result["byte_range_mismatch"] = True
                    result["notes"].append("Suspicious ByteRange: too many elements")
    except Exception as e:
        result["notes"].append(f"ByteRange parsing error: {str(e)}")

    return result