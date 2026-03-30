"""Domain interfaces — Contracts that infrastructure must implement.

These Protocols define the capabilities that the application layer needs,
without specifying HOW they are implemented. Infrastructure provides
concrete implementations (Chroma, Anthropic, SQLite, etc.).

Usage in application layer:
    async def search(query: str, store: VectorStore) -> list[Document]:
        return await store.search(query, k=5)

Usage in tests:
    class MockVectorStore:
        async def search(self, query: str, k: int) -> list[Document]:
            return [Document(doc_id="1", text="mock result")]
        async def upsert(self, documents: list[Document]) -> None:
            pass
"""

from typing import AsyncIterator, Protocol

from .models import Document, Message


class LLMProvider(Protocol):
    """Contract for any LLM provider (Claude, Gemini, etc.)."""

    async def generate(self, messages: list[Message]) -> str:
        """Generate a response from a list of messages."""
        ...

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Stream a response token by token."""
        ...


class VectorStore(Protocol):
    """Contract for any vector store (Chroma, Vertex Search, Qdrant, etc.)."""

    async def search(self, query: str, k: int) -> list[Document]:
        """Search for the top-k most relevant documents."""
        ...

    async def upsert(self, documents: list[Document]) -> None:
        """Insert or update documents in the store."""
        ...


class MemoryStore(Protocol):
    """Contract for conversational memory persistence."""

    async def get(self, session_id: str) -> list[Message]:
        """Retrieve conversation history for a session."""
        ...

    async def append(self, session_id: str, message: Message) -> None:
        """Append a message to a session's history."""
        ...

    async def clear(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        ...
