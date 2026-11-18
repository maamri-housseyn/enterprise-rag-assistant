
from sqlalchemy.orm import Session

from app.database.models import Document


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
