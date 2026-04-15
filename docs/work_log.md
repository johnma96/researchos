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

---

### 2026-04-13
- **Developer Context:** Sesión de implementación de las Tareas 2 y 3. Se completó el cliente arXiv, el servicio de ingesta y la centralización de rutas. Se recibió feedback del tutor sobre `ingestion_service.py` con refactors pendientes para la próxima sesión.
- **Work with Claude Code:** Implementado `infrastructure/data/arxiv.py` con `search_papers()` usando `httpx` + parseo XML con namespaces vía `xml.etree.ElementTree`, y `_parse_entries()` privada para separar responsabilidades. Creado `application/services/ingestion_service.py` con `extract_text_pdf()` (descarga con `httpx`, extrae texto con PyMuPDF, limpieza de nombres con `re.sub`, validación con `ValueError`). Creado `src/researchos/paths.py` como módulo transversal usando `pyprojroot` (`PROJECT_ROOT`, `DATA_DIR`, `PAPERS_DIR`, `SAMPLES_DIR`, `CHROMA_DIR`) e importado desde `ingestion_service.py`. `CLAUDE.md` traducido completamente al inglés. 16/16 tests unitarios pasando.
- **Git History:** 4 commits hoy — `feat(data)`: add arXiv API client with XML parsing and integration test · `feat(notebooks)`: add ignore notebooks in pre-commit tool · `feat(ingestion)`: add PDF download and text extraction service · `refactor(ingestion)`: centralize filesystem paths in paths.py. Rama adelantada 3 commits respecto a origin. Árbol limpio.
- **Pending Tasks:** Refactorizar `ingestion_service.py` según feedback del tutor: hacer `extract_text_pdf` async con `httpx.AsyncClient`, cambiar `ValueError` por `IngestionError`, partir en `download_pdf()` + `extract_text()` + orquestadora, cambiar `import pymupdf` por `import fitz`. Tarea 4: chunking fijo en `application/services/retrieval_service.py` (función que recibe texto y devuelve `list[Chunk]`, 500 chars con 50 de overlap, test unitario).

---

## 2026-04-15

### Trabajo desarrollado
- Refactorización de `ingestion_service.py` según feedback del tutor:
  - `extract_text_pdf` convertida a `async def` con `httpx.AsyncClient`
  - Partida en `_download_pdf()` + `_extract_text()` + orquestadora
  - `ValueError` reemplazado por `IngestionError`
  - `import pymupdf` reemplazado por `import fitz`
  - Test unitario actualizado con `AsyncMock` y mock de context manager
- Estudio de AsyncIO: event loop, coroutines, gather, as_completed, create_task
- 16/16 tests unitarios pasando

### Próximos pasos
- Tarea 4: chunking fijo en `application/services/retrieval_service.py`
  - Función que recibe texto crudo y devuelve `list[Chunk]`
  - 500 caracteres con 50 de overlap
  - Test unitario con texto de prueba
- Completar benchmark `scripts/benchmark_arxiv.py` (ejercicio async del plan de estudio)
- Continuar plan de estudio: jueves 16 abril — primera mitad del artículo async de Real Python

---
