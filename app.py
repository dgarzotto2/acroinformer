import streamlit as st
import os
import tempfile
from datetime import datetime
from decode_controller import run_forensic_pipeline
from affidavit_writer import generate_affidavit
from zip_bundler import bundle_outputs
from metadata import extract_metadata
import shutil

st.set_page_config(page_title="PDF Forensic Inspector", layout="wide")
st.title("PDF Forensic Inspector")

st.markdown("Upload one or more PDFs for forensic analysis. Results include:")
st.markdown("- Metadata tampering indicators")
st.markdown("- Registry key / parcel / financial entity extraction")
st.markdown("- CID/XFA suppression analysis")
st.markdown("- YAML, CSV, and PDF affidavit export")
st.markdown("- ZIP bundle of all outputs")

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        all_metadata = []
        output_files = []

        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Run forensic decoding pipeline
            parsed_data = run_forensic_pipeline(file_path)

            # Extract metadata
            metadata = extract_metadata(file_path)
            all_metadata.append((uploaded_file.name, metadata))

            # Save YAML
            yaml_path = os.path.join(temp_dir, uploaded_file.name.replace(".pdf", "_entities.yaml"))
            with open(yaml_path, "w", encoding="utf-8") as f:
                f.write(parsed_data["yaml_output"])
            output_files.append(yaml_path)

            # Save CSV
            csv_path = os.path.join(temp_dir, uploaded_file.name.replace(".pdf", "_summary.csv"))
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(parsed_data["csv_output"])
            output_files.append(csv_path)

            # Generate affidavit PDF
            affidavit_path = os.path.join(temp_dir, uploaded_file.name.replace(".pdf", "_affidavit.pdf"))
            generate_affidavit(file_path, parsed_data["yaml_dict"], affidavit_path)
            output_files.append(affidavit_path)

            # Show YAML
            with st.expander(f"YAML: {uploaded_file.name}"):
                st.code(parsed_data["yaml_output"], language="yaml")

        # Check for fraud indicators across multiple files
        st.markdown("### Cross-Document Fraud Flags")
        seen_doc_ids = set()
        seen_creators = set()
        seen_dates = set()
        seen_entities = set()
        duplicates = []

        for name, meta in all_metadata:
            doc_id = meta.get("document_id", "")
            creator = meta.get("creator_tool", "")
            date = meta.get("creation_date", "")
            entities = meta.get("entity_names", [])

            if doc_id in seen_doc_ids:
                duplicates.append(f"{name} reuses document_id: {doc_id}")
            if creator in seen_creators:
                duplicates.append(f"{name} reuses creator: {creator}")
            if date in seen_dates:
                duplicates.append(f"{name} reuses creation date: {date}")
            for ent in entities:
                if ent in seen_entities:
                    duplicates.append(f"{name} reuses entity: {ent}")

            seen_doc_ids.add(doc_id)
            seen_creators.add(creator)
            seen_dates.add(date)
            seen_entities.update(entities)

        if duplicates:
            for flag in duplicates:
                st.warning(flag)
        else:
            st.markdown("*No duplicate indicators detected across batch.*")

        # Bundle ZIP
        zip_path = bundle_outputs(temp_dir, output_files)
        with open(zip_path, "rb") as zip_file:
            st.download_button(
                label="Download All Forensic Outputs (.zip)",
                data=zip_file,
                file_name=os.path.basename(zip_path),
                mime="application/zip"
            )