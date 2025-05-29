import hashlib

def hash_file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def detect_duplicate_metadata(metadata_bank):
    seen = {}
    flags = []
    for sha, meta in metadata_bank.items():
        sig = (meta.get("creation_date"), meta.get("author"), meta.get("producer"))
        if sig in seen:
            flags.append(f"Duplicate: {sha} and {seen[sig]} share metadata signature {sig}")
        else:
            seen[sig] = sha
    return flags