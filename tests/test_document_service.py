
from app.database.connection import TestSessionLocal
from app.database.models import Document
from app.database.models import Document, DocumentChunk

from app.services.document_service import (
    create_document,
    get_document_by_id,
    update_document,
    delete_document,
    create_document_chunks,
    replace_document_chunks,
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



def test_delete_document_with_chunks():
    db = TestSessionLocal()

    document = None

    try:
        # 1. Create a document
        document = create_document(
            db=db,
            filename="document_with_chunks.pdf",
            file_path="data/document_with_chunks.pdf"
        )

        # 2. Create associated chunks
        chunks = [
            {
                "page_number": 1,
                "content": "First test chunk."
            },
            {
                "page_number": 2,
                "content": "Second test chunk."
            }
        ]

        embeddings = [
            [0.1] * 384,
            [0.2] * 384
        ]

        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings
        )

        # 3. Verify that chunks exist
        assert db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).count() == 2

        # 4. Delete the document
        assert delete_document(db, document.id) is True

        # 5. Verify that the document and chunks are deleted
        assert get_document_by_id(db, document.id) is None

        remaining_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).count()

        assert remaining_chunks == 0

    finally:
        if document is not None:
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete(synchronize_session=False)

            db.query(Document).filter(
                Document.id == document.id
            ).delete(synchronize_session=False)

            db.commit()

        db.close()


def test_replace_document_chunks():
    db = TestSessionLocal()
    document = None

    try:
        # 1. Create a document
        document = create_document(
            db=db,
            filename="original.pdf",
            file_path="data/original.pdf"
        )

        # 2. Add the original chunks
        original_chunks = [
            {"page_number": 1, "content": "Original content one."},
            {"page_number": 2, "content": "Original content two."}
        ]
        original_embeddings = [
            [0.1] * 384,
            [0.2] * 384
        ]

        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=original_chunks,
            embeddings=original_embeddings
        )

        # 3. Replace the document and its chunks
        new_chunks = [
            {"page_number": 1, "content": "New content one."},
            {"page_number": 3, "content": "New content three."},
            {"page_number": 4, "content": "New content four."}
        ]
        new_embeddings = [
            [0.3] * 384,
            [0.4] * 384,
            [0.5] * 384
        ]

        updated_document = replace_document_chunks(
            db=db,
            document_id=document.id,
            new_filename="updated.pdf",
            new_file_path="data/updated.pdf",
            chunks=new_chunks,
            embeddings=new_embeddings
        )

        # 4. Verify document information
        assert updated_document is not None
        assert updated_document.filename == "updated.pdf"
        assert updated_document.file_path == "data/updated.pdf"

        # 5. Verify that only the new chunks remain
        stored_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).order_by(DocumentChunk.page_number).all()

        assert len(stored_chunks) == 3
        assert [chunk.content for chunk in stored_chunks] == [
            "New content one.",
            "New content three.",
            "New content four."
        ]
        assert [chunk.page_number for chunk in stored_chunks] == [1, 3, 4]

    finally:
        if document is not None:
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete(synchronize_session=False)
            db.query(Document).filter(
                Document.id == document.id
            ).delete(synchronize_session=False)
            db.commit()

        db.close()
