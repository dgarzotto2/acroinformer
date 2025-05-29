import streamlit as st
import tempfile
import os
from metadata_comparator import extract_metadata

st.set_page_config(page_title="AcroInformer", layout="wide")

st.title("📄 AcroInformer – Forensic Metadata Comparator")

st.markdown(
    """
    Upload two or more PDF files to compare their embedded metadata, XMP toolkit versions, 
    creation/modification timestamps, and digital fingerprinting. This tool performs a chain-of-custody-safe, 
    read-only scan to detect synthetic or mass-produced document traits.
    """
)

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    with st.spinner("Analyzing PDFs..."):
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        results = []

        for uploaded in uploaded_files:
            fname = uploaded.name
            fbytes = uploaded.read()
            fpath = os.path.join(temp_dir, fname)

            with open(fpath, "wb") as f:
                f.write(fbytes)

            try:
                result = extract_metadata(fpath)
                results.append(result)
            except Exception as e:
                st.error(f"Error processing {fname}: {str(e)}")

    st.success(f"{len(results)} files analyzed.")
    st.divider()

    for r in results:
        st.subheader(f"📌 {r['filename']}")
        st.code(f"SHA-256: {r['sha256']}", language="bash")
        st.markdown(f"**Producer:** {r['producer'] or '—'}")
        st.markdown(f"**Creator:** {r['creator'] or '—'}")
        st.markdown(f"**Creation Date:** {r['creation_date'] or '—'}")
        st.markdown(f"**Modification Date:** {r['mod_date'] or '—'}")
        st.markdown(f"**XMP Toolkit:** {r['xmp_toolkit'] or '—'}")
        st.markdown(f"**Instance ID:** `{r['instance_id'] or '—'}`")
        st.markdown(f"**Document ID:** `{r['document_id'] or '—'}`")

        if r["metadata_flags"]:
            st.warning("⚠️ Forensic Flags:")
            for flag in r["metadata_flags"]:
                st.markdown(f"- {flag}")
        else:
            st.success("✅ No anomalies detected in metadata.")

        with st.expander("🔍 Raw XMP Packet", expanded=False):
            st.code(r["raw_xmp"] or "None found", language="xml")

        st.divider()

else:
    st.info("Please upload at least two PDF files to begin comparison.")