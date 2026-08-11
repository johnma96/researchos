# ResearchOS — Diario de aprendizaje (learnings.md)

> Registra lo aprendido cada semana: conceptos, errores, decisiones, reflexiones.
> Herramienta de aprendizaje + activo de portfolio para entrevistas.

---

## Semana 1 — Setup + RAG básico

### **Fecha:** 30/03/2026
#### REACT
- Chain of Taought como estrategia para prompting es una caja negra estática ya que el MODELO USA SUS REPRESENTACIONES INTERNAS PARA GENERAR EL PENSAMIENTO Y  NO LO ALIMENTA DEL MUNDO EXTERIOR. ReAct propone "Razonar para actuar" al tiempo que se "Actúa para razonar". Los modelos de tipo "acción" carecen de la capacidad de llevar objetivos de alto nivel o complejos por lo que es difícil un reflexión profunda.

- Idea central REACT: Aumentar el espacio de acción A del agente de manera que A = A U L, donde L es el espacio del lenguaje. Una acción en L será referida como "pensamiento" o "traza de razonamiento". Esta acción en el espacio L no afecta el exterior y por tanto no obtiene observación como feedback. Lo que hace es obtener información para razonar sobre el contexto c_t y actualizarlo.

- Modelo: PalM-540B con pesos congelados es solicitado with few-shot in-context examples

- Se abordaron tipos de pensamiento como: descomponer metas, inyectar conocimiento de sentido común, extraer partes importantes, rastrear el progreso y manejar excepciones. Además, en función de la pregunta, se tienen razonamiento para tareas de razonmiento en cada paso (pensar-accion-observacion) o pensamientos dispersos para tareas de toma de decisiones (los pensamientos solo están en posiicones relevantes de la trayectoria). Durante las pruebas, un humano podía ir modificanco y controlando el pensameinto del modelo

- Los resultados demostraron una mejor trabajo con ReAct VS Act, especialmente sintetizando la respuesta final

- ReAct VS CoT: Mejor en HotpotQA, y levemente inferior en Fever
    - Alucinaciones es un problema serio en CoT
    - Si bien la intercalación de pasos de razonamiento, acción y observación mejora la solidez y la fiabilidad de ReAct, dicha restricción estructural también reduce su flexibilidad a la hora de formular pasos de razonamiento, lo que da lugar a una tasa de errores de razonamiento mayor que la de CoT. Observamos que existe un patrón de error frecuente específico de ReAct, en el que el modelo genera repetidamente los pensamientos y acciones anteriores, y lo clasificamos como parte de los «errores de razonamiento», ya que el modelo no logra razonar sobre cuál es la siguiente acción adecuada a tomar y salir del bucle.
    - La recuperación de información es crítica para ReAct: Cuanod no la obitiene se descarrilla el razonamiento y le cuesta recuperarse
    - En el fine tunning, con la estrategia ReAct se obtuvo significativamente mejor desempeño que haciendo ajuste fino con las otras estrategias

Insights:
1. Costo de la Autonomía: La flexibilidad de ReAct tiene un "impuesto" de tokens y tiempo. Úsalo solo cuando el camino a la respuesta no sea previsible.

2. Observación como Correctivo: La gran ventaja de ReAct no es que "piense mejor", sino que "escucha" lo que el mundo (las herramientas) le devuelve y corrige su rumbo.

3. Determinismo vs. Agencia: Si la tarea es clasificar (PQRS), el determinismo del RAG gana. Si la tarea es diagnosticar/decidir (Pensiones), la agencia de ReAct es superior.

### Lo que construí
Cliente de Claude API (`AnthropicLLM`) que implementa el Protocol `LLMProvider` con dos métodos: `generate()` para respuestas completas y `stream()` para respuestas token a token.

### Conceptos aprendidos

**async/await**
`async def` declara una función que puede pausarse. `await` es el punto de pausa: el event loop atiende otras tareas mientras espera la respuesta externa. Sin async, el programa se bloquea esperando.

**AsyncMock vs MagicMock**
- `MagicMock` — simula objetos y atributos síncronos
- `AsyncMock` — simula funciones async (las que necesitan `await`)
- Para `async with` hay que mockear `__aenter__` y `__aexit__`
- Para `async for` se necesita un generador async (`async def` + `yield`), no un `iter()` normal

**Tests unitarios vs integración**
- Unitario: sin llamadas reales, cliente reemplazado por mock, rápido, sin costo
- Integración: llamada real a la API, marcado con `@pytest.mark.integration`, consume tokens
- `make test` corre solo `@pytest.mark.unit`. `make test-all` corre todo.

**pre-commit**
Guardián que corre antes de cada commit. Si encuentra errores autocorregibles, los corrige y bloquea el commit. Solo hay que volver a hacer el commit con los archivos ya corregidos.

