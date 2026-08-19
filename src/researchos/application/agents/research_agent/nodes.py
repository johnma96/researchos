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
from researchos.domain.interfaces import LLMProvider, RetrieveFn
from researchos.domain.models import ResearchContext
from researchos.domain.prompts import PromptTemplate

NodeFn = Callable[[ResearchContext], Awaitable[dict[str, Any]]]


def make_retrieve_node(retrieve: RetrieveFn) -> NodeFn:
    """Build a retrieve node bound to a specific retrieval strategy.

    Args:
        retrieve: A RetrieveFn implementation (vector-only, hybrid, etc.),
            injected as a closure so the node itself stays framework-free.

    Returns:
        An async node function that reads ``state.query`` and returns the
        partial state update ``{"documents": [...]}`` for LangGraph to merge.
    """

    async def retrieve_node(state: ResearchContext) -> dict[str, Any]:
        return {"documents": await retrieve(state.query)}

    return retrieve_node


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
