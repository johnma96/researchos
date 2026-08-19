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

## 2026-04-17

### Trabajo desarrollado
- Completado ejercicio de benchmark async: `scripts/benchmark_arxiv.py`
  - Descarga secuencial vs paralela de 10 papers con `asyncio.gather()`
  - Resultado: 13.6s secuencial vs 1.2s paralelo (11x más rápido sin caché)
- Tarea 4 completada: chunking fijo en `application/services/retrieval_service.py`
  - `overlap_chunking()` con 500 chars y 50 de overlap
  - Manejo de caso borde: texto más corto que chunk_size retorna 1 chunk
  - Tests parametrizados con 4 escenarios (texto corto, largo, exactamente chunk_size, chunk_size+1)
- `chunk_to_document()` implementada y testeada
- `infrastructure/retrieval/embedder.py` creado con `LocalEmbedder` (sentence-transformers)
- `infrastructure/retrieval/chroma.py` implementado con `ChromaVectorStore`:
  - Cliente persistente local con pysqlite3 workaround
  - `upsert()` con `embed_batch` para eficiencia
  - `search()` con score normalizado según métrica configurable
  - Separación de responsabilidades: embedder inyectado como dependencia
- Test de integración para Chroma: upsert + search verificados

### Próximos pasos
- Tarea 5: integración end-to-end del pipeline (arXiv → PDF → chunking → Chroma)
- Plan de estudio semana 2: pytest (artículo Real Python + libro Okken caps 1-5, 7)
- Resolver sqlite3 en Docker cuando llegue V4

---

## 2026-04-18

### Trabajo desarrollado
- Configuración del entorno Windows:
  - `pysqlite3-binary` marcado como dependencia solo para Linux en `pyproject.toml`
  - Fix de `conftest.py` para que el hack de sqlite3 sea condicional por plataforma
  - `ipykernel` agregado como dependencia dev y kernel registrado manualmente
  - `pyproject.toml` consolidado: dependencias dev unificadas en `[dependency-groups]`
  - Autor actualizado: John Mario Montoya Zapata
- `ensure_dirs()` implementada en `paths.py` — centraliza creación de directorios
- Manejo de errores en `arxiv.py`: validación de respuesta antes de parsear XML
- `ingest_papers()` completada en `ingestion_service.py`:
  - Orquesta: arXiv → descarga PDF → chunking → Chroma
  - Descarga paralela con `asyncio.gather()`
  - Parámetros configurables: `chunk_size`, `overlap`, `collection_name`
  - Probada en notebook con `max_results=2` — funcionó correctamente

### Próximos pasos
- Copiar `data/samples/sample_pdf.pdf` desde el servidor Linux a Windows
- Dataset de evaluación: 20 preguntas con respuestas de referencia
- Consultar con tutor: múltiples colecciones en Chroma, parámetros de `ingest_papers`

---

## 2026-05-21

### Trabajo desarrollado
- Docstrings Google-style agregados a 12 módulos: `arxiv.py`, `anthropic_llm.py`, `chroma.py`, `embedder.py`, `ingestion_service.py`, `retrieval_service.py`, `paths.py`, `models.py`, `exceptions.py`, `interfaces.py`, `registry.py`, `benchmark_arxiv.py`, `eval_retrieval.py`.
- `pysqlite3-binary` agregado como dependencia Linux en `pyproject.toml`; celda de patch sqlite3 agregada a notebook 007.
- Notebooks reordenados: 003=retriever_service, 004=chroma-VectorStore, 005=ingestion_service (refleja orden de dependencias).
- `registry.py` eliminado; `PromptTemplate.render()` es ahora el único mecanismo de carga de prompts.
- `ingestion_service.py` refactorizado: `store: VectorStore | None = None` como parámetro, imports de infraestructura lazy dentro de la función.
- `test_ingestion_service.py` actualizado: assertions separadas para verificar `tuple[str, Path]`.
- `pytest-cov` agregado con `addopts = "--cov=src/researchos --cov-report=term-missing"` — cobertura global 76% unit, 83% con integración.
- Protocol `Retriever` creado en `domain/interfaces.py` con solo `search` (sin `upsert`).
- `BM25Retriever` implementado en `infrastructure/retrieval/bm25.py`: índice en memoria con `BM25Okapi`, tokenizador inyectable, `search` async, scores vía `model_copy`.
- Notebook `008-jmmz-bm25-retrieval.ipynb` creado para comparar BM25 vs vectorial sobre la misma query.

