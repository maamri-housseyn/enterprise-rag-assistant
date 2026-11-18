
from app.database.connection import TestSessionLocal
from app.database.models import Document
from app.services.document_service import (
    create_document,
    get_document_by_id,
    update_document,
    delete_document,
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
