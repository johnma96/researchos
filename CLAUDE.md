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

### Commit cadence
- Claude Code should suggest a commit after each complete logical task,
  not after each modified file.
- A "logical task" is: an implemented feature, a passing test, a fixed bug,
  a finished refactor, a completed docs section.
- When finishing a task, Claude should say: "This task is complete.
  Suggested commit: `<proposed message>`. Shall I proceed?"
- Claude NEVER commits automatically without user confirmation.

### Commit message format
Use Conventional Commits. Messages must be written in English.

   **Format:** `<type>(<scope>): <description>`

   **Types:**
   - `feat` — new feature or capability
   - `fix` — bug fix
   - `refactor` — code change that neither fixes a bug nor adds a feature
   - `test` — adding or updating tests
   - `docs` — documentation only
   - `chore` — tooling, dependencies, CI, config
   - `style` — formatting, whitespace (no logic change)
   - `perf` — performance improvement

   **Scopes** match the project's architectural layers and components.
   Use lowercase, one word. Common scopes for agent projects:
   `domain`, `application`, `infrastructure`, `llm`, `retrieval`, `memory`,
   `api`, `agent`, `prompts`, `config`, `deps`, `ci`, `tests`, `docs`.

   **Examples:**
   feat(llm): add streaming support to provider
   fix(retrieval): handle empty search results
   refactor(agent): switch from inheritance to composition
   test(domain): add unit tests for Protocol implementations
   docs(architecture): add ADR for prompt loading decision
   chore(deps): upgrade pydantic to v2.9

### Commit body (optional)
Use the body to explain **why**, not **what**. The diff already shows the what.
Leave a blank line between the title and the body. Example:

   ```
   refactor(agent): switch from inheritance to composition

   Base class was creating coupling between ResearchAgent and PQRSAgent
   because streaming behavior differed. Composition via agent_utils.py
   keeps each agent self-contained.
   ```

#### Commit cadence
One commit per logical task, not per file. If you implement AnthropicLLM and its tests, that is ONE commit with both files, not two. If you implement the arXiv client and also fix a typo in the README, those are TWO separate commits (feat + docs). The rule: a commit should be revertable without breaking other things and must have a clear purpose.

For a typical development session, aim for 3–6 commits per day. Fewer means commits are too large (hard to review); more means micro-commits that clutter the history.

#### Two additional important rules
1. Commit messages are written in English even if the project code has comments in Spanish. This is industry standard convention and keeps the repo professional.
2. The commit body (optional, after the title) is used to explain the why, not the what. The diff already shows the what. If the decision is not obvious, explain it in the body.
