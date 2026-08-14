# LangGraph y agentes — banco de preguntas

3 preguntas. Fuente: `docs/interview_prep/bank.md`.

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
