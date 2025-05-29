# report_logger.py

import csv
import os
from datetime import datetime

def init_report_csv(path):
    """
    Creates a new CSV report with headers if it doesn't already exist.
    """
    if not os.path.exists(path):
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Document A", "Document B", "Score", "Reasons"])

def append_report_row(path, doc_a, doc_b, score, reasons):
    """
    Appends a row to the forensic report CSV.
    """
    timestamp = datetime.utcnow().isoformat()
    reason_str = " | ".join(reasons)
    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, doc_a, doc_b, score, reason_str])