def split_text_into_chunks(
    text: str,
    chunk_size: int = 700,
    overlap: int = 100
) -> list[str]:

    if (chunk_size <= overlap):
        raise ValueError("chunk_size must be greater than overlap")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)

        if end == text_length:
            break

        start += (chunk_size - overlap)
    
    return chunks


