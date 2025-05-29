# app.py

import streamlit as st
import os
import tempfile
import shutil
import hashlib
import traceback

from pdf_utils import extract_metadata
from scoring_engine import score_documents
from affidavit_writer import generate_affidavit
from report_logger import init_report_csv, append_report_row
from zip_exporter import create_zip_bundle

st.set_page_config(page_title="Acroform Informer", layout="wide")

# Dark UI theme
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
st.subheader("Upload 2 or more PDF files for forensic analysis")

uploaded_files = st.file_uploader("Select PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    with st.spinner("Processing uploaded PDFs..."):
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        file_map = {}
        log_entries = []

        for uploaded in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded.name)
            fbytes = uploaded.read()

            # Write to disk
            with open(file_path, "wb") as f:
                f.write(fbytes)
            file_map[uploaded.name] = (file_path, fbytes)

        st.subheader("Extracted Metadata & SHA-256")
        metadata = {}
        for fname, (fpath, fbytes) in file_map.items():
            try:
                meta = extract_metadata(fpath, fbytes)
                sha256 = hashlib.sha256(fbytes).hexdigest()
                meta['sha256'] = sha256

                # Optional repair flags
                meta['repair_attempted'] = False
                meta['repair_successful'] = False
                meta['repair_method'] = None

                metadata[fname] = meta
                st.markdown(f"**{fname}**")
                st.text(f"SHA-256: {sha256}")
                st.json(meta)

            except Exception as e:
                err = traceback.format_exc()
                log_entries.append(f"[{fname}]\n{err}")
                st.error(f"❌ Failed to extract metadata for `{fname}`")
                continue

        report_csv = os.path.join(temp_dir, "batch_report.csv")
        init_report_csv(report_csv)

        affidavit_dir = os.path.join(temp_dir, "affidavits")
        os.makedirs(affidavit_dir, exist_ok=True)

        st.subheader("Suspicious Match Report & Affidavit Generator")
        results = []
        names = list(metadata.keys())

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
                label="📥 Download Evidence Bundle (ZIP)",
                data=f,
                file_name="evidence_bundle.zip",
                mime="application/zip"
            )

        # Output error log if any
        if log_entries:
            log_path = os.path.join(temp_dir, "error_log.txt")
            with open(log_path, "w") as logf:
                logf.write("\n\n".join(log_entries))

            with open(log_path, "rb") as f:
                st.download_button(
                    label="⚠️ Download Error Log",
                    data=f,
                    file_name="error_log.txt",
                    mime="text/plain"
                )

        shutil.rmtree(temp_dir)
else:
    st.warning("Please upload at least 2 PDF files for analysis.")