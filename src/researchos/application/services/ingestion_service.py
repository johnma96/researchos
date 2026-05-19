"""Ingestion service — Orchestrates the end-to-end paper ingestion pipeline.

This service coordinates three sequential steps:
1. Fetch paper metadata from arXiv via :func:`search_papers`.
2. Download and extract raw text from each PDF.
3. Chunk the text and upsert the resulting documents into the vector store.

Design note:
    Concrete infrastructure (``ChromaVectorStore``, ``LocalEmbedder``) is
    instantiated here rather than injected, because ``ingest_papers`` is an
    operational entry-point (called by CLI scripts), not a reusable
    application-layer use-case that needs swappable dependencies.
"""
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
    """Download a paper's PDF and extract its full text.

    Args:
        paper: A :class:`~researchos.domain.models.Paper` whose ``pdf_url``
            and ``authors`` fields are populated.

    Returns:
        A tuple of ``(full_text, local_pdf_path)`` where ``full_text`` is
        the concatenated text extracted from all pages, and ``local_pdf_path``
        is the path where the PDF was saved on disk.

    Raises:
        IngestionError: If the PDF contains no extractable text.
        httpx.HTTPStatusError: If the download request fails.
    """
    pdf_path = await _download_pdf(paper=paper)
    return _extract_text(pdf_path=pdf_path), pdf_path


async def _download_pdf(paper: Paper) -> Path:
    """Download the PDF for a paper and save it to ``PAPERS_DIR``.

    The local filename is derived from the first author's last name
    (lowercased, non-alphanumeric characters replaced with underscores)
    and the publication year (e.g. ``vaswani_2017.pdf``).

    Args:
        paper: A :class:`~researchos.domain.models.Paper` with a valid
            ``pdf_url``, ``authors`` list, and ``published_date``.

    Returns:
        The absolute ``Path`` where the PDF was saved.

    Raises:
        httpx.HTTPStatusError: If the HTTP request returns a non-2xx status.
    """
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
    """Extract all text from a PDF file using PyMuPDF (fitz).

    Args:
        pdf_path: Absolute path to the PDF file on disk.

    Returns:
        Concatenated plain-text content of all pages in the PDF.

    Raises:
        IngestionError: If the extracted text is empty (e.g. scanned PDF
            without OCR or DRM-protected file).
    """
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
    """Fetch, chunk, and index papers from arXiv into the vector store.

    This is the main entry-point for the ingestion pipeline.  It runs
    PDF downloads concurrently using :func:`asyncio.gather`, then processes
    each paper serially to avoid overwhelming the embedder.

    Args:
        query: arXiv search query string (e.g. ``"LLM agents"``).
        max_results: Maximum number of papers to fetch from arXiv.
        chunk_size: Number of characters per text chunk.  Defaults to 500.
        overlap: Character overlap between consecutive chunks to preserve
            context across boundaries.  Defaults to 50.
        collection_name: Name of the ChromaDB collection to upsert into.
            Defaults to ``"papers"``.
        embedder_metadata: Optional HNSW metadata dict forwarded to ChromaDB
            (e.g. ``{"hnsw:space": "cosine"}``).  If ``None``, the
            ``ChromaVectorStore`` default is used.

    Returns:
        None.  Side-effects: PDFs saved to ``PAPERS_DIR``, chunks upserted
        into the vector store.

    Raises:
        IngestionError: If any PDF cannot be downloaded or has no
            extractable text.
    """
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
