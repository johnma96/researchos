import argparse
import asyncio

from _wiring import build_dependencies

from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.domain.models import Document, ResearchContext
from researchos.infrastructure.orchestration.research_graph import build_research_graph

parser = argparse.ArgumentParser(description="Procesador de consultas.")
parser.add_argument(
    "-q", "--query", default="Qué es RLHF?", help="La query(consulta) que deseas procesar"
)
args = parser.parse_args()

K = 5
deps = build_dependencies()


async def retrieve_with_verdict(query: str) -> tuple[list[Document], bool]:
    candidates = await hybrid_search(query, retrievers=[deps.chroma, deps.bm25], k=K * 2)
    return await hybrid_rerank_search(query=query, llm=deps.llm, documents=candidates, k=K)


graph = build_research_graph(retrieve=retrieve_with_verdict, llm=deps.llm)
result = asyncio.run(graph.ainvoke(ResearchContext(query=args.query)))
print(result["query"], "\n")
print(result["documents"], "\n")
print("has_relevant_context:", result["has_relevant_context"], "\n")
print(result["answer"], "\n")
