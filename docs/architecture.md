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

<!-- Add new ADRs below following this template -->
