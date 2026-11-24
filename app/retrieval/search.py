
from sqlalchemy.orm import Session

from app.ingestion.embeddings import generate_embedding
from app.database.models import DocumentChunk


def search_similar_chunks(
    db: Session,
    question: str,
    document_id: int | None = None,
    limit: int = 3,
    distance_threshold: float = 0.70
):
    question_embedding = generate_embedding(question)

    query = db.query(
        DocumentChunk,
        DocumentChunk.embedding.cosine_distance(
            question_embedding
        ).label("distance")
    )

    if document_id is not None:
        query = query.filter(
            DocumentChunk.document_id == document_id
        )

    results = (
        query
        .filter(
            DocumentChunk.embedding.cosine_distance(
                question_embedding
            ) <= distance_threshold
        )
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                question_embedding
            )
        )
        .limit(limit)
        .all()
    )

    return results
