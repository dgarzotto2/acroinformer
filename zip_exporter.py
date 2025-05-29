# zip_exporter.py

import zipfile
import os

def create_zip_bundle(affidavit_dir, csv_path, output_path):
    """
    Creates a ZIP file containing all affidavits and the main report CSV.
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add report CSV
        if os.path.exists(csv_path):
            zipf.write(csv_path, arcname=os.path.basename(csv_path))

        # Add affidavit PDFs
        for root, _, files in os.walk(affidavit_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arc_name = os.path.join("affidavits", file)
                zipf.write(full_path, arcname=arc_name)