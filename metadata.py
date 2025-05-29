import fitz  # PyMuPDF
import PyPDF2

def extract_metadata(pdf_path):
    results = {
        "fonts_used": set(),
        "embedded_js": [],
        "cid_font_detected": False,
        "xfa_found": False,
        "acroform_detected": False,
        "launch_action": False,
        "hidden_lib_usage": False,
    }

    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if "/AcroForm" in reader.trailer.get("/Root", {}):
                results["acroform_detected"] = True
                af = reader.trailer["/Root"]["/AcroForm"]
                if "/XFA" in af:
                    results["xfa_found"] = True
                if "/Fields" in af and isinstance(af["/Fields"], list):
                    for field in af["/Fields"]:
                        try:
                            obj = field.get_object()
                            if "/AA" in obj and "/Launch" in obj["/AA"]:
                                results["launch_action"] = True
                        except Exception:
                            pass
    except Exception as e:
        results["error_reading_py"] = str(e)

    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font = span.get("font", "")
                            results["fonts_used"].add(font)
                            if "/CIDFont" in font:
                                results["cid_font_detected"] = True

        js = doc.get_js()
        if js:
            results["embedded_js"].append(js)
    except Exception as e:
        results["error_reading_fitz"] = str(e)

    results["fonts_used"] = list(results["fonts_used"])
    if any("xfa" in f.lower() or "launch" in f.lower() for f in results["fonts_used"]):
        results["hidden_lib_usage"] = True

    return results