import fitz  # PyMuPDF
import hashlib
import re
import datetime

def extract_metadata(file_path: str) -> dict:
    result = {
        "filename": file_path.split("/")[-1],
        "sha256": "",
        "producer": None,
        "creator": None,
        "creation_date": None,
        "mod_date": None,
        "xmp_toolkit": None,
        "instance_id": None,
        "document_id": None,
        "metadata_flags": [],
        "raw_xmp": "",
    }

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            result["sha256"] = hashlib.sha256(file_bytes).hexdigest()

        doc = fitz.open(file_path)
        meta = doc.metadata

        result["producer"] = meta.get("producer")
        result["creator"] = meta.get("creator")
        result["creation_date"] = meta.get("creationDate")
        result["mod_date"] = meta.get("modDate")

        # Search for embedded XMP packet
        raw = file_bytes.decode(errors="ignore")
        xmp_match = re.search(r"<x:xmpmeta[\s\S]+?</x:xmpmeta>", raw)
        if xmp_match:
            xmp = xmp_match.group(0)
            result["raw_xmp"] = xmp

            # Extract common forensic markers
            toolkit_match = re.search(r"<xmp:Toolkit>([^<]+)</xmp:Toolkit>", xmp)
            if toolkit_match:
                result["xmp_toolkit"] = toolkit_match.group(1)

            iid_match = re.search(r"<xmpMM:InstanceID>[^:]+:([^<]+)</xmpMM:InstanceID>", xmp)
            if iid_match:
                result["instance_id"] = iid_match.group(1)

            docid_match = re.search(r"<xmpMM:DocumentID>[^:]+:([^<]+)</xmpMM:DocumentID>", xmp)
            if docid_match:
                result["document_id"] = docid_match.group(1)

            # Heuristic checks
            if result["instance_id"] == result["document_id"]:
                result["metadata_flags"].append("Single-use ID – no regeneration detected")
            elif result["instance_id"] and result["document_id"]:
                result["metadata_flags"].append("InstanceID ≠ DocumentID – reuse or flattening suspected")

            if result["xmp_toolkit"] and "Adobe" not in result["xmp_toolkit"]:
                result["metadata_flags"].append("Non-Adobe XMP toolkit – synthetic or 3rd-party generation")

        # Check for timestamp match
        if result["creation_date"] and result["mod_date"]:
            if result["creation_date"] == result["mod_date"]:
                result["metadata_flags"].append("Creation and modification dates are identical – likely mass-produced")
            else:
                # Check modification after creation
                try:
                    created = datetime.datetime.strptime(result["creation_date"][2:16], "%Y%m%d%H%M%S")
                    modified = datetime.datetime.strptime(result["mod_date"][2:16], "%Y%m%d%H%M%S")
                    if modified < created:
                        result["metadata_flags"].append("Modification date precedes creation date – metadata spoofing")
                except Exception:
                    pass

    except Exception as e:
        result["metadata_flags"].append(f"Metadata extraction failed: {str(e)}")

    return result