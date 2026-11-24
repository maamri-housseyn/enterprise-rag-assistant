
from app.database.connection import SessionLocal
from app.database.models import DocumentChunk
from app.ingestion.embeddings import generate_embeddings

db = SessionLocal()

try:
    chunks = (
        db.query(DocumentChunk)
        .order_by(DocumentChunk.id)
        .all()
    )

    print(f"Nombre de chunks : {len(chunks)}")

    if not chunks:
        print("Aucun chunk à mettre à jour.")
    else:
        texts = [chunk.content for chunk in chunks]

        print("Calcul des nouveaux embeddings...")
        embeddings = generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Le nombre d'embeddings est incorrect.")

        if any(len(embedding) != 384 for embedding in embeddings):
            raise ValueError("Une dimension d'embedding est incorrecte.")

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()

        db.commit()

        print(f"{len(chunks)} chunks mis à jour avec succès.")

except Exception as error:
    db.rollback()
    print(f"Erreur : {error}")
    raise

finally:
    db.close()
