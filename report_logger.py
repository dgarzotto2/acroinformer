# report_logger.py

import csv
import os

def init_report_csv(output_path):
    header = [
        "file_a", "file_b",
        "sha256_a", "sha256_b",
        "creation_a", "creation_b",
        "xmp_doc_id_a", "xmp_doc_id_b",
        "score", "is_flagged", "reasons"
    ]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def append_report_row(output_path, meta_a, meta_b, score, reasons):
    row = [
        meta_a["filename"], meta_b["filename"],
        meta_a["sha256"], meta_b["sha256"],
        meta_a["creation_date"], meta_b["creation_date"],
        meta_a["xmp_document_id"] or "N/A", meta_b["xmp_document_id"] or "N/A",
        score,
        "YES" if score > 50 else "NO",
        "; ".join(reasons)
    ]
    with open(output_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)