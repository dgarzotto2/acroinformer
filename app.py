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

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    if not uploaded_file:
        st.info("Please upload a PDF to begin analysis.")
        return

    file_path, file_bytes = save_uploaded_file(uploaded_file)
    # <-- NOW calling with two arguments
    metadata = extract_metadata(file_path, file_bytes)

    st.header("Metadata Summary")
    st.markdown(f"**Creation Date:** {metadata.get('creation_date', '—')}")
    st.markdown(f"**Modification Date:** {metadata.get('mod_date', '—')}")
    st.markdown(f"**PDF Library:** {metadata.get('toolkit', '—')}")
    st.markdown(f"**XMP Toolkit:** {metadata.get('xmp_toolkit', '—')}")
    st.markdown(f"**Has Signature Field:** {'Yes' if metadata.get('has_signature_field') else 'No'}")
    st.markdown(f"**AcroForm Present:** {'Yes' if metadata.get('has_acroform') else 'No'}")
    st.markdown(f"**Tamper Risk:** {metadata.get('tamper_risk', '—')}")
    st.markdown(f"**Signature Overlay Detected:** {'Yes' if metadata.get('signature_overlay_detected') else 'No'}")

    st.header("Download / Preview")
    st.download_button(
        label="Download PDF",
        data=file_bytes,
        file_name=uploaded_file.name,
        mime="application/pdf"
    )

if __name__ == "__main__":
    main()