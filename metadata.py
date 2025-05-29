import fitz  # PyMuPDF
import re
import os
from PyPDF2 import PdfReader

def extract_metadata(pdf_path):
    result = {
        "metadata": {},
        "js": [],
        "has_acroform": False,
        "has_xfa": False,
        "embedded_files": [],
        "font_warnings": [],
        "byte_range_mismatch": False,
        "hidden_lib_usage": False,
        "notes": [],
    }

    try:
        # Read metadata with PyMuPDF
        doc = fitz.open(pdf_path)
        meta = doc.metadata or {}
        result["metadata"] = meta

        # Check for embedded JavaScript
        for page in doc:
            blocks = page.get_text("rawdict")["blocks"]
            for b in blocks:
                if "js" in str(b).lower():
                    result["js"].append(str(b))

        # AcroForm / XFA detection
        reader = PdfReader(pdf_path)
        if "/AcroForm" in reader.trailer["/Root"]:
            result["has_acroform"] = True
            acroform = reader.trailer["/Root"]["/AcroForm"]
            if "/XFA" in acroform:
                result["has_xfa"] = True
                result["notes"].append("XFA form detected (potential dynamic overlay)")

        # Embedded file detection
        if "/Names" in reader.trailer["/Root"]:
            names = reader.trailer["/Root"]["/Names"]
            if "/EmbeddedFiles" in names:
                ef = names["/EmbeddedFiles"]
                result["embedded_files"].append(str(ef))
                result["notes"].append("Embedded files present (possible injection)")

        # Check fonts
        try:
            for page in reader.pages:
                if "/Resources" in page:
                    res = page["/Resources"]
                    if "/Font" in res:
                        fonts = res["/Font"]
                        for font_key in fonts:
                            font_obj = fonts[font_key]
                            font_str = str(font_obj.get_object())
                            if "/CIDFont" in font_str:
                                result["font_warnings"].append("CIDFont usage (may conceal glyph mappings)")
        except Exception as e:
            result["notes"].append(f"Font analysis error: {str(e)}")

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

        # Check for suspicious library markers
        with open(pdf_path, "rb") as f:
            raw = f.read()
            if b"ABCpdf" in raw or b"BFO" in raw or b"iText" in raw:
                result["hidden_lib_usage"] = True
                result["notes"].append("Generated using known obfuscating library (ABCpdf, iText, BFO)")

    except Exception as e:
        result["notes"].append(f"Metadata extraction failed: {str(e)}")

    return result