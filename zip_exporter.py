# zip_exporter.py

import os
import zipfile

def create_zip_bundle(affidavit_dir, report_csv_path, zip_output_path):
    with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add CSV report
        if os.path.exists(report_csv_path):
            zipf.write(report_csv_path, arcname=os.path.basename(report_csv_path))
        
        # Add affidavit PDFs
        if os.path.isdir(affidavit_dir):
            for fname in os.listdir(affidavit_dir):
                fpath = os.path.join(affidavit_dir, fname)
                if os.path.isfile(fpath):
                    zipf.write(fpath, arcname=os.path.join("affidavits", fname))