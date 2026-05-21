import asyncio

from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore

from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.domain.models import Message
from researchos.domain.prompts.registry import load_prompt

def answer_query(user_query: str, max_results: int = 10, **kwargs) -> list[Message]:
    embedder = LocalEmbedder()
    chroma_store = ChromaVectorStore(embedder, **kwargs)

    docs = asyncio.run(chroma_store.search(query=user_query, k=max_results))
    print(docs)
    context = ''.join([doc.text for doc in docs if doc.score > 0.7])

    system_prompt = Message(
        role="system",
        content=load_prompt("system", "agent")
    )

    corpus = Message(
        role="user",
        content=f"""
        Based on the context provided below in triple backticks, answer 
        the following question: {user_query} 

        ```
        {context}
        ```
        """
    )
    
    messages = [
        system_prompt,
        corpus
    ]
        
    llm_model = AnthropicLLM()
    answer_model = asyncio.run(llm_model.generate(messages))
    messages.append(Message(role='assistant', content=answer_model))

    return messages