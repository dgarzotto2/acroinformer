# decode_controller.py

import os
from metadata import extract_metadata
from suppression_detector import detect_suppression_flags
from license_checker import check_pdf_license
from gpt_fraud_summary import generate_fraud_summary
from entity_extraction import extract_entities
from signature_validator import validate_signatures

def decode_single_pdf(file_path):
    metadata = extract_metadata(file_path)
    suppression_flags = detect_suppression_flags(file_path)
    license_flags = check_pdf_license(metadata)
    signature_flags = validate_signatures(file_path)
    entities = extract_entities(file_path, metadata)
    summary = generate_fraud_summary(metadata, entities, suppression_flags)

    return {
        "filename": os.path.basename(file_path),
        "metadata": metadata,
        "entities": entities,
        "suppression_flags": suppression_flags,
        "license_flags": license_flags,
        "signature_flags": signature_flags,
        "summary": summary
    }

def decode_batch_pdfs(file_paths):
    results = []
    seen_keys = set()
    for path in file_paths:
        result = decode_single_pdf(path)
        batch_flags = []

        key = (
            result["metadata"].get("document_id"),
            str(result["metadata"].get("creation_date")),
            str(result["metadata"].get("entities"))
        )

        if key in seen_keys:
            batch_flags.append("❗ Duplicate document metadata detected across batch.")
        else:
            seen_keys.add(key)

        result["batch_duplicate_flags"] = batch_flags
        results.append(result)
    return results