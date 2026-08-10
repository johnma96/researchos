# Async y concurrencia — banco de preguntas

3 preguntas. Fuente: `docs/interview_prep/bank.md`.

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
