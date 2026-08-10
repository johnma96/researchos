"""Unit tests for agent utilities — uses mock Protocols, no IO."""

import pytest

from researchos.application.agents.agent_utils import (
    build_rag_messages,
    retrieve_and_generate,
    retrieve_context,
)
from researchos.domain.models import Document
from tests.conftest import MockLLMProvider, MockVectorStore


@pytest.mark.unit
class TestRetrieveContext:
    @pytest.mark.asyncio
    async def test_returns_documents(self, mock_vector_store: MockVectorStore):
        docs = await retrieve_context("test query", mock_vector_store, top_k=2)
        assert len(docs) == 2
        assert isinstance(docs[0], Document)


@pytest.mark.unit
class TestBuildRagMessages:
    def test_builds_correct_message_structure(self, sample_documents: list[Document]):
        messages = build_rag_messages("What is RAG?", sample_documents, "You are helpful.")
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert messages[1].role == "user"
        assert "What is RAG?" in messages[1].content


@pytest.mark.unit
class TestRetrieveAndGenerate:
    @pytest.mark.asyncio
    async def test_full_rag_flow(
        self, mock_llm: MockLLMProvider, mock_vector_store: MockVectorStore
    ):
        result = await retrieve_and_generate(
            query="What is RAG?",
            llm=mock_llm,
            store=mock_vector_store,
            system_prompt="You are helpful.",
        )
        assert result == "This is a mock response."
        assert len(mock_llm.calls) == 1
