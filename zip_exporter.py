import zipfile
import os
from datetime import datetime

def create_zip_bundle(affidavit_dir, report_csv, output_path=None):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        output_path = f"/tmp/evidence_bundle_{timestamp}.zip"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add report CSV
        if os.path.exists(report_csv):
            zipf.write(report_csv, arcname="batch_report.csv")

        # Add all affidavits
        if os.path.exists(affidavit_dir):
            for fname in os.listdir(affidavit_dir):
                fpath = os.path.join(affidavit_dir, fname)
                zipf.write(fpath, arcname=os.path.join("affidavits", fname))

    return output_path