### Próximos pasos
- T7: Hybrid search con Reciprocal Rank Fusion en `retrieval_service.py`
- T8: Reranker con Claude sobre top-10 del hybrid
- Re-ejecutar evaluación comparando las cuatro estrategias

---

## 2026-06-01

### Trabajo desarrollado
- Refactor: `retrieval_service.py` renombrado a `chunking_service.py`; nuevo `retrieval_service.py` creado para orquestación de retrieval.
- T7 completado: `hybrid_search` en `retrieval_service.py` con RRF, `asyncio.gather` paralelo, deduplicación y top-k. Test unitario verifica que documento en ambos retrievers gana el ranking.
- T8 completado: `hybrid_rerank_search` en `retrieval_service.py` — usa Claude como juez para reordenar candidatos del hybrid. Prompt en `domain/prompts/tasks/rerank.txt`. Parseo robusto del JSON de respuesta con extracción por `find("[")`.
- T9 completado: `scripts/eval_retrieval.py` refactorizado para comparar las cuatro estrategias (vector, BM25, hybrid, hybrid+rerank) con métricas P@k y MRR. Resultados: vector=1.000/1.000, bm25=0.950/0.925, hybrid=1.000/1.000, hybrid+rerank=1.000/1.000.
- 25/25 tests unitarios pasando.

### Análisis de resultados
- Resultados altos esperados: el eval dataset fue construido sobre los mismos documentos indexados (data leakage). En producción con queries reales los scores serían menores.
- BM25 levemente inferior al vectorial — falla en una pregunta sobre `imad_aouali_2026` y tiene RR=0.50 en una pregunta sobre Idea3 (lo encuentra en posición 2 en lugar de 1).
- Hybrid y hybrid+rerank igualan al vectorial en este corpus controlado.

### Próximos pasos
- Merge de `feature/v1-infrastructure-setup` a `main` — V1 completada.
- Nombrar siguiente rama por feature concreta (e.g. `feature/v1-hybrid-rerank` ya hecho, próxima podría ser `feature/v2-telegram-bot`).
- Evaluar con queries reales para obtener métricas más representativas.

---

## 2026-07-29

### Trabajo desarrollado
- Retorno al proyecto tras pausa de ~8 semanas; taller de retorno a ResearchOS
  completado (~60%, sección 7 saltada por decisión consciente)
- Sistema de estudio conceptual implementado: skills `interview-bank`,
  `weekly-essay`, `git-commits`, `arquitectura-drawio` y `daily-closeout`
  agregadas en `.claude/skills/`
- Banco de preguntas poblado (`docs/interview_prep/bank.md`) con 15 preguntas
  semilla derivadas del taller — Clean Architecture (5), Protocols (3), RAG y
  retrieval (4), Async (3) — con archivos por tema regenerados en `by_topic/`
- Estructura de `docs/interview_prep/weekly_drafts/` y `docs/essays/prompts/`
  completada
- Revisión de cierre de jornada sobre `docs/learnings.md`: corregidos tres
  errores conceptuales en la entrada de hoy (dirección de dependencia
  infrastructure↔application, ubicación de la lógica de negocio, terminología
  de composición de agentes), dejando registro en "¿Qué no entendí bien?"
  para monitorear en próximas sesiones

### Próximos pasos
- Jueves 30/07: refuerzo arquitectural (diagramas de flujo + reescritura
  de respuestas 8.1–8.4 del taller)
- Viernes 31/07: primer ciclo real del sistema (banco semanal + ensayo)
- Verificar en próximas sesiones si los tres conceptos corregidos hoy en
  learnings.md ya quedaron interiorizados

---

## 2026-08-10