**Claude Pro vs Anthropic API**
Son productos separados. Claude Pro cubre claude.ai (interfaz web). La API requiere créditos independientes en console.anthropic.com.

### Decisiones técnicas
- `_format_messages()` separa el system prompt de los mensajes de conversación antes de enviar a la API
- Re-exports explícitos (`Document as Document`) requeridos por ruff para imports públicos en `__init__.py`
- Notebooks excluidos del linting de ruff en `pyproject.toml`

### ¿Qué no entendí bien?
- Cuándo usar async-await: debo reforzar este concepto porque veo que está muy rlacionado con el uso de APIs
- Protocol: Entiendo que es más como una maqueta que le dice a python que el método debe cumplir X cosas: Eso hace que cuando alguien quiera implementar un nuevo proveedor, mínimamente debe ajustarse al contrato?
- test: el uso de mocks es complejo, seguir profundizando y tal vez buscar hacer ejercicios?

**Fecha:** 09/04/2026

### ¿Qué aprendí?
-  En la creación de los repos hermanos debo customizar el CLAUDE.md para que sepa hacia dónde apunta el proyecto y sus pormenores
- También aprendía acerca de .pre-commit y solucioné algunos inconvenientes con su uso, entendí que usa ruff y linter para mantener el código limpio y ordenado
- Establecí una rutina para hacer commits que se basa en hacer cerca de 4 a 6 commits diarios de manera que el avance sea continuo pero contenido, y además se estableció Conventional Commits con una estructura <type>(<scoper>): <description> y se incluyó en los CLAUDE.md para que el asistente de código ayude a hacer commits y avice cuando note que ya es hora.
- Aprendía sobre uv y su uso para la gestión de dependecias: actualmente es un estandar en python porque permite mantener ambienestes aislados, disminuye el consumo de recursos ya que trabaja como apuntador a librerías que ya se han descargado en lugar de descargar cada una en el ambiente particular; y como bonues es mucho más rápido que la estrategia pip + venv.

### Que no entendí bien
- Aún tengo dudas sobre el uso de arquitectura limpia y sus beneficios
- También debo de ahondar en cuál es la importnacia de establecer modelos y protocolos que además están aislados de la infraestructura

### Decisiones de diseño
- Se modificó el CLAUDE.md
- Se replanteó el desarrollo de múltiples proyectos al tiempo
- Hay que actualizar algunas cosas en el template clean-agents-template (NO URGENTE)

### Errores interesantes
- Pensé que no podía trabajar con uv en el server pero descrubrí que sí

**Fecha:** 15/04/2026

### ¿Qué aprendí?
- AsyncIO: La analogía es "imagina una persona jugando ajedrez contra otras 15 personas, cada partida toma cerca de 30 minutos y la persona principal mueve en 5 segundos. Si los procesos fueran síncronos, es decir, la persona jugara la partida 1 completa, luego la 2 completa, luego la 3, etc. se demoría en terminar cerca de 7.5 horas. Sin embargo, si la persona juega de manera asíncrona, es decir, mueve en cada partida y va atentiendo cada mesa según su contrincante vaya realizando su movimiento, entonces la misma persona podría terminar en más rápido (supón 5 seg por mesa son 15*5=75 seg y luego ese tiempo en promedio sería 75*30=2250 seg = 37.5 minutos)
- Está relacionado con los conceptos de paralelismos, multihilo, multiproceso y concurrencia:
    - El paralelismo implica que varias tareas se ejecutan al mismo tiempo, cada un en un núcleo diferente. Suelen ser tareas liminatas por CPU, es decir, se realizan cálculos.
    - El multiproceso es una manera de lograr paralelismo
    - La concurrencia es más amplio que el paralelismo y sugiere que multiples tareas tienen la habilidad de correr traslapándose. Concurrencia no necesarimanete implica paralelismo.
    - El miltihilo es una manera de lograr concurrencia en la que múltiples hilos toman turnos para ejecutar tareas.
Estos enfoques tienen sus propias librerías como multiprocessing, concurrent.futures y threading.
- Se puede usar async para crear una función asíncrona (función corrutina) o un generados asíncrono (usando yield)
- También usar async con with para un contexto asíncrono o async con for para iterar sobre un generador asíncrono
- El event loop es el que se encarga de ejecutar las tareas asíncronas. Normalmente se dispara con un asyncio.run() pero también se puede obtener una instancia con asyncio.get_running_loop() para interactur con el objet, como por ejemplo cuando quieres programar un callback pasando el loop como un argumento
- El patrón, que consiste en esperar una corrutina y pasar su resultado a la siguiente, crea una cadena de corrutinas
    - Otros patrones importantes:
        - Integración de corrutinas y colas
