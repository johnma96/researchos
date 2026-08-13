from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import fitz
import pytest

from researchos.application.services.ingestion_service import extract_text_pdf
from researchos.domain.models import Paper


def _fake_pdf_bytes() -> bytes:
    """Build a minimal valid PDF in memory — no disk, no fixture file."""
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "Test PDF content")
    return doc.tobytes()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_text_pdf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("researchos.application.services.ingestion_service.PAPERS_DIR", tmp_path)

    paper = Paper(
        source_id="1",
        source="arxiv",
        title="Test Title",
        authors=["Test Author"],
        published_date=datetime(2022, 1, 1),
        pdf_url="https://fake-url/paper.pdf",
        abstract="Test Abstract",
        categories=["test"],
    )

    mock_response = MagicMock()
    mock_response.content = _fake_pdf_bytes()
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "researchos.application.services.ingestion_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await extract_text_pdf(paper=paper)

    assert isinstance(result, tuple)
    assert isinstance(result[0], str)
    assert isinstance(result[1], Path)

    assert len(result) == 2
