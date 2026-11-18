from sqlalchemy import text

from app.database.connection import TestSessionLocal


def test_test_database_connection():
    db = TestSessionLocal()

    try:
        result = db.execute(text("SELECT 1"))

        assert result.scalar() == 1

    finally:
        db.close()