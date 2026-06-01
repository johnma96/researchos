"""Unit tests for hybrid_search in retrieval_service."""

import pytest

from researchos.application.services.retrieval_service import hybrid_search
from researchos.domain.models import Document
from tests.conftest import MockVectorStore


def _make_docs(*ids: str) -> list[Document]:
    return [Document(doc_id=doc_id, text=f"text for {doc_id}") for doc_id in ids]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_search_doc_in_both_retrievers_wins():
    """A document appearing in both retrievers must rank first — RRF accumulates scores."""
    retriever_a = MockVectorStore(_make_docs("doc1", "doc2", "doc3"))
    retriever_b = MockVectorStore(_make_docs("doc2", "doc4", "doc5"))

    results = await hybrid_search(
        query="test query",
        retrievers=[retriever_a, retriever_b],
        k=5,
    )

    assert results[0].doc_id == "doc2"
    assert results[0].score > results[1].score
    doc_ids = [r.doc_id for r in results]
    assert len(doc_ids) == len(set(doc_ids))
    assert len(results) <= 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_search_empty_retrievers_raises():
    """Passing an empty retrievers list must raise ValueError immediately."""
    with pytest.raises(ValueError):
        await hybrid_search(query="test", retrievers=[])
