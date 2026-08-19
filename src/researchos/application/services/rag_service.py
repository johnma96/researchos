from researchos.application.agents.agent_utils import build_rag_messages
from researchos.domain.interfaces import LLMProvider, RetrieveFn
from researchos.domain.prompts import PromptTemplate


async def answer_query(query: str, llm: LLMProvider, retrieve: RetrieveFn) -> str:
    system_prompt = PromptTemplate("system", "agent").render()

    docs = await retrieve(query)
    messages = build_rag_messages(query, docs, system_prompt)
    return await llm.generate(messages)
