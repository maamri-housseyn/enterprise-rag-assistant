
import pymupdf
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text from all pages.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not pdf_path.is_file():
        raise ValueError(f"The path is not a file: {file_path}")

    extracted_text = ""

    try:
        with pymupdf.open(file_path) as document:
            for page in document:
                extracted_text += page.get_text()

    except pymupdf.FileDataError as error:
        raise ValueError(
            f"Invalid or corrupted PDF file: {file_path}"
        ) from error

    return extracted_text

def extract_pages_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF while preserving page numbers.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not pdf_path.is_file():
        raise ValueError(f"The path is not a file: {file_path}")

    pages = []

    try:
        with pymupdf.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):

                pages.append({
                    "page_number": page_number,
                    "content": page.get_text()
                })

    except pymupdf.FileDataError as error:
        raise ValueError(
            f"Invalid or corrupted PDF file: {file_path}"
        ) from error

    return pages