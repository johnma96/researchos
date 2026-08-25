import json
import logging
from datetime import UTC, datetime

from _wiring import build_dependencies

from researchos.application.services.rag_service import answer_query
from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.config import settings
from researchos.domain.interfaces import AnswerFn
from researchos.domain.models import Document, ResearchContext
from researchos.infrastructure.bot.telegram_bot import TelegramBot
from researchos.infrastructure.orchestration.research_graph import build_research_graph
from researchos.paths import DATA_DIR

query_logger = logging.getLogger("researchos.queries")

K = 5
deps = build_dependencies()


async def retrieve_with_verdict(query: str) -> tuple[list[Document], bool]:
    candidates = await hybrid_search(query, retrievers=[deps.chroma, deps.bm25], k=K * 2)
    return await hybrid_rerank_search(query=query, llm=deps.llm, documents=candidates, k=K)


async def retrieve_hybrid_rerank(query: str) -> list[Document]:
    documents, _ = await retrieve_with_verdict(query)
    return documents


# V1 pipeline (function calls, no LangGraph). Not wired to the bot below —
# kept so T24 can run it and answer_v2_graph side by side over the same queries.
async def answer_v1_pipeline(query: str) -> str:
    return await answer_query(query, deps.llm, retrieve=retrieve_hybrid_rerank)


# V2 agent (LangGraph), wired to the bot below.
research_graph = build_research_graph(retrieve=retrieve_with_verdict, llm=deps.llm)


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
