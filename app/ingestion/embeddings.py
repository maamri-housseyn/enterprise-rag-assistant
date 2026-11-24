from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

model = SentenceTransformer(MODEL_NAME)

def generate_embedding(text: str):
    """
    Generate an embedding vector from a text.

    Args:
        text: Input text.

    Returns:
        A numerical vector representing the text.
    """
    embedding = model.encode(text)

    return embedding

def generate_embeddings(texts: list[str]):
    """
    Generate embeddings for multiple texts.

    Args:
        texts: A list of input texts.

    Returns:
        A numerical array containing all embeddings.
    """
    embeddings = model.encode(texts)

    return embeddings