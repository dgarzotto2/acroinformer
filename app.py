import streamlit as st
import tempfile
import os
from metadata import extract_metadata

st.set_page_config(page_title="AcroInformer - PDF Metadata Forensics", layout="wide")

def main():
    st.title("📄 AcroInformer: PDF Metadata & Obfuscation Scan")

    uploaded_file = st.file_uploader("Upload a PDF for forensic metadata analysis", type=["pdf"])
    if uploaded_file is None:
        st.info("Please upload a PDF to begin.")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully. Running analysis...")

        results = extract_metadata(file_path)

        st.subheader("🔍 Metadata Summary")
        st.markdown(f"- **Title:** {results.get('title') or 'Unknown'}")
        st.markdown(f"- **Author:** {results.get('author') or 'Unknown'}")
        st.markdown(f"- **Producer:** {results.get('producer') or 'Unknown'}")
        st.markdown(f"- **Creation Date:** {results.get('created') or 'Unknown'}")
        st.markdown(f"- **Modification Date:** {results.get('modified') or 'Unknown'}")

        st.subheader("🛑 Obfuscation & Threat Flags")
        st.markdown(f"- **Hidden Library Usage:** {'Yes' if results.get('hidden_lib_usage') else 'No'}")
        st.markdown(f"- **XFA Detected:** {'Yes' if results.get('xfa_found') else 'No'}")
        st.markdown(f"- **CID Font Present:** {'Yes' if results.get('cid_fonts_present') else 'No'}")
        st.markdown(f"- **Launch Action Present:** {'Yes' if results.get('launch_action_found') else 'No'}")

        st.subheader("🔐 Signature & Structure")
        st.markdown(f"- **AcroForm Present:** {'Yes' if results.get('acroform') else 'No'}")
        st.markdown(f"- **XMP Toolkit:** {results.get('xmp_toolkit') or 'None'}")
        st.markdown(f"- **ByteRange Present:** {'Yes' if results.get('byte_range') else 'No'}")

        st.subheader("🧬 Internal Metadata Dump")
        st.json(results)

if __name__ == "__main__":
    main()