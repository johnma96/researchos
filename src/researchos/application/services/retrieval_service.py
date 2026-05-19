"""Retrieval service — Text chunking utilities for the ingestion pipeline.

Provides pure, stateless functions for splitting paper text into overlapping
chunks and converting those chunks into the ``Document`` format expected by
the vector store.  These utilities are shared by the ingestion service and
can be reused in evaluation scripts.

Design note:
    Functions here have no side-effects and no external dependencies beyond
    domain models.  They belong in ``application/services/`` (not ``domain/``)
because they encode an operational decision (chunk size, overlap strategy)
    rather than a business concept.
"""
from researchos.domain.models import Chunk, Document


def overlap_chunking(
    text: str, paper_id: str, chunk_size: int = 500, overlap: int = 50
) -> list[Chunk]:
    """Split a text string into overlapping fixed-size chunks.

    Each chunk starts at ``chunk_size - overlap`` characters after the
    previous one, so adjacent chunks share ``overlap`` characters of context.
    This sliding-window approach reduces information loss at chunk boundaries.

    Args:
        text: Full text content of the paper to be chunked.
        paper_id: Identifier used as the prefix for each ``chunk_id``
            (e.g. the PDF stem).
        chunk_size: Number of characters in each chunk.  Defaults to 500.
        overlap: Number of characters shared between consecutive chunks.
            Defaults to 50.

    Returns:
        Ordered list of :class:`~researchos.domain.models.Chunk` objects
        with ``chunk_id``, ``paper_id``, ``text``, ``chunk_index``, and
        position metadata (``start_char``, ``end_char``).

    Example:
        >>> chunks = overlap_chunking("Hello world " * 100, "paper_abc")
        >>> chunks[0].chunk_id
        'paper_abc_0'
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
    """Convert a :class:`~researchos.domain.models.Chunk` into a :class:`~researchos.domain.models.Document`.

    Merges the chunk's own metadata with ``paper_id`` and ``chunk_index``
    fields so that documents stored in the vector store can be traced back
    to their source paper and position.

    Args:
        chunk: A populated :class:`~researchos.domain.models.Chunk` object.

    Returns:
        A :class:`~researchos.domain.models.Document` ready to be upserted
        into the vector store, with ``doc_id == chunk.chunk_id``.
    """
    return Document(
        doc_id=chunk.chunk_id,
        text=chunk.text,
        metadata={**chunk.metadata, "paper_id": chunk.paper_id, "chunk_index": chunk.chunk_index},
    )
