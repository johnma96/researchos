import pytest
from src.researchos.domain.models import Paper
from src.researchos.infrastructure.data.arxiv import search_papers


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_papers_integration():
    results = await search_papers(query="LLM agents", max_results=3)

    assert isinstance(results, list)
    assert len(results) == 3
    assert all(isinstance(paper, Paper) for paper in results)
    assert all(paper.title for paper in results)
    assert all(paper.abstract for paper in results)
    assert all(paper.authors for paper in results)
    assert all(paper.published_date for paper in results)
    assert all(paper.url for paper in results)
    assert all(paper.pdf_url for paper in results)
    assert all(paper.categories for paper in results)
    assert all(paper.source_id for paper in results)
    assert all(paper.source == "arxiv" for paper in results)
