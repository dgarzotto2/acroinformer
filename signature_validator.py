from PyPDF2 import PdfReader
import re

def validate_signatures(filepath, file_bytes):
    reader = PdfReader(filepath)
    results = {
        "has_acroform": False,
        "has_xfa": False,
        "has_sig_fields": False,
        "has_signature": False,
        "sig_names": [],
        "flags": []
    }

    # Check AcroForm
    root = reader.trailer.get("/Root")
    if root and "/AcroForm" in root:
        results["has_acroform"] = True
        acroform = root["/AcroForm"]

        # Check for XFA
        if "/XFA" in acroform:
            results["has_xfa"] = True
            results["flags"].append("XFA form structure present – likely system-generated")

        # Check signature fields
        fields = acroform.get("/Fields", [])
        for field in fields:
            try:
                field_obj = field.get_object()
                if "/FT" in field_obj and field_obj["/FT"] == "/Sig":
                    results["has_sig_fields"] = True
                    sig_name = field_obj.get("/T", "")
                    results["sig_names"].append(sig_name)
            except:
                continue

    # Byte-layer scan for embedded signature structures
    byte_str = file_bytes.decode("latin-1", errors="ignore")
    if re.search(r"/Sig|/ByteRange|/Contents", byte_str):
        results["has_signature"] = True
    else:
        results["flags"].append("No embedded signature object – may be pasted image or flattened")

    if not results["has_acroform"]:
        results["flags"].append("No AcroForm found – PDF likely static or scanned")

    return results