- Async iterators, loops and comprehensions:
    - iterador: async for -> el async for solo funciona con objetos que implementa '__alter__' y '__anext__' como un generador o **Strams de datos que llegan por partes** como stream.text_stream, por ejemplo.
    - generador asíncrono: async def ... yield
    - comprehension: [x async for x in f() if ...]
- También es importatne los statements async with ya que garantizan que los recursos se liberen correctamente
- asyncio.create_task() para iniciar corrutinas sin esperar el await
- asyncio.gather() para ejecutar múltiples corrutinas al mismo tiempo y esperar resultados en el orden que las corrutinas son pasadas
- asyncio.as_completed() para ejecutar múltiples corrutinas al mismo tiempo y esperar resultados en el orden que las corrutinas son completadas
- Puedes agrupar los errores que suceden en llamadas asíncronas con un ExceptionGroup y puedes manejarlas desde un bloque try usando except* para cada tipo de excepción generada

Usa async cuando:

- Haces llamadas HTTP — arXiv, Anthropic API, NewsAPI (esperas respuesta de red)
- Lees/escribes archivos en volumen — descargar múltiples PDFs en paralelo
- Telegram bot — recibes mensajes mientras procesas otros

No uses async cuando:

- Procesas texto en memoria — chunking, parseo XML, re.sub()
- Operaciones CPU intensivas — embeddings, modelos ML (ahí es multiprocessing)

Regla simple para ResearchOS:

- ¿Esperas algo externo (API, disco, red)? → async def
- ¿Solo calculas en memoria? → def normal

### ¿Qué no entendí bien?
- No entiendo la importancia del event loop a nivel práctico. Entiendo que es quien orquesta las ejecuciones pero a nivel de programación no veo la necesidad de interactuar con él directamente
- Tengo que ahondar en el patrón de integración de corrutinas y colas
- también en el entendimiento de asyncio.create_task()

### Decisiones de diseño
- Solo patrón de cadena para versión 1, en versión 2 podríamos implementa patrones de integración entre corrutinas y colas. También puedo usar gather, task, as_completed y el manejo de errores
- En V1 todas las funciones que hacen I/O externo son async def. Las que solo procesan datos en memoria son def síncronas. Esta distinción se aplica consistentemente en todo el proyecto.

### Errores interesantes
- async for -> Solo usado con iteradores o con un stream objetc
- usar un for y al interior llamar una función async sigue siendo un sistema secuencial. El patró busca que el for esté dentro de un async.gather() para disparar la cadena de asincronismos y así ir trayendo o procesando la I/O al mismo tiempo. Si el orden de las corrutinas no importa se podría usar async.as_completed()

**Fecha:** 17/04/2026

### ¿Qué aprendí?
- Benchmark async confirmado en código real: asyncio.gather() fue 11x más rápido que secuencial descargando 10 papers. La segunda ejecución fue más rápida por caché HTTP y reutilización de conexiones TCP — no significa que async sea menos útil, sino que el caché redujo el tiempo de espera.
- `async for` solo funciona con objetos que implementan `__aiter__` y `__anext__`. Una lista normal usa `for` común. `asyncio.gather()` es lo que genera el paralelismo, no el tipo de loop.
- Overlap en chunking es para no perder contexto dentro del mismo documento. Una oración que cae en el borde entre dos chunks queda partida sin overlap. Con 50 chars de overlap, esa oración aparece en ambos chunks y el retriever puede encontrarla completa.
- Tests parametrizados con `@pytest.mark.parametrize`: permiten probar múltiples escenarios con una sola función de test usando tuplas de parámetros (ver `tests/unit/application/test_retrieval_service.py`).
- Chroma solo maneja ids, embeddings, textos y metadatas — no sabe nada de `Document`. `ChromaVectorStore` actúa como adaptador que traduce en ambas direcciones.
- Mutable default arguments en Python son un antipatrón (`B006` en ruff): usar `dict = {}` como default puede causar bugs sutiles. Siempre usar `None` e inicializar dentro de la función.

### ¿Qué no entendí bien?
- por qué el score se cambia en función de la distancia cuando uso coseno o l2?

### Decisiones de diseño
- `LocalEmbedder` separado de `ChromaVectorStore` — si cambia el modelo de embeddings, no se toca el vector store.
- `embedder_metadata` configurable en `ChromaVectorStore` para soportar diferentes métricas de distancia (coseno, L2).
- Hack de pysqlite3 en `conftest.py`, no en código de producción. Se resolverá en Dockerfile en V4.


**Fecha:** 18/04/2026

