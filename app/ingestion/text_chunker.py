def chunk_text(text, chunk_size, overlap=0):

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])

        chunks.append(chunk)

    return chunks

def chunk_pages(pages, chunk_size, overlap=0):

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks = []

    step = chunk_size - overlap

    for page in pages:

        page_number = page["page_number"]
        text = page["content"]

        words = text.split()

        for i in range(0, len(words), step):

            chunk = " ".join(words[i:i + chunk_size])

            chunks.append({
                "page_number": page_number,
                "content": chunk
            })

    return chunks