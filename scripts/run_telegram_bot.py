import sys

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb

from researchos.application.services.rag_service import answer_query
from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.config import settings
from researchos.domain.models import Document
from researchos.infrastructure.bot.telegram_bot import TelegramBot
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.retrieval.bm25 import BM25Retriever
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR

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


async def answer(query: str) -> str:
    return await answer_query(query, llm, retrieve=retrieve_hybrid_rerank)


bot = TelegramBot(token=settings.telegram_bot_token, answer_fn=answer)
bot.run()
