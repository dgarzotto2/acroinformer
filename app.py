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

# Minimalist UI
st.markdown("""
    <style>
    body { color: #EEE; background-color: #111; }
    .stTextInput > div > div > input {
        background-color: #222;
        color: #EEE;
    }
    .stDownloadButton > button {
        background-color: #444;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Acroform Informer")
st.subheader("Forensic PDF Comparison and Affidavit Generator")

uploaded_files = st.file_uploader("Upload 2 or more PDF files for analysis", type="pdf", accept_multiple_files=True)

if not uploaded_files or len(uploaded_files) < 2:
    st.warning("Please upload at least 2 PDF files.")
    st.stop()

with st.spinner("Processing uploaded files..."):
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    file_map = {}

    for uploaded in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded.name)
        file_bytes = uploaded.read()

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        file_map[uploaded.name] = {
            "path": file_path,
            "bytes": file_bytes
        }

    metadata = {}
    st.subheader("📄 Extracted Metadata + Hashes")

    for fname, data in file_map.items():
        try:
            meta = extract_metadata(data["path"], data["bytes"])
            sha256 = hashlib.sha256(data["bytes"]).hexdigest()
            meta["sha256"] = sha256
            metadata[fname] = meta

            st.markdown(f"**{fname}**")
            st.text(f"SHA-256: {sha256}")
            st.json(meta)

        except Exception as e:
            st.error(f"Metadata extraction failed for {fname}: {str(e)}")

    if not metadata:
        st.error("No valid metadata found in any file.")
        st.stop()

    report_csv = os.path.join(temp_dir, "comparison_report.csv")
    affidavit_dir = os.path.join(temp_dir, "affidavits")
    os.makedirs(affidavit_dir, exist_ok=True)
    init_report_csv(report_csv)

    st.subheader("🔍 Document Match Summary")
    st.markdown("Pairs with suspicious similarity will generate downloadable affidavits.")

    summary_rows = []
    affidavit_files = []

    names = list(metadata.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            f1, f2 = names[i], names[j]
            meta1, meta2 = metadata[f1], metadata[f2]

            try:
                score, reasons = score_documents(meta1, meta2)
            except Exception as e:
                st.error(f"Error comparing {f1} vs {f2}: {str(e)}")
                continue

            if score > 50:
                aff_name = f"{f1.replace('.pdf', '')}__{f2.replace('.pdf', '')}.pdf"
                aff_path = os.path.join(affidavit_dir, aff_name)

                generate_affidavit(meta1, meta2, score, reasons, aff_path)
                append_report_row(report_csv, f1, f2, score, reasons)
                affidavit_files.append((aff_name, aff_path))

                summary_rows.append((f1, f2, score, reasons))

    if summary_rows:
        for f1, f2, score, reasons in summary_rows:
            st.markdown(f"**{f1} ⇄ {f2}** — Risk Score: `{score}`")
            for r in reasons:
                st.markdown(f"- {r}")

        st.subheader("📄 Download Individual Affidavits")
        for fname, fpath in affidavit_files:
            with open(fpath, "rb") as aff:
                st.download_button(
                    label=f"Download Affidavit: {fname}",
                    data=aff,
                    file_name=fname,
                    mime="application/pdf"
                )
    else:
        st.info("✅ No suspicious matches detected.")

    # Bundle all
    zip_path = os.path.join(temp_dir, "evidence_bundle.zip")
    create_zip_bundle(affidavit_dir, report_csv, zip_path)

    with open(zip_path, "rb") as zipfile:
        st.download_button(
            label="📦 Download Full Evidence Bundle (ZIP)",
            data=zipfile,
            file_name="evidence_bundle.zip",
            mime="application/zip"
        )

shutil.rmtree(temp_dir)