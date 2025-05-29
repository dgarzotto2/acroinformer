import PyPDF2
from PyPDF2.generic import IndirectObject

def extract_metadata(file_path):
    result = {
        "metadata": {},
        "embedded_js": [],
        "tamper_flags": [],
        "notes": [],
        "obfuscating_library": None,
        "byte_range_mismatch": False,
        "has_launch_action": False,
        "hidden_lib_usage": False,
    }

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            doc_info = reader.metadata or {}

            # Convert indirect metadata safely
            metadata_clean = {}
            for key, value in doc_info.items():
                if isinstance(value, IndirectObject):
                    try:
                        value = value.get_object()
                    except Exception:
                        value = str(value)
                metadata_clean[str(key)] = str(value)
            result["metadata"] = metadata_clean

            # Detect suspicious producer/tool
            producer = metadata_clean.get("/Producer", "").lower()
            creator = metadata_clean.get("/Creator", "").lower()
            tool = producer + " " + creator

            if "abc" in tool or "bfo" in tool or "itext" in tool:
                result["obfuscating_library"] = producer or creator
                result["tamper_flags"].append("Known obfuscating PDF library used")
                result["notes"].append(f"Generated using obfuscating tool: {result['obfuscating_library']}")
                result["hidden_lib_usage"] = True

            # ByteRange checks
            try:
                if "/ByteRange" in reader.trailer:
                    br = reader.trailer["/ByteRange"]
                elif "/Root" in reader.trailer and "/ByteRange" in reader.trailer["/Root"]:
                    br = reader.trailer["/Root"]["/ByteRange"]
                else:
                    br = None

                if isinstance(br, IndirectObject):
                    br = br.get_object()

                if isinstance(br, list) and len(br) > 4:
                    result["byte_range_mismatch"] = True
                    result["notes"].append("Suspicious ByteRange length (may indicate tampering)")
            except Exception as e:
                result["notes"].append(f"ByteRange check error: {str(e)}")

            # Check for JavaScript and Launch Actions
            try:
                for page in reader.pages:
                    annots = page.get("/Annots")
                    if annots:
                        if isinstance(annots, IndirectObject):
                            annots = annots.get_object()
                        for annot in annots:
                            aobj = annot.get_object()
                            if "/A" in aobj:
                                action = aobj["/A"]
                                if "/JS" in action or action.get("/S") == "/JavaScript":
                                    js_code = action.get("/JS", "")
                                    result["embedded_js"].append(str(js_code))
                                    result["tamper_flags"].append("Embedded JavaScript detected")
                                if action.get("/S") == "/Launch":
                                    result["has_launch_action"] = True
                                    result["tamper_flags"].append("LaunchAction trigger detected")
                                    result["notes"].append("LaunchAction detected (may run executables)")
            except Exception as e:
                result["notes"].append(f"LaunchAction check error: {str(e)}")

    except Exception as e:
        result["notes"].append(f"Metadata extraction error: {str(e)}")
        result["tamper_flags"].append("Critical read error")

    return result