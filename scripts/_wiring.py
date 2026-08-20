"""Shared wiring for the operational scripts in this directory.

Not part of the installable package (scripts/ isn't). Each script runs via
``uv run python scripts/<name>.py``, so this module is imported by its bare
name (``_wiring``, not ``scripts._wiring``) — Python puts the running
script's own directory on ``sys.path``, not the repo root.

The pysqlite3 patch below must run before anything imports ``chromadb``
(which imports ``sqlite3`` internally), so it stays at module level here
instead of inside a function — importing this module is what applies it.
"""

import sys
from typing import NamedTuple

if sys.platform == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb

from researchos.domain.models import Document
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
from researchos.infrastructure.retrieval.bm25 import BM25Retriever
from researchos.infrastructure.retrieval.chroma import ChromaVectorStore
from researchos.infrastructure.retrieval.embedder import LocalEmbedder
from researchos.paths import CHROMA_DIR


class Dependencies(NamedTuple):
    """The embedder/Chroma/BM25/LLM stack shared by the bot and graph scripts."""

    chroma: ChromaVectorStore
    bm25: BM25Retriever
    llm: AnthropicLLM


def build_dependencies(collection_name: str = "papers") -> Dependencies:
    """Build retrievers and LLM against an existing Chroma collection.

    Loads every document already indexed in ``collection_name`` to build the
    BM25 side of hybrid search — there is no BM25 persistence, so it's
    rebuilt in memory from Chroma's stored documents on every run.

    Args:
        collection_name: Chroma collection to read from. Defaults to "papers".

    Returns:
        A Dependencies tuple with a ready-to-use chroma store, bm25
        retriever, and LLM provider.
    """
    embedder = LocalEmbedder()
    chroma = ChromaVectorStore(embedder=embedder, collection_name=collection_name)
    llm = AnthropicLLM()

    raw = (
        chromadb.PersistentClient(path=str(CHROMA_DIR))
        .get_collection(collection_name)
        .get(include=["documents", "metadatas"])
    )
    all_docs = [
        Document(doc_id=doc_id, text=text, metadata=metadata)
        for doc_id, text, metadata in zip(
            raw["ids"], raw["documents"], raw["metadatas"], strict=False
        )
    ]
    bm25 = BM25Retriever(documents=all_docs)

    return Dependencies(chroma=chroma, bm25=bm25, llm=llm)
