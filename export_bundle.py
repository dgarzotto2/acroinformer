# export_bundle.py

import zipfile
import os
import tempfile
import shutil

def bundle_export(evidence_files, output_zip_path="forensic_export.zip"):
    with tempfile.TemporaryDirectory() as tmpdir:
        for label, src_path in evidence_files.items():
            if src_path and os.path.exists(src_path):
                dst_path = os.path.join(tmpdir, os.path.basename(src_path))
                shutil.copy(src_path, dst_path)

        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)

    return output_zip_path