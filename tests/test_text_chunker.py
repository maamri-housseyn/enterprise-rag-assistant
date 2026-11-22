from app.ingestion.text_chunker import chunk_text

import pytest

def test_chunk_text_without_overlap():
    text = "Le Machine Learning utilise les données"

    chunks = chunk_text(text, chunk_size=3)

    assert chunks == [
        "Le Machine Learning",
        "utilise les données"
    ]

def test_chunk_text_with_overlap():
    text = "Le Machine Learning utilise les données"

    chunks = chunk_text(text, chunk_size=3, overlap=1)

    assert chunks == [
        "Le Machine Learning",
        "Learning utilise les",
        "les données"
    ]    



def test_chunk_text_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Bonjour tout le monde", chunk_size=0)


def test_chunk_text_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("Bonjour tout le monde", chunk_size=4, overlap=4)   


def test_chunk_text_empty_string():
    chunks = chunk_text("", chunk_size=3)

    assert chunks == []
