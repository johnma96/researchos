"""Retrieval evaluation script — Manual sanity-check for the vector store.

Loads a JSON evaluation dataset from ``data/samples/eval_dataset.json``,
runs each question through the :class:`ChromaVectorStore`, and prints the
top retrieved documents with their relevance scores.  Useful for quickly
validating retrieval quality after changing chunk size, overlap, or the
embedding model.

Usage:
    uv run python scripts/eval_retrieval.py

Eval dataset format (``eval_dataset.json``):
    [
        {"question": "What is RAG?", "source_paper": "vaswani_2017"},
        ...
    ]
"""

import asyncio
import json

from researchos.domain.interfaces import VectorStore
from researchos.domain.models import Document
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import SAMPLES_DIR

path_examples = SAMPLES_DIR / "eval_dataset.json"


async def answer_question(
    question: str, store: VectorStore, max_results: int = 10
) -> list[Document]:
    """Retrieve and print the top documents for a given question.

    Searches the vector store for the most relevant chunks and prints each
    result's score and a 200-character preview of the text to stdout.

    Args:
        question: Natural-language question to search for.
        store: A :class:`~researchos.domain.interfaces.VectorStore`
            implementation (typically :class:`ChromaVectorStore`).
        max_results: Maximum number of documents to retrieve.  Defaults to 10.

    Returns:
        List of :class:`~researchos.domain.models.Document` objects returned
        by the vector store, in descending relevance order.
    """
    results = await store.search(query=question, k=max_results)
    for r in results:
        print(f"\nscore: {r.score:.3f}")
        print(f"text: {r.text[:200]}")
    return results


async def main() -> None:
    """Run the full retrieval evaluation loop.

    Reads each question from the eval dataset, calls :func:`answer_question`,
    and prints a summary showing which papers appeared in the top results
    compared to the expected ``source_paper``.

    Raises:
        FileNotFoundError: If ``data/samples/eval_dataset.json`` does not exist.
        json.JSONDecodeError: If the dataset file is malformed.
    """
    with open(path_examples, encoding="utf-8") as f:
        data = json.load(f)

    embedder = LocalEmbedder()
    store = ChromaVectorStore(embedder=embedder)

    answers = []
    for dict_question in data:
        print("-" * 10 + dict_question["question"] + "*" * 10)
        print(f"- pdf_ref: {dict_question['source_paper']}")
        answer = await answer_question(dict_question["question"], store=store, max_results=3)
        print(f"- papers in answer: {set([doc.metadata['paper_id'] for doc in answer])}")
        print("\n")
        answers.append(answer)


if __name__ == "__main__":
    asyncio.run(main())
