import pytest

from app.ingestion.pdf_extractor import extract_text_from_pdf


def test_extract_text_from_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("data/samples/inexistant.pdf")

def test_extract_text_from_pdf_invalid_file(tmp_path):
    invalid_pdf = tmp_path / "invalid.pdf"
    invalid_pdf.write_text("ceci n'est pas un PDF")

    with pytest.raises(ValueError):
        extract_text_from_pdf(str(invalid_pdf))

def test_extract_text_from_pdf_success():
    text = extract_text_from_pdf("data/samples/sample.pdf")

    assert isinstance(text, str)
    assert len(text) > 0