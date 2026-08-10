import sys

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

from researchos.application.services.rag_service import answer_query
from researchos.config import settings
from researchos.infrastructure.bot.telegram_bot import TelegramBot
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder

embedder = LocalEmbedder()
chroma = ChromaVectorStore(embedder=embedder, collection_name="papers")
llm = AnthropicLLM()


async def answer(query: str) -> str:
    return await answer_query(query, llm=llm, store=chroma)


bot = TelegramBot(token=settings.telegram_bot_token, answer_fn=answer)
bot.run()