### ¿Qué aprendí?
- en función del nombre de la colección los textos se guardan aisladamente
- el await asyncio.gather no tiene mucha razón de ser si justamente después de éste viene un ciclo for que procesa en orden cada resultado recuperado -> Preguntar a mi tutor
- Cuando estoy en un script .py y quiero disparar una función async, no puedo usar await (esto solo en el REPL o en notebooks), tengo que usar asyncio.run -> Verificar y preguntar cómo sería algo con create_task()

### ¿Qué no entendí bien?
- Debo consultar si se puede hacer una consulta general en chroma sin importar la colección para que busque en absolutamente toda la base -> Lo que entiendo es que chroma divide los documentos guardamos conforme las colecciones

### Decisiones de diseño
-

### Errores interesantes
- `uv run pip list` en Windows mostraba el entorno global de pipx en lugar del `.venv` del proyecto — engañoso. La forma correcta de verificar es `uv run python -c "import <paquete>; print('ok')"` o `uv run python -c "import sys; print(sys.executable)"`.
- `ipykernel` no se instala automáticamente con `jupyter` en `uv` — debe agregarse explícitamente como dependencia dev. Sin él, Jupyter no puede registrar el kernel del proyecto. Solución: `uv add --dev ipykernel` y luego `uv run python -m ipykernel install --user --name researchos --display-name "ResearchOS"`.
- `pysqlite3-binary` solo tiene wheels para Linux — en Windows sqlite3 ya viene actualizado con Python. Solución: `"pysqlite3-binary>=0.5.4; sys_platform == 'linux'"` en `pyproject.toml`.
- El hack de sqlite3 en `conftest.py` fallaba en Windows porque `pysqlite3` no existe ahí. Solución: condicional por plataforma `if sys.platform == "linux":` antes del import.
- `asyncio.gather` sin `await` no ejecuta las coroutines — retorna un objeto coroutine sin resolver. Siempre `await asyncio.gather(...)`.
- `Path.stem` retorna el nombre del archivo sin extensión — más limpio que hacer `split(os.sep)[-1].split('.pdf')[0]` sobre un string.

**Fecha:** 21/05/2026

### ¿Qué aprendí?

**Protocols y Clean Architecture — el propósito real**
- Recibir `VectorStore` en lugar de `ChromaVectorStore` desacopla la capa de aplicación de la infraestructura. Beneficios concretos: (1) testabilidad — se inyecta un mock sin tocar BD real; (2) intercambiabilidad — cambiar de Chroma a Qdrant solo requiere crear una nueva clase que cumpla el Protocol, sin tocar código de negocio; (3) contrato explícito — el Protocol documenta exactamente qué necesita la aplicación.
- Los Protocols en Python se validan en tiempo de chequeo estático (mypy), NO en runtime. En runtime Python no lanza error si falta un método — solo falla cuando se llama. En proyectos maduros mypy corre en CI como barrera automática.
- Structural subtyping ("duck typing con tipos"): una clase satisface un Protocol simplemente teniendo los métodos con las mismas firmas — no necesita heredar explícitamente ni declararlo.

**RAG: vector search vs BM25 vs hybrid**
- Búsqueda vectorial: texto → embedding → similitud coseno. Encuentra contenido semánticamente cercano aunque las palabras sean distintas.
- BM25: recuperación por coincidencia exacta de términos, ponderada por frecuencia y rareza. Trabaja en memoria, sin base vectorial. Fuerte donde el vectorial falla: siglas, nombres propios, términos técnicos exactos.
- Hybrid search: combina ambos resultados con Reciprocal Rank Fusion (RRF). El objetivo no es más chunks sino mejor ranking, considerando señales semánticas y de coincidencia exacta simultáneamente.

**Cobertura de tests por capa**
- Infraestructura (`arxiv.py`, `chroma.py`, `embedder.py`) tiene baja cobertura unitaria por diseño — dependen de sistemas externos y pertenecen a tests de integración.
- Medir cobertura de código sin tests asociados solo genera ruido en el reporte.
- `addopts` en `[tool.pytest.ini_options]` pasa flags automáticamente a cada ejecución de pytest.
- `isinstance` no puede verificar tipos genéricos como `tuple[str, Path]` en runtime — hay que usar assertions separadas por elemento.

**BM25 y la relación con la base vectorial**
- Chroma cumple dos roles distintos: persistencia de chunks en disco y retrieval vectorial. BM25 solo necesita el primero — usa Chroma como almacén y construye su propio índice en memoria con `collection.get()`.
- Los scores de BM25 y vectorial son incomparables directamente: BM25 retorna frecuencias ponderadas (sin límite superior), vectorial retorna similitud coseno (0 a 1). RRF resuelve esto comparando posiciones en el ranking, no scores absolutos.
- Una función `async` que no contiene `await` es perfectamente válida — se resuelve inmediatamente sin suspenderse. Útil para que BM25Retriever sea uniforme con ChromaVectorStore en `asyncio.gather()`.
- `model_copy(update={...})` en Pydantic crea una copia del objeto con campos modificados sin mutar el original — necesario para asignar el `score` calculado en cada búsqueda.

