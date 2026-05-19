"""arXiv data client — Fetches paper metadata from the arXiv Atom API.

Uses the public arXiv query API (``https://export.arxiv.org/api/query``)
to search for papers by keyword and parses the Atom XML response into
:class:`~researchos.domain.models.Paper` domain objects.

No authentication is required.  Rate limits apply: the arXiv ToS asks
callers to stay below 3 requests per second.

Example:
    >>> from researchos.infrastructure.data.arxiv import search_papers
    >>> papers = await search_papers("LLM agents", max_results=5)
    >>> papers[0].title
    'ReAct: Synergizing Reasoning and Acting in Language Models'
"""
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
    """Search arXiv for papers matching a query string.

    Sends a GET request to the arXiv Atom API and parses the response
    into a list of :class:`~researchos.domain.models.Paper` objects.

    Args:
        query: arXiv search query string.  Supports the ``all:``, ``ti:``,
            ``au:``, ``abs:`` field prefixes (e.g. ``"ti:LLM agents"``).
        max_results: Maximum number of papers to return.  ArXiv caps this
            at 30 000; realistic values are 1–50 for ingestion runs.

    Returns:
        List of :class:`~researchos.domain.models.Paper` objects populated
        with title, abstract, authors, URL, PDF URL, and categories.

    Raises:
        IngestionError: If the API response is not valid XML.
        httpx.HTTPStatusError: If the HTTP request fails.
    """
    params = {"search_query": query, "start": 0, "max_results": max_results}

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return _parse_entries(response)


def _parse_entries(results: httpx.Response) -> list[Paper]:
    """Parse an arXiv Atom API response into a list of Paper objects.

    Args:
        results: The raw :class:`httpx.Response` from the arXiv API.

    Returns:
        List of :class:`~researchos.domain.models.Paper` objects, one per
        ``<entry>`` element found in the Atom feed.

    Raises:
        IngestionError: If the response body does not start with ``<``
            (i.e. is not XML), which typically indicates an API error page.
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
