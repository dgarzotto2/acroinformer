from metadata import extract_metadata
from gpt_fraud_summary import summarize_fraud
from signature_validator import validate_signature
from pdf_license_fingerprint import detect_pdf_tool

def process_pdf(file_path, sha256):
    result = {}
    metadata = extract_metadata(file_path)
    sig_results = validate_signature(file_path)
    agpl_flags = detect_pdf_tool(metadata)

    result.update(metadata)
    result.update(sig_results)
    result.update(agpl_flags)

    gpt_output = summarize_fraud(metadata, sig_results, agpl_flags)
    result["summary"] = gpt_output.get("summary", "")
    return result