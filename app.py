import streamlit as st
import os
import hashlib
import tempfile
import zipfile
from utils.metadata import extract_metadata
from utils.utility import display_pdf, compare_metadata_across_files

st.set_page_config(page_title="PDF Forensic Metadata Audit", layout="wide")

def compute_sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def handle_single_file(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        file_sha256 = compute_sha256(open(file_path, "rb").read())
        result = extract_metadata(file_path)
        result["filename"] = uploaded_file.name
        result["sha256"] = file_sha256
        return [result]

def handle_zip_file(zip_file):
    extracted_results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "batch.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
            for filename in zip_ref.namelist():
                if filename.lower().endswith(".pdf"):
                    file_path = os.path.join(tmpdir, filename)
                    file_sha256 = compute_sha256(open(file_path, "rb").read())
                    result = extract_metadata(file_path)
                    result["filename"] = filename
                    result["sha256"] = file_sha256
                    extracted_results.append(result)
    return extracted_results

def main():
    st.title("PDF Forensic Metadata and Tampering Audit")

    st.markdown("Upload a single PDF file or a ZIP archive containing multiple PDFs.")

    uploaded_file = st.file_uploader("Upload PDF or ZIP", type=["pdf", "zip"])

    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            results = handle_single_file(uploaded_file)
        elif uploaded_file.name.endswith(".zip"):
            results = handle_zip_file(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return

        if results:
            if len(results) > 1:
                st.subheader("Batch Report Summary")
                collisions = compare_metadata_across_files(results)
                if collisions:
                    st.warning("Metadata overlaps detected across multiple files.")
                    for note in collisions:
                        st.text(note)
                else:
                    st.text("No metadata collisions detected across uploaded files.")

            for r in results:
                st.markdown("---")
                st.subheader(f"File: {r.get('filename', 'Unknown')}")
                st.markdown(f"SHA-256: `{r.get('sha256', '')}`")

                st.markdown("Metadata Fields:")
                for k, v in r.get("metadata", {}).items():
                    st.text(f"{k}: {v}")

                st.markdown("Tampering Flags:")
                if r.get("cid_font_usage"):
                    st.text("CID font usage detected")
                if r.get("agpl_license_flag"):
                    st.text("Generated with AGPL/GPL-bound PDF library (e.g., iText, BFO)")
                if r.get("error"):
                    st.error(f"Error during metadata extraction: {r['error']}")
                if not r.get("cid_font_usage") and not r.get("agpl_license_flag") and not r.get("error"):
                    st.text("No red flags detected.")

                st.markdown("Preview:")
                with open(r["filename"], "rb") as f:
                    display_pdf(f.read(), width=700)

if __name__ == "__main__":
    main()