"""Retrieval service — Orchestrates document retrieval strategies.

Provides hybrid search by combining multiple Retriever implementations
(vector, BM25, etc.) via Reciprocal Rank Fusion (RRF). All retrievers
are queried in parallel using asyncio.gather and results are merged into
a single ranked list of Documents.
"""
