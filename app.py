import os
import hashlib
import tempfile
import streamlit as st
from extract_metadata import extract_metadata  # Ensure this function accepts (file_path, file_bytes)

st.set_page_config(page_title="AcroInformer", layout="wide")

st.title("AcroInformer – PDF Metadata Auditor")
st.markdown("This tool extracts technical and forensic metadata from uploaded legal PDF documents to assess authenticity and tampering risk.")

uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

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
        try:
            with open(fpath, "rb") as f:
                fbytes = f.read()
            metadata = extract_metadata(fpath, fbytes)  # ✅ fix: pass both arguments
            metadata_list.append(metadata)
        except Exception as e:
            st.error(f"❌ Failed to extract metadata from {fname}: {str(e)}")

    # Display results
    for r in metadata_list:
        st.subheader(f"{r['filename']}")
        st.code(f"SHA-256: {r['sha256']}", language="bash")
        st.markdown(f"**Producer:** {r['producer'] or '—'}")
        st.markdown(f"**Creator:** {r['creator'] or '—'}")
        st.markdown(f"**Creation Date:** {r['creation_date'] or '—'}")
        st.markdown(f"**Modification Date:** {r['mod_date'] or '—'}")
        st.markdown(f"**PDF Library:** {r['toolkit'] or '—'}")
        st.markdown(f"**XMP Toolkit:** {r['xmp_toolkit'] or '—'}")
        st.markdown(f"**Has Signature Field:** {'✅' if r.get('has_signature') else '—'}")
        st.markdown(f"**AcroForm Present:** {'✅' if r.get('has_acroform') else '—'}")
        st.markdown(f"**Tamper Risk:** {r.get('tamper_risk', '—')}")
        st.markdown("---")