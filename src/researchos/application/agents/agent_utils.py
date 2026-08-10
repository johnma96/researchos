"""Shared agent utilities — building blocks for agents via composition.

Instead of a base class with inheritance, agents import and compose these
functions. This pattern keeps each agent self-contained, independently
testable, and free from hidden behavior inherited from a parent class.

All functions here:
    - Accept domain interfaces (Protocols) as parameters, never concrete types.
    - Return domain models (Pydantic), never raw dicts or SDK objects.
    - Are async to support non-blocking I/O throughout the call stack.

How to use:
    Import only the functions your agent needs::

        from researchos.application.agents.agent_utils import (
            retrieve_context,
            build_rag_messages,
            retrieve_and_generate,
            load_history_and_append,
            wrap_output,
        )

How to extend:
    Add new utility functions here when the same pattern appears in two or
    more agents. Do not add agent-specific logic here — keep it in the agent.
"""

from researchos.domain.interfaces import LLMProvider, MemoryStore, VectorStore
from researchos.domain.models import AgentOutput, Document, Message


async def retrieve_context(
    query: str,
    store: VectorStore,
    top_k: int = 5,
) -> list[Document]:
    """Retrieve relevant documents from the vector store for a given query.

    Args:
        query: The search string to use for retrieval.
        store: A VectorStore implementation (injected, never instantiated here).
        top_k: Number of documents to retrieve.

    Returns:
        List of documents ranked by relevance score, descending.
    """
    return await store.search(query, k=top_k)


def build_rag_messages(
    query: str,
    documents: list[Document],
    system_prompt: str,
) -> list[Message]:
    """Build the message list for a RAG call: system prompt + context + query.

    Args:
        query: The user's question.
        documents: Retrieved documents to use as context.
        system_prompt: The rendered system prompt for the agent.

    Returns:
        A two-element list: [system message, user message with embedded context].
    """
    context = "\n\n".join(f"[{i + 1}] {doc.text}" for i, doc in enumerate(documents))
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
    """Execute the full RAG pattern: retrieve → build context → generate.

    This is the most common single-turn agent pattern. For multi-turn
    conversations or tool-use loops, build a dedicated agent function instead.

    Args:
        query: The user's question.
        llm: An LLMProvider implementation (injected).
        store: A VectorStore implementation (injected).
        system_prompt: The rendered system prompt for the agent.
        top_k: Number of documents to retrieve.

    Returns:
        The LLM's response as a plain string.
    """
    docs = await retrieve_context(query, store, top_k)
    messages = build_rag_messages(query, docs, system_prompt)
    return await llm.generate(messages)


async def load_history_and_append(
    session_id: str,
    new_message: Message,
    memory: MemoryStore,
) -> list[Message]:
    """Load conversation history and append the new message.

    Use this when building multi-turn agents that need conversational context.

    Args:
        session_id: The session identifier for the conversation.
        new_message: The message to append to the history.
        memory: A MemoryStore implementation (injected).

    Returns:
        The full conversation history including the new message.
    """
    history = await memory.get(session_id)
    await memory.append(session_id, new_message)
    return [*history, new_message]


def wrap_output(answer: str, sources: list[Document] | None = None) -> AgentOutput:
    """Wrap a raw LLM response string into a typed AgentOutput.

    Args:
        answer: The raw text response from the LLM.
        sources: Optional list of documents used as context.

    Returns:
        A typed AgentOutput ready to return from the agent function.
    """
    return AgentOutput(answer=answer, sources=sources or [])
