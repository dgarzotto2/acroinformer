import pytest
from metadata import extract_metadata

def test_extract_nonpdf(tmp_path, monkeypatch):
    # create a fake non-PDF
    f = tmp_path/"fake.txt"
    f.write_bytes(b"NOTPDF")
    md = extract_metadata(str(f), b"NOTPDF")
    assert "error" in md or md.get("producer") is None

def test_extract_valid_pdf(sample_pdf_path):
    # assume sample_pdf_path fixture gives a real PDF path+bytes
    path, data = sample_pdf_path
    md = extract_metadata(path, data)
    assert "creation_date" in md
    assert "has_acroform" in md