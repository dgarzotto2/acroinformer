# decode_controller.py

import os
import hashlib
import tempfile
from pdf_utils import extract_text_and_entities
from metadata import extract_metadata
from license_checker import check_pdf_license
from suppression_detector import detect_suppression_flags
from gpt_fraud_summary import generate_fraud_summary

# Optional: stores seen metadata for batch analysis
seen_metadata = {}

def decode_pdf(file_path):
    filename = os.path.basename(file_path)

    try:
        # Text & entity extraction
        entities = extract_text_and_entities(file_path)

        # Metadata
        metadata = extract_metadata(file_path)

        # License flags (GPL, AGPL)
        license_flags = check_pdf_license(metadata)

        # Suppression pattern scan (CID font, Unicode map, etc.)
        suppression_flags = detect_suppression_flags(file_path)

        # Detect batch-level fraud via metadata reuse
        batch_flags = []
        key_tuple = (
            metadata.get("/Producer"),
            metadata.get("/Author"),
            metadata.get("/CreationDate"),
            metadata.get("/ModDate")
        )
        if key_tuple in seen_metadata.values():
            batch_flags.append("Document shares metadata with another file in this batch (potential duplication or forgery).")
        seen_metadata[filename] = key_tuple

        # GPT Fraud Summary
        summary = generate_fraud_summary(
            entities=entities,
            metadata=metadata,
            filename=filename,
            suppression_flags=suppression_flags,
            license_flags=license_flags,
            batch_duplicates=batch_flags
        )

        return {
            "filename": filename,
            "sha256": compute_sha256(file_path),
            "entities": entities,
            "metadata": metadata,
            "suppression_flags": suppression_flags,
            "license_flags": license_flags,
            "batch_flags": batch_flags,
            "gpt_summary": summary
        }

    except Exception as e:
        return {
            "filename": filename,
            "error": str(e)
        }

def compute_sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()