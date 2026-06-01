import pytest

from researchos.application.services.chunking_service import chunk_to_document, overlap_chunking
from researchos.domain.models import Chunk, Document


@pytest.mark.parametrize(
    "text,chunk_size,overlap,expected_single_chunk",
    [
        ("texto corto", 500, 50, True),
        ("Lorem ipsum dolor sit amet. " * 50, 500, 50, False),
        ("a" * 500, 500, 50, True),  # exactamente chunk_size
        ("a" * 501, 500, 50, False),  # un char más que chunk_size
    ],
)
@pytest.mark.unit
def test_overlap_chunking(text, chunk_size, overlap, expected_single_chunk):
    chunks = overlap_chunking(text=text, paper_id="test", chunk_size=chunk_size, overlap=overlap)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)

    if expected_single_chunk:
        assert len(chunks) == 1
        assert chunks[0].text == text
    else:
        assert len(chunks) > 1
        assert all(len(chunk.text) == chunk_size for chunk in chunks[:-1])
        assert all(
            chunks[i].text[-overlap:] == chunks[i + 1].text[:overlap]
            for i in range(len(chunks) - 1)
        )


@pytest.mark.unit
def test_chunk_to_document():
    chunk = Chunk(chunk_id="test_0", paper_id="test", text="Hello world!", chunk_index=0)

    doc = chunk_to_document(chunk=chunk)

    assert isinstance(doc, Document)
    assert doc.doc_id == chunk.chunk_id
    assert doc.text == chunk.text
    assert doc.metadata["paper_id"] == chunk.paper_id