### ¿Qué no entendí bien?
- El rol práctico del event loop a nivel de programación (cuándo y por qué interactuar con él directamente).
- Cómo integrar mypy en el pipeline de CI para que valide Protocols automáticamente.

### Decisiones de diseño
- `BM25Retriever` implementa el Protocol `Retriever` (solo `search`) — no `VectorStore` (que exige también `upsert`). `ChromaVectorStore` satisface ambos por structural subtyping.
- `BM25Retriever.search` definido como `async` aunque opera en memoria, para ser uniforme con `ChromaVectorStore` y poder usarse en `asyncio.gather()` en el hybrid search.
- `ingest_papers` acepta `store: VectorStore | None = None` — imports de infraestructura son lazy dentro de la función para no violar la dependencia application → infrastructure a nivel de módulo.
- Tests de cobertura se acumulan en lotes por sesión dedicada, no después de cada feature.
- Tokenizador de BM25 inyectado como callable (`tokenizer=None`) en lugar de string selector — más flexible y Pythónico.

### Errores interesantes
- `registry.py` y `PromptTemplate` hacían lo mismo — tener ambos era redundancia. Se eliminó `registry.py` y se consolidó en `PromptTemplate.render()`.
- El reporte de un bug en `overlap_chunking` era incorrecto: la lógica `start = i * (chunk_size - overlap)` produce un paso fijo, no un overlap acumulativo. Verificar con math antes de reportar un bug.
- `isinstance` no puede verificar tipos genéricos como `tuple[str, Path]` en runtime — usar assertions separadas por elemento.

---

**Fecha:** 01/06/2026

### ¿Qué aprendí?
- hybrid rerank con LLM com juez busca solucionar el problema de orden de los retrievers que se basan exclusivamente en el score y que no toman en cuenta el contexto de la pregunta como es el caso de BM25
- en asyncio.gather lo que debo tener en mente es que se pasan argumentos por lo que el operador * lo que hace es desempaquetar tuplas o listas
- los mocks de protocolos personaizados se realizan en conftest.py, los que involucran llamados a serivicos externos son reemplazados por mocks en librerías estandar
- Para que una evaluación de un retriever sea justa es necesario que el set de evaluación no sufra de data leakege, esto es, que no conozco qué hay explicitamente en el corpus actual. Mi conjunto está sesgado porque se hizo exactamente con documentos que sí o sí ya sabíamos que estaban en el vector store

### ¿Qué no entendí bien?
- Debo profundizar sobre métricas de evaluación de un retriever. Entiendo que el MRR mide en qué posición es recuperado un documento y luego se saca un promedio, pero no me queda claro cómo opera esta métrica en el caso por ejemplo de un RAG donde el corpus son ejemplos históricos como el de PQRs.

### Decisiones de diseño
- Modificamos retrieval_service para que quedar acomo chunking service y agregamos un retrieval service real que se enfoca justamente en un servicio de retreival

### Errores interesantes
- Claude puede devolver JSON envuelto en markdown o con texto adicional — `json.loads()` falla. Solución: extraer el array con `find("[")` y `rfind("]")` antes de parsear.
- Las lambdas en un dict de estrategias capturan variables del scope exterior por referencia — en este caso no fue problema, pero es un antipatrón a tener en mente si las variables cambian en el loop.

---

**Fecha:** 29/07/2026

### ¿Qué aprendí?
- Se repasaron conceptos de Clean Architecture: application se codifica contra domain; infrastructure también se codifica contra domain (para implementar sus Protocols) e infrastructure sí importa de application — por ejemplo, un router o un bot llaman a un service como `rag_service.answer_query`. Lo que nunca ocurre es que domain importe de alguien, o que application importe de infrastructure.
- Se refuerza la idea de sumar contribuciones en Reciprocal Rank Fusion (RRF) porque así se premia el consenso entre retrievers. Si se promediara, un rank muy alto se compensaría con la ausencia en otro y se perdería la señal de que 2 o más retrievers coincidieron. -> Aún falta reforzar e interiorizar más este concepto
- las funciones asíncronas existen para permitir que el event loop pueda ejecutar otras corrutinas mientras se realizan operaciones de I/O, por ejemplo cuando se hace una petición HTTP. Es diferente a trabajo paralelo porque ese trabajo sí requiere uso de CPU. La analogía es un mesero que atiende muchas mesas: en lugar de quedarse esperando, pide al chef que prepare un plato y mientras tanto va y toma el pedido en otra mesa o la limpia.
- Los agentes importan funciones de `agent_utils.py` (composición) en lugar de heredar de una clase base, porque así, si se modifica un método de la clase base, todos los agentes heredarían el cambio (y un posible error), mientras que con composición solo se ve afectado el agente que efectivamente importa esa función. Es menos elegante pero más aislado.

