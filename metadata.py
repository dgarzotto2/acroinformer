from PyPDF2 import PdfReader
import os

def extract_metadata(file_path):
    result = {
        "obfuscation_libraries": [],
        "hidden_lib_usage": False,
        "byte_range_mismatch": False,
        "font_warnings": False,
        "has_xfa": False,
        "has_acroform": False,
        "embedded_files": False,
        "js": [],
        "notes": [],
    }

    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)

            # Producer and Creator
            info = reader.metadata
            producer = info.get("/Producer", "").lower() if info else ""
            creator = info.get("/Creator", "").lower() if info else ""

            if "abcpdf" in producer or "abcpdf" in creator:
                result["obfuscation_libraries"].append("ABCpdf")
                result["hidden_lib_usage"] = True
            if "itext" in producer or "itext" in creator:
                result["obfuscation_libraries"].append("iText")
                result["hidden_lib_usage"] = True
            if "bfo" in producer or "big.faceless" in producer:
                result["obfuscation_libraries"].append("BFO")
                result["hidden_lib_usage"] = True

            # Check for JavaScript
            if "/Names" in reader.trailer.get("/Root", {}):
                names = reader.trailer["/Root"]["/Names"]
                if "/JavaScript" in names:
                    js_names = names["/JavaScript"]
                    if isinstance(js_names, dict) and "/Names" in js_names:
                        js_array = js_names["/Names"]
                        for i in range(0, len(js_array), 2):
                            js_entry = js_array[i+1]
                            if "/JS" in js_entry:
                                js_code = js_entry["/JS"]
                                result["js"].append(str(js_code))

            # Check for embedded files
            catalog = reader.trailer["/Root"]
            if "/Names" in catalog:
                names_dict = catalog["/Names"]
                if "/EmbeddedFiles" in names_dict:
                    result["embedded_files"] = True

            # AcroForm and XFA detection
            if "/AcroForm" in catalog:
                result["has_acroform"] = True
                acroform = catalog["/AcroForm"]
                if isinstance(acroform, dict):
                    if "/XFA" in acroform:
                        result["has_xfa"] = True

            # CID font warning
            for page in reader.pages:
                if "/Resources" in page:
                    res = page["/Resources"]
                    if "/Font" in res:
                        fonts = res["/Font"]
                        for font_key in fonts:
                            font = fonts[font_key]
                            font_str = str(font)
                            if "/CIDFont" in font_str:
                                result["font_warnings"] = True
                                result["notes"].append(f"CID font detected in font {font_key}")

            # ByteRange check (only from trailer-level metadata if accessible)
            try:
                if info and "/ByteRange" in info:
                    b_range = info.get("/ByteRange")
                    if isinstance(b_range, str) and len(b_range.split()) > 4:
                        result["byte_range_mismatch"] = True
                        result["notes"].append("Suspicious ByteRange length")
            except Exception:
                pass

            # Final summary if no flags
            if not result["notes"]:
                result["notes"].append("No overt tampering or suppression techniques detected.")

    except Exception as e:
        result["notes"].append(f"Error during metadata extraction: {str(e)}")

    return result