"""Project path constants — single source of truth for filesystem locations.

All paths are derived from the project root discovered by ``pyprojroot``
(looks for ``pyproject.toml``). Import these constants instead of
building paths manually to stay resilient against directory changes.

Exported constants:
    PROJECT_ROOT: Absolute path to the repository root.
    DATA_DIR: Root directory for all persistent data (``data/``).
    PAPERS_DIR: Downloaded raw PDF files (``data/papers/``).
    SAMPLES_DIR: Evaluation datasets and sample files (``data/samples/``).
    CHROMA_DIR: ChromaDB persistence directory (``data/chroma/``).

Example:
    >>> from researchos.paths import PAPERS_DIR
    >>> pdf_path = PAPERS_DIR / "attention_2017.pdf"
"""

from pathlib import Path

import pyprojroot

PROJECT_ROOT: Path = pyprojroot.here()
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = DATA_DIR / "papers"
SAMPLES_DIR = DATA_DIR / "samples"
SCHEMAS_DIR = DATA_DIR / "schemas"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"


def ensure_dirs() -> None:
    """Create all data directories if they do not already exist.

    Iterates over every module-level variable whose value is a ``Path``
    instance (excluding ``PROJECT_ROOT`` itself, which is not a data
    directory) and calls ``mkdir(parents=True, exist_ok=True)`` on each.

    Typical call site: application startup or the ingestion script entry-point
    to guarantee the directory tree is present before writing files.

    Example:
        >>> from researchos.paths import ensure_dirs
        >>> ensure_dirs()  # Creates data/, data/papers/, data/samples/, data/chroma/
    """
    dirs = [v for v in globals().values() if isinstance(v, Path) and v != PROJECT_ROOT]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
