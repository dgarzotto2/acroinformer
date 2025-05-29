# app.py

import streamlit as st
import tempfile
import os
import shutil
from decode_controller import decode_single_pdf, decode_batch_pdfs
from affidavit_writer import generate_affidavit_pdf
from zip_bundle import bundle_forensic_outputs
from utils.utility import preview_pdf

st.set_page_config(page_title="Forensic PDF Decoder", layout="wide")

st.title("Forensic PDF Decoder")
st.markdown("This tool extracts hidden financial data, detects document tampering, and generates a forensic report from uploaded PDFs.")

mode = st.radio("Select Upload Mode:", ["Single PDF", "Batch Upload (multiple PDFs)"])
uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=(mode == "Batch Upload (multiple PDFs)"))

if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            file_paths.append(file_path)

        st.divider()

        if mode == "Single PDF":
            result = decode_single_pdf(file_paths[0])

            st.subheader("PDF Preview")
            preview_pdf(file_paths[0])

            st.subheader("Metadata")
            st.json(result["metadata"], expanded=False)

            st.subheader("Entities & Routing")
            st.json(result["entities"], expanded=False)

            st.subheader("Suppression Flags")
            st.json(result["suppression_flags"], expanded=False)

            st.subheader("License Flags")
            st.json(result["license_flags"], expanded=False)

            st.subheader("GPT Fraud Summary")
            st.markdown(result["summary"])

            st.download_button(
                "Download Affidavit PDF",
                generate_affidavit_pdf(result),
                file_name="affidavit_summary.pdf"
            )

        else:
            results = decode_batch_pdfs(file_paths)

            for result in results:
                st.subheader(f"📄 {result['filename']}")
                preview_pdf(os.path.join(temp_dir, result["filename"]))
                with st.expander("Metadata"):
                    st.json(result["metadata"])
                with st.expander("Entities & Routing"):
                    st.json(result["entities"])
                with st.expander("Suppression Flags"):
                    st.json(result["suppression_flags"])
                with st.expander("License Flags"):
                    st.json(result["license_flags"])
                with st.expander("Batch Duplicate Alert"):
                    st.warning(result["batch_duplicate_flags"])
                with st.expander("GPT Fraud Summary"):
                    st.markdown(result["summary"])

            zip_data = bundle_forensic_outputs(results)
            st.download_button("📥 Download ZIP Bundle of Reports", zip_data, file_name="forensic_reports.zip")

st.divider()
st.caption("This forensic decoder checks CID masking, raster overlays, AGPL/GPL risks, LaunchActions, and synthetic metadata patterns.")