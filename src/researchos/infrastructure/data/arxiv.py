import xml.etree.ElementTree as ET

import httpx

from researchos.domain.exceptions import IngestionError
from researchos.domain.models import Paper

BASE_URL = "https://export.arxiv.org/api/query"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


async def search_papers(query: str, max_results: int) -> list[Paper]:
    params = {"search_query": query, "start": 0, "max_results": max_results}

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return _parse_entries(response)


def _parse_entries(results: httpx.Response) -> list[Paper]:
    if not results.text.strip().startswith("<"):
        raise IngestionError(f"arXiv returned unexpected response: {results.text[:100]}")

    root = ET.fromstring(results.text)

    papers = []

    for entry in root.findall("atom:entry", NS):
        id = entry.findtext("atom:id", namespaces=NS)
        title = entry.findtext("atom:title", namespaces=NS)
        summary = entry.findtext("atom:summary", namespaces=NS)
        published = entry.findtext("atom:published", namespaces=NS)
        authors = [
            author.findtext("atom:name", namespaces=NS)
            for author in entry.findall("atom:author", NS)
        ]
        categories = [cat.get("term") for cat in entry.findall("atom:category", NS)]
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
            elif link.get("rel") == "alternate":
                url = link.get("href")

        paper = Paper(
            source_id=id,
            source="arxiv",
            title=title,
            abstract=summary,
            authors=authors,
            published_date=published,
            url=url,
            pdf_url=pdf_url,
            categories=categories,
        )
        papers.append(paper)

    return papers
