# report_logger.py

import csv
import os

def init_report_csv(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["File A", "File B", "Score", "Reasons"])

def append_report_row(path, file_a, file_b, score, reasons):
    with open(path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            file_a,
            file_b,
            score,
            "; ".join(reasons)
        ])