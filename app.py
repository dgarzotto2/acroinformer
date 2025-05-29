import streamlit as st
import os
import tempfile
from extract_metadata import extract_metadata

st.set_page_config(page_title="AcroInformer – PDF Forensic Metadata Scanner", layout="wide")

st.title("📄 AcroInformer – PDF Forensic Metadata Scanner")
st.markdown("Upload at least two PDF documents to begin forensic comparison.")

uploaded_files = st.file_uploader(
    "Select two or more PDF files for analysis",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.warning("Please upload at least two PDF files to begin.")
    st.stop()

temp_dir = tempfile.mkdtemp(dir="/tmp")
file_map = {}

for uploaded in uploaded_files:
    file_path = os.path.join(temp_dir, uploaded.name)
    file_bytes = uploaded.read()
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    file_map[uploaded.name] = {
        "path": file_path,
        "bytes": file_bytes
    }

st.success(f"✅ {len(file_map)} PDF files successfully uploaded and saved.")
st.markdown("---")

results = []

for fname, data in file_map.items():
    try:
        metadata = extract_metadata(data["path"], data["bytes"])
        results.append(metadata)
    except Exception as e:
        st.error(f"❌ Failed to extract metadata from {fname}: {str(e)}")

# Display extracted metadata
for r in results:
    st.subheader(f"📌 {r.get('filename', 'Unnamed')}")
    st.code(f"SHA-256: {r.get('sha256', '—')}", language="bash")
    st.markdown(f"**Producer:** {r.get('producer', '—')}")
    st.markdown(f"**Creator:** {r.get('creator', '—')}")
    st.markdown(f"**Creation Date:** {r.get('creation_date', '—')}")
    st.markdown(f"**Modification Date:** {r.get('mod_date', '—')}")
    st.markdown(f"**XMP Toolkit:** {r.get('xmp_toolkit', '—')}")
    st.markdown(f"**XMP Instance ID:** {r.get('xmp_instance_id', '—')}")
    st.markdown(f"**XMP Document ID:** {r.get('xmp_document_id', '—')}")
    st.markdown(f"**Has AcroForm Fields:** {r.get('has_acroform', False)}")
    st.markdown(f"**Has Digital Signature:** {r.get('has_signature', False)}")
    st.markdown(f"**Signature Type:** {r.get('signature_type', '—')}")
    st.markdown("---")