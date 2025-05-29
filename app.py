import os
import tempfile
import streamlit as st
from extract_metadata import extract_metadata
import hashlib

st.set_page_config(page_title="AcroInformer", layout="wide")

st.title("AcroInformer – Forensic PDF AcroForm & Metadata Validator")
st.markdown("Upload one or more PDF files to extract metadata, AcroForm structure, and signature indicators.")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
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
            metadata["filename"] = fname
            metadata["sha256"] = hashlib.sha256(fbytes).hexdigest()
            metadata_list.append(metadata)
        except Exception as e:
            st.error(f"❌ Failed to extract metadata from {fname}: {str(e)}")
            continue

    for r in metadata_list:
        st.subheader(f"📌 {r['filename']}")
        st.code(f"SHA-256: {r['sha256']}", language="bash")
        st.markdown(f"**Producer:** {r.get('producer') or '—'}")
        st.markdown(f"**Creator:** {r.get('creator') or '—'}")
        st.markdown(f"**Creation Date:** {r.get('creation_date') or '—'}")
        st.markdown(f"**Modification Date:** {r.get('mod_date') or '—'}")
        st.markdown(f"**XMP Toolkit:** {r.get('xmp_toolkit') or '—'}")
        st.markdown(f"**AcroForm Present:** {'✅' if r.get('has_acroform') else '—'}")
        st.markdown(f"**XFA Present:** {'✅' if r.get('has_xfa') else '—'}")
        st.markdown(f"**Signature Valid:** {'✅' if r.get('has_valid_signature') else '—'}")
        st.markdown(f"**Signature Overlay Detected:** {'⚠️' if r.get('suspect_overlay') else '—'}")
        st.markdown(f"**Instance ID:** `{r.get('instance_id') or '—'}`")
        st.markdown(f"**Document ID:** `{r.get('document_id') or '—'}`")
        st.markdown("---")

else:
    st.info("Please upload at least one PDF file to begin analysis.")