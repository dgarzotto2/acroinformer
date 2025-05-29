# export_bundle.py

import zipfile
import os
import tempfile
import yaml
from affidavit_writer import write_affidavit
from reportlab.lib.utils import ImageReader

def create_export_bundle(filename, sha256, metadata, findings, decoded_text, yaml_data, output_zip_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save YAML
        yaml_path = os.path.join(tmpdir, f"{filename}_entities.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True)

        # Save decoded text
        decoded_path = os.path.join(tmpdir, f"{filename}_decoded.txt")
        with open(decoded_path, "w", encoding="utf-8") as f:
            f.write(decoded_text)

        # Save affidavit
        affidavit_path = os.path.join(tmpdir, f"{filename}_affidavit.pdf")
        write_affidavit(
            output_path=affidavit_path,
            metadata=metadata,
            filename=filename,
            sha256=sha256,
            findings=findings,
        )

        # Create ZIP
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(yaml_path, arcname=os.path.basename(yaml_path))
            zf.write(decoded_path, arcname=os.path.basename(decoded_path))
            zf.write(affidavit_path, arcname=os.path.basename(affidavit_path))