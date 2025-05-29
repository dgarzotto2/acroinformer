import streamlit as st
import tempfile
import os
from modules.decode_controller import decode_pdf
from modules.gpt_fraud_summary import summarize_fraud

st.set_page_config(page_title="PDF Forensic Scanner", layout="wide")

st.title("PDF Forensic Scanner")
st.markdown("Upload one or more PDFs to perform a formal fraud risk assessment. All output is formatted for evidentiary review.")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            file_path = tmp_file.name

        st.subheader(f"File: {uploaded_file.name}")
        result = decode_pdf(file_path)

        st.markdown(f"**SHA-256 Hash:** `{result.get('sha256')}`")

        if result.get("agpl_license_flag"):
            st.markdown("**License Flag:** Document generated using AGPL/GPL-bound PDF software (e.g., iText, BFO). This may introduce licensing constraints or exportability concerns.")

        if result.get("cid_font_usage"):
            st.markdown("**Obfuscation Flag:** CID font usage detected. Text suppression or glyph masking may be present.")

        if result.get("fraud_flags"):
            st.markdown("### Identified Fraud Flags")
            for flag in result["fraud_flags"]:
                st.markdown(f"- {flag}")
        else:
            st.markdown("### Identified Fraud Flags")
            st.markdown("*No fraud risk markers were detected based on current decoding heuristics.*")

        if result.get("metadata"):
            st.markdown("### Extracted Metadata")
            for key, val in result["metadata"].items():
                st.markdown(f"- **{key}**: {val}")

        st.markdown("### GPT-Based Risk Summary")
        summary = summarize_fraud(result)
        st.markdown(summary)