### Trabajo desarrollado
- Implementado el adapter `TelegramBot` en `infrastructure/bot/telegram_bot.py`:
  recibe `token` y una función `answer_fn: AnswerFn`
  (`Callable[[str], Awaitable[str]]`) inyectada por constructor, sin conocer
  `LLMProvider`, `VectorStore`, `AnthropicLLM` ni `ChromaVectorStore`
- Composition root en `scripts/run_telegram_bot.py`: instancia `LocalEmbedder`,
  `ChromaVectorStore`, `AnthropicLLM` y arma un closure que satisface `AnswerFn`
  llamando a `rag_service.answer_query` (vector-only)
- Detectado en pruebas manuales: el bot falla en preguntas de seguimiento
  anafóricas — dos causas distintas identificadas: falta de memoria
  conversacional (`answer_query` no recibe historial/`session_id`) y falta
  de query rewriting antes del retrieval

### Próximos pasos
- Diseñar memoria conversacional vía el Protocol `MemoryStore` e inyectarla
  en `answer_query`
- Investigar query rewriting para resolver referencias anafóricas antes del
  retrieval
- Evaluar si conectar hybrid search al canal de Telegram (hoy es vector-only)
- Manejar el límite de 4096 caracteres por mensaje de Telegram — el bot hoy
  no trunca ni divide respuestas largas antes de `reply_text`

---

## 2026-08-11

### Trabajo desarrollado
- `rag_service.answer_query` refactorizado: recibe `retrieve: RetrieveFn`
  (`Callable[[str], Awaitable[list[Document]]]`) inyectado en vez de
  `store: VectorStore`; compone directamente `retrieve(query)` →
  `build_rag_messages(...)` → `llm.generate(...)` en lugar de llamar a
  `retrieve_and_generate`
- `scripts/run_telegram_bot.py` rearmado como composition root: construye
  `ChromaVectorStore` y `BM25Retriever`, y un closure `retrieve_hybrid_rerank`
  que encadena `hybrid_search` + `hybrid_rerank_search`; el bot ahora
  responde con hybrid+rerank en vez de vector-only
- `scripts/eval_retrieval.py`: `_rerank` movida antes de `main` para mejorar
  legibilidad, y su `k` hardcodeado (`10`) reemplazado por `K * 2` (`152d651`)
- `TelegramBot` no se modificó — el cambio de estrategia de retrieval quedó
  completamente aislado del adaptador, validando el diseño de `AnswerFn`

### Próximos pasos
- Evaluar eliminación de `retrieve_and_generate` al construir el grafo de
  V2 — sin llamadores en producción; al eliminar, actualizar también el
  ejemplo del docstring de `agent_utils.py` (línea 18) y su test en
  `tests/unit/application/test_agent_utils.py`
- Arreglar `test_extract_text_pdf`: depende de un PDF no versionado
  (`data/samples/sample_pdf.pdf` no está en git), falla en clon limpio
- Manejar el límite de 4096 caracteres por mensaje de Telegram
- Medir la latencia añadida por el paso de rerank

---

## 2026-08-12

### Trabajo desarrollado
- Fix `test_extract_text_pdf`: PDF simulado en memoria vía `fitz` en vez de
  leer `data/samples/sample_pdf.pdf` (no versionado) — ya no falla en clon
  limpio
- Fix límite de 4096 caracteres de Telegram: `_split_message()` en
  `telegram_bot.py` parte respuestas largas y las envía en secuencia
- `scripts/ingest_documents.py` implementado: CLI delgado (`argparse` +
  `ensure_dirs()` + `asyncio.run`) sobre `ingest_papers()` — quedó de stub
  desde V1 semana 1-2
- `ROADMAP.md` reestructurado con las ventanas de fecha del plan v3.0;
  T11-T16 marcados completos; deuda técnica de `ingestion_service.py`
  (imports de infra a nivel de módulo) registrada
- `docs/architecture.md`: ADR-004 documentando el patrón
  `AnswerFn`/`RetrieveFn`; corregidos ejemplos obsoletos del banco de
  preguntas (CA-004, CA-005)
