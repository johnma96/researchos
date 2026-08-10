# Banco de preguntas — ResearchOS

Preguntas de entrevista para AI Engineer, derivadas del código real del
proyecto. Meta: 80–100 preguntas al final de V5.

## Índice por tema

- [Clean Architecture (CA)](#clean-architecture) — 5 preguntas
- [Protocols (PR)](#protocols) — 3 preguntas
- [RAG y retrieval (RG)](#rag-y-retrieval) — 4 preguntas
- [Async y concurrencia (AS)](#async-y-concurrencia) — 3 preguntas
- [Testing (TS)](#testing) — 0 preguntas
- [LangGraph y agentes (LG)](#langgraph-y-agentes) — 0 preguntas
- [Observabilidad y evals (OB)](#observabilidad-y-evals) — 0 preguntas
- [Guardrails y seguridad (GR)](#guardrails-y-seguridad) — 0 preguntas
- [LLM providers y SDKs (LM)](#llm-providers-y-sdks) — 0 preguntas
- [Ingesta (IN)](#ingesta) — 0 preguntas

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
extrae texto y contexto (user_id, channel_id); (3) el bot llama a
`rag_service.answer_query(text=..., llm=..., store=...)` — llamada
agnóstica al canal; (4) `rag_service` orquesta hybrid_search + rerank +
generación; (5) devuelve el string; (6) el bot publica la respuesta en
Slack usando el SDK. Motor no sabe que existe Slack.

**Trampa común:** Meter el bot en `application/`. Los SDKs de Slack o
Telegram son dependencias externas — pertenecen a infrastructure. El bot
importa del motor, no al revés.

**Ejemplo en el proyecto:** Planeado para V2 —
`infrastructure/bot/telegram.py` seguirá el mismo patrón.

---

#### [CA-005] Nivel: avanzado
**Pregunta:** Alguien te pide agregar Qdrant como vector store alternativo
a Chroma. ¿Qué archivos crear? ¿Qué archivos modificar? ¿Qué archivos NO
deberías tocar y por qué?

**Respuesta esperada:** Crear: `infrastructure/retrieval/qdrant.py` con
clase `QdrantVectorStore` que implementa el Protocol `VectorStore`;
`tests/integration/test_qdrant.py`. Modificar: `config.py` para agregar
la opción `Literal["chroma", "qdrant"]` en Settings; el composition root
donde se instancia el store (scripts como `scripts/ingest_papers.py`).
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

**Ejemplo en el proyecto:** `application/services/rag_service.py` recibe
`llm: LLMProvider` y `store: VectorStore` — no sabe si son AnthropicLLM,
GeminiLLM, ChromaVectorStore o mocks; solo sabe qué métodos puede llamar.

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

## Testing

_(sin preguntas todavía)_

## LangGraph y agentes

_(sin preguntas todavía)_

## Observabilidad y evals

_(sin preguntas todavía)_

## Guardrails y seguridad

_(sin preguntas todavía)_

## LLM providers y SDKs

_(sin preguntas todavía)_

## Ingesta

_(sin preguntas todavía)_
