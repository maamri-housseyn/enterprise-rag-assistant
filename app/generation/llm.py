import ollama


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using the question and retrieved context.
    """
    prompt = f"""
    You are an assistant specialized in analyzing enterprise documents.

    Instructions:
    - Always respond in the same language as the user's question.
    - The language of your instructions and context must not determine the response language.
    - If the user's question is in French, answer entirely in French.
    - If the user's question is in English, answer entirely in English.
    - Use only information explicitly provided in the context.
    - Never invent, assume, or add unsupported information.
    - Present information clearly and in a structured way.
    - Distinguish between explicitly mentioned methods and general explanations.
    - Cite the supporting page numbers using the format [Page X].
    - If the context does not contain enough information, state this clearly in the user's language.
    - Do not include explanations or recommendations that are not supported by the context.

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