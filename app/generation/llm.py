import ollama


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using the question and retrieved context.
    """

    prompt = f"""
    You are an assistant specialized in analyzing enterprise documents.

    Instructions:
    - Answer the question using only the provided context.
    - Do not invent or assume information that is not present in the context.
    - Present information clearly and in a structured way.
    - Distinguish between required steps and optional strategies to be tested.
    - Cite the page numbers supporting your answer using the format [Page X].
    - If the context does not contain enough information to answer the question, state this clearly.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    response = ollama.chat(
        model="mistral:latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]