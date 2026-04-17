import asyncio
import re
import time

import httpx

from researchos.domain.models import Paper
from researchos.infrastructure.data.arxiv import search_papers
from researchos.paths import PAPERS_DIR


async def sequential_benchmark(query: str, max_results: int):
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


async def parallel_benchmark(query: str, max_results: int):
    start_time = time.perf_counter()

    papers = await search_papers(query, max_results)

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    await asyncio.gather(*(_download_one_paper(paper) for paper in papers))

    end_time = time.perf_counter()
    print(f"Parallel betchmark completed in {end_time - start_time} seconds")


async def _download_one_paper(paper: Paper):
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
