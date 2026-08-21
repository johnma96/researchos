# Banco de preguntas — ResearchOS

Preguntas de entrevista para AI Engineer, derivadas del código real del
proyecto. Meta: 80–100 preguntas al final de V5.

## Índice por tema

- [Clean Architecture (CA)](#clean-architecture) — 5 preguntas
- [Protocols (PR)](#protocols) — 4 preguntas
- [RAG y retrieval (RG)](#rag-y-retrieval) — 5 preguntas
- [Async y concurrencia (AS)](#async-y-concurrencia) — 3 preguntas
- [Testing (TS)](#testing) — 0 preguntas
- [LangGraph y agentes (LG)](#langgraph-y-agentes) — 6 preguntas
- [Observabilidad y evals (OB)](#observabilidad-y-evals) — 0 preguntas
- [Guardrails y seguridad (GR)](#guardrails-y-seguridad) — 0 preguntas
- [LLM providers y SDKs (LM)](#llm-providers-y-sdks) — 0 preguntas
- [Ingesta (IN)](#ingesta) — 0 preguntas
- [Proceso y colaboración (PC)](#proceso-y-colaboración) — 1 pregunta

---

## Clean Architecture

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

---

## Protocols

#### [PR-001] Nivel: básico
**Pregunta:** ¿Qué es un `Protocol` de Python y en qué se diferencia de
una clase abstracta (`ABC`)?

**Respuesta esperada:** Un Protocol define un contrato **estructural** —
cualquier clase con los métodos y firmas correctas lo satisface, sin
necesidad de heredar. La verificación es típicamente estática (mypy). Una
ABC define un contrato **nominal** — requiere herencia explícita
(`class Foo(BaseClass):`) y hace enforcement en runtime (`TypeError` si
un método abstracto no se implementa al instanciar). Protocol permite
que clases de librerías externas cumplan el contrato sin modificarlas;
ABC obliga a controlar el árbol de herencia.

**Trampa común:** Tratarlos como sinónimos "más modernos" uno del otro.
Son diferentes en runtime behavior y en filosofía de diseño.

**Ejemplo en el proyecto:** `domain/interfaces.py` define
`LLMProvider(Protocol)` con métodos `generate` y `stream`. Cualquier clase
con esos métodos lo satisface, incluyendo mocks de test que no heredan
de nada.

---

#### [PR-002] Nivel: intermedio
**Pregunta:** ¿Por qué en tu proyecto usás Protocols para las abstracciones
de `application/` en lugar de clases abstractas?

**Respuesta esperada:** Los Protocols evitan acoplar `application/` a
jerarquías de herencia. Si Anthropic saca un SDK nuevo con estructura
distinta, la nueva implementación de `LLMProvider` vive en infrastructure
sin necesitar herencia común. También facilita testing: los mocks pueden
ser clases simples sin importar nada de infrastructure. Además, structural
subtyping permite que clases de terceros cumplan el contrato sin tocar
su código.

**Trampa común:** Pensar que "ABC hace lo mismo con más rigor". El
"rigor" adicional de ABC (enforcement al instanciar) es innecesario si
usás mypy en CI — y a cambio pagás con acoplamiento por herencia.

**Ejemplo en el proyecto:** `application/services/ingestion_service.py`
recibe `store: VectorStore | None` — no sabe si es `ChromaVectorStore` o un
mock; solo sabe qué métodos puede llamar. (`rag_service.answer_query` ya no
recibe `store` directamente — inyecta `retrieve: RetrieveFn`, ver PR-004.)

---

#### [PR-003] Nivel: avanzado
**Pregunta:** ¿Cómo se testea código de `application/` que depende de un
Protocol, sin usar implementaciones reales de infrastructure?

**Respuesta esperada:** Se crea una clase mock local (en el test o en
`conftest.py`) que implementa los métodos del Protocol con comportamiento
controlado. Como Protocol es structural, no hace falta heredar de nada —
solo tener los métodos con las firmas correctas. Ejemplo: `MockVectorStore`
en `tests/conftest.py` con `search` y `upsert` que operan sobre una lista
en memoria. Los tests de `application/` inyectan estos mocks y verifican
comportamiento sin tocar Chroma real. Alternativa débil: `unittest.mock.
MagicMock` — funciona pero pierde chequeo estático (podés llamar métodos
que el Protocol no declara y no te avisa).

**Trampa común:** Usar `MagicMock` universalmente por comodidad. Perdés la
señal de mypy sobre si tu test está usando el Protocol correctamente.

**Ejemplo en el proyecto:** `tests/conftest.py` tiene `MockVectorStore` y
mocks de LLMProvider usados en `tests/unit/application/`.

---

#### [PR-004] Nivel: intermedio
**Pregunta:** `rag_service.answer_query` recibe `retrieve: RetrieveFn`, un
alias `Callable[[str], Awaitable[list[Document]]]`, en vez de un Protocol.
¿Por qué no un Protocol acá, si ya se usa `VectorStore` y `LLMProvider` en
el resto del proyecto?

**Respuesta esperada:** Un Protocol tiene sentido cuando hay varios métodos
relacionados que comparten estado (`VectorStore` con `search` + `upsert`).
Acá la dependencia es un solo comportamiento anónimo — un parámetro, un
retorno — y envolver eso en una clase con un único método es ceremonia sin
beneficio. El alias de función sigue siendo estáticamente verificable
(mypy valida la firma) pero es más liviano. Regla: un comportamiento →
alias de función; varios comportamientos relacionados → Protocol o clase.

**Trampa común:** Pensar que "más formal siempre es mejor" y usar Protocol
por defecto. La complejidad debe ser proporcional al número de
comportamientos que la dependencia agrupa, no una preferencia estilística
fija.

**Ejemplo en el proyecto:**
`src/researchos/application/services/rag_service.py:8` —
`RetrieveFn = Callable[[str], Awaitable[list[Document]]]`; documentado en
ADR-004 de `docs/architecture.md`.

---

## RAG y retrieval

#### [RG-001] Nivel: básico
**Pregunta:** Dame un ejemplo concreto de una query donde BM25 supera a
la búsqueda vectorial, y otro donde vectorial supera a BM25. Explicá por qué.

**Respuesta esperada:** BM25 supera cuando la query contiene siglas,
nombres propios técnicos o términos raros con coincidencia exacta: por
ejemplo `"BERT vs GPT-3"` — un vectorizador puede diluir esas siglas en un
embedding genérico, pero BM25 encuentra ocurrencias exactas. Vectorial
supera cuando la query es semántica y el corpus usa vocabulario distinto:
por ejemplo `"papers on models that reason step by step"` — encuentra
papers de "chain-of-thought" aunque la query no contenga esas palabras.
Son complementarios: por eso hybrid search existe.

**Trampa común:** Pensar que uno es "mejor" en absoluto. Cada uno tiene
un tipo de query donde brilla.

**Ejemplo en el proyecto:** `infrastructure/retrieval/bm25.py` y
`infrastructure/retrieval/chroma.py` — ambos en producción, combinados
vía `application/services/retrieval_service.py`.

---

#### [RG-002] Nivel: intermedio
**Pregunta:** Explicá Reciprocal Rank Fusion (RRF) paso a paso. ¿Por qué
suma las contribuciones cuando un documento aparece en dos rankings, en
lugar de promediarlas o quedarse con la mayor?

**Respuesta esperada:** RRF recibe rankings (no scores) de N retrievers,
cada uno con sus top-K candidatos. Descarta los scores originales — trabaja
solo con posiciones (rank 1, 2, 3...). Por cada documento en cada ranking,
calcula contribución `1 / (rrf_k + rank)` con rank 1-indexed. Cuando un
doc aparece en múltiples rankings, **suma** las contribuciones. Ordena por
score total descendente y devuelve top-K. La suma premia el consenso:
docs que dos retrievers rankean alto suben más que docs rankeados alto
por uno solo. Promediar diluiría la señal (un rank alto se compensaría
con la ausencia); quedarse con la mayor ignoraría el consenso.

**Trampa común:** Decir que RRF "combina scores". No combina scores —
descarta los scores originales precisamente porque tienen escalas
incomparables (BM25 sin límite superior, coseno entre -1 y 1). Combina
**posiciones**, que sí son comparables.

**Ejemplo en el proyecto:** `application/services/retrieval_service.py`
implementa `hybrid_search` con RRF.

---

#### [RG-003] Nivel: intermedio
**Pregunta:** En tu hybrid_search, cada retriever devuelve `k*2`
candidatos aunque al final devuelvas solo `k`. ¿Por qué no pedir
exactamente `k`?

**Respuesta esperada:** Porque después de la fusión hay deduplicación y
reordenamiento. Si dos retrievers devuelven exactamente los mismos `k`
docs, después de deduplicar quedás con `k` únicos y la fusión no aportó
nada — mismo resultado que un solo retriever. Con `k*2`, tenés material
adicional: docs que aparecen en posiciones 4-6 de ambos retrievers son
consensuados aunque ninguno los rankee arriba, y RRF los promueve. En
producción el overlap entre vectorial y BM25 sobre el mismo corpus está
entre 20% y 60%, entonces `k*2` es un colchón razonable.

**Trampa común:** Pensar que el escenario "cero overlap" invalida `k*2`.
Cierto, ahí `k=candidatos` da lo mismo — pero no sabés el overlap antes
de correr, y el default tiene que servir para el caso peor.

**Ejemplo en el proyecto:** `hybrid_search` en `retrieval_service.py`,
parámetro `candidates_per_retriever` con default `k*2` cuando es `None`.

---

#### [RG-004] Nivel: avanzado
**Pregunta:** ¿Cómo evaluarías un sistema RAG en producción sin caer en
data leakage? Mencioná qué medís, cómo obtenés ground truth, y qué hacés
con las queries que fallan.

**Respuesta esperada:** Métricas objetivas: faithfulness (¿el LLM inventa
cosas no soportadas por los docs?), context precision (¿los docs
recuperados son relevantes?), answer relevancy (¿la respuesta contesta la
pregunta?). Todas con LLM-as-judge externo — un modelo distinto al que
genera, para evitar sesgo de auto-evaluación (ej. Gemini Flash mientras
generás con Claude). Ground truth: dos fuentes. (a) curación humana
externa — alguien que NO conoce el corpus escribe queries que representan
cómo un usuario preguntaría, y anota respuesta esperada. (b) feedback en
producción — thumbs up/down, reformulaciones (señal de que la primera
respuesta no sirvió). Queries que fallan: van a un regression dataset,
etiquetadas manualmente, corren en CI/CD, bloquean deploys que degraden
el score.

**Trampa común:** Construir queries de test conociendo el corpus indexado.
Eso es data leakage — el sistema "acierta" porque las queries están
alineadas con el contenido, no porque sea bueno. Mide qué tan bien recuerda
lo que ya sabías que estaba, no calidad de retrieval.

**Ejemplo en el proyecto:** El `learnings.md` del 01/06/2026 documenta
exactamente este problema al observar scores 1.000/1.000 en el eval — la
razón fue leakage por construir queries desde el corpus.

---

#### [RG-005] Nivel: avanzado
**Pregunta:** `build_dependencies()` reconstruye el índice BM25 cargando
**todos** los documentos de Chroma en memoria en cada arranque del bot,
porque BM25 no persiste. ¿Qué problema anticipás cuando el corpus
crezca, y cómo lo abordarías?

**Respuesta esperada:** Hoy es instantáneo porque el corpus es pequeño
(cientos de documentos), pero T21 (briefing matutino) va a ingerir papers
todos los días, así que ese arranque va a crecer linealmente con el tiempo
sin que nada lo frene. El síntoma no es un bug — es una decisión de diseño
(BM25 en memoria, sin persistencia) que funciona mientras una asunción
implícita (corpus chico) sea cierta, y deja de serlo silenciosamente.
Abordajes posibles: persistir el índice BM25 serializado junto a Chroma y
reconstruirlo solo si el corpus cambió; o mover la reconstrucción a un
proceso de fondo desacoplado del arranque del bot, para que un arranque
lento no bloquee la disponibilidad del canal.

**Trampa común:** Descartarlo como "no es un problema hoy" sin dejarlo
anotado. Las asunciones de escala que dejan de cumplirse silenciosamente
son más peligrosas que un error explícito — no hay señal hasta que duele.

**Ejemplo en el proyecto:** `scripts/_wiring.py:38-67` (`build_dependencies`);
pendiente anotado en `docs/work_log.md` del 20/08, ligado a issue
[#9](https://github.com/johnma96/researchos/issues/9) (T21).

---

## Async y concurrencia

#### [AS-001] Nivel: intermedio
**Pregunta:** ¿Cuál es la diferencia entre async y paralelismo real?
¿Cuándo usás cada uno?

**Respuesta esperada:** Async es concurrencia cooperativa en un solo
thread. Un event loop rota entre corrutinas cuando alguna hace `await`
sobre I/O — el thread nunca está inactivo, pero solo una cosa se ejecuta
a la vez. Analogía: un mesero muy hábil que nunca se queda parado.
Paralelismo real es múltiples procesos (o threads con caveats por el GIL)
ejecutando código simultáneamente en cores distintos — múltiples cuerpos
haciendo trabajo real al mismo tiempo. Async para I/O bound (HTTP, disco,
red); multiprocessing para CPU bound (embeddings, ML inference).
Combinables: uvicorn con N workers procesos, cada uno con event loop
async, escala bien para APIs con alto tráfico.

**Trampa común:** Marcar todo `async def` porque "quiero que sea rápido".
Async no acelera CPU — solo aprovecha tiempos muertos de I/O. Sin `await`
adentro, `async def` es una mentira que confunde y bloquea el event loop.

**Ejemplo en el proyecto:** `infrastructure/llm/anthropic_llm.py` es
async correctamente (HTTP a Anthropic). `infrastructure/retrieval/bm25.py`
es async por excepción consciente — uniformidad con Chroma en
`asyncio.gather`, aunque adentro no haya `await`.

---

#### [AS-002] Nivel: intermedio
**Pregunta:** Tenés una función `embed_text(text) -> list[float]` que usa
`sentence-transformers` con un modelo local en CPU. ¿Va como `def` normal
o `async def`? ¿Por qué?

**Respuesta esperada:** `def` normal. sentence-transformers en CPU es
cálculo puro — tokeniza, pasa por la red neuronal, devuelve el vector. No
hay I/O esperando en background. Marcarlo `async def` no lo paraleliza; en
realidad lo empeora, porque si adentro no hay `await`, la corrutina
bloquea el event loop mientras calcula, impidiendo que otras corrutinas
de I/O (llamadas HTTP, timers) corran en paralelo. Para paralelizar
embeddings, se usa (a) batching nativo del modelo (`model.encode(lista)`
es vectorizado internamente), o (b) `asyncio.to_thread(embed_text, texto)`
si estás en un pipeline async y necesitás no bloquear el loop.

**Trampa común:** Marcarlo `async def` "por si acaso" o "porque el
pipeline es async". Ese razonamiento crea deuda técnica y bugs de
performance difíciles de diagnosticar.

**Ejemplo en el proyecto:** Regla mental documentada en `learnings.md`
del 15/04/2026 — "¿Esperás algo externo? async. ¿Solo calculás en
memoria? def normal."

---

#### [AS-003] Nivel: básico
**Pregunta:** El siguiente código pretende descargar tres URLs en
paralelo pero corre secuencial. Identificá el bug y explicá cómo
diagnosticarlo.

```python
async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        results = []
        for url in urls:
            result = await fetch(client, url)
            results.append(result)
        return results
```

**Respuesta esperada:** El bug es que `await` dentro del `for` serializa
las llamadas. Cada `await fetch(...)` espera que la anterior complete
antes de arrancar la siguiente. El event loop no está bloqueado —
simplemente no le dieron trabajo concurrente; nadie tiene múltiples
corrutinas en vuelo. Diagnóstico: tiempo total ≈ suma de tiempos
individuales, cuando debería ser ≈ tiempo del más lento. Corrección:
`results = await asyncio.gather(*[fetch(client, url) for url in urls])`.
Ahora las N corrutinas están en vuelo simultáneamente y el event loop
rota entre ellas mientras esperan I/O.

**Trampa común:** Decir que "el for detiene el event loop". El for no
detiene nada — un for normal en código async es legítimo. El bug es la
falta de trabajo concurrente. La distinción importa: en producción,
diagnosticar "event loop bloqueado" vs "falta de concurrencia" lleva a
soluciones diferentes.

**Ejemplo en el proyecto:** Ejercicio 6.2 del taller de retorno a
ResearchOS.

---

## Proceso y colaboración

#### [PC-001] Nivel: intermedio
**Pregunta:** Trabajaste cuatro meses en una sola rama de feature sin
mergearla a `main`. ¿Qué problemas concretos genera eso y cuál es el criterio
para decidir cuánto debe vivir una rama?

**Respuesta esperada:** Genera cuatro problemas. Primero, `main` no refleja
nada de lo que existe: si alguien clona el repo por defecto, obtiene un
esqueleto vacío. Segundo, el merge final es un evento grande y riesgoso — 56
commits de una sola vez son imposibles de revisar con atención. Tercero, no
hay ningún punto en el historial que marque "acá terminó una versión", así que
no se puede hacer rollback a un estado conocido ni etiquetar hitos. Cuarto, en
equipo la rama divergiría de `main` y acumularía conflictos, aunque en
solitario ese riesgo no se materializa. El criterio de duración es el tamaño
del entregable, no el tamaño de la versión: una rama debe cerrar algo
mostrable y revertible en una o dos semanas. Si un entregable no cabe en dos
semanas, se divide.

**Trampa común:** Justificar la rama larga con "estaba trabajando en una
versión completa". La versión es la unidad del roadmap, no la unidad de la
rama. V2 son siete semanas de roadmap y cuatro ramas de dos semanas cada una.
Otra trampa es proponer squash merge para "limpiar" el historial: en un
proyecto de aprendizaje los commits individuales son el registro del proceso.

**Ejemplo en el proyecto:** `feature/v1-infrastructure-setup` acumuló 56
commits entre abril y agosto de 2026 sin mergear, `main` permaneció congelada en `e3a6ac2` (el esqueleto inicial) hasta el merge del PR #1 el 10/08/2026

. El nombre además quedó desactualizado: la
rama se llamaba `infrastructure-setup` pero terminó conteniendo el pipeline
RAG completo, el sistema de estudio y el bot de Telegram. V2 se estructuró en
cuatro ramas de dos semanas para evitar repetirlo.

---

## Testing

_(sin preguntas todavía)_

## LangGraph y agentes

#### [LG-001] Nivel: básico
**Pregunta:** ¿Cuál es la diferencia entre LangChain y LangGraph, y por qué
`create_agent` de LangChain se apoya en LangGraph por debajo?

**Respuesta esperada:** LangGraph es orquestación de bajo nivel — control
de flujo explícito, human-in-the-loop, ejecución duradera y persistencia
de estado. LangChain es construcción de agentes de alto nivel, con modelos
y herramientas ya integrados en abstracciones como `create_agent`. Desde
la migración de LangGraph 0.x a 1.x (que deprecó `create_react_agent`),
`create_agent` de LangChain usa LangGraph internamente para ese control de
flujo — LangChain no reemplaza a LangGraph, se apoya en él.

**Trampa común:** Tratarlos como alternativas competidoras ("¿uso
LangChain o LangGraph?") en vez de verlos como capas — LangGraph es la
base de orquestación, LangChain es la abstracción de más alto nivel
construida encima.

**Ejemplo en el proyecto:** `notebooks/201-jmmz-langraph-study.ipynb`;
versiones fijadas en `pyproject.toml`
(`langgraph>=1.2.11`, `langchain>=1.3.15`, `langchain-anthropic>=1.5.6`).

---

#### [LG-002] Nivel: intermedio
**Pregunta:** Tu pipeline de V1 es dos pasos lineales
(`retrieve → generate`). ¿Qué gana un grafo sobre eso, y por qué vale la
pena montarlo en T18 si hoy, aislado, no aporta ningún beneficio?

**Respuesta esperada:** El estado explícito es el mecanismo, no el fin —
permite leer el estado de un nodo no adyacente y persistir para retomar
tras un fallo — pero la razón de fondo es que el grafo habilita
bifurcaciones condicionales (T19: ir a una tool si la recuperación local
es pobre) y ciclos (T22: recuperar, evaluar, reescribir query, recuperar
de nuevo), algo que una cadena de funciones no puede hacer porque va en
una sola dirección. Para dos pasos sin ramas ni ciclos, un grafo es
sobrecosto puro: la justificación de T18 no está en T18 mismo, sino en que
T19 y T22 no se pueden construir sin el grafo ya montado — es
infraestructura que se paga por adelantado.

**Trampa común:** (a) Decir que un pipeline lineal "no permite conocer el
estado intermedio" — sí permite, con logging manual; la diferencia real es
que el grafo lo da por construcción, no por instrumentación. (b)
Justificar T18 por "mejor arquitectura" en vez de por secuenciación, sin
reconocer que hoy es sobrecosto sin beneficio inmediato.

**Ejemplo en el proyecto:**
`src/researchos/application/services/rag_service.py` (`answer_query`, el
pipeline lineal candidato a convertirse en el grafo); `ROADMAP.md` muestra
T19 y T22 dependiendo de T18.

---

#### [LG-003] Nivel: avanzado
**Pregunta:** En LangGraph, un nodo de clasificación puede enrutar con una
conditional edge (el nodo devuelve `dict`, un router aparte decide el
destino) o devolviendo `Command(goto=...)` (el nodo decide y enruta en un
solo retorno). Para tu T19 (decidir si ir a una tool de arXiv o responder
directo), ¿cuál usarías y por qué?

**Respuesta esperada:** Conditional edge. El criterio real no es cuál es
más simple, sino si el nodo *calcula* algo que sirve solo para decidir o si
esa información ya se necesita en el estado de todas formas. En T19 los
documentos recuperados van al estado igual — el nodo de generación los
necesita — así que no hay campo transitorio que `Command` evitaría
persistir. Con conditional edge el router queda como función pura,
testeable con estados fabricados sin ejecutar el nodo completo ni golpear
el LLM, y la estructura de ruteo queda declarada en `add_conditional_edges`,
visible en el builder.

**Trampa común:** Pensar que `Command` es "la forma moderna" y usarla por
defecto. `Command` es obligatorio en un caso real y puntual: enrutar desde
un subgrafo hacia el grafo padre (`Command(graph=Command.PARENT)`), porque
las edges no cruzan fronteras de subgrafo — eso es multi-agente (V6), no
T19. Fuera de ese caso, la pregunta correcta es si el nodo calcula algo
transitorio que solo sirve para decidir (ahí `Command` evita ensuciar el
esquema de estado) o si el nodo solo decide sobre información que ya está
en el estado (ahí conditional edge).

**Ejemplo en el proyecto:** Aplica directamente al criterio de aceptación
de T19 ([#7](https://github.com/johnma96/researchos/issues/7)): "test del
grafo verificando que la conditional edge enruta correctamente en ambos
casos" ya asume el patrón de router-como-función-pura que impone un
conditional edge, no `Command`.

---

#### [LG-004] Nivel: básico
**Pregunta:** Un nodo de LangGraph, ¿recibe todo el estado del grafo o
solo los campos que necesita? ¿Qué debe devolver? ¿Hay alguna forma de que
un nodo declare explícitamente un esquema distinto al del grafo?

**Respuesta esperada:** Por default, en `nodes.py` todos los nodos reciben
el mismo esquema del grafo — no existe una vista parcial automática. La
firma es uniforme: `(ResearchContext) -> dict`. Lo que varía nodo a nodo es
qué campos lee internamente y qué claves incluye en el dict que devuelve.
Ese dict es una actualización **parcial** — LangGraph la fusiona con el
estado existente; el nodo no reconstruye el objeto completo. Ahora bien,
LangGraph sí permite que un nodo declare explícitamente en su firma un
esquema *distinto* — `input_schema`/tipos como `InputState`,
`PrivateState`, `OutputState` ("multiple schemas" en la documentación
oficial): un nodo puede leer un esquema y escribir en otro, y de hecho
**cualquier nodo puede escribir a cualquier canal del estado del grafo**
aunque no forme parte de su esquema declarado. Esto no es "recibir menos
estado" — es una forma de tipar más estrictamente la comunicación
*interna* entre nodos (un canal privado que no es parte del input/output
público del grafo), no un mecanismo para reducir lo que el nodo puede
tocar en tiempo de ejecución.

**Trampa común:** Intentar que un nodo devuelva el estado completo
reconstruido "por seguridad" — innecesario, y con reducers de acumulación
puede duplicar datos que ya estaban. Trampa relacionada: pensar que
declarar `PrivateState` en la firma de un nodo *restringe* en runtime qué
puede leer o escribir — no lo hace; es tipado para claridad y chequeo
estático, LangGraph igual permite escribir a cualquier canal. Y ojo con
streaming: los canales privados no se ocultan automáticamente en
`stream_mode="values"` — hay que pasar `output_keys` explícito si se
quiere restringir qué se expone.

**Ejemplo en el proyecto:**
`src/researchos/application/agents/research_agent/nodes.py:33,53` —
`retrieve_node` devuelve `{"documents": ...}`, `generate_node` devuelve
`{"answer": ...}`; ambos usan el mismo `ResearchContext` porque el grafo
de T18 es lineal y no necesita estado privado entre nodos. El caso de
esquemas múltiples (`InputState`/`PrivateState`/`OutputState`) todavía no
aplica en el repo — sería relevante si T22 necesita pasar un
`rewritten_query` intermedio que no forma parte del output público del
grafo.

---

#### [LG-005] Nivel: intermedio
**Pregunta:** Un nodo de LangGraph solo recibe el estado como parámetro —
no admite argumentos extra. Tu `generate_node` necesita un `LLMProvider`.
¿Qué opciones tenés para inyectarlo y cuál elegiste?

**Respuesta esperada:** Tres opciones: (1) meter el `LLMProvider` en el
estado del grafo — se descarta porque en T22 el checkpointer tiene que
serializar el estado en cada paso, y un cliente HTTP no es serializable;
(2) un global de módulo — se descarta porque acopla `application/` a una
instancia concreta de infraestructura, violando la regla de capas; (3) una
fábrica que recibe la dependencia y devuelve el nodo, capturándola en un
closure. Se eligió la tercera: `make_generate_node(llm)` construye el nodo
una sola vez, en el composition root, y el nodo en sí sigue siendo
`(ResearchContext) -> dict` sin saber que existe LangGraph.

**Trampa común:** Pensar que el estado es "el lugar natural" para
cualquier dependencia porque "así viaja con el grafo". El estado se
serializa (checkpointing); una dependencia con I/O no debería.

**Ejemplo en el proyecto:**
`src/researchos/application/agents/research_agent/nodes.py:21,39` —
`make_retrieve_node` y `make_generate_node`.

---

#### [LG-006] Nivel: avanzado
**Pregunta:** ¿Qué es exactamente un reducer en LangGraph? Un colega
propone anotar `messages: Annotated[list, add_messages]` para que cada
usuario del bot tenga su propia conversación aislada. ¿Es correcto?

**Respuesta esperada:** Un reducer es simplemente un `Callable[[T, T], T]`
— el quickstart oficial usa `operator.add`. `Callable[[Arg1, Arg2],
Return]` es el type hint para "algo invocable que toma esos argumentos y
devuelve eso" — acá `Callable[[T, T], T]` dice "una función que toma dos
valores del mismo tipo (el viejo y el nuevo) y devuelve uno de ese tipo":
literalmente la firma de "combinar A y B en uno". No es magia de
LangGraph, es una función corriente; sin reducer, una clave del estado se
sobreescribe en cada update, con uno se acumula o fusiona según la lógica
que definas. `Annotated[list, add_messages]` usa `Annotated[Tipo,
metadata]`, que envuelve un tipo con metadata adicional que no cambia el
tipo en runtime (`messages` sigue siendo `list`) pero que herramientas
como LangGraph sí leen: al construir el grafo, LangGraph inspecciona esa
metadata por campo y, si encuentra un reducer anotado, lo usa para
fusionar; si no, aplica el default (sobreescribir). `add_messages` en sí
es un reducer sincrónico (no async) que recibe la lista vieja y la lista
de mensajes nuevos y hace *upsert* por `id`: mensajes con `id` nuevo se
appendean, mensajes con `id` ya existente reemplazan al anterior en su
posición — así se editan o corrigen mensajes sin duplicarlos, todo
**dentro de un mismo hilo**. Esto es ortogonal a `Awaitable`: los nodos que
producen esos mensajes nuevos sí son `async` — su firma real es
`Callable[[ResearchContext], Awaitable[dict[str, Any]]]`, o sea "invocar
el nodo devuelve algo *awaitable* (una corrutina) que al resolverse
entrega el dict" — pero el reducer que combina esos valores una vez
producidos es una función sync corriente, sin `await` de por medio. Sobre
el aislamiento entre usuarios: eso lo da el `thread_id` que maneja el
checkpointer (T22) — cada `thread_id` tiene su propio estado persistido
por separado. `add_messages` nunca ve mensajes de otro hilo; no hay ningún
mecanismo de reducer que "separe" usuarios, porque la separación ocurre un
nivel antes, en qué estado se carga para ejecutar el grafo.

**Trampa común:** Confundir "reducer que combina valores" con "mecanismo
que aísla sesiones". Son conceptos ortogonales — casi se justificó una
excepción a la regla de capas del proyecto sobre esa premisa equivocada
antes de verificarla contra la documentación. Trampa secundaria: pensar
que `Annotated` cambia el tipo en runtime — no lo hace; es puramente
metadata que frameworks conscientes de ella (como LangGraph) eligen leer.

**Ejemplo en el proyecto:** `docs/architecture.md` ADR-005 (línea sobre
"a reducer is just a Callable[[T, T], T]");
`src/researchos/application/agents/research_agent/nodes.py:10` — `NodeFn =
Callable[[ResearchContext], Awaitable[dict[str, Any]]]`, mismo patrón de
tipado que el reducer pero para el nodo, no para la fusión. `messages`
deliberadamente no está en `ResearchContext` todavía — llega en T22
(issue [#10](https://github.com/johnma96/researchos/issues/10)) una vez
que se conoce la semántica de fusión necesaria.

---

## Observabilidad y evals

_(sin preguntas todavía)_

## Guardrails y seguridad

_(sin preguntas todavía)_

## LLM providers y SDKs

_(sin preguntas todavía)_

## Ingesta

_(sin preguntas todavía)_
