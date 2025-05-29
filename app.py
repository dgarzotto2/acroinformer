import streamlit as st
import tempfile
import os
from metadata import extract_metadata
from report_generator import generate_pdf_report

st.set_page_config(page_title="AcroInformer: PDF Forensics", layout="centered")

def main():
    st.title("🕵️ AcroInformer – PDF Metadata & Tamper Audit")
    st.write("Upload a PDF to analyze metadata, obfuscation techniques, and digital tampering.")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            st.markdown("## 🔍 Analysis Results")

            try:
                result = extract_metadata(file_path)

                st.markdown("### Obfuscation Flags")
                st.markdown(f"- **Obfuscation Library Used:** `{', '.join(result.get('obfuscation_libraries', [])) or 'None'}`")
                st.markdown(f"- **Hidden Library Usage:** {'Yes' if result.get('hidden_lib_usage') else 'No'}")
                st.markdown(f"- **ByteRange Tampering:** {'Yes' if result.get('byte_range_mismatch') else 'No'}")
                st.markdown(f"- **CID Font Warnings:** {'Yes' if result.get('font_warnings') else 'No'}")
                st.markdown(f"- **XFA Fields Present:** {'Yes' if result.get('has_xfa') else 'No'}")
                st.markdown(f"- **AcroForm Present:** {'Yes' if result.get('has_acroform') else 'No'}")
                st.markdown(f"- **Embedded Files:** {'Yes' if result.get('embedded_files') else 'No'}")

                st.markdown("### Embedded JavaScript")
                js_list = result.get("js", [])
                if js_list:
                    for js in js_list:
                        st.code(js, language="javascript")
                else:
                    st.markdown("*None detected*")

                st.markdown("### Notes & Forensic Flags")
                notes = result.get("notes", [])
                if notes:
                    for note in notes:
                        st.markdown(f"- {note}")
                else:
                    st.markdown("*None detected*")

                # Generate PDF report
                report_path = generate_pdf_report(temp_dir, uploaded_file.name.replace(".pdf", ""), result)
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Full Forensic Report (PDF)",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")

if __name__ == "__main__":
    main()