import pytest

from main import app
from app.database.connection import (
    TestSessionLocal,
    test_engine
)
from app.database.connection import get_db
from app.database.models import Base, Document


@pytest.fixture(autouse=True)
def use_test_database():
    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)

    # Override the database dependency
    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    # Clean test data after each test
    db = TestSessionLocal()

    try:
        db.query(Document).delete()
        db.commit()
    finally:
        db.close()

    # Restore the original dependency
    app.dependency_overrides.pop(get_db, None)