# app.py

import streamlit as st
import os
import tempfile
import shutil
from pdf_utils import extract_metadata
from scoring_engine import score_documents
from affidavit_writer import generate_affidavit
from report_logger import init_report_csv, append_report_row
from zip_exporter import create_zip_bundle
import hashlib
import fitz

st.set_page_config(page_title="Acroform Informer", layout="wide")

st.title("Acroform Informer")
st.subheader("Forensic PDF Comparison and Affidavit Generator")

st.markdown("""
**Purpose:**  
This system detects and reports forensic similarities between PDF files. It generates court-ready affidavits detailing metadata matches, AcroForm reuse, and potential flattening or stealth editing.

**Certification:**  
All reports are signed by David Garzotto, Founder of Forensix, LLC  
Certified by Mile2 Investigations
""")

uploaded_files = st.file_uploader("Upload 2 or more PDF files for analysis", type="pdf", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    with tempfile.TemporaryDirectory() as tmpdir:
        st.info("Processing uploaded files...")
        affidavits_dir = os.path.join(tmpdir, "affidavits")
        os.makedirs(affidavits_dir, exist_ok=True)
        report_csv = os.path.join(tmpdir, "batch_report.csv")
        zip_output = os.path.join(tmpdir, "evidence_bundle.zip")

        # Parse metadata for all files
        metadata_list = []
        for file in uploaded_files:
            path = os.path.join(tmpdir, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            metadata = extract_metadata(path)
            metadata["filename"] = file.name
            metadata_list.append(metadata)

        # Initialize report
        init_report_csv(report_csv)

        st.success("Metadata extracted. Comparing files...")

        # Compare all pairs
        for i in range(len(metadata_list)):
            for j in range(i + 1, len(metadata_list)):
                meta_a = metadata_list[i]
                meta_b = metadata_list[j]
                score, reasons = score_documents(meta_a, meta_b)
                affidavit_path = os.path.join(affidavits_dir, f"{meta_a['filename']}__{meta_b['filename']}.docx")
                generate_affidavit(meta_a, meta_b, score, reasons, affidavit_path)
                append_report_row(report_csv, meta_a, meta_b, score, reasons)

        # Bundle results
        create_zip_bundle(affidavits_dir, report_csv, zip_output)

        st.markdown("### ✅ Batch Report & Affidavits Ready")

        with open(report_csv, "rb") as f:
            st.download_button("Download CSV Report", f, file_name="batch_report.csv", mime="text/csv")

        with open(zip_output, "rb") as f:
            st.download_button("Download ZIP Bundle (Affidavits + Report)", f, file_name="evidence_bundle.zip", mime="application/zip")