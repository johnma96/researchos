---
name: interview-bank
description: Generar candidatos de preguntas de entrevista de AI Engineer basados en el trabajo real de la semana (commits, work_log, learnings), y curar las seleccionadas hacia el banco maestro. Usar cuando el usuario pida "generá el borrador de preguntas de esta semana" o "movés las marcadas al banco".
---

# Banco de preguntas de entrevista

Sistema semanal para generar y curar preguntas de entrevista para AI Engineer,
derivadas del código real del proyecto — no de libros genéricos. El objetivo es
llegar a 80–100 preguntas al final del proyecto, categorizadas por tema, cada
una con respuesta esperada, trampa común y ejemplo del código propio.

## Archivos involucrados

- `docs/interview_prep/bank.md` — banco maestro, fuente de verdad
- `docs/interview_prep/by_topic/{tema}.md` — vistas por tema (regenerables desde bank.md)
- `docs/interview_prep/weekly_drafts/YYYY-WNN.md` — borradores semanales antes de curar
- `docs/interview_prep/weekly_drafts/YYYY-WNN.done.md` — draft archivado tras curación

## Comandos del usuario

| Comando (aprox.) | Acción del agente |
|---|---|
| `Generá el borrador de preguntas de esta semana` | Crea `weekly_drafts/YYYY-WNN.md` con 8–12 candidatos |
| `Movés las marcadas al banco` | Migra checkboxed al banco maestro, regenera `by_topic/` |
| `Mostrame las preguntas del tema X` | Lee `by_topic/{tema}.md` y responde inline |

## Generación de candidatos

Cuando el usuario pide el borrador semanal, el proceso es:

1. Ejecutar `git log --since='7 days ago' --oneline --stat` para conocer commits
   y archivos tocados esta semana.
2. Leer las entradas más recientes de `docs/work_log.md` y `docs/learnings.md`.
3. Leer `docs/interview_prep/bank.md` completo para conocer preguntas existentes
   y evitar duplicados.
4. Identificar los temas técnicos que aparecen esta semana. Prefijos válidos:
   - `CA` — Clean Architecture
   - `PR` — Protocols
   - `RG` — RAG y retrieval (BM25, vector, hybrid, RRF, rerank)
   - `AS` — Async y concurrencia
   - `TS` — Testing con mocks
   - `LG` — LangGraph y agentes
   - `OB` — Observabilidad y evals
   - `GR` — Guardrails y seguridad
   - `LM` — LLM providers y SDKs
   - `IN` — Ingesta (chunking, embeddings, PDF parsing)
5. Por cada tema tocado, generar 2–4 candidatos con niveles progresivos:
   - **básico**: definición del concepto
   - **intermedio**: trade-off, "por qué X en vez de Y"
   - **avanzado**: extensión, "cómo diseñarías Z" o "qué falla si Y"
6. **Regla anti-duplicado**: si una pregunta candidata cubre el mismo concepto
   que una ya presente en `bank.md`, marcarla como `[DUP de ID-XXX]` y omitirla.
7. Cada pregunta debe tener un ejemplo concreto del código del proyecto (ruta
   de archivo y línea, o SHA del commit que la origina). No respuestas de libro.

## Formato de cada candidato en el draft

```markdown
- [ ] **Tema: {nombre}** — Nivel: básico|intermedio|avanzado
  - **Pregunta:** ...
  - **Respuesta esperada** (3–5 oraciones): ...
  - **Trampa común:** ...
  - **Ejemplo en el proyecto:** `src/researchos/.../archivo.py:LN` o commit `abc1234`
  - **Generada desde:** commit `abc1234` o "learnings del DD/MM"
```

## Curación al banco maestro

Cuando el usuario dice "movés las marcadas al banco":

1. Leer `weekly_drafts/YYYY-WNN.md` y filtrar solo los items con `[x]`.
2. Asignar ID incremental por tema usando el prefijo (ej. `CA-006`, `AS-004`).
   El próximo número se calcula leyendo el ID más alto existente en `bank.md`
   para ese prefijo.
3. Insertar cada pregunta curada en `bank.md` bajo la sección del tema
   correspondiente, en orden de ID ascendente.
4. Regenerar los archivos `by_topic/{tema}.md` a partir de `bank.md`
   (sobrescribir completamente).
5. Renombrar el draft: `weekly_drafts/YYYY-WNN.md` → `weekly_drafts/YYYY-WNN.done.md`.
   Nunca borrar drafts — son histórico.
6. Confirmar al usuario cuántas preguntas se agregaron por tema.

## Formato del banco maestro (`bank.md`)

```markdown
# Banco de preguntas — ResearchOS

## Índice por tema
- [Clean Architecture (CA)](#clean-architecture) — N preguntas
- [Protocols (PR)](#protocols) — N preguntas
- ...

---

## Clean Architecture

### [CA-001] Nivel: básico
**Pregunta:** ...
**Respuesta esperada:** ...
**Trampa común:** ...
**Ejemplo en el proyecto:** ...

### [CA-002] Nivel: intermedio
...
```

## Anti-patrones

- No generar preguntas genéricas sin conexión al código del repo
- No superar 12 candidatos por semana (calidad > cantidad)
- No re-generar preguntas ya presentes en `bank.md`, aunque estén en semanas
  distintas del historial
- No inventar rutas de archivos o commits que no existan en el repo
- No escribir respuestas esperadas que superen 5 oraciones (rigor sobre extensión)
- No mezclar temas en una sola pregunta — si toca dos temas, cortarla en dos
