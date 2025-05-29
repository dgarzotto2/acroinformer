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
        "hidden_lib_usage": False
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

        # Check for XMP toolkit
        if reader.xmp_metadata:
            xmp = reader.xmp_metadata
            result["xmp_toolkit"] = getattr(xmp, 'xmp_toolkit', None)

        # Look for ByteRange (digital sig placeholder)
        for page in reader.pages:
            contents = str(page.get_contents())
            if "/ByteRange" in contents:
                result["byte_range"] = True
                break

        # Scan raw objects for AcroForm, XFA, LaunchAction
        for obj in reader.trailer["/Root"].values():
            raw = str(obj)
            if "/AcroForm" in raw:
                result["acroform"] = True
            if "/XFA" in raw:
                result["xfa_found"] = True
            if "/Launch" in raw:
                result["launch_action_found"] = True

        # Scan for CID fonts
        for page in reader.pages:
            resources = page.get("/Resources", {})
            fonts = resources.get("/Font", {})
            for font_obj in fonts.values():
                font_str = str(font_obj)
                if "/CIDFont" in font_str:
                    result["cid_fonts_present"] = True
                    break

        # Hidden lib markers
        all_text = ""
        for page in reader.pages:
            try:
                all_text += page.extract_text() or ""
            except:
                pass

        # Check for known JS library indicators
        libs = ["ABCpdf", "iText", "jsPDF", "Prince", "BFO", "Aspose", "AlivePDF"]
        for lib in libs:
            if lib.lower() in (result["producer"] or "").lower() or lib.lower() in all_text.lower():
                result["hidden_lib_usage"] = True
                break

    except Exception as e:
        result["error"] = f"Extraction failed: {str(e)}"

    return result