import streamlit as st
import tempfile
import os
from metadata import extract_metadata

st.set_page_config(page_title="AcroInformer", layout="centered")
st.title("📄 PDF Metadata & Tampering Risk Audit")

def main():
    st.info("Upload any PDF suspected of manipulation, embedded JavaScript, XFA overlays, or CID font suppression.")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.markdown("---")

            r = extract_metadata(file_path)

            # --- METADATA ---
            st.subheader("🧾 Core Metadata")
            if r.get("metadata"):
                for k, v in r["metadata"].items():
                    st.markdown(f"- **{k}**: {v}")
            else:
                st.markdown("*None found*")

            # --- XFA & ACROFORM ---
            st.subheader("📑 Form & Dynamic Content")
            st.markdown(f"- **Has AcroForm:** {'Yes' if r.get('has_acroform') else 'No'}")
            st.markdown(f"- **Has XFA:** {'Yes' if r.get('has_xfa') else 'No'}")

            # --- EMBEDDED FILES ---
            st.subheader("📎 Embedded Files")
            if r.get("embedded_files"):
                for item in r["embedded_files"]:
                    st.code(item)
            else:
                st.markdown("*None detected*")

            # --- JAVASCRIPT ---
            st.subheader("⚠️ Embedded JavaScript")
            if r.get("js"):
                for js_snippet in r["js"]:
                    st.code(js_snippet)
            else:
                st.markdown("*None detected*")

            # --- FONT WARNINGS ---
            st.subheader("🧵 Font Obfuscation Warnings")
            if r.get("font_warnings"):
                for warn in r["font_warnings"]:
                    st.warning(warn)
            else:
                st.markdown("*None detected*")

            # --- BYTE RANGE / LIBRARY CHECKS ---
            st.subheader("🔒 Signature & Generation Info")
            st.markdown(f"- **ByteRange Tamper Detected:** {'Yes' if r.get('byte_range_mismatch') else 'No'}")
            st.markdown(f"- **Hidden Library Usage:** {'Yes' if r.get('hidden_lib_usage') else 'No'}")

            # --- NOTES / FLAGS ---
            st.subheader("📝 Notes & Forensic Flags")
            if r.get("notes"):
                for note in r["notes"]:
                    st.markdown(f"- {note}")
            else:
                st.markdown("*None*")

            st.markdown("---")
            st.success("✅ Scan Complete – Review all sections above.")

if __name__ == "__main__":
    main()