from collections.abc import Awaitable, Callable

from researchos.application.agents.agent_utils import build_rag_messages
from researchos.domain.interfaces import LLMProvider
from researchos.domain.models import Document
from researchos.domain.prompts import PromptTemplate

RetrieveFn = Callable[[str], Awaitable[list[Document]]]


async def answer_query(query: str, llm: LLMProvider, retrieve: RetrieveFn) -> str:
    system_prompt = PromptTemplate("system", "agent").render()

    docs = await retrieve(query)
    messages = build_rag_messages(query, docs, system_prompt)
    return await llm.generate(messages)
