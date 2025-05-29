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

# Dark theme UI override
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

st.markdown("""
**Purpose:**  
This system detects and reports forensic similarities between PDF files. It generates court-ready affidavits detailing metadata matches, AcroForm reuse, and potential flattening or stealth editing.
""")

uploaded_files = st.file_uploader("Upload 2 or more PDF files for analysis", type="pdf", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    temp_dir = tempfile.mkdtemp()
    st.success(f"{len(uploaded_files)} PDF files uploaded.")

    file_map = {}
    for file in uploaded_files:
        try:
            file_path = os.path.join(temp_dir, file.name)
            bytes_data = file.read()
            if not bytes_data:
                st.warning(f"File {file.name} is empty or unreadable.")
                continue
            with open(file_path, "wb") as f:
                f.write(bytes_data)
            file_map[file.name] = file_path
        except Exception as e:
            st.error(f"Failed to process {file.name}: {e}")

    if not file_map:
        st.error("No valid PDF files processed. Aborting.")
    else:
        st.subheader("Extracted Metadata & SHA-256 Hashes")
        metadata = {}

        for fname, fpath in file_map.items():
            try:
                if not os.path.exists(fpath):
                    st.warning(f"File missing: {fpath}")
                    continue
                meta = extract_metadata(fpath)
                with open(fpath, "rb") as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
                meta['sha256'] = sha256
                metadata[fname] = meta

                st.markdown(f"**{fname}**")
                st.text(f"SHA-256: {sha256}")
                st.json(meta)
            except Exception as e:
                st.error(f"Metadata extraction failed for {fname}: {e}")

        if not metadata:
            st.error("No metadata could be extracted from the files.")
        else:
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
                    meta1, meta2 = metadata.get(f1), metadata.get(f2)

                    if not meta1 or not meta2:
                        continue

                    score, reasons = score_documents(meta1, meta2)
                    if score > 50:
                        st.markdown(f"**{f1} ⇄ {f2}** — Score: {score}")
                        for reason in reasons:
                            st.markdown(f"- {reason}")

                        affidavit_path = os.path.join(
                            affidavit_dir,
                            f"{f1.replace('.pdf', '')}__{f2.replace('.pdf', '')}.pdf"
                        )
                        try:
                            generate_affidavit(meta1, meta2, score, reasons, affidavit_path)
                            append_report_row(report_csv, f1, f2, score, reasons)
                            results.append((f1, f2, score))
                        except Exception as e:
                            st.error(f"Failed to generate affidavit for {f1} ⇄ {f2}: {e}")

            if not results:
                st.info("No suspicious matches (score > 50) were detected.")

            try:
                zip_path = os.path.join(temp_dir, "evidence_bundle.zip")
                create_zip_bundle(affidavit_dir, report_csv, zip_path)

                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Evidence Bundle (ZIP)",
                        data=f,
                        file_name="evidence_bundle.zip",
                        mime="application/zip"
                    )
            except Exception as e:
                st.error(f"Failed to package ZIP evidence bundle: {e}")

    shutil.rmtree(temp_dir)