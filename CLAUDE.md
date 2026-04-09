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

---

## Adding a dependency

```bash
uv add <package>          # Producción
uv add --dev <package>    # Solo desarrollo
```

Siempre agregar el campo correspondiente en `config.py` y `.env.example`
cuando el SDK requiera credenciales.

---

## Work log y Resumen de Jornada

El registro histórico del proyecto vive en `docs/work_log.md` en la raíz del repositorio.

**Protocolo de cierre de jornada:**
Cuando el usuario solicite un resumen de la jornada de trabajo (o use comandos similares como "Genera el resumen del día...", "Resume el trabajo que hicimos ..."), DEBES ejecutar este flujo exacto para actualizar el archivo `work_log.md`:

1. **Analizar el Contexto Manual:** Extrae y resume cualquier información explícita que el usuario te haya dado en ese mismo prompt (ej. reuniones externas, investigación paralela, conversaciones con otros modelos).
2. **Analizar la Sesión de Claude Code:** Revisa tu propia memoria de la sesión actual: ¿Qué archivos de la Clean Architecture exploramos? ¿Qué problemas de código o dependencias resolvimos juntos? ¿Qué nuevas implementaciones se desarrollaron? ¿Qué tareas quedaron pendientes?
3. **Analizar el Repositorio (Git):** Usa tus herramientas de terminal para revisar los commits de las últimas 24 horas (`git log --since="1 day ago"`) y los cambios actuales sin commitear (`git status` o `git diff`).
4. **Redactar y Guardar:** Crea una nueva entrada al final de `work_log.md` con la fecha de hoy. El formato DEBE ser:

   ### [Fecha en formato YYYY-MM-DD]
   - **Contexto del Desarrollador:** [Resumen del input manual del usuario]
   - **Trabajo con Claude Code:** [Resumen de los archivos tocados, bugs arreglados o lógica discutida en la sesión]
   - **Historial de Git:** [Resumen de los commits realizados y estado actual del repo]
   - **Tareas Pendientes:** [Resumen de las tareas pendientes para trabajar la próxima sesión]

---

## Git workflow

### Commit cadence
- Claude Code debe sugerir hacer commit al finalizar cada tarea lógica completa,
  no cada archivo modificado.
- Una "tarea lógica" es: un feature implementado, un test que pasa, un bug
  corregido, un refactor terminado, una sección de docs completa.
- Al terminar una tarea, Claude debe decir: "Esta tarea está completa.
  Sugiero commit: `<mensaje propuesto>`. ¿Procedo?"
- Claude NUNCA hace commit automático sin confirmación del usuario.

### Commit message format
Utiliza Conventional Commits. Los mensajes deben estar escritos en inglés.

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
Utiliza el cuerpo del texto para explicar **por qué**, no **qué**. El «diff» muestra el «qué».
Deja una línea en blanco entre el título y el cuerpo del texto. Ejemplo en triple backticks:

   ```
   refactor(agent): switch from inheritance to composition

   Base class was creating coupling between ResearchAgent and PQRSAgent
   because streaming behavior differed. Composition via agent_utils.py
   keeps each agent self-contained.
   ```

#### Cadencia de commits
Commit por tarea lógica, no por archivo. Si implementas AnthropicLLM y sus tests, es UN commit con ambos archivos, no dos. Si implementas el cliente arXiv y además arreglas un typo en el README, son DOS commits separados (feat + docs). La regla es: un commit debe poder revertirse sin romper otras cosas y debe tener un propósito claro.
Para tu flujo típico de desarrollo, apunta a 3-6 commits por jornada de trabajo. Menos de eso y los commits son demasiado grandes (difíciles de revisar); más y son micro-commits que ensucian el historial.

#### Dos reglas adicionales importantes:
1. Primera: el mensaje de commit se escribe en inglés aunque el código del proyecto tenga comentarios en español. Es convención estándar en la industria y te ayuda a mantener profesionalismo en el repo.
2. Segunda: el cuerpo del mensaje (opcional, después del título) se usa para explicar el por qué, no el qué. El diff ya muestra el qué. Si la decisión no es obvia, explícala en el cuerpo
