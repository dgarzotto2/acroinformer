from PyPDF2 import PdfReader
from datetime import datetime
import re

def clean_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value.strip("D:").split("+")[0], "%Y%m%d%H%M%S").isoformat()
    except Exception:
        return value

def extract_metadata(filepath, file_bytes):
    reader = PdfReader(filepath)
    info = reader.metadata or {}
    xmp = reader.xmp_metadata if hasattr(reader, "xmp_metadata") else {}

    meta = {
        "filename": filepath.split("/")[-1],
        "producer": info.get("/Producer", "Unknown"),
        "created": clean_date(info.get("/CreationDate")),
        "modified": clean_date(info.get("/ModDate")),
        "xmp_toolkit": xmp.get("xmp:CreatorTool") if xmp else None,
        "flags": []
    }

    # Detect reused XMP IDs
    if xmp:
        xmp_id = xmp.get("xmpMM:DocumentID")
        instance_id = xmp.get("xmpMM:InstanceID")
        if xmp_id and instance_id and xmp_id == instance_id:
            meta["flags"].append("XMP DocumentID matches InstanceID – static reuse")

    # Detect matching create/modify timestamps
    if meta["created"] and meta["modified"] and meta["created"] == meta["modified"]:
        meta["flags"].append("Created == Modified – potential batch document")

    # Detect Paycom signs
    if re.search(r"Paycom|signExe|sigId|csrf", str(file_bytes)):
        meta["flags"].append("Paycom submission endpoint or signature token detected")

    # Detect tool-based anomalies
    if "/Annots" not in str(reader.pages[0]):
        meta["flags"].append("Missing annotation dictionary – flattened form or image overlay")

    return meta