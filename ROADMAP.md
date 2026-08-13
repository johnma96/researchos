# ResearchOS — Roadmap de aprendizaje

> Roadmap v3.0 (10/08/2026). Ventanas por fecha calendario en vez de semanas
> relativas — reemplaza el plan de marzo 2026. Detalle completo (objetivos
> SMART, distribución semanal de horas, sistema de consolidación conceptual)
> vive en los documentos personales de planificación; este archivo es solo
> el checklist de tareas por versión.

## Abril 2026 — V1 pipeline RAG básico
- [x] T1: AnthropicLLM provider (completado 30 mar)
- [x] T2: Cliente arXiv API (completado 13 abr)
- [x] T3: Servicio de ingesta PDFs (completado 15 abr) — nota: el servicio
      (`ingestion_service.py`) quedó completo en esta fecha, pero el CLI que
      lo envuelve (`scripts/ingest_documents.py`) quedó como stub sin
      implementar hasta el 12/08/2026 (ver T16)
- [x] T4: Chunking fijo (completado 17 abr)
- [x] T5: Integración end-to-end (completado 18 abr)

## Mayo–Junio 2026 — V1 hybrid search y evaluación
- [x] T6: BM25 retrieval (completado 21 may)
- [x] T7: Hybrid search con RRF (completado 01 jun)
- [x] T8: Reranker con Claude (completado 01 jun)
- [x] T9: Dataset de evaluación (20 preguntas) (completado 18 abr)
- [x] T10: Script de evaluación comparativa (completado 01 jun)

## V1 real — Cierre con Telegram (10/08 – 14/08/2026) · Hito: 14/08/2026
- [x] T11: Bot de Telegram como adapter (`infrastructure/bot/telegram_bot.py`, `AnswerFn` inyectado, completado 10 ago)
- [x] T12: Composition root `scripts/run_telegram_bot.py` con wiring hybrid+rerank (completado 11 ago)
- [x] T13: `answer_query` inyecta `retrieve: RetrieveFn` en vez de `store: VectorStore` (completado 11 ago)
- [x] T14: Fix — `test_extract_text_pdf` sin depender de un PDF no versionado
      (marcado completado 12 ago, pero **no lo estaba**: seguía fallando en
      clon limpio porque `_download_pdf` escribía a `data/papers/` sin crear
      el directorio, y el test escribía sobre el `data/papers/` real del
      repo. Corregido de verdad y verificado en un clon limpio real —
      completado 13 ago)
- [x] T15: Fix — límite de 4096 caracteres por mensaje de Telegram (completado 12 ago)
- [x] T16: `scripts/ingest_documents.py` implementado — CLI delgado sobre `ingest_papers` (completado 12 ago)
- [x] T17: Merge de la rama de V1 real a `main` (completado 13 ago, PR#4)

## Deuda técnica conocida
- [ ] `ingestion_service.py` (`application/`) importa `httpx`, `fitz` y
      `infrastructure.data.arxiv.search_papers` **a nivel de módulo** — viola
      la regla "application solo depende de domain" (ADR-001, y CA-001/CA-002
      del banco de preguntas). Detectado el 12/08/2026 al construir el
      diagrama de arquitectura de V1 real. `rag_service.py` ya recibió este
      tratamiento (inyecta `retrieve`/`llm` en vez de instanciar); pendiente
      decidir si `ingestion_service.py` se refactoriza igual — candidato
      natural: V2, al tocar el pipeline de ingesta para LangGraph.

## V2 — Agente LangGraph + Briefing matutino (17/08 – 02/10/2026) · Hito: 02/10/2026
- [ ] T18: LangGraph fundamentals — grafo mínimo `retrieve → generate`
- [ ] T19: Primera tool tipada: `search_papers()`
- [ ] T20: Tools adicionales: `fetch_paper()`, `search_news()`, `query_vector_store()`, `explain_concept()`
- [ ] T21: Briefing matutino con APScheduler (7am — top 5 papers + 3 noticias + 1 concepto)
- [ ] T22: Memoria conversacional con SQLite checkpointer
- [ ] T23: Dockerización (`docker-compose` con bot + Chroma + scheduler)
- [ ] T24: Eval V1 vs V2 con queries reales acumuladas del bot

## V3 — Observabilidad + Evals + Testing (05/10 – 06/11/2026) · Hito: 06/11/2026
- [ ] T25: Langfuse self-hosted instrumentando el agente
- [ ] T26: Deuda de testing pagada — separación `make test` / `make test-all`
- [ ] T27: Dataset de evaluación a 40 preguntas sin data leakage
- [ ] T28: Métricas RAGAS con Gemini Flash como juez externo
- [ ] T29: 1–2 tools migradas a MCP (FastMCP)

## V4 — Guardrails + Despliegue + Vertex AI (09/11/2026 – 08/01/2027) · Hito: 08/01/2027
- [ ] T30: Guardrails AI + PII masking con Presidio
- [ ] T31: Despliegue en Cloud Run + Secret Manager
- [ ] T32: CI/CD en GitHub Actions con evals bloqueando deploys degradados
- [ ] T33: Exploración de Vertex AI Agent Engine
- [ ] T34: Apertura del canal público de Telegram

## V5 — Consolidación + Portfolio (11/01 – 12/02/2027) · Hito: 12/02/2027
- [ ] T35: Router inteligente por dominio + Vertex AI Search
- [ ] T36: App Streamlit con streaming
- [ ] T37: API REST autenticada (FastAPI)
- [ ] T38: Documentación técnica con MkDocs
- [ ] T39: Video demo + post de LinkedIn

## V6 — Laboratorio de exploración (desde 15/02/2027, sin deadline)
- [ ] Módulos independientes de 1–2 semanas (multi-agente, MCP a fondo,
      comparación de frameworks, RAG avanzado, voice interface, fine-tuning,
      infra avanzada, evals como producto, Vertex AI + ADK, CI/CD
      alternativo, comparación de IDEs agénticos) — detalle en el roadmap
      de aprendizaje personal, sin checklist fijo por diseño
