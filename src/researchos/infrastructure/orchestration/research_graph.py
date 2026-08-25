"""LangGraph assembly for the research agent.

Per ADR-005, this is the only module in the project allowed to import
``langgraph`` — ``StateGraph``, edges and ``compile()`` are the one part of
the graph that truly requires the framework. Nodes and state stay
framework-free (see ``application/agents/research_agent/nodes.py`` and
``domain/models.ResearchContext``).
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from researchos.application.agents.research_agent.nodes import (
    RetrieveWithVerdictFn,
    make_generate_node,
    make_retrieve_node,
)
from researchos.domain.interfaces import LLMProvider
from researchos.domain.models import ResearchContext


def build_research_graph(
    retrieve: RetrieveWithVerdictFn, llm: LLMProvider
) -> CompiledStateGraph[ResearchContext, None, ResearchContext, ResearchContext]:
    """Assemble and compile the minimal retrieve-then-generate research graph.

    Args:
        retrieve: A RetrieveWithVerdictFn implementation, injected into the
            retrieve node.
        llm: An LLMProvider implementation, injected into the generate node.

    Returns:
        A compiled LangGraph graph ready to run via ``.ainvoke(ResearchContext(...))``.
    """
    builder = StateGraph(ResearchContext)

    # Add nodes. The ignores below are a stub limitation (langgraph==1.2.11,
    # mypy==1.20.1), not a real type error: mypy cannot bind add_node's generic
    # NodeInputT against a plain async Callable (reproduced with a minimal
    # StateGraph outside this project too, including passing input_schema
    # explicitly). Tracked upstream as langchain-ai/langgraph#5000 (making
    # StateGraph/CompiledStateGraph generic-safe is still open, no target
    # version yet) — re-check this ignore next time langgraph is upgraded.
    builder.add_node("retrieve", make_retrieve_node(retrieve))  # type: ignore[call-overload]
    builder.add_node("generate", make_generate_node(llm))  # type: ignore[call-overload]

    # Add edges to connect nodes
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)

    # Compile the agent
    return builder.compile()
