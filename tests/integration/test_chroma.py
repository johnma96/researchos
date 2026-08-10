import pytest

from researchos.domain.models import Document
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chroma_upsert_and_search():
    embedder = LocalEmbedder()
    store = ChromaVectorStore(embedder=embedder, collection_name="test_collection")

    docs = [
        Document(
            doc_id="t1", text="LLM agents use reasoning to solve tasks", metadata={"source": "test"}
        ),
        Document(
            doc_id="t2", text="RAG combines retrieval with generation", metadata={"source": "test"}
        ),
        Document(doc_id="t3", text="Python is a programming language", metadata={"source": "test"}),
    ]

    await store.upsert(docs)
    results = await store.search("how do agents reason?", k=2)

    assert isinstance(results, list)
    assert len(results) == 2
    assert all(isinstance(r, Document) for r in results)
    assert all(0 <= r.score <= 1 for r in results)
    assert results[0].doc_id == "t1"
