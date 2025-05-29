# utils/decode_streams.py

import io
import zlib
import re
import fitz  # PyMuPDF
from PyPDF2 import PdfReader

def decode_streams(file_bytes: bytes, use_fitz: bool = True) -> list:
    """
    Dual-mode decoder:
    - If use_fitz is True, extract with PyMuPDF.
    - If False, use static stream and FlateDecode parsing.
    Returns list of decoded block dicts.
    """
    if use_fitz:
        return _decode_with_fitz(file_bytes)
    else:
        return _decode_static(file_bytes)

def _decode_with_fitz(file_bytes: bytes) -> list:
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
            "text": f"[fitz error] {e}",
            "source": "fitz"
        })
    return blocks

def _decode_static(file_bytes: bytes) -> list:
    blocks = []
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for obj in reader.pages:
            raw_text = obj.extract_text() or ""
            if raw_text.strip():
                blocks.append({
                    "page": obj.get("/StructParents", -1),
                    "text": raw_text.strip(),
                    "source": "static"
                })

        # Direct stream extraction from raw bytes
        raw = file_bytes.decode('latin1', errors='ignore')
        streams = re.findall(r'stream(.*?)endstream', raw, re.DOTALL)
        for idx, stream in enumerate(streams):
            stream_data = stream.strip().encode('latin1', errors='ignore')
            try:
                decompressed = zlib.decompress(stream_data)
                text = decompressed.decode('utf-8', errors='ignore')
                if text.strip():
                    blocks.append({
                        "page": None,
                        "text": text.strip(),
                        "source": "flate"
                    })
            except Exception:
                continue

    except Exception as e:
        blocks.append({
            "page": -1,
            "text": f"[static error] {e}",
            "source": "static"
        })

    return blocks