### ¿Qué no entendí bien?
- Me hicieron preguntas sobre cómo evaluar un RAG. Entendí que la manera es con métricas claras y un ground truth que viene de dos fuentes: (a) una entidad externa que no conoce el contenido de la BD vectorial y por tanto no está sesgada, y (b) retroalimentación de producción señalando si una recuperación fue buena o mala. Las queries que fallan no son una tercera fuente de verdad — se etiquetan y se mandan a un dataset de regresión para monitoreo futuro, eso es manejo de fallos, no una fuente adicional de ground truth. No tengo claras las métricas concretas (formulación matemática, en qué se sustentan) ni si existen herramientas de evaluación automática de RAG en el mercado o solo metodologías.
- **[corregido hoy]** Dirección de dependencia infrastructure↔application: escribí dos veces en esta misma entrada que "infrastructure nunca importa de application" — es al revés, infrastructure sí importa de application (routers/bots llaman a services). Es la misma confusión de dirección de dependencias ya fichada como hueco recurrente; revisar en próximas sesiones si ya quedó interiorizada.
- **[corregido hoy]** Ubicación de la lógica de negocio: escribí que infrastructure incluye "lógica propia del negocio" — no es así, la lógica de negocio vive en domain/application; infrastructure es solo detalle técnico (SDKs, llamados a APIs, drivers).
- **[corregido hoy]** Terminología de composición de agentes: escribí "los agentes exportan de agent_utils.py" — es al revés, `agent_utils.py` exporta funciones y los agentes las importan/consumen.

### Decisiones de diseño
- Se decide modificar el esquema de trabajo: con 5h/semana se van a emplear cerca de 4 en el desarrollo de código y 1h en la revisión conceptual: llenado de un banco de preguntas y revisión de un ensayo sobre un tema específico

### Errores interesantes
- Confundí la dirección de dependencia entre infrastructure y application: dije que "infrastructure nunca importa de application", cuando es lo opuesto — infrastructure sí importa de application (ej. un router o un bot llaman a un service). Lo que nunca ocurre es que domain importe de alguien o que application importe de infrastructure. Application se encarga de orquestar contra Protocols de domain; infrastructure implementa detalle técnico (SDKs, llamados a APIs, drivers) sin lógica de negocio; domain establece el contrato (requisitos de modelos y Protocols).

---

**Fecha:** 10/08/2026

### ¿Qué aprendí?

- **`AnswerFn = Callable[[str], Awaitable[str]]` es un alias de tipo que declara un contrato mínimo de comportamiento.** Se lee: "una función que recibe un `str` y devuelve algo que, al esperarlo, produce un `str`". Es el contrato completo que el bot de Telegram necesita conocer del motor RAG: nada más.

- **Por qué `Awaitable[str]` y no `str`.** Cuando escribo `async def answer(query: str) -> str`, la anotación `-> str` describe lo que la corrutina *resuelve*, no lo que la llamada *retorna*. Llamar `answer("hola")` sin `await` devuelve una corrutina, no un string. Por eso, visto como valor de primera clase, el tipo de esa función es `Callable[[str], Awaitable[str]]`. Si escribiera `Callable[[str], str]`, estaría describiendo una función sincrónica y mypy me marcaría el error al inyectar la async.

- **Un alias de función es un contrato más liviano que un Protocol.** Un Protocol declara varios métodos con nombre; `AnswerFn` declara un solo comportamiento anónimo: un parámetro, un retorno. Regla que me llevo: cuando lo que inyecto es *un solo comportamiento*, alcanza un tipo de función; cuando son *varios comportamientos relacionados que comparten estado*, ahí sí conviene un Protocol o una clase. Envolver una sola función en una clase es ceremonia sin beneficio.

- **`AnswerFn` es el mecanismo concreto que hace al bot agnóstico al motor.** El bot no importa `LLMProvider`, ni `VectorStore`, ni `AnthropicLLM`, ni `ChromaVectorStore`. Solo sabe que le dieron algo llamable con esa firma. Mañana puedo cambiar el motor de vector-only a hybrid+rerank, o cambiar Chroma por Qdrant, y `telegram.py` no se entera. El mismo `AnswerFn` va a servir para Slack, para un router de FastAPI y para un CLI.

