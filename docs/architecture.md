# Architecture Decision Records (ADRs)

## ADR-001: Clean Architecture with 3 layers

**Date:** 2026-03
**Status:** Accepted

**Context:** Need a project structure that scales from V1 (simple RAG) to V5 (production system with multiple channels) and is replicable across 3 projects.

**Decision:** Adopt Clean Architecture with domain/ (pure logic), application/ (orchestration), infrastructure/ (external systems). Contracts defined via Python Protocols in domain/interfaces.py.

**Consequences:** Slightly more boilerplate upfront. Significantly easier to test, swap implementations, and onboard new team members.

---

## ADR-002: Composition over inheritance for agents

**Date:** 2026-03
**Status:** Accepted

**Context:** Agents share some patterns (retrieve-and-generate, tool calling) but differ in behavior.

**Decision:** Use shared functions in agent_utils.py instead of a base_agent.py class with inheritance.

**Consequences:** More explicit imports. No hidden behavior from parent classes. Each agent is self-contained and independently testable.

---

## ADR-003: Prompts as .txt files with str.format()

**Date:** 2026-03
**Status:** Accepted

**Context:** Need versionable, diffable prompts without adding external dependencies to domain layer.

**Decision:** Store prompts as .txt files in domain/prompts/ with Python str.format() for variable substitution. No Jinja2.

**Consequences:** Limited to simple variable substitution. If conditional logic is needed in prompts, re-evaluate Jinja2 as a conscious decision.

---

## ADR-004: Function-type aliases for single-behavior dependencies

**Date:** 2026-08
**Status:** Accepted

**Context:** `rag_service.answer_query` needed to depend on "something that answers" (for the Telegram adapter) and, one layer down, on "something that retrieves" (to swap vector-only, hybrid, and hybrid+rerank without touching the service). A `Protocol` is built for contracts with several named methods that share state; here each dependency is a single anonymous behavior — one parameter, one return. A `strategy="hybrid"` flag was also considered and rejected: it produces parameters that are conditionally required depending on another parameter's value, which a type checker cannot express, so a wrong combination only fails at runtime.

**Decision:** Model single-behavior dependencies as `Callable` type aliases (`AnswerFn = Callable[[str], Awaitable[str]]`, `RetrieveFn = Callable[[str], Awaitable[list[Document]]]`) instead of a `Protocol` or a strategy flag. The concrete choice of implementation is captured as a closure built once in the composition root (`scripts/run_telegram_bot.py`) and passed down — the consuming code (`TelegramBot`, `answer_query`) only knows the function signature.

**Consequences:** Lighter than a `Protocol` for the common case of one behavior, still statically checkable via the `Callable` signature. Swapping retrieval strategy (vector-only → hybrid+rerank) required zero changes to `TelegramBot` — only the closure built in the composition root changed. Rule going forward: one behavior → function-type alias; several related behaviors sharing state → `Protocol` or a class.

---

<!-- Add new ADRs below following this template -->
