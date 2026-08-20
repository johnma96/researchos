"""Unit tests for the compiled research graph — retrieve and LLM mocked.

Unlike tests/unit/application/test_research_agent_nodes.py (nodes tested in
isolation), this exercises the assembled graph end to end via .ainvoke(),
confirming the wiring between nodes/edges actually works.
"""

import pytest
from tests.conftest import MockLLMProvider

from researchos.domain.models import Document, ResearchContext
from researchos.infrastructure.orchestration.research_graph import build_research_graph


@pytest.mark.unit
class TestBuildResearchGraph:
    @pytest.mark.asyncio
    async def test_retrieve_then_generate_end_to_end(
        self, mock_llm: MockLLMProvider, sample_documents: list[Document]
    ):
        async def fake_retrieve(query: str) -> list[Document]:
            return sample_documents

        graph = build_research_graph(retrieve=fake_retrieve, llm=mock_llm)
        result = await graph.ainvoke(ResearchContext(query="What is RAG?"))

        assert result["query"] == "What is RAG?"
        assert result["documents"] == sample_documents
        assert result["answer"] == "This is a mock response."
