# utils/utility.py

import hashlib
import os

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_ascii85_encoded(stream_bytes):
    return b"~>" in stream_bytes and b"<~" in stream_bytes

def file_size_in_kb(file_path):
    return round(os.path.getsize(file_path) / 1024, 2)

def redact_sensitive(text):
    return text.replace("@", "[at]").replace(".", "[dot]")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)