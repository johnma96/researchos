from researchos.domain.models import Chunk


def overlap_chunking(
    text: str, paper_id: str, chunk_size: int = 500, overlap: int = 50
) -> list[Chunk]:
    chunks = []

    for i, initial_car in enumerate(range(0, len(text), chunk_size)):
        start_chunk = initial_car - overlap * i
        end_chunk = start_chunk + chunk_size
        text_chunk = text[start_chunk:end_chunk]
        chunk_id = f"{paper_id}_{i}"
        start_char = start_chunk
        end_char = min(end_chunk, len(text))

        chunk = Chunk(
            chunk_id=chunk_id,
            paper_id=paper_id,
            text=text_chunk,
            metadata={
                "chunk_size": chunk_size,
                "overlap": overlap,
                "start_char": start_char,
                "end_char": end_char,
            },
            chunk_index=i,
        )

        chunks.append(chunk)
    return chunks
