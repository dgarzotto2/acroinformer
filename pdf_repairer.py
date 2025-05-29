# pdf_repairer.py

import subprocess
import os
import tempfile

def repair_pdf(input_path):
    repaired_path = os.path.join(tempfile.gettempdir(), "repaired_" + os.path.basename(input_path))

    try:
        gs_cmd = [
            "gs",
            "-o", repaired_path,
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            input_path
        ]
        result = subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

        if os.path.exists(repaired_path) and os.path.getsize(repaired_path) > 1000:
            return repaired_path
        else:
            return None
    except Exception as e:
        return None