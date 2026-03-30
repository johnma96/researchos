"""Agent utilities — Shared functions for agents via composition.

Instead of a base class with inheritance, agents import and use these
functions as building blocks. This is more flexible and testable.

Usage:
    from researchos.application.agents.agent_utils import retrieve_and_generate

    answer = await retrieve_and_generate(query, llm, store, system_prompt)
"""

from researchos.domain.interfaces import LLMProvider, VectorStore
from researchos.domain.models import Document, Message


async def retrieve_context(
    query: str,
    store: VectorStore,
    top_k: int = 5,
) -> list[Document]:
    """Retrieve relevant documents from the vector store."""
    return await store.search(query, k=top_k)


def build_rag_messages(
    query: str,
    documents: list[Document],
    system_prompt: str,
) -> list[Message]:
    """Build a message list for RAG: system prompt + context + query."""
    context = "\n\n".join(
        f"[{i + 1}] {doc.text}" for i, doc in enumerate(documents)
    )
    return [
        Message(role="system", content=system_prompt),
        Message(
            role="user",
            content=f"Context:\n{context}\n\nQuestion: {query}",
        ),
    ]


async def retrieve_and_generate(
    query: str,
    llm: LLMProvider,
    store: VectorStore,
    system_prompt: str,
    top_k: int = 5,
) -> str:
    """Full RAG pattern: retrieve documents, build context, generate answer."""
    docs = await retrieve_context(query, store, top_k)
    messages = build_rag_messages(query, docs, system_prompt)
    return await llm.generate(messages)
