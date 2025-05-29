import streamlit as st
from affidavit_writer import render_affidavit
from acroform_audit import audit_acroform_fields
from metadata_comparator import compare_metadata

# Example metadata collection loop — assumed earlier
all_metadata = []
all_acroforms = []

for fname, fpath in file_map.items():
    with open(fpath, "rb") as f:
        file_bytes = f.read()

    metadata = extract_metadata(fpath, file_bytes)
    acro_data = audit_acroform_fields(file_bytes, filename=fname)

    all_metadata.append(metadata)
    all_acroforms.append(acro_data)

# Metadata Summary
st.header("📄 Metadata Comparison Report")

if len(all_metadata) >= 2:
    meta_result = compare_metadata(all_metadata)
    for issue in meta_result["discrepancies"]:
        st.warning(f"⚠️ {issue}")
    if meta_result["flags"]:
        for f in meta_result["flags"]:
            st.error(f"🚨 {f}")
else:
    st.info("Upload at least two files for metadata comparison.")

# AcroForm Summary
st.header("🧾 AcroForm Audit Summary")

for acro in all_acroforms:
    with st.expander(f"Form Audit: {acro['filename']}"):
        if not acro["has_acroform"]:
            st.info("No AcroForm found.")
        else:
            st.success("AcroForm structure detected.")
            st.write(f"Fields found: {acro['field_names']}")
            if acro["empty_fields"]:
                st.warning(f"Empty fields: {acro['empty_fields']}")
            if acro["signature_fields"]:
                st.info(f"Signature fields: {acro['signature_fields']}")
            if acro["synthetic_warnings"]:
                for warn in acro["synthetic_warnings"]:
                    st.error(f"⚠️ {warn}")

# Optional PDF affidavit generation
st.header("📑 Forensic Affidavit Summary")
if st.button("Generate Forensic PDF Report"):
    affidavit_path = render_affidavit(all_metadata, all_acroforms)
    st.success("Affidavit ready.")
    st.download_button("Download Affidavit", open(affidavit_path, "rb"), file_name="forensic_affidavit.pdf")