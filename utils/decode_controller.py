import fitz
import io
from utils.deobfuscation import decode_ascii85_streams, decode_cid_fonts
from utils.ocr_engine import extract_text_via_ocr
from utils.suppression_detector import detect_suppression_patterns
from utils.entity_extraction import extract_entities
from utils.gpt_fraud_summary import generate_fraud_summary
from utils.metadata import extract_metadata

def decode_pdf(file_bytes, static_mode=False):
    try:
        suppression_flags = detect_suppression_patterns(file_bytes)
    except Exception as e:
        suppression_flags = [f"Suppression detection failed: {str(e)}"]

    decoded_text = ""
    cid_data, ascii85_data, ocr_data = "", "", ""

    if not static_mode:
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text = page.get_text("text")
                    if text.strip():
                        decoded_text += text + "\n"
        except Exception as e:
            decoded_text += f"\n[fitz decoding failed: {str(e)}]"

    try:
        ascii85_data = decode_ascii85_streams(file_bytes)
    except Exception as e:
        ascii85_data = f"[ascii85 decode failed: {str(e)}]"

    try:
        cid_data = decode_cid_fonts(file_bytes)
    except Exception as e:
        cid_data = f"[cid decode failed: {str(e)}]"

    if not decoded_text.strip():
        try:
            ocr_data = extract_text_via_ocr(file_bytes)
        except Exception as e:
            ocr_data = f"[ocr failed: {str(e)}]"

    combined_text = "\n".join([decoded_text, ascii85_data, cid_data, ocr_data])
    entities = extract_entities(combined_text)

    metadata_result = extract_metadata(file_bytes)
    metadata = metadata_result.get("metadata", {})
    fraud_flags = metadata_result.get("fraud_flags", [])

    try:
        gpt_result = generate_fraud_summary(entities, metadata=metadata, suppression_flags=suppression_flags)
    except Exception as e:
        gpt_result = {"error": str(e)}

    return {
        "decoded_text": combined_text,
        "entities": entities,
        "suppression_flags": suppression_flags,
        "metadata": metadata,
        "fraud_flags": fraud_flags,
        "gpt_summary": gpt_result.get("fraud_summary", "GPT summary not available."),
        "sha256": metadata_result.get("sha256"),
        "error": metadata_result.get("error")
    }