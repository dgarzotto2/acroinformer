# zip_exporter.py

import zipfile
import os

def create_zip_bundle(affidavit_dir, report_csv, zip_output):
    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(affidavit_dir):
            for file in files:
                if file.endswith(".docx"):
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, affidavit_dir)
                    zipf.write(full_path, arcname)
        if os.path.exists(report_csv):
            zipf.write(report_csv, os.path.basename(report_csv))