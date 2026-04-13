from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from researchos.application.services.ingestion_service import extract_text_pdf
from researchos.domain.models import Paper

PAPERS_SAMPLE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "samples"


@pytest.mark.unit
def test_extract_text_pdf():
    local_pdf = PAPERS_SAMPLE_DIR / "sample_pdf.pdf"

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

    with patch(
        "researchos.application.services.ingestion_service.httpx.get", return_value=mock_response
    ):
        result = extract_text_pdf(paper=paper)

    assert isinstance(result, str)
    assert len(result) > 0
