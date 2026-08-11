"""Retrieval evaluation script — Compares four retrieval strategies.

Loads the evaluation dataset from ``data/samples/eval_dataset.json`` and
runs each question through four strategies:
    1. Vector search (ChromaVectorStore)
    2. BM25 (BM25Retriever)
    3. Hybrid RRF (vector + BM25)
    4. Hybrid + LLM rerank

Reports P@k and MRR per strategy across all questions.

Usage:
    uv run python scripts/eval_retrieval.py

Eval dataset format (``eval_dataset.json``):
    [
        {"question": "...", "reference_answer": "...", "source_paper": "paper_stem.pdf"},
        ...
    ]
"""

import asyncio
import json
import sys

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb

from researchos.application.services.retrieval_service import hybrid_rerank_search, hybrid_search
from researchos.domain.models import Document
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.retrieval.bm25 import BM25Retriever
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR, SAMPLES_DIR

COLLECTION_NAME = "papers"
K = 5
path_examples = SAMPLES_DIR / "eval_dataset.json"


def _paper_id(source_paper: str) -> str:
    """Normalize source_paper to match the paper_id stored in chunk metadata."""
    return source_paper.replace(".pdf", "")


def _precision_at_k(results: list[Document], source_paper: str, k: int) -> float:
    """Return 1.0 if source_paper appears in the top-k results, else 0.0."""
    top_k_ids = {doc.metadata.get("paper_id", "") for doc in results[:k]}
    return 1.0 if _paper_id(source_paper) in top_k_ids else 0.0


def _reciprocal_rank(results: list[Document], source_paper: str) -> float:
    """Return 1/rank of the first result matching source_paper, or 0.0."""
    target = _paper_id(source_paper)
    for rank, doc in enumerate(results, start=1):
        if doc.metadata.get("paper_id", "") == target:
            return 1.0 / rank
    return 0.0


async def _rerank(
    query: str, chroma: ChromaVectorStore, bm25: BM25Retriever, llm: AnthropicLLM
) -> list[Document]:
    """Run hybrid search then rerank the top-10 with Claude."""
    candidates = await hybrid_search(query, retrievers=[chroma, bm25], k=K * 2)
    return await hybrid_rerank_search(query=query, llm=llm, documents=candidates, k=K)


async def main() -> None:
    """Run the full evaluation loop and print a strategy comparison table."""
    with open(path_examples, encoding="utf-8") as f:
        data = json.load(f)

    # ── Build retrievers ──
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
        for doc_id, text, metadata in zip(
            raw["ids"], raw["documents"], raw["metadatas"], strict=False
        )
    ]
    bm25 = BM25Retriever(documents=all_docs)

    strategies = {
        "vector": lambda q: chroma.search(q, K),
        "bm25": lambda q: bm25.search(q, K),
        "hybrid": lambda q: hybrid_search(q, retrievers=[chroma, bm25], k=K),
        "hybrid+rerank": lambda q: _rerank(q, chroma, bm25, llm),
    }

    scores: dict[str, list[float]] = {s: [] for s in strategies}
    mrr: dict[str, list[float]] = {s: [] for s in strategies}

    for item in data:
        question = item["question"]
        source = item["source_paper"]
        print(f"\nQ: {question[:80]}...")
        print(f"   expected: {_paper_id(source)}")

        for name, fn in strategies.items():
            results = await fn(question)
            p = _precision_at_k(results, source, K)
            rr = _reciprocal_rank(results, source)
            scores[name].append(p)
            mrr[name].append(rr)
            found = _paper_id(source) in {doc.metadata.get("paper_id", "") for doc in results[:K]}
            print(f"   {name:15s} P@{K}={'✓' if found else '✗'}  RR={rr:.2f}")

    # ── Summary table ──
    print("\n" + "=" * 50)
    print(f"{'Strategy':<15} {'P@' + str(K):>6}  {'MRR':>6}")
    print("-" * 30)
    for name in strategies:
        avg_p = sum(scores[name]) / len(scores[name])
        avg_mrr = sum(mrr[name]) / len(mrr[name])
        print(f"{name:<15} {avg_p:>6.3f}  {avg_mrr:>6.3f}")


if __name__ == "__main__":
    asyncio.run(main())
