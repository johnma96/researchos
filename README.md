# 🔬 ResearchOS

Open-source research engine that monitors scientific and tech sources (arXiv, PubMed, RSS), answers questions in natural language, and sends personalized morning briefings.

> **Status:** V1 — RAG pipeline + Telegram bot (in progress)

## What it does

- **Ingests** papers from arXiv and PubMed via their public APIs
- **Indexes** content using hybrid search (BM25 + vector embeddings)
- **Answers** questions about papers using Claude as the LLM
- **Delivers** a morning briefing via Telegram with the latest research

## Architecture

```
Sources (arXiv, PubMed, RSS)
        │
    Ingestion → Chunking → Embeddings
        │
    Chroma DB (vector store) + BM25 index
        │
    Retrieval (hybrid search + reranking)
        │
    Claude API (generation)
        │
    Telegram Bot / FastAPI
```

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| V1 | RAG pipeline + Telegram bot | 🟡 In progress |
| V2 | LangGraph agent + daily briefing | ⬜ Planned |
| V3 | Observability (Langfuse) + evals | ⬜ Planned |
| V4 | Guardrails + GCP deploy + Vertex AI | ⬜ Planned |
| V5 | Smart router + Streamlit + portfolio | ⬜ Planned |
| V6 | Exploration: multi-agent, MCP, ADK | ⬜ Planned |

## Quick start

### Prerequisites

- Python 3.11
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (package manager)
- Anthropic API key
- Telegram bot token (via [@BotFather](https://t.me/BotFather))

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/researchos.git
cd researchos

# Install dependencies
uv sync --all-extras

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Verify setup
make test

# Run the bot
make run-bot
```

## Project structure

```
src/researchos/
├── ingestion/      # Paper download and parsing
├── retrieval/      # Chunking, embeddings, search
├── generation/     # Claude API calls
├── bot/            # Telegram bot
└── api/            # FastAPI endpoints
tests/              # Test suite
docs/               # Documentation + learnings diary
data/               # Downloaded papers (not in git)
```

## Tech stack (V1)

- **LLM:** Claude API (Anthropic)
- **Vector store:** Chroma DB
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Search:** Hybrid (BM25 + vector) with reranking
- **API:** FastAPI
- **Bot:** python-telegram-bot
- **Validation:** Pydantic v2

## License

MIT
