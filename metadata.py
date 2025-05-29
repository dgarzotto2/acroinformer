from PyPDF2 import PdfReader
import re

def extract_metadata(pdf_path):
    result = {
        "title": None,
        "author": None,
        "producer": None,
        "created": None,
        "modified": None,
        "xmp_toolkit": None,
        "byte_range": False,
        "acroform": False,
        "xfa_found": False,
        "cid_fonts_present": False,
        "launch_action_found": False,
        "hidden_lib_usage": False,
        "error": None,
    }

    try:
        reader = PdfReader(pdf_path)

        # Basic metadata
        doc_info = reader.metadata or {}
        result["title"] = doc_info.get("/Title")
        result["author"] = doc_info.get("/Author")
        result["producer"] = doc_info.get("/Producer")
        result["created"] = doc_info.get("/CreationDate")
        result["modified"] = doc_info.get("/ModDate")

        # XMP Toolkit
        try:
            if reader.xmp_metadata:
                xmp = reader.xmp_metadata
                result["xmp_toolkit"] = getattr(xmp, 'xmp_toolkit', None)
        except:
            result["xmp_toolkit"] = None

        # ByteRange scan
        for page in reader.pages:
            try:
                contents = str(page.get_contents())
                if "/ByteRange" in contents:
                    result["byte_range"] = True
                    break
            except:
                continue

        # Root object scans
        try:
            root_obj = reader.trailer.get("/Root", {})
            root_str = str(root_obj)

            if "/AcroForm" in root_str:
                result["acroform"] = True
            if "/XFA" in root_str:
                result["xfa_found"] = True
            if "/Launch" in root_str:
                result["launch_action_found"] = True
        except:
            pass

        # CID font detection
        try:
            for page in reader.pages:
                resources = page.get("/Resources", {})
                fonts = resources.get("/Font", {})
                for font_obj in fonts.values():
                    font_str = str(font_obj)
                    if "/CIDFont" in font_str:
                        result["cid_fonts_present"] = True
                        break
        except:
            pass

        # Library markers
        all_text = ""
        for page in reader.pages:
            try:
                all_text += page.extract_text() or ""
            except:
                continue

        known_libs = ["ABCpdf", "iText", "jsPDF", "Prince", "Aspose", "AlivePDF", "BFO"]
        for lib in known_libs:
            if lib.lower() in (result["producer"] or "").lower() or lib.lower() in all_text.lower():
                result["hidden_lib_usage"] = True
                break

    except Exception as e:
        result["error"] = f"Failed to parse PDF: {str(e)}"

    return result