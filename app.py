import streamlit as st
import tempfile
import os
from metadata import extract_metadata

st.set_page_config(page_title="PDF Forensic Metadata Auditor", layout="wide")

def main():
    st.title("PDF Metadata & Tamper Audit")
    st.info("Upload a PDF document to extract metadata, detect obfuscation, and analyze for tampering or JavaScript.")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    if uploaded_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Analyzing PDF..."):
                try:
                    result = extract_metadata(file_path)
                except Exception as e:
                    st.error(f"Failed to extract metadata: {e}")
                    return

            st.subheader("📌 Basic Metadata")
            if result["metadata"]:
                for key, value in result["metadata"].items():
                    st.markdown(f"**{key}**: {value}")
            else:
                st.markdown("*No metadata found*")

            st.subheader("⚠️ Forensic Tamper Flags")
            if result["tamper_flags"]:
                for flag in result["tamper_flags"]:
                    st.markdown(f"- {flag}")
            else:
                st.markdown("*None detected*")

            st.subheader("🛠 Obfuscation & Generation Tool")
            st.markdown(f"- **Obfuscating Library Detected:** `{result['obfuscating_library'] or 'No'}`")
            st.markdown(f"- **Hidden Library Usage:** {'Yes' if result.get('hidden_lib_usage') else 'No'}")

            st.subheader("📜 Embedded JavaScript")
            if result["embedded_js"]:
                for js in result["embedded_js"]:
                    st.code(js)
            else:
                st.markdown("*None detected*")

            st.subheader("🚨 LaunchAction Detected")
            st.markdown(f"- {'Yes' if result.get('has_launch_action') else 'No'}")

            st.subheader("📎 ByteRange Validation")
            if result.get("byte_range_mismatch"):
                st.error("⚠️ Suspicious ByteRange length – may indicate digital tampering.")
            else:
                st.markdown("ByteRange appears normal.")

            st.subheader("📝 Notes & Forensic Commentary")
            if result["notes"]:
                for note in result["notes"]:
                    st.markdown(f"- {note}")
            else:
                st.markdown("*No specific notes recorded*")

if __name__ == "__main__":
    main()