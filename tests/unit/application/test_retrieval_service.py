"""Unit tests for hybrid_search and hybrid_rerank_search in retrieval_service."""

import json

import pytest

from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.domain.models import Document
from tests.conftest import MockLLMProvider, MockVectorStore


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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_rerank_search_respects_llm_order():
    """Documents must be returned in the order the LLM specifies."""
    docs = _make_docs("doc1", "doc2", "doc3")
    llm_order = ["doc3", "doc1", "doc2"]
    llm = MockLLMProvider(
        response=json.dumps({"ranked_ids": llm_order, "has_sufficient_context": True})
    )

    results, has_sufficient_context = await hybrid_rerank_search(
        query="test query", llm=llm, documents=docs, k=3
    )

    assert [r.doc_id for r in results] == llm_order
    assert has_sufficient_context is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_rerank_search_trims_to_k():
    """Only the first k documents from the LLM ranking are returned."""
    docs = _make_docs("doc1", "doc2", "doc3", "doc4", "doc5")
    llm_order = ["doc5", "doc3", "doc1", "doc4", "doc2"]
    llm = MockLLMProvider(
        response=json.dumps({"ranked_ids": llm_order, "has_sufficient_context": True})
    )

    results, _ = await hybrid_rerank_search(query="test query", llm=llm, documents=docs, k=3)

    assert len(results) == 3
    assert results[0].doc_id == "doc5"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_rerank_search_returns_false_verdict_when_llm_judges_insufficient():
    """The has_sufficient_context verdict from the LLM is propagated, not just the ranking."""
    docs = _make_docs("doc1", "doc2")
    llm = MockLLMProvider(
        response=json.dumps({"ranked_ids": ["doc1", "doc2"], "has_sufficient_context": False})
    )

    _, has_sufficient_context = await hybrid_rerank_search(
        query="test query", llm=llm, documents=docs, k=2
    )

    assert has_sufficient_context is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_rerank_search_defaults_to_sufficient_when_llm_omits_verdict():
    """A malformed response missing the verdict key must not crash the query.

    Models are more likely to omit a negative boolean verdict than to skip
    the ranking itself — failing open here means the query still gets an
    answer instead of raising KeyError up through the graph (no
    add_error_handler on the bot yet to catch it gracefully).
    """
    docs = _make_docs("doc1", "doc2")
    llm = MockLLMProvider(response=json.dumps({"ranked_ids": ["doc1", "doc2"]}))

    _, has_sufficient_context = await hybrid_rerank_search(
        query="test query", llm=llm, documents=docs, k=2
    )

    assert has_sufficient_context is True
