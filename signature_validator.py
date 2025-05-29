# signature_validator.py

from PyPDF2 import PdfReader

def validate_signatures(file_path):
    results = []
    try:
        reader = PdfReader(file_path)
        root = reader.trailer["/Root"]
        if "/AcroForm" in root:
            form = root["/AcroForm"]
            if "/SigFlags" in form:
                results.append("PDF includes signature flags.")
            if "/Fields" in form and len(form["/Fields"]) > 0:
                results.append(f"{len(form['/Fields'])} AcroForm fields found – inspect for overlays.")

        if "/Annots" in root:
            results.append("Page annotations present – potential for invisible overlays.")

    except Exception as e:
        results.append(f"Signature validation failed: {e}")

    return results