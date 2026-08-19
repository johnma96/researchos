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

## ADR-005: LangGraph layer placement — state in domain, nodes in application, assembly in infrastructure

**Date:** 2026-08
**Status:** Accepted

**Context:** V2 introduces LangGraph, which is a borderline case for the dependency rule: unlike an SDK or a DB driver, it expresses control flow, and control flow is `application/`'s job. Three options were evaluated:
1. state, nodes and graph all in `application/agents/research_agent/`, accepting the `langgraph` import as a documented exception
2. state in `domain/`, pure nodes in `application/`, assembly in `infrastructure/`;
3.  everything in `infrastructure/orchestration/`, with `application/` exposing only the functions nodes call.

Option 1 is what every official example does but creates an erosion precedent — the project already carries `ingestion_service.py` importing `httpx`/`fitz` as *debt*, not as an accepted exception. Option 3 would put business rules like "if local retrieval is thin, search arXiv" (T19) inside `infrastructure/`. The deciding finding: a reducer is just a `Callable[[T, T], T]` (the official quickstart uses stdlib `operator.add`), so **only `StateGraph`/`START`/`END`/`compile()` truly require the framework** — the state and the nodes do not. A premise in favour of importing `add_messages` into the state was investigated and discarded: it dedupes messages by `id` *within a thread*, it is not what isolates concurrent users — that is the checkpointer's `thread_id` (T22).

**Decision:** Option 2. `ResearchContext` (`query`, `documents`, `answer`) in `domain/models.py` with no external imports; nodes as pure `(ResearchContext) -> dict` functions in `application/agents/research_agent/nodes.py`; `StateGraph`, edges and `compile()` in `infrastructure/orchestration/research_graph.py` — the only file in the project importing `langgraph`. T19 routing uses **conditional edges**, not `Command(goto=...)`, so the routing function stays a pure `state -> str` in `application/` and can be tested without executing the node (and its LLM call). `messages` and `rewritten_query` are deliberately not declared yet: they arrive in T22, once the required merge semantics is known.

**Consequences:** `domain/` and `application/` tests run without `langgraph` installed; nodes are tested by passing a fabricated state and asserting the returned dict. `answer_query` keeps working without the graph, which T24 needs to run the V1 pipeline and the V2 agent side by side over the same queries. Fourth instance of the same project pattern after `AnswerFn`, `RetrieveFn` and `with_logging`: the core never knows the mechanism invoking it. Cost: the agent lives across three files in two layers, no official example looks like this, so tutorial code must be relocated rather than copied. Framework portability was *not* a reason — node return conventions are LangGraph-specific and would be rewritten anyway; ADK appears in V6 as a comparison exercise, not a migration. Re-evaluate if: multi-agent in V6 forces `Command` (mandatory for subgraph→parent routing, which would make those nodes impure), the assembly file starts accumulating business logic, or a second piece outside the assembly requires the framework. For T22, `messages` will first get a hand-written reducer in `domain/` (a dedupe-by-`id` dict comprehension, ~15 lines) and later the split-state variant as a comparison exercise — `GraphState(TypedDict)` in `infrastructure/` composing `ResearchContext` from `domain/` plus `Annotated[list, add_messages]`, on the grounds that a LangChain-formatted message list with a LangGraph reducer is a framework structure, not a domain model.


---

<!-- Add new ADRs below following this template -->
