from researchos.application.agents.agent_utils import retrieve_and_generate
from researchos.domain.interfaces import LLMProvider, VectorStore
from researchos.domain.prompts import PromptTemplate


async def answer_query(
    query: str,
    llm: LLMProvider,
    store: VectorStore,
    top_k: int = 5,
) -> str:
    system_prompt = PromptTemplate("system", "agent").render()
    return await retrieve_and_generate(query, llm, store, system_prompt, top_k)
