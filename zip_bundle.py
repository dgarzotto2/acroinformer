# zip_bundle.py

import io
import zipfile
import json
from affidavit_writer import generate_affidavit_pdf

def bundle_forensic_outputs(results):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for result in results:
            base = result["filename"].replace(".pdf", "")
            zipf.writestr(f"{base}_metadata.json", json.dumps(result["metadata"], indent=2))
            zipf.writestr(f"{base}_entities.json", json.dumps(result["entities"], indent=2))
            zipf.writestr(f"{base}_summary.md", result["summary"])
            zipf.writestr(f"{base}_suppression.json", json.dumps(result["suppression_flags"], indent=2))
            zipf.writestr(f"{base}_license.json", json.dumps(result["license_flags"], indent=2))
            zipf.writestr(f"{base}_affidavit.pdf", generate_affidavit_pdf(result))
    zip_buffer.seek(0)
    return zip_buffer.read()