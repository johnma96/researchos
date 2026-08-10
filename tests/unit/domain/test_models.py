"""Unit tests for domain models — no IO, no APIs, pure logic."""

import pytest

from researchos import __version__
from researchos.domain.exceptions import (
    GenerationError,
    IngestionError,
    PaperNotFoundError,
    PromptNotFoundError,
    ResearchOSError,
    RetrievalError,
)
from researchos.domain.models import Chunk, Message, Paper, Query


@pytest.mark.unit
class TestVersion:
    def test_version_exists(self):
        assert isinstance(__version__, str)
        assert __version__ == "0.1.0"


@pytest.mark.unit
class TestPaperModel:
    def test_paper_creation(self, sample_paper: Paper):
        assert sample_paper.source_id == "2210.03629"
        assert sample_paper.source == "arxiv"
        assert len(sample_paper.authors) == 3

    def test_paper_defaults(self):
        paper = Paper(source_id="test", source="arxiv", title="Test")
        assert paper.authors == []
        assert paper.abstract == ""
        assert paper.categories == []


@pytest.mark.unit
class TestChunkModel:
    def test_chunk_creation(self, sample_chunks: list[Chunk]):
        assert len(sample_chunks) == 2
        assert sample_chunks[0].chunk_index == 0
        assert "ReAct" in sample_chunks[0].text


@pytest.mark.unit
class TestQueryModel:
    def test_query_defaults(self):
        query = Query(text="What is RAG?")
        assert query.top_k == 5
        assert "arxiv" in query.sources


@pytest.mark.unit
class TestMessageModel:
    def test_message_creation(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"


@pytest.mark.unit
class TestExceptions:
    def test_all_exceptions_inherit_from_base(self):
        assert issubclass(PaperNotFoundError, ResearchOSError)
        assert issubclass(IngestionError, ResearchOSError)
        assert issubclass(RetrievalError, ResearchOSError)
        assert issubclass(GenerationError, ResearchOSError)
        assert issubclass(PromptNotFoundError, ResearchOSError)
