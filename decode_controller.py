# decode_controller.py

import os
from pdf_utils import extract_text_and_entities
from metadata import extract_metadata
from license_checker import check_pdf_license
from suppression_detector import detect_suppression_flags
from gpt_fraud_summary import generate_fraud_summary

def decode_single_pdf(file_path):
    result = {}

    # Extract raw entities and text
    entities = extract_text_and_entities(file_path)

    # Extract metadata
    metadata = extract_metadata(file_path)

    # Suppression flags (CID, preview overlays, etc)
    suppression_flags = detect_suppression_flags(file_path)

    # License risks (AGPL/GPL engines like iText, Ghostscript, BFO)
    license_flags = check_pdf_license(metadata)

    # Final summary
    summary = generate_fraud_summary(
        entities=entities,
        metadata=metadata,
        filename=os.path.basename(file_path),
        suppression_flags=suppression_flags,
        license_flags=license_flags,
        batch_duplicates=None  # Filled in during batch mode
    )

    result["filename"] = os.path.basename(file_path)
    result["entities"] = entities
    result["metadata"] = metadata
    result["suppression_flags"] = suppression_flags
    result["license_flags"] = license_flags
    result["summary"] = summary

    return result


def decode_batch_pdfs(file_list):
    results = []
    seen_fingerprints = {}

    for file_path in file_list:
        r = decode_single_pdf(file_path)

        doc_id = r["metadata"].get("/ModDate", "") + "::" + r["metadata"].get("/Title", "")
        duplicates = seen_fingerprints.get(doc_id, [])
        if duplicates:
            r["batch_duplicate_flags"] = f"Shared ModDate/Title with: {', '.join(duplicates)}"
        else:
            r["batch_duplicate_flags"] = "None"
        seen_fingerprints.setdefault(doc_id, []).append(r["filename"])

        # Re-run summary with batch context
        r["summary"] = generate_fraud_summary(
            entities=r["entities"],
            metadata=r["metadata"],
            filename=r["filename"],
            suppression_flags=r["suppression_flags"],
            license_flags=r["license_flags"],
            batch_duplicates=r["batch_duplicate_flags"]
        )

        results.append(r)

    return results