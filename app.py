import streamlit as st
import os
import tempfile
from decode_controller import process_pdf
from affidavit_writer import generate_affidavit
from utils import hash_file_sha256, detect_duplicate_metadata
import zipfile

st.set_page_config(page_title="X-Ray PDF Forensic Decoder", layout="wide")

def save_uploaded_files(uploaded_files, temp_dir):
    saved_paths = []
    for f in uploaded_files:
        file_path = os.path.join(temp_dir, f.name)
        with open(file_path, "wb") as out:
            out.write(f.read())
        saved_paths.append(file_path)
    return saved_paths

st.title("X-Ray PDF Forensic Decoder")
st.markdown("Upload one or more **PDF files** for full forensic extraction and fraud flagging.")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        saved_files = save_uploaded_files(uploaded_files, temp_dir)
        results = []
        metadata_bank = {}

        for path in saved_files:
            st.subheader(f"📄 {os.path.basename(path)}")
            sha256 = hash_file_sha256(path)
            try:
                result = process_pdf(path, sha256)
                result["sha256"] = sha256
                metadata_bank[sha256] = result.get("metadata", {})
                results.append(result)

                st.markdown(f"**Risk Score:** {result.get('risk_score', 'N/A')}")
                st.markdown(f"**Document ID:** {result.get('document_id', 'Unknown')}")
                st.markdown(f"**Real Grantor:** {result.get('real_grantor_inferred', 'Not found')}")
                st.markdown("✅ YAML and affidavit generated.")
                st.download_button("📄 Download Affidavit", generate_affidavit(result), file_name=f"affidavit_{sha256}.pdf")

            except Exception as e:
                st.error(f"Failed to process {os.path.basename(path)}: {str(e)}")

        # Check for metadata duplicates
        dup_flags = detect_duplicate_metadata(metadata_bank)
        if dup_flags:
            st.warning("⚠️ Duplicate metadata patterns detected across uploaded files. This may indicate synthetic or duplicated documents:")
            for f in dup_flags:
                st.code(f)

        # ZIP results
        zip_path = os.path.join(temp_dir, "bundle_results.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for r in results:
                aff = generate_affidavit(r)
                fname = f"affidavit_{r['sha256']}.pdf"
                with open(os.path.join(temp_dir, fname), "wb") as f:
                    f.write(aff)
                zipf.write(os.path.join(temp_dir, fname), arcname=fname)

        st.download_button("⬇️ Download All Affidavits (ZIP)", open(zip_path, "rb").read(), file_name="forensic_bundle.zip")