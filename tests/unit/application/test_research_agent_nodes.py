"""Unit tests for research agent nodes — pure functions, no LangGraph involved.

Per ADR-005, each node is tested by passing a fabricated ResearchContext and
asserting the returned partial-state dict, with no graph execution needed.
"""

import pytest

from researchos.application.agents.research_agent.nodes import (
    make_generate_node,
    make_retrieve_node,
)
from researchos.domain.models import Document, ResearchContext
from tests.conftest import MockLLMProvider


@pytest.mark.unit
class TestRetrieveNode:
    @pytest.mark.asyncio
    async def test_returns_documents_from_retrieve_fn(self, sample_documents: list[Document]):
        async def fake_retrieve(query: str) -> list[Document]:
            assert query == "What is RAG?"
            return sample_documents

        retrieve_node = make_retrieve_node(fake_retrieve)
        result = await retrieve_node(ResearchContext(query="What is RAG?"))

        assert result == {"documents": sample_documents}


@pytest.mark.unit
class TestGenerateNode:
    @pytest.mark.asyncio
    async def test_returns_llm_answer(
        self, mock_llm: MockLLMProvider, sample_documents: list[Document]
    ):
        generate_node = make_generate_node(mock_llm)
        state = ResearchContext(query="What is RAG?", documents=sample_documents)

        result = await generate_node(state)

        assert result == {"answer": "This is a mock response."}
        assert len(mock_llm.calls) == 1

    @pytest.mark.asyncio
    async def test_passes_query_and_documents_to_llm(
        self, mock_llm: MockLLMProvider, sample_documents: list[Document]
    ):
        """A node that ignored state.documents would still return an answer —
        this asserts on what was actually sent to the LLM, not just the output."""
        generate_node = make_generate_node(mock_llm)
        state = ResearchContext(query="What is RAG?", documents=sample_documents)

        await generate_node(state)

        messages = mock_llm.calls[0]
        assert messages[0].role == "system"
        assert messages[1].role == "user"
        assert "What is RAG?" in messages[1].content
        for doc in sample_documents:
            assert doc.text in messages[1].content
