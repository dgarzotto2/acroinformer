import streamlit as st
import os
import hashlib
import tempfile
from extract_metadata import extract_metadata

# Set page configuration
st.set_page_config(
    page_title="AcroForm Informer",
    layout="centered"
)

st.title("AcroForm Informer")
st.markdown("Upload **two or more PDF files** to perform a forensic comparison based on metadata, AcroForm structures, XMP toolkit signatures, and timestamp analysis.")

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    file_map = {}

    for uploaded in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        file_map[uploaded.name] = file_path

    metadata_list = []

    for fname, fpath in file_map.items():
        with open(fpath, "rb") as f:
            fbytes = f.read()

        try:
            metadata = extract_metadata(fpath, fbytes)
            metadata_list.append(metadata)
        except Exception as e:
            st.error(f"Failed to extract metadata from {fname}: {e}")

    if metadata_list:
        st.header("Metadata Comparison Results")

        for r in metadata_list:
            st.subheader(f"{r['filename']}")
            st.code(f"SHA-256: {r['sha256']}", language="bash")
            st.markdown(f"**Producer:** {r['producer'] or '—'}")
            st.markdown(f"**Creator:** {r['creator'] or '—'}")
            st.markdown(f"**Creation Date:** {r['creation_date'] or '—'}")
            st.markdown(f"**Modification Date:** {r['mod_date'] or '—'}")
            st.markdown(f"**PDF Version:** {r['pdf_version'] or '—'}")
            st.markdown(f"**XMP Toolkit:** {r['xmp_toolkit'] or '—'}")
            st.markdown(f"**Document ID:** {r['doc_id'] or '—'}")
            st.markdown(f"**Instance ID:** {r['instance_id'] or '—'}")
            st.markdown(f"**AcroForm Detected:** {'Yes' if r['acroform'] else 'No'}")
            st.markdown(f"**Digital Signature Present:** {'Yes' if r['has_signature'] else 'No'}")
            st.markdown(f"**Key Flags:** {', '.join(r['flags']) if r['flags'] else 'None'}")

        st.success("Metadata extraction and comparison complete.")

else:
    st.info("Please upload **at least two** PDF files to begin comparison.")