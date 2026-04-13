from pathlib import Path

import pyprojroot

PROJECT_ROOT: Path = pyprojroot.here()
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = DATA_DIR / "papers"
SAMPLES_DIR = DATA_DIR / "samples"
CHROMA_DIR = DATA_DIR / "chroma"
