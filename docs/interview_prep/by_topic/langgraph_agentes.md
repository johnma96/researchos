# LangGraph y agentes — banco de preguntas

6 preguntas. Fuente: `docs/interview_prep/bank.md`.

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
