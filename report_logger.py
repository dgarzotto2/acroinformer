# report_logger.py

import csv
import os

def init_report_csv(path):
    """
    Initializes the report CSV file with headers.
    """
    headers = ["File 1", "File 2", "Suspicion Score", "Reasons"]
    with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

def append_report_row(path, file1, file2, score, reasons):
    """
    Appends a new row to the report CSV file.
    """
    with open(path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([file1, file2, score, "; ".join(reasons)])