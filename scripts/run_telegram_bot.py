import sys

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import json
import logging
from datetime import UTC, datetime

import chromadb

from researchos.application.services.rag_service import answer_query
from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.config import settings
from researchos.domain.models import Document, ResearchContext
from researchos.infrastructure.bot.telegram_bot import AnswerFn, TelegramBot
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.orchestration.research_graph import build_research_graph
from researchos.infrastructure.retrieval.bm25 import BM25Retriever
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR, DATA_DIR

query_logger = logging.getLogger("researchos.queries")

# ── Build retrievers ──
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


# V1 pipeline (function calls, no LangGraph). Not wired to the bot below —
# kept so T24 can run it and answer_v2_graph side by side over the same queries.
async def answer_v1_pipeline(query: str) -> str:
    return await answer_query(query, llm, retrieve=retrieve_hybrid_rerank)


# V2 agent (LangGraph), wired to the bot below.
research_graph = build_research_graph(retrieve=retrieve_hybrid_rerank, llm=llm)


async def answer_v2_graph(query: str) -> str:
    result = await research_graph.ainvoke(ResearchContext(query=query))
    return result["answer"]


def with_logging(answer_fn: AnswerFn) -> AnswerFn:
    """Wrap an AnswerFn so every incoming query is appended to a JSONL file.

    Setup runs once at construction; the inner function runs per query.
    Used to collect real user queries for the V2 evaluation dataset (T24),
    avoiding the data leakage of writing eval questions against a known corpus.
    """
    log_path = DATA_DIR / "raw" / "queries.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    query_logger.addHandler(file_handler)
    query_logger.setLevel(logging.INFO)
    query_logger.propagate = False

    async def logged_answer(query: str) -> str:
        query_logger.info(
            json.dumps(
                {"ts": datetime.now(UTC).isoformat(), "query": query},
                ensure_ascii=False,
            )
        )
        return await answer_fn(query)

    return logged_answer


bot = TelegramBot(token=settings.telegram_bot_token, answer_fn=with_logging(answer_v2_graph))
bot.run()
