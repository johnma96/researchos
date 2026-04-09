# Work Log — ResearchOS

---

### 2026-04-01
- **Developer Context:** Sesión retomando la rama `feature/v1-infrastructure-setup` tras finalizar el cookiecutter de agentes. Se completaron los tests de streaming de `AnthropicLLM` (unitario con `AsyncMock`, `__aenter__`/`__aexit__` y generador async; integración contra la API real). Se revisó y enriqueció `CLAUDE.md` (Project Overview, traducción al inglés de las secciones Work Log y Git Workflow). Se aclararon conceptos clave: `async/await`, `AsyncMock` vs `MagicMock`, test unitario vs integración y comportamiento de pre-commit.
- **Work with Claude Code:** Exploración de `infrastructure/llm/anthropic.py` y sus tests. Corrección de setup de `AsyncMock` para simular el context manager de `stream()`. Alineación del `CLAUDE.md` con la estructura clean-agents-template.
- **Git History:** Commits relevantes — `feat(llm)`: implement AnthropicLLM provider; `test(llm)`: add unit and integration tests for AnthropicLLM; `feat(domain)`: align with clean-agents-template.
- **Pending Tasks:** Iniciar Tarea 2: cliente arXiv en `infrastructure/data/arxiv.py` (httpx + XML → `list[Paper]`). Verificar que se usa `None` (no `""`) cuando no hay system prompt en `AnthropicLLM`.

---

### 2026-04-09
- **Developer Context:** Sesión de configuración y refuerzo de la estructura del proyecto. No se desarrolló nueva funcionalidad de negocio; el foco estuvo en formalizar flujos de trabajo, proteger ramas críticas y dejar el entorno listo para la siguiente iteración de desarrollo.
- **Work with Claude Code:** Se revisó y enriqueció `CLAUDE.md` con la sección completa de **Git Workflow** (convenciones de commits, cadencia, formato Conventional Commits, cuerpo del commit). Se creó `ROADMAP.md` con el plan de versiones V1–V3. Se actualizó `docs/learnings.md` con notas de aprendizaje sobre pre-commit. Se ajustó el flujo de fin de sesión (`docs/work_log.md` creado, protocolo documentado en CLAUDE.md). El `work_log.md` se inicializó como archivo vacío en el commit `a90db6e`.
- **Git History:** 4 commits hoy — `docs: Update CLAUDE.md with GIT workflow, add learning and add new ROADMAP.md to work` · `test: Test pre-commit tootl` · `update: update pre-commit file to no commit to master or certifications brances` · `docs: update workflow to end session`. Rama `feature/v1-infrastructure-setup` adelantada 1 commit respecto a origin. Sin cambios sin commitear.
- **Pending Tasks:** Iniciar Tarea 2: cliente arXiv en `infrastructure/data/arxiv.py` (httpx, parseo XML con `xml.etree.ElementTree`, retorna `list[Paper]`, test de integración con 3 papers sobre "LLM agents"). Verificar uso de `None` vs `""` en system prompt de `AnthropicLLM`. Hacer push de la rama al remoto.
