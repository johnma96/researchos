import re
from pathlib import Path

import httpx
import pymupdf
from src.researchos.domain.models import Paper

PAPERS_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "papers"


def extract_text_pdf(paper: Paper) -> str:
    url = paper.pdf_url
    pdf_name = paper.authors[0].lower().strip()
    pdf_name = re.sub(r"[^a-z0-9_]", "_", pdf_name)
    pdf_name = pdf_name + "_" + paper.published_date.strftime("%Y")
    local_pdf_path = PAPERS_DIR / f"{pdf_name}.pdf"

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    response = httpx.get(url)
    response.raise_for_status()

    # save pdf in local as .pdf
    with open(local_pdf_path, "wb") as f:
        f.write(response.content)

    # extract text
    full_text = ""
    doc = pymupdf.open(local_pdf_path)
    for page in doc:
        full_text += page.get_text()

    if not full_text.strip():
        raise ValueError(f"PDF has no extractable text: {url}")

    return full_text
