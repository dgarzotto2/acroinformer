#!/usr/bin/env python3
import os
import streamlit as st
from pdf_utils import extract_metadata

def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file under /tmp and return its path and raw bytes.
    """
    tmp_dir = "/tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    file_bytes = uploaded_file.read()
    file_path = os.path.join(tmp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path, file_bytes

def main():
    st.set_page_config(page_title="AcroInformer", layout="wide")
    st.title("AcroInformer")
    st.write("**Digital Forensic Document Examination**")

    # Accept multiple PDF files
    uploaded_files = st.file_uploader(
        "Upload one or more PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )
    if not uploaded_files:
        st.info("Please upload at least one PDF to begin analysis.")
        return

    # Process each upload
    for uploaded_file in uploaded_files:
        file_path, file_bytes = save_uploaded_file(uploaded_file)
        metadata = extract_metadata(file_path, file_bytes)

        # Show each file’s results in a collapsible panel
        with st.expander(f"Results for: {uploaded_file.name}", expanded=True):
            st.markdown(f"**Creation Date:** {metadata.get('creation_date', '—')}")
            st.markdown(f"**Modification Date:** {metadata.get('mod_date', '—')}")
            st.markdown(f"**PDF Library:** {metadata.get('toolkit', '—')}")
            st.markdown(f"**XMP Toolkit:** {metadata.get('xmp_toolkit', '—')}")
            st.markdown(f"**Has Signature Field:** {'Yes' if metadata.get('has_signature_field') else 'No'}")
            st.markdown(f"**AcroForm Present:** {'Yes' if metadata.get('has_acroform') else 'No'}")
            st.markdown(f"**Tamper Risk:** {metadata.get('tamper_risk', '—')}")
            st.markdown(
                f"**Signature Overlay Detected:** "
                f"{'Yes' if metadata.get('signature_overlay_detected') else 'No'}"
            )
            # Provide download for this specific PDF
            st.download_button(
                label="Download PDF",
                data=file_bytes,
                file_name=uploaded_file.name,
                mime="application/pdf"
            )
            st.markdown("---")  # separator

if __name__ == "__main__":
    main()