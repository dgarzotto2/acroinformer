import fitz  # PyMuPDF

def extract_metadata(pdf_path):
    result = {
        "metadata": {},
        "has_xfa": False,
        "has_acroform": False,
        "embedded_files": [],
        "js": [],
        "font_warnings": [],
        "notes": [],
        "hidden_lib_usage": False,
        "byte_range_mismatch": False,
        "obfuscation_libraries": []
    }

    known_obfuscators = {
        "ABCpdf": "ABCpdf",
        "iText": "iText",
        "Big Faceless": "BFO",
        "BFO": "BFO",
        "PDFLib": "PDFLib",
        "Prince": "Prince",
        "Flying Saucer": "Flying Saucer",
        "Apitron": "Apitron",
        "Aspose": "Aspose",
        "TallComponents": "TallPDF",
        "PdfSharp": "PdfSharp"
    }

    try:
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        result["metadata"] = meta

        # --- Obfuscation Library Detection ---
        obfuscators_found = []
        for key in [meta.get("producer", ""), meta.get("creator", "")]:
            for marker, lib in known_obfuscators.items():
                if marker.lower() in key.lower():
                    obfuscators_found.append(lib)
        result["obfuscation_libraries"] = list(set(obfuscators_found))
        if obfuscators_found:
            result["hidden_lib_usage"] = True
            result["notes"].append("PDF generated using known obfuscating library.")

        # --- Form & XFA Check ---
        if "XFA" in doc.xref_object(1):
            result["has_xfa"] = True
        if "/AcroForm" in str(doc.read_metadata()):
            result["has_acroform"] = True

        # --- Embedded JavaScript ---
        for page_num in range(len(doc)):
            page = doc[page_num]
            js = page.get_text("rawdict").get("js", "")
            if js:
                result["js"].append(js)

        # --- Embedded Files (via Names dictionary) ---
        if "Names" in doc.pdf_catalog():
            names_dict = doc.pdf_catalog()["Names"]
            if "EmbeddedFiles" in str(names_dict):
                result["notes"].append("Embedded files detected (not fully extracted).")

        # --- Font Warnings ---
        for i in range(len(doc)):
            page = doc[i]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0 and "font" in block:
                    font_str = block.get("font", "")
                    if "/CIDFont" in font_str:
                        result["font_warnings"].append("CID font usage detected – may suppress Unicode mapping.")

        # --- ByteRange Tamper Check ---
        try:
            b_range = meta.get("/ByteRange") or meta.get("ByteRange")
            if isinstance(b_range, str) and len(b_range.split()) > 4:
                result["byte_range_mismatch"] = True
                result["notes"].append("Suspicious ByteRange length – possible tampering.")
        except Exception:
            pass

    except Exception as e:
        result["notes"].append(f"Error reading PDF: {e}")

    return result