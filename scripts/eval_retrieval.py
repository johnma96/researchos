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
    results = await store.search(query=question, k=max_results)
    for r in results:
        print(f"\nscore: {r.score:.3f}")
        print(f"text: {r.text[:200]}")
    return results


async def main() -> None:
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
