import argparse
import sys

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import asyncio

import chromadb

from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.domain.models import Document, ResearchContext
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.orchestration.research_graph import build_research_graph
from researchos.infrastructure.retrieval.bm25 import BM25Retriever
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR

parser = argparse.ArgumentParser(description="Procesador de consultas.")
parser.add_argument(
    "-q", "--query", default="Qué es RLHF?", help="La query(consulta) que deseas procesar"
)
args = parser.parse_args()

COLLECTION_NAME = "papers"
K = 5
embedder = LocalEmbedder()
chroma = ChromaVectorStore(embedder=embedder, collection_name=COLLECTION_NAME)
llm = AnthropicLLM()

raw = (
    chromadb.PersistentClient(path=str(CHROMA_DIR))
    .get_collection(COLLECTION_NAME)
    .get(include=["documents", "metadatas"])
)
all_docs = [
    Document(doc_id=doc_id, text=text, metadata=metadata)
    for doc_id, text, metadata in zip(raw["ids"], raw["documents"], raw["metadatas"], strict=False)
]
bm25 = BM25Retriever(documents=all_docs)


async def retrieve_hybrid_rerank(query: str) -> list[Document]:
    candidates = await hybrid_search(query, retrievers=[chroma, bm25], k=K * 2)
    return await hybrid_rerank_search(query=query, llm=llm, documents=candidates, k=K)


graph = build_research_graph(retrieve=retrieve_hybrid_rerank, llm=llm)
result = asyncio.run(graph.ainvoke(ResearchContext(query=args.query)))
print(result["query"], "\n")
print(result["documents"], "\n")
print(result["answer"], "\n")
