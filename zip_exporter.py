import io, zipfile, yaml
from .metadata import extract_metadata

def build_forensic_package(files: list) -> bytes:
    """
    Given a list of Streamlit-UploadedFiles, returns a ZIP (bytes)
    containing each PDF plus a YAML of its metadata.
    """
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w") as z:
        for uf in files:
            path, b = uf.name, uf.read()
            z.writestr(f"pdfs/{uf.name}", b)
            md = extract_metadata(path, b)
            z.writestr(f"metadata/{uf.name}.yaml", yaml.safe_dump(md))
    return mem.getvalue()