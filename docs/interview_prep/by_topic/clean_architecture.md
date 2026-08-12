# Clean Architecture — banco de preguntas

5 preguntas. Fuente: `docs/interview_prep/bank.md`.

#### [CA-001] Nivel: básico
**Pregunta:** Explicá la regla de dependencia entre las tres capas
(`domain`, `application`, `infrastructure`) y qué se rompe si se viola.

**Respuesta esperada:** La dirección de dependencia es
`infrastructure → application → domain`. Domain no importa de nadie;
application importa solo de domain (Protocols y modelos); infrastructure
importa de domain para implementar los Protocols. Los composition roots
(scripts, factories, `__main__`) son los únicos que conocen tanto
application como infrastructure, típicamente inyectando implementaciones
concretas. Si domain importa de infrastructure, cambiar de Chroma a Qdrant
obliga a tocar código de negocio, y los tests unitarios de dominio dejan
de correr sin instalar el stack completo.

**Trampa común:** Invertir la dirección diciendo "application importa de
infrastructure". Es al revés — application no sabe qué implementaciones
concretas existen; solo conoce los Protocols de domain.

**Ejemplo en el proyecto:**
`src/researchos/application/services/ingestion_service.py` recibe
`store: VectorStore | None` — un Protocol de `domain/interfaces.py`, no
`ChromaVectorStore` de `infrastructure/`.

---

#### [CA-002] Nivel: intermedio
**Pregunta:** Dado un archivo cualquiera del proyecto, ¿cómo decidís a qué
capa pertenece? Dame la regla en una oración y tres ejemplos concretos del
repo.

**Respuesta esperada:** Regla: **domain** contiene lógica pura sin
dependencias externas (modelos Pydantic, Protocols, excepciones de negocio,
prompts .txt); **application** contiene orquestación programada contra
Protocols (services y agents); **infrastructure** contiene implementaciones
concretas con dependencias externas (SDKs, drivers, frameworks web).
Ejemplos del repo: `domain/models.py` (Document, Chunk) es domain porque
solo usa Pydantic; `application/services/retrieval_service.py`
(hybrid_search) es application porque orquesta contra Protocols;
`infrastructure/retrieval/chroma.py` (ChromaVectorStore) es infrastructure
porque depende del SDK de Chroma.

**Trampa común:** Colocar código con lógica de negocio dentro de
infrastructure porque "toca a Chroma", o colocar código de infrastructure
dentro de application porque "hace algo importante". La distinción no es
por importancia — es por dependencias externas.

**Ejemplo en el proyecto:** Ver la estructura completa en
`src/researchos/{domain,application,infrastructure}/`.

---

#### [CA-003] Nivel: intermedio
**Pregunta:** Te piden agregar un endpoint HTTP nuevo (con FastAPI) que
reciba un caso y devuelva una recomendación. ¿En qué capa vive el endpoint?
¿Cuál es el rol de FastAPI?

**Respuesta esperada:** El endpoint vive en `infrastructure/api/routers/`.
FastAPI es canal, no motor — expone el motor (services y agentes de
`application/`) por HTTP. El router es delgado: recibe el payload como
Pydantic model, valida, llama a un service o agente, devuelve el response
model. El router en sí no computa nada — solo traduce HTTP a llamadas
internas y viceversa.

**Trampa común:** Colocar la lógica de negocio (la "recomendación") dentro
del router o en `application/services`. La lógica de recomendación es
application; el endpoint que la expone es infrastructure. Si mañana
descontinúan FastAPI y aparece un framework nuevo, cambiás el router sin
tocar la lógica.

**Ejemplo en el proyecto:** Estructura existente en
`src/researchos/infrastructure/api/routers/`.

---

#### [CA-004] Nivel: intermedio
**Pregunta:** Querés agregar un canal nuevo: Slack. ¿Dónde va el código
del bot? Trazá el flujo de un mensaje entrando por Slack hasta la
respuesta.

**Respuesta esperada:** El bot va en `infrastructure/bot/slack.py`. Flujo:
(1) llega evento HTTP de Slack al webhook expuesto en el bot; (2) el bot
extrae texto y contexto (user_id, channel_id); (3) el bot llama a una
función `answer_fn(query)` inyectada — típicamente un closure armado en el
composition root que envuelve `rag_service.answer_query(query, llm,
retrieve)`; (4) `answer_query` ejecuta `retrieve(query)` (hybrid+rerank u
otra estrategia) y genera con el LLM; (5) devuelve el string; (6) el bot
publica la respuesta en Slack usando el SDK. Motor no sabe que existe Slack.

**Trampa común:** Meter el bot en `application/`. Los SDKs de Slack o
Telegram son dependencias externas — pertenecen a infrastructure. El bot
importa del motor, no al revés.

**Ejemplo en el proyecto:** Implementado en V1 real —
`infrastructure/bot/telegram_bot.py` (`TelegramBot(token, answer_fn)`, con
`AnswerFn = Callable[[str], Awaitable[str]]`). El closure que satisface
`answer_fn` se arma en `scripts/run_telegram_bot.py`, no en el bot. Un canal
nuevo (Slack) seguiría exactamente el mismo patrón sin tocar
`TelegramBot`.

---

#### [CA-005] Nivel: avanzado
**Pregunta:** Alguien te pide agregar Qdrant como vector store alternativo
a Chroma. ¿Qué archivos crear? ¿Qué archivos modificar? ¿Qué archivos NO
deberías tocar y por qué?

**Respuesta esperada:** Crear: `infrastructure/retrieval/qdrant.py` con
clase `QdrantVectorStore` que implementa el Protocol `VectorStore`;
`tests/integration/test_qdrant.py`. Modificar: `config.py` para agregar
la opción `Literal["chroma", "qdrant"]` en Settings; el composition root
donde se instancia el store (scripts como `scripts/ingest_documents.py`).
No tocar: nada en `domain/` (las abstracciones no cambian); nada en
`application/services/*` (programan contra Protocols); ni los tests
unitarios de application (los mocks de conftest.py siguen sirviendo).
Este es el pago concreto de haber aplicado Clean Architecture desde el
inicio.

**Trampa común:** Modificar `application/services/ingestion_service.py`
para "adaptarlo a Qdrant". Eso rompe la razón de existir del Protocol
VectorStore — si tenés que tocar application cada vez que agregás una
implementación nueva, el patrón está mal aplicado.

**Ejemplo en el proyecto:** Mismo patrón que ya se usó al agregar
`BM25Retriever` como segunda implementación de `Retriever`.