- Diagrama de arquitectura de V1 (`docs/architecture.drawio`, tres vistas)
  y expansión de la skill `arquitectura-drawio` (linter de 4 a 11 checks,
  `legend_edge`, `check_labels.py`) — trabajo de un segundo agente sobre
  la misma rama
- Fix `telegram_bot.py`: dejó de imprimirse el token de Telegram al
  arrancar
- Incidente de git resuelto: un rebase para corregir el email de autor se
  aplicó sobre un commit huérfano, reescribiendo los 75 commits del
  historial sin ancestro común con `main`. Se recuperó el estado bueno vía
  reflog y se reescribió el email real de forma controlada con
  `git filter-repo` (mailmap, solo los correos empresariales → gmail),
  verificando hashes de árbol idénticos antes/después

### Próximos pasos
- Merge manual de `fix/clean-clone-and-message-limit` a `main`
- Re-apuntar el tag `v1.0.0` al nuevo commit de merge
- V1 real cerrada tras el merge — arrancar V2 (T18: LangGraph fundamentals)

---

## 2026-08-13

### Trabajo desarrollado
- Fix real de T14: `_download_pdf` crea el directorio padre antes de escribir
  (`ingestion_service.py`), y `test_extract_text_pdf` parcha `PAPERS_DIR` a
  `tmp_path` para no ensuciar el repo — verificado en un clon fresco real,
  no solo en el working copy (`9491967`, merge PR#5)
- `ROADMAP.md` corregido: T14 tenía fecha de cierre falsa (12/08), quedó con
  la fecha real (13/08) y la nota de qué faltaba; T17 (merge a `main`) marcado
- Tag `v1.0.0` re-apuntado al commit de merge de PR#5 — V1 real cerrada
- Tracking de V2 configurado en GitHub: 11 labels, milestone "V2 — Agente
  LangGraph + Briefing matutino" (vence 02/10), `.github/ISSUE_TEMPLATE/task.md`,
  y los 7 issues T18–T24 con estimaciones, dependencias y labels
- Estudio de LangGraph: notebook de práctica, dependencias agregadas
  (`langgraph`, `langchain`, `langchain-anthropic`), y entrada en
  `learnings.md` sobre por qué un grafo aporta (bifurcaciones y ciclos, no
  el estado) — corregida una confusión conceptual real en la conversación
  con el tutor
- `CLAUDE.md` actualizado con el ciclo semanal de trabajo vía GitHub Project

### Próximos pasos
- Abrir PR y mergear `docs/v2-github-tracking` a `main`
- Arrancar T18 (LangGraph fundamentals) el lunes 17/08
- Mañana (14/08, viernes): agregar la pregunta de grafo-vs-pipeline al banco
  de preguntas en el ritual normal

---

## 2026-08-18

### Trabajo desarrollado
- `scripts/run_telegram_bot.py`: agregado `with_logging(answer_fn) -> AnswerFn`,
  un wrapper que registra cada query entrante en `data/raw/queries.jsonl`
  (timestamp UTC + texto) — insumo real para T24 (eval V1 vs V2 sin data
  leakage). Corregida de paso la duplicación de `AnswerFn`: ahora se importa
  de `telegram_bot.py` en vez de redefinirse
- `mypy` conectado a `make lint` — ya estaba como dependencia dev y con
  config básica desde antes, pero nunca se ejecutaba. Corrida completa: 38
  errores encontrados; arreglados los de configuración/ruido (`rank_bm25` y
  `fitz` sin stubs de tipos) y dos `var-annotated` en `retrieval_service.py`;
  quedan 34 errores reales (gaps de manejo de `None` en 6 archivos) sin
  tocar, a la espera de decidir alcance
- `make run-bot` corregido: apuntaba a un módulo inexistente
  (`researchos.infrastructure.bot.main`); ahora corre el script real
  (`scripts/run_telegram_bot.py`)
- Verificado manualmente que el bot arranca sin errores con el wrapper de
  logging activo: `data/raw/queries.jsonl` se crea al construir
  `with_logging`, embedder/Chroma/BM25 se construyen sin fallas. Falta
  confirmar con un mensaje real desde Telegram
- `notebooks/201-jmmz-langraph-study.ipynb`: práctica de `StateGraph` —
  nodos, edges fijos y condicionales, ciclos (verificado quitando y
  reordenando edges), reducers, y esquemas de estado separados
  (`InputState`/`OutputState`/`PrivateState`)
- `docs/learnings.md`: entrada de hoy documenta el patrón wrapper/decorador
  (con ejemplo propio del taller de retorno) y los conceptos de estado,
  nodo y edge de LangGraph con evidencia de los experimentos del notebook 201

### Próximos pasos
- Decidir qué hacer con los 34 errores de mypy restantes (`arxiv.py`,
  `telegram_bot.py`, `anthropic_llm.py`, `chroma.py`, `embedder.py`,
  `ingestion_service.py`) — arreglar ahora, un subconjunto, o registrar
  como deuda en `ROADMAP.md`
- Confirmar el logging de queries con un mensaje real por Telegram
- Arrancar T18 (LangGraph fundamentals) con el borrador de estado ya
  escrito en el notebook 201 (`query`, `documents`, `answer`, `messages`,
  `rewritten_query`)

---

## 2026-08-19

### Trabajo desarrollado
- Arrancado T18: primer grafo LangGraph mínimo (`retrieve → generate`),
  siguiendo la ubicación de capas decidida en ADR-005
- `domain/models.py`: nuevo `ResearchContext` (dataclass) — estado del agente
  (`query`, `documents`, `answer`); `messages`/`rewritten_query` quedan para
  T22, cuando se conozca la semántica de merge que necesitan
- `domain/interfaces.py`: `RetrieveFn` y `AnswerFn` se relocalizan aquí desde
  `rag_service.py` y `telegram_bot.py` respectivamente — quedan como los
  primeros alias de tipo compartidos entre más de un consumidor (ADR-004)
- `application/agents/research_agent/nodes.py` (nuevo): `make_retrieve_node`
  y `make_generate_node`, fábricas que devuelven nodos puros
  `(ResearchContext) -> dict`, inyectando `RetrieveFn`/`LLMProvider` por
  clausura — cero imports de LangGraph, tal como fija ADR-005
- `infrastructure/orchestration/research_graph.py` (nuevo):
  `build_research_graph()` ensambla el `StateGraph` (`retrieve → generate`)
  — único archivo del proyecto que importa `langgraph`
- `scripts/run_research_graph.py` (nuevo): script de humo con CLI (`-q`) que
  corre el grafo contra Chroma/Anthropic reales para verificación manual
- `docs/architecture.md`: agregado ADR-005 (ubicación de capas para
  LangGraph — estado en domain, nodos en application, ensamblaje en
  infrastructure), con la comparación de las 3 opciones evaluadas
- Revisión de calidad sobre todo lo anterior: `ruff check --fix` +
  `ruff format` (imports desordenados, whitespace, EOF); agregados
  docstrings y type hints faltantes (`build_research_graph`, nodos); un
  error real de `mypy` en `add_node` resulta ser una limitación de los stubs
  de LangGraph (reproducida en un caso mínimo fuera del proyecto, incluso
  pasando `input_schema` explícito) — silenciado con `type: ignore` puntual
  y documentado, no es deuda de código propio
- `tests/unit/application/test_research_agent_nodes.py` (nuevo): cubre
  ambos nodos (`retrieve_node`, `generate_node`) con `ResearchContext`
  fabricado, verificando el dict parcial devuelto — sin ejecutar el grafo

### Próximos pasos
- Conectar el grafo al bot de Telegram (T18, cierre)
- Extraer el wiring duplicado entre `run_telegram_bot.py` y
  `run_research_graph.py` a una función compartida — ya hay dos
  consumidores, la abstracción se justifica
- Silenciar los ~34 errores de mypy provenientes de `chromadb` con overrides
  en `pyproject.toml`, y arreglar los de código propio (el `datetime | None`
  en `ingestion_service.py:70`)
- Confirmar la decisión de que `documents` se reemplace y no se acumule
  entre reintentos (relevante para T22)