- **El closure es lo que llena el contrato.** En `scripts/run_telegram_bot.py` defino `async def answer(query: str) -> str` que captura `llm` y `chroma` del scope exterior. Su firma resultante es exactamente `AnswerFn`. Las dependencias concretas quedan atrapadas en el closure y nunca cruzan la frontera hacia el bot.

- **El wiring pertenece al composition root, no al adapter.** Si `telegram.py` instanciara `ChromaVectorStore`, no sería una violación de capas (ambos son `infrastructure/`), pero rompería tres cosas: el bot quedaría intesteable sin un Chroma real, agregar Slack duplicaría el wiring, y cambiar la composición del motor obligaría a editar cada canal.

### ¿Qué no entendí bien?

- El bot responde bien la primera pregunta y falla en la de seguimiento ("cuál es el mecanismo"). Identifiqué que son **dos** problemas distintos, no uno: (1) no hay memoria conversacional — `answer_query` no recibe historial ni `session_id`, cada mensaje es independiente; (2) aunque hubiera memoria, el retrieval seguiría fallando, porque se hace con la query cruda y "cuál es el mecanismo" es anafórica: su embedding no se parece a ningún chunk. Agregar memoria no arregla retrieval. Falta entender bien cómo se implementa el query rewriting y en qué punto del grafo va.

### Decisiones de diseño

- El bot recibe `answer_fn` inyectada en el constructor, no instancia infraestructura. `TelegramBot(token, answer_fn)`.
- `run()` es `def` normal, no `async def`: `app.run_polling()` gestiona su propio event loop, así que el script de arranque es sincrónico de punta a punta. Llamarlo desde `asyncio.run` produciría un conflicto de loops.
- Se descartó usar `context.user_data` de `python-telegram-bot` para guardar historial. Es memoria en RAM que se pierde al reiniciar, no se comparte entre canales, y pondría estado del motor en el adaptador. La memoria pertenece al motor vía el Protocol `MemoryStore`.
- Alcance deliberado: el bot conecta `answer_query` (vector-only). Conectar hybrid search es un cambio en `application/`, no en el bot.

### Errores interesantes

- Escribí `self.answer_fn: answer_fn` en vez de `self.answer_fn = answer_fn`. Con dos puntos, Python lo lee como anotación de tipo, no como asignación: es sintácticamente válido, la clase se define sin error, pero **el atributo nunca se crea**. Habría explotado con `AttributeError` en el primer mensaje. Segundo error mecánico de este tipo en dos semanas (el anterior fue omitir `self` en firmas de Protocol) — es un hueco de escritura de Python, no conceptual.
- Usé un f-string innecesario en `.token(f"{self.token}")` cuando `self.token` ya es `str`.
- Guardé el retorno de `await update.message.reply_text(...)` en una variable sin usar.

---

**Fecha:** 11/08/2026

### ¿Qué aprendí?

- **`RetrieveFn = Callable[[str], Awaitable[list[Document]]]` es el mismo patrón de ayer, una capa más abajo.** Ayer inyecté al bot una función que responde (`AnswerFn`); hoy inyecté al servicio una función que recupera. La simetría no es casual: cuando lo que necesito inyectar es *un solo comportamiento*, un tipo de función alcanza. Protocol o clase solo cuando son varios comportamientos que comparten estado.

- **Por qué un parámetro tipo `strategy="hybrid"` habría sido peor.** La firma quedaría `answer_query(query, llm, store=None, retrievers=None, strategy="vector", top_k=5)`: dos parámetros opcionales que son *condicionalmente obligatorios* según el valor de un tercero. Puedo llamar `strategy="hybrid"` pasando solo `store` y compila perfecto — explota en runtime. El type checker no puede expresar "si strategy es hybrid, retrievers es obligatorio". Inyectar la función elimina el problema: la dependencia correcta ya está capturada en el closure.

- **`retrieve_and_generate` es una composición de conveniencia, no el único camino.** Su paso 1 (`retrieve_context`) está soldado a búsqueda vectorial y exige un `store`. Cuando necesito otra estrategia no la parametrizo: armo mi propia composición con las mismas piezas primitivas — `retrieve(query)` → `build_rag_messages(...)` → `llm.generate(...)`. Por eso `build_rag_messages` está expuesta como función independiente y no escondida dentro de `retrieve_and_generate`.

- **Este es el pago concreto de composición sobre herencia** (la pregunta 1.4 del taller que dejé en blanco). Con herencia tendría un `BaseRagAgent` con un método `retrieve()` que habría que sobrescribir, y cambiar de estrategia significaría crear una subclase. Con composición elijo otra función para ese paso. El costo de cambiar la estrategia bajó de "nueva clase" a "otra línea".

