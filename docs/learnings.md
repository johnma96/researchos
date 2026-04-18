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

**Fecha:** _[completar]_

### ¿Qué aprendí?
-

### ¿Qué no entendí bien?
-

### Decisiones de diseño
-

### Errores interesantes
-

---
<!-- Copiar plantilla para cada semana -->
