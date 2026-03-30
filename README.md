# ResearchOS

Open-source research engine that monitors scientific and tech sources (arXiv, PubMed, RSS), answers questions in natural language, and sends personalized morning briefings.

> **Status:** V1 — RAG pipeline + Telegram bot (in progress)

## Architecture

Clean Architecture with three layers and explicit contracts:

```
Domain (pure logic + Protocols) → Application (orchestration) → Infrastructure (external systems)
```

- **Domain:** Models, exceptions, interfaces (Protocols), prompt templates. Zero external deps.
- **Application:** Agents (autonomous) and Services (deterministic) that orchestrate workflows.
- **Infrastructure:** Claude API, Chroma, Telegram, FastAPI, Langfuse, BigQuery.

See [docs/architecture.md](docs/architecture.md) for detailed decision records.

## Quick start

```bash
# Prerequisites: Python 3.11, uv, Anthropic API key
git clone https://github.com/YOUR_USERNAME/researchos.git
cd researchos
uv sync --all-extras
cp .env.example .env        # Edit with your API keys
make test                   # Verify setup
```

## Project structure

```
src/researchos/
├── config.py               # Pydantic Settings
├── domain/                 # Pure business logic + Protocols
├── application/
│   ├── agents/             # Autonomous behavior
│   └── services/           # Deterministic flows
└── infrastructure/         # All external implementations
```

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| V1 | RAG pipeline + Telegram bot | In progress |
| V2 | LangGraph agent + daily briefing | Planned |
| V3 | Observability (Langfuse) + evals | Planned |
| V4 | Guardrails + GCP deploy + Vertex AI | Planned |
| V5 | Smart router + Streamlit + portfolio | Planned |
| V6 | Exploration lab | Planned |

## Commands

```bash
make test       # Unit tests
make test-all   # All tests
make lint       # Linter
make format     # Format code
make run-api    # FastAPI server
make run-bot    # Telegram bot
```

## License

MIT
