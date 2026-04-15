from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from researchos.application.services.ingestion_service import extract_text_pdf
from researchos.domain.models import Paper
from researchos.paths import SAMPLES_DIR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_text_pdf():
    local_pdf = SAMPLES_DIR / "sample_pdf.pdf"

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
    mock_response.content = local_pdf.read_bytes()
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

    assert isinstance(result, str)
    assert len(result) > 0
