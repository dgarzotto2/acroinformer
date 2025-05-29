# app.py

import streamlit as st
import os
import tempfile
import shutil
import hashlib
from pdf_utils import extract_metadata
from scoring_engine import score_documents
from affidavit_writer import generate_affidavit
from report_logger import init_report_csv, append_report_row
from zip_exporter import create_zip_bundle

st.set_page_config(page_title="Acroform Informer", layout="wide")

# Custom dark styling
st.markdown("""
    <style>
    body {
        color: #DCDCDC;
        background-color: #111111;
    }
    .stTextInput > div > div > input {
        background-color: #222;
        color: #eee;
    }
    .stDownloadButton > button {
        background-color: #444;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Acroform Informer")
st.subheader("Forensic PDF Comparison and Affidavit Generator")
st.markdown("Upload 2 or more PDF files for analysis.")

uploaded_files = st.file_uploader("Select PDF files", type="pdf", accept_multiple_files=True)

def process_files(uploaded_files):
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    file_map = {}

    for uploaded in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        file_map[uploaded.name] = file_path

    st.subheader("Extracted Metadata & SHA-256 Hashes")
    metadata = {}
    for fname, fpath in file_map.items():
        meta = extract_metadata(fpath)
        with open(fpath, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        meta['sha256'] = sha256
        metadata[fname] = meta

        st.markdown(f"**{fname}**")
        st.text(f"SHA-256: {sha256}")
        st.json(meta)

    report_csv = os.path.join(temp_dir, "batch_report.csv")
    init_report_csv(report_csv)

    affidavit_dir = os.path.join(temp_dir, "affidavits")
    os.makedirs(affidavit_dir, exist_ok=True)

    st.subheader("Suspicious Match Report & Affidavit Generation")
    results = []
    names = list(file_map.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            f1, f2 = names[i], names[j]
            meta1, meta2 = metadata[f1], metadata[f2]
            score, reasons = score_documents(meta1, meta2)

            if score > 50:
                st.markdown(f"**{f1} ⇄ {f2}** — Score: {score}")
                for reason in reasons:
                    st.markdown(f"- {reason}")

                affidavit_path = os.path.join(
                    affidavit_dir,
                    f"{f1.replace('.pdf', '')}__{f2.replace('.pdf', '')}.pdf"
                )
                generate_affidavit(meta1, meta2, score, reasons, affidavit_path)
                append_report_row(report_csv, f1, f2, score, reasons)
                results.append((f1, f2, score))

    if not results:
        st.info("No suspicious matches (score > 50) were detected.")

    zip_path = os.path.join(temp_dir, "evidence_bundle.zip")
    create_zip_bundle(affidavit_dir, report_csv, zip_path)

    with open(zip_path, "rb") as f:
        st.download_button(
            label="Download Evidence Bundle (ZIP)",
            data=f,
            file_name="evidence_bundle.zip",
            mime="application/zip"
        )

    shutil.rmtree(temp_dir)

if uploaded_files is not None and len(uploaded_files) >= 2:
    with st.spinner("Processing uploaded PDFs..."):
        process_files(uploaded_files)
elif uploaded_files is not None and len(uploaded_files) < 2:
    st.warning("Please upload at least 2 PDF files.")