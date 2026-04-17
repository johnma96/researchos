import pytest

from researchos.application.services.retrieval_service import overlap_chunking
from researchos.domain.models import Chunk


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
