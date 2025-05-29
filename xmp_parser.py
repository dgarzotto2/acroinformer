from .utils.xml_utils import parse_xmp_toolkit

def get_toolkit_from_pdf(file_path: str, file_bytes: bytes) -> str:
    """
    Helper wrapper: loads XMP then returns toolkit.
    """
    # We assume metadata.extract_metadata already parsed it;
    # This is here if you need standalone access.
    from .metadata import extract_metadata
    md = extract_metadata(file_path, file_bytes)
    return md.get("xmp_toolkit", "")