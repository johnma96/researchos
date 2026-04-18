from pathlib import Path

import pyprojroot

PROJECT_ROOT: Path = pyprojroot.here()
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = DATA_DIR / "papers"
SAMPLES_DIR = DATA_DIR / "samples"
CHROMA_DIR = DATA_DIR / "chroma"


def ensure_dirs() -> None:
    """Create all data directories if they don't exist."""
    dirs = [v for v in globals().values() if isinstance(v, Path) and v != PROJECT_ROOT]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
