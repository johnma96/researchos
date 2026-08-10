"""Benchmark script — Compares sequential vs. concurrent PDF download speed.

Measures wall-clock time for downloading a batch of arXiv papers using two
strategies: sequential (one request at a time) and parallel (all requests
concurrent via ``asyncio.gather``).  Results are printed to stdout.

Usage:
    uv run python scripts/betchmark_arxiv.py

Note:
    The filename contains a deliberate typo (``betchmark`` instead of
    ``benchmark``) preserved from the original commit; do not rename without
    also updating Makefile references.
"""

import asyncio
import re
import time

import httpx

from researchos.domain.models import Paper
from researchos.infrastructure.data.arxiv import search_papers
from researchos.paths import PAPERS_DIR


async def sequential_benchmark(query: str, max_results: int) -> None:
    """Download arXiv papers sequentially and report elapsed time.

    Fetches paper metadata, then downloads each PDF one after the other
    using a synchronous :class:`httpx.Client` inside an ``async`` function.
    Use this as the baseline to compare against :func:`parallel_benchmark`.

    Args:
        query: arXiv search query string (e.g. ``"LLM agents"``).
        max_results: Number of papers to download.
    """
    start_time = time.perf_counter()

    papers = await search_papers(query, max_results)

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    for paper in papers:
        url = paper.pdf_url
        pdf_name = paper.authors[0].lower().strip()
        pdf_name = re.sub(r"[^a-z0-9_]", "_", pdf_name)
        pdf_name = pdf_name + "_" + paper.published_date.strftime("%Y")
        local_pdf_path = PAPERS_DIR / f"{pdf_name}.pdf"

        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            with open(local_pdf_path, "wb") as f:
                f.write(response.content)

    end_time = time.perf_counter()
    print(f"Sequential benchmark completed in {end_time - start_time} seconds")


async def parallel_benchmark(query: str, max_results: int) -> None:
    """Download arXiv papers concurrently and report elapsed time.

    Fetches paper metadata, then downloads all PDFs simultaneously using
    :func:`asyncio.gather` and :func:`_download_one_paper`.  Compare
    against :func:`sequential_benchmark` to measure the concurrency speedup.

    Args:
        query: arXiv search query string (e.g. ``"LLM agents"``).
        max_results: Number of papers to download in parallel.
    """
    start_time = time.perf_counter()

    papers = await search_papers(query, max_results)

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    await asyncio.gather(*(_download_one_paper(paper) for paper in papers))

    end_time = time.perf_counter()
    print(f"Parallel betchmark completed in {end_time - start_time} seconds")


async def _download_one_paper(paper: Paper) -> None:
    """Download a single paper PDF and save it to ``PAPERS_DIR``.

    Derives the local filename from the first author's name
    (lowercased, sanitised) and publication year, matching the convention
    used by the ingestion service.

    Args:
        paper: A :class:`~researchos.domain.models.Paper` with ``pdf_url``,
            ``authors``, and ``published_date`` populated.

    Raises:
        httpx.HTTPStatusError: If the download request fails.
    """
    url = paper.pdf_url
    pdf_name = paper.authors[0].lower().strip()
    pdf_name = re.sub(r"[^a-z0-9_]", "_", pdf_name)
    pdf_name = pdf_name + "_" + paper.published_date.strftime("%Y")
    local_pdf_path = PAPERS_DIR / f"{pdf_name}.pdf"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(local_pdf_path, "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    q = "LLM agents"
    asyncio.run(sequential_benchmark(q, 10))
    asyncio.run(parallel_benchmark(q, 10))
