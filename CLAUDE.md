# ResearchOS — Context for Claude Code

> Read automatically by Claude Code at the start of every session.

## Project Overview
ResearchOS is an open-source research engine that monitors scientific sources
(arXiv, PubMed, RSS), answers questions in natural language, and sends
personalized morning briefings. Primary channel: Telegram bot.
Target domains: ML/AI, health/biomedicine, tech news.

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

---

## Adding a dependency

```bash
uv add <package>          # Production
uv add --dev <package>    # Development only
```

Always add the corresponding field in `config.py` and `.env.example`
when the SDK requires credentials.

---

## Work Log and Session Summary

The project's historical record lives in `docs/work_log.md` at the repo root.

**End-of-session protocol:**
When the user requests a session summary (or uses similar commands like "Generate today's summary...", "Summarize the work we did..."), you MUST execute this exact flow to update `work_log.md`:

1. **Analyze Manual Context:** Extract and summarize any explicit information the user provided in that same prompt (e.g., external meetings, parallel research, conversations with other models).
2. **Analyze the Claude Code Session:** Review your own memory of the current session: Which Clean Architecture files did we explore? What code or dependency problems did we solve together? What new implementations were developed? What tasks remain pending?
3. **Analyze the Repository (Git):** Use your terminal tools to review commits from the last 24 hours (`git log --since="1 day ago"`) and current uncommitted changes (`git status` or `git diff`).
4. **Draft and Save:** Create a new entry at the end of `work_log.md` with today's date. The format MUST be:

   ### [Date in YYYY-MM-DD format]
   - **Developer Context:** [Summary of the user's manual input]
   - **Work with Claude Code:** [Summary of files touched, bugs fixed, or logic discussed in the session]
   - **Git History:** [Summary of commits made and current repo state]
   - **Pending Tasks:** [Summary of tasks pending for the next session]

---

## Git Workflow

Git conventions — commit format, cadence, branching strategy, pull requests
and tags — live in `.claude/skills/git-workflow/SKILL.md`. Consult that skill
before writing a commit message, creating a branch, or closing a roadmap
version.

Two rules that always apply, regardless of the skill being loaded:

1. **Never commit without explicit user confirmation.** When a task is
   complete, say: "This task is complete. Suggested commit:
   `<proposed message>`. Shall I proceed?"
2. Commit messages are written in English, even though code comments and
   project docs may be in Spanish.


---

## Weekly Work Cycle (GitHub Project)

Given that the repo already has a Project and associated Issues on GitHub, the weekly workflow is as follows:

- Monday. Choose the issue for the week, move it to “In Progress” in the Project, and enter an estimate (h). Create a branch with a name matching the issue.

- Monday through Thursday. Make commits referencing the issue with (#N). Acceptance criteria are checked off as they’re met—this gives you visible progress without having to write reports.
Upon closing. Create a pull request with “Closes #N” in the description; merge it, and the issue closes automatically, advancing the milestone bar. Enter the Actual (h).

- Friday. The closed issues from the week serve as input for generating the question bank. The “interview-bank” skill reads the git log; if the commits reference issues, the context it receives is richer.

And the metric that really matters in the long run isn’t the milestone bar: it’s the ratio of Estimate to cumulative Actual. In three months, you’ll know whether you systematically underestimate infrastructure work, refactoring, or integration with external APIs. That data stays with you for the rest of your career, and almost no one has it because almost no one measures it.
