
from sqlalchemy.orm import Session

from app.database.models import Document

from app.database.models import Document, DocumentChunk

def create_document(
    db: Session,
    filename: str,
    file_path: str
) -> Document:
    """
    Create a new document in the database.
    """

    document = Document(
        filename=filename,
        file_path=file_path
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise


def get_document_by_id(
    db: Session,
    document_id: int
) -> Document | None:
    """
    Retrieve a document by its ID.
    """

    return db.query(Document).filter(
        Document.id == document_id
    ).first()


def update_document(
    db: Session,
    document_id: int,
    new_filename: str
) -> Document | None:
    """
    Update the filename of an existing document.
    """

    document = get_document_by_id(db, document_id)

    if document is None:
        return None

    try:
        document.filename = new_filename

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise


def delete_document(
    db: Session,
    document_id: int
) -> bool:
    """
    Delete a document by its ID.
    """

    document = get_document_by_id(db, document_id)

    if document is None:
        return False

    try:
        db.delete(document)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise


def create_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[dict],
    embeddings: list[list[float]]
) -> list[DocumentChunk]:

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    document_chunks = []

    for chunk, embedding in zip(chunks, embeddings):

        document_chunk = DocumentChunk(
            document_id=document_id,
            page_number=chunk["page_number"],
            content=chunk["content"],
            embedding=embedding
        )

        document_chunks.append(document_chunk)
    try:
        db.add_all(document_chunks)
        db.commit()

        for document_chunk in document_chunks:
            db.refresh(document_chunk)

        return document_chunks

    except Exception:
        db.rollback()
        raise