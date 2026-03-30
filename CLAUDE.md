# ResearchOS — Context for Claude Code

> Read automatically by Claude Code at the start of every session.

## Current Phase

- **Version:** V1 — RAG Robusto + Telegram
- **Weeks:** 1–4
- **Focus:** Iterative RAG (fixed → semantic → hybrid → reranking), Telegram bot

> **UPDATE THIS** as you progress through versions.

## Architecture: Clean Architecture (3 layers)

```
src/researchos/
├── config.py                          # Pydantic Settings (single source of config)
├── domain/                            # PURE LOGIC — zero external deps
│   ├── models.py                      # Paper, Chunk, Query, Document, Message, etc.
│   ├── exceptions.py                  # Typed business errors
│   ├── interfaces.py                  # Protocols: LLMProvider, VectorStore, MemoryStore
│   └── prompts/                       # .txt templates + registry.py (str.format)
├── application/                       # USE CASE ORCHESTRATION
│   ├── agents/                        # Autonomous (decides, iterates, calls tools)
│   │   ├── agent_utils.py             # Shared functions via COMPOSITION (not inheritance)
│   │   └── research_agent/            # One folder per agent
│   └── services/                      # Deterministic flows (always same steps)
│       ├── ingestion_service.py
│       ├── retrieval_service.py
│       └── evaluation_service.py
└── infrastructure/                    # CONCRETE IMPLEMENTATIONS
    ├── api/                           # FastAPI + routers
    ├── bot/                           # Telegram
    ├── llm/                           # anthropic.py, vertex_ai.py → implement LLMProvider
    ├── memory/                        # in_memory.py, sqlite.py → implement MemoryStore
    ├── retrieval/                     # chroma.py, vertex_search.py → implement VectorStore
    ├── data/                          # bigquery.py, database.py (corporate data)
    └── monitoring/                    # langfuse.py, cloud_logging.py
```

### Layer Rules (NEVER violate)
- **domain/** has ZERO external deps. Only stdlib + Pydantic. NEVER import infra here.
- **application/** programs against Protocols from domain/interfaces.py, never concrete infra.
- **infrastructure/** implements Protocols. All external libraries live here.
- Dependency direction: infrastructure → application → domain (never reverse).

## Key Patterns

### Adding a new agent
1. Create folder: `application/agents/new_agent/`
2. Create `agent.py` — import from `agent_utils.py` what you need (composition)
3. Create `tools.py` if the agent has specific tools
4. Register router in `infrastructure/api/routers/`
5. Add tests in `tests/unit/application/`

### Adding a new LLM provider
1. Create file: `infrastructure/llm/new_provider.py`
2. Implement `LLMProvider` Protocol from `domain/interfaces.py`
3. Add Literal option in `config.py`

### Adding a new vector store
1. Create file: `infrastructure/retrieval/new_store.py`
2. Implement `VectorStore` Protocol from `domain/interfaces.py`
3. Add Literal option in `config.py`

## Tech Stack (V1)

- Python 3.11 | uv | Pydantic v2 + Pydantic Settings
- Claude API (anthropic SDK) | Chroma | sentence-transformers (all-MiniLM-L6-v2)
- rank_bm25 | FastAPI | python-telegram-bot v21+
- pytest + pytest-asyncio | ruff

## Coding Conventions

- Type hints on all function signatures
- Pydantic models for all data (no raw dicts)
- Google-style docstrings on public functions
- Config via `from researchos.config import settings`
- `logging` module (no print())
- Line length: 100 | Imports sorted by ruff

## What NOT to do

- Do NOT use LangChain/LangGraph in V1. Direct Claude API calls only.
- Do NOT put business logic in infrastructure/
- Do NOT import infrastructure in domain/
- Do NOT use class inheritance for agents — use composition via agent_utils.py
- Do NOT hardcode prompts in Python files — use domain/prompts/*.txt

## Useful Commands

```bash
make test          # Unit tests only
make test-all      # Unit + integration
make lint          # ruff check
make format        # ruff format
make run-api       # FastAPI server
make run-bot       # Telegram bot
```
