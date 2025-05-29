from PyPDF2 import PdfReader

def list_form_fields(file_path: str) -> list:
    """
    Returns a list of all AcroForm field names.
    """
    reader = PdfReader(file_path)
    root = reader.trailer.get("/Root", {})
    if "/AcroForm" not in root:
        return []
    acro = root["/AcroForm"]
    names = []
    for fld in acro.get("/Fields", []):
        try:
            obj = fld.get_object()
            names.append(obj.get("/T"))
        except Exception:
            continue
    return names