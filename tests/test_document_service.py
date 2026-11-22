
from app.database.connection import TestSessionLocal
from app.database.models import Document
from app.database.models import Document, DocumentChunk

from app.services.document_service import (
    create_document,
    get_document_by_id,
    update_document,
    delete_document,
    create_document_chunks,
)
from app.database.connection import test_engine
from app.database.models import Base

Base.metadata.create_all(bind=test_engine)
def test_document_crud():
    db = TestSessionLocal()

    try:
        # 1. Create
        document = create_document(
            db=db,
            filename="pytest_document.pdf",
            file_path="data/pytest_document.pdf"
        )

        assert document.id is not None

        # 2. Read
        retrieved_document = get_document_by_id(
            db=db,
            document_id=document.id
        )

        assert retrieved_document is not None
        assert retrieved_document.filename == "pytest_document.pdf"

        # 3. Update
        updated_document = update_document(
            db=db,
            document_id=document.id,
            new_filename="pytest_document_updated.pdf"
        )

        assert updated_document is not None
        assert updated_document.filename == "pytest_document_updated.pdf"

        # 4. Delete
        assert delete_document(db, document.id) is True

        # 5. Verify deletion
        assert get_document_by_id(db, document.id) is None

    finally:
        db.query(Document).delete()
        db.commit()
        db.close()


def test_create_document_chunks():
    db = TestSessionLocal()

    try:
        # 1. Create a document
        document = create_document(
            db=db,
            filename="rag_test.pdf",
            file_path="data/rag_test.pdf"
        )

        # 2. Prepare chunks
        chunks = [
            {
                "page_number": 1,
                "content": "Les antivirus protègent les ordinateurs."
            },
            {
                "page_number": 2,
                "content": "Le Machine Learning utilise les données."
            }
        ]

        # 3. Prepare embeddings (384 dimensions each)
        embeddings = [
            [0.1] * 384,
            [0.2] * 384
        ]

        # 4. Store chunks and embeddings
        stored_chunks = create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings
        )

        # 5. Verify results
        assert len(stored_chunks) == 2

        assert stored_chunks[0].content == chunks[0]["content"]
        assert stored_chunks[1].content == chunks[1]["content"]

        assert stored_chunks[0].page_number == chunks[0]["page_number"]
        assert stored_chunks[1].page_number == chunks[1]["page_number"]

        assert len(stored_chunks[0].embedding) == 384
        assert len(stored_chunks[1].embedding) == 384

        assert stored_chunks[0].document_id == document.id

    finally:
        # Delete chunks before deleting their document
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.commit()
        db.close()