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
    """Search for papers on arXiv using the public API.

    Args:
        query: Search query string (supports arXiv query syntax).
        max_results: Maximum number of papers to return.

    Returns:
        List of Paper objects parsed from the arXiv Atom feed.

    Raises:
        httpx.HTTPStatusError: If the HTTP request fails.
        IngestionError: If the response cannot be parsed as XML.
    """
    params = {"search_query": query, "start": 0, "max_results": max_results}

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return _parse_entries(response)


def _parse_entries(results: httpx.Response) -> list[Paper]:
    """Parse an arXiv Atom XML response into a list of Paper objects.

    Args:
        results: The raw HTTP response from the arXiv API.

    Returns:
        List of Paper objects, one per ``<entry>`` element.

    Raises:
        IngestionError: If the response body is not valid XML.
    """
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
