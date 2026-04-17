"""Shared test fixtures — mocks for Protocols and sample data."""

import sys

import pytest

from researchos.domain.models import Chunk, Document, Message, Paper

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# ── Sample data fixtures ──


@pytest.fixture
def sample_paper() -> Paper:
    return Paper(
        source_id="2210.03629",
        source="arxiv",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao", "Dian Yu"],
        abstract="While large language models have demonstrated impressive capabilities...",
        url="https://arxiv.org/abs/2210.03629",
        pdf_url="https://arxiv.org/pdf/2210.03629",
        categories=["cs.CL", "cs.AI"],
    )


@pytest.fixture
def sample_chunks(sample_paper: Paper) -> list[Chunk]:
    return [
        Chunk(
            chunk_id=f"{sample_paper.source_id}_0",
            paper_id=sample_paper.source_id,
            text="ReAct prompts LLMs to generate both reasoning traces and actions.",
            metadata={"section": "abstract"},
            chunk_index=0,
        ),
        Chunk(
            chunk_id=f"{sample_paper.source_id}_1",
            paper_id=sample_paper.source_id,
            text="The reasoning trace helps the model induce and track plans.",
            metadata={"section": "introduction"},
            chunk_index=1,
        ),
    ]


@pytest.fixture
def sample_documents() -> list[Document]:
    return [
        Document(doc_id="1", text="ReAct prompts LLMs to generate reasoning traces.", score=0.95),
        Document(doc_id="2", text="Chain-of-thought prompting improves reasoning.", score=0.87),
    ]


# ── Mock implementations of Protocols ──


class MockLLMProvider:
    """Mock LLM that returns a fixed response. Implements LLMProvider Protocol."""

    def __init__(self, response: str = "This is a mock response."):
        self.response = response
        self.calls: list[list[Message]] = []

    async def generate(self, messages: list[Message]) -> str:
        self.calls.append(messages)
        return self.response

    async def stream(self, messages: list[Message]):
        self.calls.append(messages)
        for word in self.response.split():
            yield word + " "


class MockVectorStore:
    """Mock vector store. Implements VectorStore Protocol."""

    def __init__(self, documents: list[Document] | None = None):
        self.documents = documents or []
        self.upserted: list[Document] = []

    async def search(self, query: str, k: int) -> list[Document]:
        return self.documents[:k]

    async def upsert(self, documents: list[Document]) -> None:
        self.upserted.extend(documents)


class MockMemoryStore:
    """Mock memory store. Implements MemoryStore Protocol."""

    def __init__(self):
        self.sessions: dict[str, list[Message]] = {}

    async def get(self, session_id: str) -> list[Message]:
        return self.sessions.get(session_id, [])

    async def append(self, session_id: str, message: Message) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)

    async def clear(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)


@pytest.fixture
def mock_llm() -> MockLLMProvider:
    return MockLLMProvider()


@pytest.fixture
def mock_vector_store(sample_documents: list[Document]) -> MockVectorStore:
    return MockVectorStore(documents=sample_documents)


@pytest.fixture
def mock_memory() -> MockMemoryStore:
    return MockMemoryStore()
