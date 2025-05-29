# app.py

import streamlit as st
import os
import tempfile
from metadata import extract_metadata
from suppression_detector import detect_suppression_flags
from signature_validator import validate_signatures
from license_checker import check_pdf_license
from entity_extraction import extract_entities_from_text
from gpt_fraud_summary import generate_fraud_summary

st.set_page_config(page_title="Forensic PDF Auditor", layout="centered")

def process_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    metadata = extract_metadata(tmp_path)
    suppression_flags = detect_suppression_flags(tmp_path)
    signature_flags = validate_signatures(tmp_path)
    license_flags = check_pdf_license(metadata)

    all_flags = suppression_flags + signature_flags + license_flags

    with open(tmp_path, "rb") as f:
        raw_text = f.read().decode(errors="ignore")
    entities = extract_entities_from_text(raw_text)

    fraud_summary = generate_fraud_summary(metadata, entities, all_flags)

    st.subheader(f"📄 {uploaded_file.name}")
    st.markdown(f"**SHA256:** `{uploaded_file.name}`")
    st.markdown("### Forensic Summary")
    st.code(fraud_summary, language="markdown")

    st.markdown("### Entity Extraction")
    for key, value in entities.items():
        st.markdown(f"**{key.title()}**: {value if value else '*None*'}")

    st.markdown("### Flags & Notes")
    for flag in all_flags:
        st.markdown(f"- {flag}")

def main():
    st.title("PDF Forensic Metadata & Fraud Analyzer")
    st.write("Upload individual or multiple PDF files for batch scanning.")

    uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            process_file(uploaded_file)

if __name__ == "__main__":
    main()