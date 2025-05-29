import PyPDF2
from PyPDF2.generic import IndirectObject

def extract_metadata(file_path):
    result = {
        "sha256": None,
        "metadata": {},
        "fraud_flags": [],
        "cid_font_usage": False,
        "agpl_license_flag": False,
        "error": None,
    }

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            doc_info = reader.metadata

            # Safely extract metadata
            meta_dict = {}
            for key in doc_info:
                val = doc_info[key]
                if isinstance(val, IndirectObject):
                    try:
                        val = val.get_object()
                    except:
                        val = str(val)
                meta_dict[str(key)] = str(val)
            result["metadata"] = meta_dict

            # Flag known AGPL-bound producers
            producer = str(meta_dict.get("/Producer", "")).lower()
            creator = str(meta_dict.get("/Creator", "")).lower()
            if any(x in producer for x in ["itext", "bfo", "ghostscript"]) or \
               any(x in creator for x in ["itext", "bfo", "ghostscript"]):
                result["agpl_license_flag"] = True

            # Detect CID usage in font dictionaries
            for page in reader.pages:
                if "/Resources" in page and "/Font" in page["/Resources"]:
                    fonts = page["/Resources"]["/Font"]
                    for font_ref in fonts.values():
                        font_obj = font_ref.get_object()
                        if "/Subtype" in font_obj and "/CIDFont" in str(font_obj["/Subtype"]):
                            result["cid_font_usage"] = True
                            break

    except Exception as e:
        result["error"] = f"Metadata extraction failed: {str(e)}"

    return result