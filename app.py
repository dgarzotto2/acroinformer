#!/usr/bin/env python3
import streamlit as st
import os
import tempfile
import hashlib

from extract_metadata import extract_metadata
from gpt_fraud_summary import generate_gpt_summary
from affidavit_writer import generate_affidavit_pdf

st.set_page_config(page_title="Forensic PDF Analyzer", layout="wide")
st.title("Forensic PDF Analyzer")
st.markdown(
    "Upload *two or more* PDF documents to analyze metadata, detect tampering, "
    "and generate affidavit-ready forensic summaries."
)

# 1) Allow multi-file upload
uploaded_files = st.file_uploader(
    "Choose two or more PDF files",
    type="pdf",
    accept_multiple_files=True
)

# 2) Don’t proceed until we have at least two
if not uploaded_files or len(uploaded_files) < 2:
    st.warning("🚨 Please upload **at least two** PDF documents to analyze.")
    st.stop()

# 3) Process all uploaded files
with tempfile.TemporaryDirectory() as temp_dir:
    st.success(f"{len(uploaded_files)} files uploaded. Processing…")

    metadata_list = []
    for uploaded in uploaded_files:
        # Save to temp
        file_path = os.path.join(temp_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())

        # Read bytes and hash
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        sha256 = hashlib.sha256(file_bytes).hexdigest()

        # Extract metadata
        try:
            md = extract_metadata(file_path, file_bytes)
            md["filename"] = uploaded.name
            md["sha256"] = sha256
            metadata_list.append(md)
        except Exception as e:
            st.error(f"Failed to extract metadata from {uploaded.name}: {e}")

    # 4) Display each file’s results
    for r in metadata_list:
        st.subheader(r["filename"])
        st.code(f"SHA-256: {r['sha256']}", language="bash")
        st.markdown(f"**Producer:** {r.get('producer', '—')}")
        st.markdown(f"**Creator:** {r.get('creator', '—')}")
        st.markdown(f"**Creation Date:** {r.get('creation_date', '—')}")
        st.markdown(f"**Modification Date:** {r.get('mod_date', '—')}")
        st.markdown(f"**XMP Toolkit:** {r.get('xmp_toolkit', '—')}")
        st.markdown(f"**Has Signature Field:** {'Yes' if r.get('has_signature_field') else 'No'}")
        st.markdown(f"**AcroForm Present:** {'Yes' if r.get('has_acroform') else 'No'}")
        st.markdown(f"**Signature Overlay Detected:** {'Yes' if r.get('signature_overlay_detected') else 'No'}")
        st.markdown(f"**Hidden Library Usage:** {'Yes' if r.get('hidden_lib_usage') else 'No'}")
        st.markdown("---")

        # 5) GPT forensic summary
        if "openai_api_key" in st.secrets:
            with st.spinner("Generating GPT summary…"):
                try:
                    summary = generate_gpt_summary(r)
                    st.markdown("### GPT Forensic Summary")
                    st.markdown(summary)
                except Exception as e:
                    st.warning(f"GPT analysis failed: {e}")

        # 6) Affidavit generation
        btn_key = f"affidavit_{r['sha256']}"
        if st.button(f"Generate Affidavit for {r['filename']}", key=btn_key):
            try:
                pdf_path = generate_affidavit_pdf(r, temp_dir)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Affidavit (PDF)",
                        data=pdf_file.read(),
                        file_name=f"{r['filename'].rsplit('.', 1)[0]}_affidavit.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Failed to generate affidavit: {e}")