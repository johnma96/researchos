from researchos.domain.models import Chunk, Document


def overlap_chunking(
    text: str, paper_id: str, chunk_size: int = 500, overlap: int = 50
) -> list[Chunk]:
    """Split a text into fixed-size chunks with character-level overlap.

    Each chunk's start position is shifted back by ``overlap * chunk_index``
    characters so consecutive chunks share context at their boundaries.

    Args:
        text: Full document text to split.
        paper_id: Identifier of the source paper, used as a prefix in chunk IDs.
        chunk_size: Number of characters per chunk.
        overlap: Number of characters of overlap between consecutive chunks.

    Returns:
        Ordered list of Chunk objects covering the full text.
    """
    chunks = []

    for i, initial_car in enumerate(range(0, len(text), chunk_size)):
        start_chunk = initial_car - overlap * i
        end_chunk = start_chunk + chunk_size

        chunk = Chunk(
            chunk_id=f"{paper_id}_{i}",
            paper_id=paper_id,
            text=text[start_chunk:end_chunk],
            metadata={
                "chunk_size": chunk_size,
                "overlap": overlap,
                "start_char": start_chunk,
                "end_char": min(end_chunk, len(text)),
            },
            chunk_index=i,
        )

        chunks.append(chunk)
    return chunks


def chunk_to_document(chunk: Chunk) -> Document:
    """Convert a Chunk into a Document suitable for vector store indexing.

    Merges chunk-level metadata with ``paper_id`` and ``chunk_index`` so that
    retrieved Documents retain full provenance information.

    Args:
        chunk: Source Chunk to convert.

    Returns:
        Document with the same text and enriched metadata.
    """
    return Document(
        doc_id=chunk.chunk_id,
        text=chunk.text,
        metadata={**chunk.metadata, "paper_id": chunk.paper_id, "chunk_index": chunk.chunk_index},
    )
