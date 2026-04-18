import asyncio
import re
from pathlib import Path

import fitz
import httpx

from researchos.application.services.retrieval_service import chunk_to_document, overlap_chunking
from researchos.domain.exceptions import IngestionError
from researchos.domain.models import Paper
from researchos.infrastructure.data.arxiv import search_papers
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import PAPERS_DIR


async def extract_text_pdf(paper: Paper) -> tuple[str, Path]:
    pdf_path = await _download_pdf(paper=paper)
    return _extract_text(pdf_path=pdf_path), pdf_path


async def _download_pdf(paper: Paper) -> Path:
    url = paper.pdf_url
    pdf_name = paper.authors[0].lower().strip()
    pdf_name = re.sub(r"[^a-z0-9_]", "_", pdf_name)
    pdf_name = pdf_name + "_" + paper.published_date.strftime("%Y")
    local_pdf_path = PAPERS_DIR / f"{pdf_name}.pdf"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        # save pdf in local system
        with open(local_pdf_path, "wb") as f:
            f.write(response.content)

    return local_pdf_path


def _extract_text(pdf_path: Path) -> str:
    full_text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        full_text += page.get_text()

    if not full_text.strip():
        raise IngestionError(f"PDF has no extractable text: {pdf_path}")

    return full_text


async def ingest_papers(
    query: str,
    max_results: int,
    chunk_size: int = 500,
    overlap: int = 50,
    collection_name: str = "papers",
    embedder_metadata: dict | None = None,
) -> None:
    embedder = LocalEmbedder()
    store = ChromaVectorStore(
        embedder=embedder, collection_name=collection_name, embedder_metadata=embedder_metadata
    )

    papers = await search_papers(query, max_results)

    results = await asyncio.gather(*(extract_text_pdf(paper) for paper in papers))
    texts = [r[0] for r in results]
    local_paths = [r[1] for r in results]

    for text, pdf_path in zip(texts, local_paths, strict=False):
        chunks = overlap_chunking(
            text=text, paper_id=pdf_path.stem, chunk_size=chunk_size, overlap=overlap
        )

        docs = [chunk_to_document(chunk) for chunk in chunks]

        await store.upsert(docs)
