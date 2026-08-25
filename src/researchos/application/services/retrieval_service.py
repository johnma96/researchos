"""Retrieval service — Orchestrates document retrieval strategies.

Provides hybrid search by combining multiple Retriever implementations
(vector, BM25, etc.) via Reciprocal Rank Fusion (RRF). All retrievers
are queried in parallel using asyncio.gather and results are merged into
a single ranked list of Documents.
"""

import asyncio
import json

from researchos.domain.interfaces import LLMProvider, Retriever
from researchos.domain.models import Document, Message
from researchos.domain.prompts import PromptTemplate


async def hybrid_search(
    query: str,
    retrievers: list[Retriever],
    k: int = 5,
    candidates_per_retriever: int | None = None,
    rrf_k: int = 60,
) -> list[Document]:
    """Combine multiple retrievers into a single ranked list using Reciprocal Rank Fusion.

    Each retriever is queried in parallel for ``candidates_per_retriever`` documents.
    Results are merged with RRF: documents that appear in multiple rankings accumulate
    higher scores. The final list is deduplicated and trimmed to top-k.

    Args:
        query: Natural-language query string passed to every retriever.
        retrievers: List of Retriever implementations to query (e.g. BM25, vector).
            Must contain at least one retriever.
        k: Number of documents to return in the final ranked list.
        candidates_per_retriever: Documents fetched from each retriever before fusion.
            Defaults to ``k * 2`` to ensure enough candidates after deduplication.
        rrf_k: RRF smoothing constant (default 60, per Cormack et al. 2009).
            Higher values reduce the influence of top-ranked documents.

    Returns:
        List of up to ``k`` Documents sorted by RRF score descending, with the
        ``score`` field set to the accumulated RRF score.

    Raises:
        ValueError: If ``retrievers`` is empty.
    """
    if not retrievers:
        raise ValueError("At least one retriever is required.")

    n = candidates_per_retriever or k * 2

    results = await asyncio.gather(*[retriever.search(query, n) for retriever in retrievers])

    rrf_scores: dict[str, float] = {}
    docs_by_id: dict[str, Document] = {}

    for ranking in results:
        for rank, doc in enumerate(ranking, start=1):  # 1-indexed
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1 / (rrf_k + rank)
            docs_by_id.setdefault(doc.doc_id, doc)

    sorted_by_scores = dict(sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True))
    first_k = list(sorted_by_scores.items())[:k]

    return [docs_by_id[doc_id].model_copy(update={"score": score}) for doc_id, score in first_k]


async def hybrid_rerank_search(
    query: str,
    llm: LLMProvider,
    documents: list[Document],
    k: int = 5,
) -> tuple[list[Document], bool]:
    """Reorder candidate documents by relevance and judge if any are useful.

    Renders the ``tasks/rerank`` prompt with the query and document texts,
    asks the LLM to return a JSON object with the ranked document IDs and a
    verdict on whether the documents provide enough context to answer the
    query, and maps the IDs back to the original Document objects.

    Intended to be called after ``hybrid_search`` — pass its output as
    ``documents`` and this function returns the top-k reranked subset.

    Args:
        query: The original user query used to judge relevance.
        llm: An LLMProvider implementation (injected).
        documents: Candidate documents to rerank (typically hybrid top-10).
        k: Number of documents to return after reranking.

    Returns:
        A tuple of (documents, any_relevant): up to ``k`` Documents in
        LLM-ranked order (scores are not updated — the ordering itself is
        the signal), and a bool indicating whether the LLM judged any of
        them relevant enough to answer the query.

    Raises:
        json.JSONDecodeError: If the LLM response is not valid JSON.
        KeyError: If the LLM returns a doc_id not present in ``documents``,
            or omits ``ranked_ids``/``any_relevant`` from the response.
    """
    docs_str = "\n".join(f'"{doc.doc_id}": {doc.text}' for doc in documents)
    prompt = PromptTemplate("tasks", "rerank").render(query=query, documents=docs_str)
    message = Message(role="user", content=prompt)
    llm_answer = await llm.generate([message])

    # Extract the JSON array from the response — Claude may wrap it in markdown or add text.
    start = llm_answer.find("{")
    end = llm_answer.rfind("}") + 1
    payload = json.loads(llm_answer[start:end])

    ranked_ids = payload["ranked_ids"]
    any_relevant = payload["any_relevant"]

    docs_by_id = {doc.doc_id: doc for doc in documents}
    return [docs_by_id[doc_id] for doc_id in ranked_ids[:k] if doc_id in docs_by_id], any_relevant
