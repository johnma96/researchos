import re
from pathlib import Path

import fitz
import httpx

from researchos.domain.exceptions import IngestionError
from researchos.domain.models import Paper
from researchos.paths import PAPERS_DIR

PAPERS_DIR.mkdir(parents=True, exist_ok=True)


async def extract_text_pdf(paper: Paper) -> str:
    pdf_path = await _download_pdf(paper=paper)
    return _extract_text(pdf_path=pdf_path)


async def _download_pdf(paper: Paper) -> Path:
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

    return local_pdf_path


def _extract_text(pdf_path: Path) -> str:
    full_text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        full_text += page.get_text()

    if not full_text.strip():
        raise IngestionError(f"PDF has no extractable text: {pdf_path}")

    return full_text
