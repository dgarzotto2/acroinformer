import fitz  # PyMuPDF
import re
import os
from PyPDF2 import PdfReader

def extract_metadata(pdf_path):
    result = {
        "fonts_used": [],
        "embedded_js": [],
        "xfa_found": False,
        "launch_action": False,
        "acroform_detected": False,
        "hidden_lib_usage": False,
        "cid_font_detected": False,
    }

    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("rawdict")
                blocks = text.get("blocks", [])
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            font = span.get("font", "")
                            if font and font not in result["fonts_used"]:
                                result["fonts_used"].append(font)
                            # Detect CID font usage (e.g., /CIDFontType2)
                            font_str = str(font)
                            if font_str and "/CIDFont" in font_str:
                                print(f"[DEBUG] CID font detected on page {page_num}: {font_str}")
                                result["cid_font_detected"] = True

    except Exception as e:
        print(f"Error reading with fitz: {e}")

    # Try PyPDF2 for deeper structure
    try:
        reader = PdfReader(pdf_path)

        # AcroForm/XFA check
        if "/AcroForm" in reader.trailer["/Root"]:
            result["acroform_detected"] = True
            form = reader.trailer["/Root"]["/AcroForm"]
            if "/XFA" in form:
                result["xfa_found"] = True

        # LaunchAction or OpenAction
        root = reader.trailer["/Root"]
        if "/OpenAction" in root:
            result["launch_action"] = True

        # Embedded JavaScript
        if "/Names" in root and "/JavaScript" in root["/Names"]:
            result["embedded_js"].append("Root level JavaScript found")

        # Check for hidden libraries
        for page in reader.pages:
            content = page.get_contents()
            if content:
                content_data = content.get_data()
                if b"eval(" in content_data or b"this.exportDataObject" in content_data:
                    result["hidden_lib_usage"] = True

    except Exception as e:
        print(f"Error reading with PyPDF2: {e}")

    return result