- **Por qué NO modifiqué `retrieve_context`.** Tres razones: su firma recibe `store: VectorStore` mientras hybrid necesita `retrievers: list[Retriever]` (dependencias distintas); `hybrid_search` ya existe en `retrieval_service.py` y duplicarla en `agent_utils` pondría la misma lógica en dos lugares; y `retrieve_context` sigue siendo útil tal como está — si mañana quiero volver a vectorial puro, mi closure sería `retrieve_context(q, chroma, K)`. La pieza no muere, solo se mueve de ser llamada dentro del service a ser llamada en el composition root.

- **Las dependencias se construyen una vez, al arrancar, no dentro del closure.** Mi primer intento construía `LocalEmbedder()` dentro de la función de recuperación. `LocalEmbedder` carga un modelo de sentence-transformers en memoria: se habría recargado en cada pregunta que llegara al bot. Eso es literalmente lo que significa "composition root" — el lugar donde se arma, no donde se usa.

- **El patrón de dispatch ya existía en mi propio repo.** El dict `strategies` de `scripts/eval_retrieval.py` (línea 88) tiene cuatro lambdas que son, cada una, un `RetrieveFn`. Escribí cuatro instancias del tipo antes de nombrarlo. Si mañana quiero elegir estrategia por configuración, muevo ese dict al script y leo `settings.retrieval_strategy` — sin cadena de `if`.

- **Pasar una función vs. llamarla.** `retrieve=retrieve_hybrid_rerank` pasa la función; `retrieve=retrieve_hybrid_rerank(query)` la ejecuta y pasa una corrutina. Los paréntesis significan "ejecuta ahora y dame el resultado". Cuando el parámetro se va a llamar más tarde (dentro de `answer_query`, dentro de `_handle_message`), va el nombre desnudo.

- **El bot no se tocó.** El cambio de estrategia del motor no requirió ni una línea en `infrastructure/bot/telegram_bot.py`. Es la validación del diseño de ayer: el adaptador solo conoce `AnswerFn`, así que cambiar lo que hay detrás le es invisible.

### ¿Qué no entendí bien / queda abierto?

- No medí el costo de latencia del rerank. Ahora hay una llamada extra al LLM por cada pregunta, y eso es un trade-off real que introduje sin cuantificar.
- No sé todavía si hybrid+rerank mejora las respuestas en la práctica. El eval actual tiene data leakage y da ~1.000 en las cuatro estrategias, así que no discrimina. Solo lo voy a saber con queries reales acumuladas del bot (V3).
- Me costó ver que "reemplazar `retrieve_and_generate`" significaba escribir sus tres pasos, no llamarla con otros argumentos. Intenté tres veces reusarla antes de entender que su paso 1 era justo lo que quería cambiar.

### Decisiones de diseño

- `answer_query` recibe `retrieve: RetrieveFn` en lugar de `store: VectorStore`. `top_k` desaparece de la firma porque queda capturado en el closure.
- Un solo closure hoy (hybrid+rerank), no las dos estrategias con un `if`. Construir un interruptor que nadie va a mover es generalización prematura. El dispatch por configuración se hará cuando haga falta alternar de verdad.
- `retrieve_and_generate` se deja en su lugar aunque quedó sin llamadores en producción. Eliminarla hoy habría mezclado dos cambios en un commit. Se evalúa en V2, al construir el grafo, donde `retrieve` y `generate` se vuelven nodos separados.
- Se acepta la latencia extra del rerank sin optimizar. Medirla primero, decidir después.

### Errores interesantes

- Escribí `RetrieveFn = Callable[[str]], Awaitable[list[Document]]` — corchetes mal cerrados. `Callable[[str]]` se cierra solo y la coma convierte todo en una **tupla** de dos elementos, no en un tipo de función. `Callable` recibe sus dos argumentos dentro de un solo par de corchetes.
- Pasé `retrieve=retrieve_hybrid_rerank(query)` con paréntesis. Habría fallado con `TypeError: 'coroutine' object is not callable` más un `RuntimeWarning` de corrutina nunca esperada. Curioso: tres líneas abajo pasé `answer_fn=answer` correctamente, sin paréntesis.
- Primer intento de los closures: sin parámetro `query` (no cumplían `Callable[[str], ...]`), construyendo el embedder adentro, y sin `return`.
- Nombré mi closure `hybrid_search`, colisionando con el import de `retrieval_service`. El `def` local habría tapado el import.
- Import de `SAMPLES_DIR` sin uso.
- Tercer error mecánico de escritura de Python en una semana (los anteriores: `:` en vez de `=` en una asignación, `self` omitido en firmas de Protocol). No son conceptuales — es un hueco de automatismo que se cierra con repetición.

---
