"""Research agent nodes — pure functions consumed by the LangGraph assembly.

Per ADR-005, nodes live in application/ as plain ``(ResearchContext) -> dict``
functions with zero LangGraph imports. Dependencies (RetrieveFn, LLMProvider)
cannot be passed as extra node parameters — LangGraph only calls a node with
the state — so each node is built by a factory that closes over its
dependency once, in the composition root (infrastructure/orchestration/).
"""

from collections.abc import Awaitable, Callable
from typing import Any

from researchos.application.agents.agent_utils import build_rag_messages
from researchos.domain.interfaces import LLMProvider
from researchos.domain.models import Document, ResearchContext
from researchos.domain.prompts import PromptTemplate

NodeFn = Callable[[ResearchContext], Awaitable[dict[str, Any]]]

# Local to this module, not domain/interfaces.py: RetrieveFn (list[Document]
# only) still serves the V1 pipeline and any plain retrieval need. This
# variant is specific to the graph's retrieve node, which also needs the
# LLM-judge verdict on relevance to route afterward — single consumer today
# (make_retrieve_node); promote to domain/interfaces.py if a second one
# appears, same criterion used for scripts/_wiring.py this week.
RetrieveWithVerdictFn = Callable[[str], Awaitable[tuple[list[Document], bool]]]


def make_retrieve_node(retrieve: RetrieveWithVerdictFn) -> NodeFn:
    """Build a retrieve node bound to a specific retrieval strategy.

    Args:
        retrieve: A RetrieveWithVerdictFn implementation (hybrid+rerank with
            an LLM-judge relevance verdict), injected as a closure so the
            node itself stays framework-free.

    Returns:
        An async node function that reads ``state.query`` and returns the
        partial state update ``{"documents": [...], "has_relevant_context":
        ...}`` for LangGraph to merge.
    """

    async def retrieve_node(state: ResearchContext) -> dict[str, Any]:
        documents, has_relevant_context = await retrieve(state.query)
        return {"documents": documents, "has_relevant_context": has_relevant_context}

    return retrieve_node


def should_search_arxiv(state: ResearchContext) -> str:
    """Route after retrieve: generate directly, or fall back to arXiv search.

    Pure ``state -> str`` function, per ADR-005/T19: testable with a
    fabricated state, without executing retrieve_node or calling the LLM.
    The arXiv tool node doesn't exist yet (T19 in progress) — this router
    is ready to wire into a conditional edge once it does.

    Args:
        state: Current graph state, read after the retrieve node ran.

    Returns:
        ``"generate"`` if local retrieval judged relevant context;
        ``"search_arxiv"`` otherwise.
    """
    return "generate" if state.has_relevant_context else "search_arxiv"


def make_generate_node(llm: LLMProvider) -> NodeFn:
    """Build a generate node bound to a specific LLM provider.

    The system prompt is rendered once at construction time, not per call.

    Args:
        llm: An LLMProvider implementation, injected as a closure.

    Returns:
        An async node function that reads ``state.query``/``state.documents``
        and returns the partial state update ``{"answer": "..."}``.
    """
    system_prompt = PromptTemplate("system", "agent").render()

    async def generate_node(state: ResearchContext) -> dict[str, Any]:
        messages = build_rag_messages(state.query, state.documents, system_prompt)
        return {"answer": await llm.generate(messages)}

    return generate_node
