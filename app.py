import streamlit as st
import os
import tempfile
import hashlib
import shutil
import zipfile
import base64
from pdf_utils import extract_metadata
from affidavit_writer import generate_affidavit

st.set_page_config(page_title="Acroform Informer", layout="wide")

st.title("Acroform Informer")
st.markdown("Upload 2 or more PDF files for analysis.")

uploaded_files = st.file_uploader(
    "Select PDF files", type="pdf", accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 2:
    with st.spinner("Processing uploaded PDFs..."):
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        file_map = {}
        file_hashes = {}
        metadata_map = {}

        for uploaded in uploaded_files:
            fname = uploaded.name
            file_path = os.path.join(temp_dir, fname)
            file_bytes = uploaded.read()

            if len(file_bytes) < 1000:
                st.warning(f"{fname} appears to be too small. Skipping.")
                continue

            with open(file_path, "wb") as f:
                f.write(file_bytes)

            file_map[fname] = file_path
            file_hashes[fname] = hashlib.sha256(file_bytes).hexdigest()

            try:
                metadata = extract_metadata(file_path, file_bytes)
                metadata_map[fname] = metadata
            except Exception as e:
                st.error(f"Failed to extract metadata from {fname}: {e}")

        # Compare metadata
        report_html, risk_score = generate_affidavit(metadata_map, file_hashes)

        # Save affidavit
        affidavit_path = os.path.join(temp_dir, "affidavit_report.pdf")
        with open(affidavit_path, "wb") as f:
            f.write(report_html)

        # Zip everything
        zip_path = os.path.join(temp_dir, "acroinformer_output.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for f in file_map.values():
                zipf.write(f, os.path.basename(f))
            zipf.write(affidavit_path, "affidavit_report.pdf")

        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Download ZIP Bundle",
                data=f,
                file_name="acroinformer_output.zip",
                mime="application/zip",
            )

        # SHA-256 and Preview
        st.markdown("### 📄 Preview Uploaded PDFs")

        for fname, fpath in file_map.items():
            sha256 = file_hashes.get(fname, "N/A")
            with open(fpath, "rb") as f:
                pdf_bytes = f.read()
                b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

            st.markdown(
                f"""
                <div style="border:1px solid #999;padding:8px;margin-bottom:12px;">
                    <strong>{fname}</strong><br>
                    <span title="SHA-256: {sha256}" style="font-size:0.9em;color:#666;">
                        Hover to view SHA-256 hash
                    </span><br>
                    <iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500px" style="border:none;"></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    st.warning("Please upload at least 2 PDF files for analysis.")