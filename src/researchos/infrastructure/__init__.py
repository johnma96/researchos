"""Infrastructure Layer — Concrete implementations of external systems.

Contains:
- api/: FastAPI endpoints (HTTP channel)
- bot/: Telegram bot (messaging channel)
- llm/: LLM providers (Claude, Vertex AI) — implements LLMProvider Protocol
- memory/: Conversation persistence — implements MemoryStore Protocol
- retrieval/: Vector stores (Chroma, Vertex Search) — implements VectorStore Protocol
- data/: Corporate data access (BigQuery, RDBMS)
- monitoring/: Langfuse, Cloud Logging

RULES:
- This is where ALL external libraries and API calls live
- Each module implements a Protocol from domain/interfaces.py
- If you switch Chroma → Qdrant, only this layer changes
- If you switch Claude → GPT, only this layer changes
"""
