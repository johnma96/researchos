"""Retrieval service — Orchestrates document retrieval strategies.

Provides hybrid search by combining multiple Retriever implementations
(vector, BM25, etc.) via Reciprocal Rank Fusion (RRF). All retrievers
are queried in parallel using asyncio.gather and results are merged into
a single ranked list of Documents.
"""

import asyncio

from researchos.domain.interfaces import Retriever
from researchos.domain.models import Document


async def hybrid_search(
    query: str,
    retrievers: list[Retriever],
    k: int = 5,
    candidates_per_retriever: int | None = None,
    rrf_k: int = 60,
) -> list[Document]:
    if not retrievers:
        raise ValueError("Without retrievers. Add retrieves, please")

    n = candidates_per_retriever or k * 2

    results = await asyncio.gather(*[retriever.search(query, n) for retriever in retrievers])

    rrf_scores = {}
    docs_by_id = {}

    for ranking in results:
        for rank, doc in enumerate(ranking, start=1):  # 1-indexed
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1 / (rrf_k + rank)
            docs_by_id.setdefault(doc.doc_id, doc)

    sorted_by_scores = dict(sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True))
    first_k = list(sorted_by_scores.items())[:k]

    return [docs_by_id[doc_id].model_copy(update={"score": score}) for doc_id, score in first_k]
