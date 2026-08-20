"""Script: Ingest arXiv papers into the vector store.

Thin CLI wrapper around ``ingest_papers`` — fetches papers matching a query,
downloads and chunks them, and upserts the resulting documents into Chroma.
The service does all the work; this script only parses arguments and drives it.

Usage:
    uv run python scripts/ingest_documents.py --query "LLM agents reasoning" --max-results 5
    uv run python scripts/ingest_documents.py --query "chaos and fluids" \
        --max-results 2 --collection hydraulics

This is an operational script, not part of the installable package.
"""

import argparse
import asyncio

import _wiring  # noqa: F401  # applies the pysqlite3 patch before ingest_papers touches chromadb

from researchos.application.services.ingestion_service import ingest_papers
from researchos.paths import ensure_dirs


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the ingestion run."""
    parser = argparse.ArgumentParser(description="Ingest arXiv papers into the vector store.")
    parser.add_argument("--query", required=True, help="arXiv search query, e.g. 'LLM agents'")
    parser.add_argument(
        "--max-results", type=int, default=5, help="Max papers to fetch. Default: 5"
    )
    parser.add_argument(
        "--collection", default="papers", help="Chroma collection name. Default: 'papers'"
    )
    return parser.parse_args()


async def main() -> None:
    """Parse arguments and run the ingestion pipeline."""
    args = parse_args()
    ensure_dirs()
    await ingest_papers(
        query=args.query,
        max_results=args.max_results,
        collection_name=args.collection,
    )


if __name__ == "__main__":
    asyncio.run(main())
