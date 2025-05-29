# utils/decode_streams.py

import fitz  # PyMuPDF

def decode_streams(file_bytes: bytes) -> list:
    """
    Extracts visible text blocks from the PDF using PyMuPDF.
    Returns a list of block dictionaries with page number and text.
    """
    blocks = []
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                if text.strip():
                    blocks.append({
                        "page": page_num,
                        "text": text.strip(),
                        "source": "fitz"
                    })
    except Exception as e:
        blocks.append({
            "page": -1,
            "text": f"Error during decoding: {e}",
            "source": "error"
        })
    return blocks