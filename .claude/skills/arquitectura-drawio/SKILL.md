---
name: arquitectura-drawio
description: Lee un repositorio, deriva su arquitectura real y la dibuja en draw.io (.drawio) con el estilo visual de la organización — paleta, cajas por categoría, edges ortogonales animados theme-aware y logos oficiales de la tecnología que sea (GCP, AWS, Azure, LangChain, React, Node, Python, Docker…) con glifo genérico de fallback. Incluye el criterio para decidir con el usuario si conviene una página o varias, y un linter de legibilidad. Agnóstica del stack. Usar cuando se pida crear, rediseñar, documentar o exportar una arquitectura/diagrama en draw.io, diagramar un repositorio, o convertir una descripción o boceto en un .drawio con el look de la casa.
---

# Arquitecturas draw.io con el estilo de la organización

Skill **portable y transversal**: para llevarla a otro repo, copiar la carpeta
`.claude/skills/arquitectura-drawio/` completa. Los scripts son solo stdlib de Python; `gcp_icon.py`
descarga iconos desde URLs públicas de Google (internet una vez, luego cacheado).

## Principio

Un `.drawio` es XML de mxGraph (texto plano). Lo mejor es **generarlo directamente** con el motor
`scripts/drawio_kit.py`, que ya trae los tokens de estilo de la casa, asegura IDs únicos, escapa el
XML y valida el resultado. No hace falta ningún MCP ni servicio online.

## Qué entrega esta skill (y qué NO) — leer antes de prometer nada

**El resultado es un borrador de alta fidelidad, no un entregable final.** Un diagrama de arquitectura
publicable siempre necesita una pasada humana. Decirlo por adelantado evita la frustración de esperar
que salga perfecto de una corrida.

La razón es estructural, no de esfuerzo: quien genera el diagrama **no ve el resultado**. Se coloca
cada caja por coordenadas y se rutea cada flecha a ciegas, mientras que el render depende de métricas
de fuente reales, del algoritmo de ruteo de draw.io y de si el SVG de cada icono cargó. `check_layout`
cubre la parte geométrica —y cubre bastante: los diagramas de referencia de la organización lo pasan
casi limpios— pero **no ve** el ancho real del texto, ni dónde acaba draw.io dibujando una etiqueta,
ni un icono en blanco, ni si el conjunto está equilibrado.

Reparto realista del trabajo:

| Lo hace bien la skill | Lo tiene que hacer una persona |
|---|---|
| Inventario completo y fiel de componentes leyendo el repo | Confirmar que las conexiones reflejan la intención del sistema |
| Estilo, paleta, iconos y leyenda consistentes con la casa | Ajuste fino de posiciones y ruteo tras ver el render |
| Detectar traslapes geométricos y texto que no cabe | Juzgar el equilibrio visual y qué sobra o falta |
| Estructura de páginas y densidad razonable de arranque | Decidir qué se enfatiza para la audiencia concreta |

Al entregar, **dilo explícitamente**: esto es un insumo inicial, revisalo en draw.io y ajustá.
No presentes el resultado como terminado ni prometas que no hay traslapes sin un export confirmado.

### Con qué modelo lanzar esta skill

Generar una arquitectura desde un repo pide tres cosas a la vez: leer y sintetizar código, razonar
sobre geometría sin verla, e iterar contra los linters hasta que queden en verde. Es una tarea de
razonamiento largo y **conviene el modelo más capaz disponible con esfuerzo alto**; con un modelo
intermedio el patrón observado es diagramas de pocas cajas —el inventario se queda en los nombres de
módulo— y traslapes que no se corrigen porque no se itera contra el linter.

Sea cual sea el modelo, lo no negociable es el bucle: correr `check_layout` **hasta exit 0**, y no
dar el diagrama por bueno sin un export visual confirmado por el usuario.

## Flujo de trabajo

**No empieces a dibujar hasta haber completado los pasos 1 y 2.** El error caro no es un diagrama
feo: es un diagrama bonito que muestra una arquitectura que no es la del repositorio, o que mete en
un lienzo tres preguntas distintas.

### 1. Levantar el inventario leyendo el repositorio

Cuando el diagrama sale de un repo (lo normal), no preguntes al usuario lo que puedes leer. Recorre
estas fuentes y anota qué extraes de cada una:

| Dónde miras | Qué sacas |
|---|---|
| Manifiestos: `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, `requirements.txt` | El stack real, y con él **qué logo lleva cada caja** |
| `README`, `docs/`, ADRs, `CLAUDE.md`/`AGENTS.md` | La **intención** declarada y el vocabulario del equipo (úsalo en las etiquetas) |
| Puntos de entrada: `main`/`__main__`, `scripts/`, `cmd/`, `CMD` del Dockerfile, targets del Makefile, workflows de CI | **Cuántos flujos independientes hay** — el insumo del paso 2 |
| Composition roots, contenedores de DI, módulos de *wiring* | **Quién construye e inyecta a quién** (el grafo real, no el declarado) |
| Interfaces, Protocols, puertos, clases abstractas | Los **contratos** y qué implementación concreta cumple cada uno |
| Clientes de SDK, llamadas HTTP, colas, drivers de BD | Las **fronteras del sistema**: qué es externo y qué es propio |
| Tests | Qué se ejecuta de verdad; lo que no aparece suele ser código muerto o aspiracional |

Reglas de fidelidad:

- **Dibuja el estado REAL, no el ideal.** Si el código viola su propia arquitectura, el diagrama lo
  muestra. Un diagrama que solo describe la intención es peor que no tener diagrama, porque nadie
  descubre la deuda mirándolo.
- Cuando encuentres deuda o violaciones, **pregunta explícitamente** si el usuario quiere el estado
  real (marcado en rojo con `EDGE["warn"]`), el estado objetivo, o ambos en páginas distintas.
- Marca lo que existe pero está **vacío o sin implementar** — decir "este paquete está creado pero
  vacío hasta V2" es información, y evita que el lector lo crea funcional.
- Si algo del código contradice la documentación, gana el código; señálalo al usuario.

### 2. Decidir el encuadre y OFRECER OPCIONES (paso obligatorio)

Cuenta primero, decide después. Con el inventario en mano:

- **N** = nodos-componente (sin notas ni leyenda).
- **F** = flujos independientes, entendiendo por independiente "con disparador distinto": CLI,
  petición HTTP, webhook, cron, mensaje de cola.

Criterio de partición:

| Señal | Qué hacer |
|---|---|
| N ≤ 12 y F = 1 | **Una sola página.** Partir de más también hace daño: obliga al lector a saltar entre pestañas para entender algo que cabía junto. |
| N > 55 o más de ~40 flechas en una página | Partir. |
| Conviven la vista **estática** (qué existe, quién depende de quién) y la **dinámica** (qué pasa cuando ocurre X) | Separarlas siempre. Responden preguntas distintas y comparten muy pocas flechas; juntas obligan a que cada paso cruce de banda. |
| F ≥ 2 | Una página por flujo. |
| Al bocetar, más de 3 flechas cruzan más de una banda | Señal de que sobra una vista en esa página. |

> **La zona buena para una arquitectura técnica es 25–50 nodos por página, no 8.** Medido sobre los
> diagramas de referencia de la organización: 52 nodos / 33 flechas en el de MLOps, 37 / 19 y 30 / 2
> en el de un sistema multiagente, 130–200 en los de proceso de negocio. Un diagrama de 8 cajas para
> un público técnico **no está simplificado, está incompleto**: no dice qué SDK hay detrás de cada
> adapter, ni dónde vive la configuración, ni qué contratos median, ni qué es externo al proceso.
>
> Esa densidad **no se consigue con cajas más grandes sino con más cajas y menos texto en cada una**.
> Las medidas de la referencia: caja de **~180×56 px** (no 300×88) y etiqueta de **~30–45 caracteres**
> (no un párrafo). El detalle se lleva a las etiquetas de flecha, a las zonas que agrupan y a una nota
> al pie — no dentro de la caja. Si tus cajas necesitan 90 px de alto, estás metiendo prosa donde
> debería ir un nombre.

Para repositorios grandes, encuadra por **niveles de zoom al estilo C4** (contexto → contenedores →
componentes → código) en vez de inventar cortes: es vocabulario estándar y le da al usuario una
escala reconocible para elegir.

Después **presenta 2–3 encuadres al usuario y espera su elección antes de dibujar**. Cada opción
lleva el reparto de páginas y el conteo de nodos por página, y el trade-off dicho en voz alta:
más páginas = más fiel al detalle técnico pero más salto entre vistas; menos páginas = una lectura
de golpe pero menos precisión.

En la misma tanda, resuelve las dos decisiones que cambian el diagrama **más que cualquier regla de
layout**, y que no se pueden inferir del código: el **nivel de detalle** y el **público**.

### Qué significa "público técnico" (no es una etiqueta, es una lista)

Si el usuario dice que la audiencia es técnica, el diagrama tiene que responder **qué, cómo, cuándo y
por qué** se conecta cada cosa. En la práctica, cada una de estas debe estar en el lienzo, y su
ausencia es lo que hace que un diagrama se sienta simplista:

- **Qué SDK o librería concreta hay detrás de cada adapter** (`chromadb PersistentClient`,
  `rank_bm25 BM25Okapi`, `AsyncAnthropic`), no solo "vector store".
- **Qué contrato media** entre dos piezas: el Protocol, la interfaz, el tipo de la función inyectada.
- **Qué tipo de dato viaja** por cada flecha (`list[Paper]`, `list[Document]`, `str`).
- **Qué es externo al proceso** y por qué canal se le habla (HTTP, gRPC, cola, disco).
- **Dónde vive el estado**: almacenes, índices en memoria, caché, y quién los escribe y quién los lee.
- **Qué es concurrente o diferido**: `asyncio.gather`, colas, reintentos, jobs programados.
- **Dónde está la configuración y los secretos**, y quién los inyecta.
- **Cuándo ocurre cada flujo**: disparado por el usuario, por un cron, al arrancar el proceso.
- **Qué NO existe todavía**: paquetes vacíos, contratos sin implementación, deuda registrada.

Un diagrama técnico con 8 cajas no cumple ninguna de estas. Si al terminar el inventario te salen
menos de ~20 nodos para un sistema real, es que te quedaste en los nombres de módulo y no bajaste a
las herramientas, los contratos y las fronteras. Volvé al paso 1.

Para público de negocio, en cambio, se sube de nivel: cajas por capacidad, sin SDKs ni tipos, y las
fronteras del sistema como lo importante.

### 3. Generar

**Archivo de salida: `docs/architecture.drawio`.** Es la ruta por defecto salvo que el usuario pida
otra. Un repositorio normalmente tiene una sola arquitectura, y las distintas vistas van como páginas
dentro de ese archivo, no como archivos sueltos: así el diagrama tiene una ubicación previsible y no
se acumulan versiones con nombres inventados. Solo se usa otro nombre cuando de verdad hay diagramas
de sistemas distintos en el mismo repo.

**Si el archivo ya existe, no lo sobrescribas sin avisar.** Puede tener retoques manuales que no están
en ningún script (ver la sección de alcance). Ábrelo, mira qué páginas tiene, y confirma con el
usuario si se reemplaza entero, se añade una página o se conserva una copia.

Escribir un script con `drawio_kit` (ver `scripts/ejemplo.py`, que ya es multipágina) que:

- agregue `scripts/` de esta skill a `sys.path` e importe `Diagram, STYLE, EDGE` y `glyph.icon`
  (logo oficial de cualquier tecnología con caída automática a glifo genérico);
- use `Page.zone()` para las bandas, `Page.banner()` para la cabecera y `Page.legend()` para la
  leyenda, en vez de reimplementarlos — así todos los diagramas salen iguales;
- defina nodos con coordenadas en grilla y edges con **anclajes explícitos** (`exit=`/`entry=`) —
  clave para que no se traslapen las flechas;
- aplique los **patrones de composición** de `references/estilo.md` (serpentina, pasos numerados,
  corredores reservados) antes de pelear con waypoints;
- llame `Diagram.write(ruta)`, que valida (IDs únicos, edges íntegros, XML), corre el linter de
  legibilidad y avisa si supera 500 KB.

**El script es andamiaje, no fuente de verdad.** Sirve para colocar decenas de cajas por coordenadas
sin escribir XML a mano, pero en cuanto una persona retoca el `.drawio` en draw.io —y casi siempre lo
hace, ver la sección de alcance— volver a ejecutarlo **destruye ese trabajo manual**. A partir de ese
momento la fuente de verdad es el `.drawio`.

Por defecto, **déjalo en un temporal y no lo versiones**; entrega el `.drawio` y menciona que el
script existe por si lo quieren. Guardarlo en el repo solo compensa en un caso concreto: que el
diagrama se vaya a **regenerar entero y periódicamente** desde el código (por ejemplo en CI, o en un
repo que cambia rápido y donde nadie va a retocar a mano). Si es ese caso, ponlo en
`docs/build_architecture.py`, junto al diagrama; documenta en el docstring cómo ejecutarlo y por qué
ese encuadre de páginas, y **avisa en el propio archivo que regenerar pisa los ajustes manuales**.

Pregúntaselo al usuario en vez de decidirlo tú.

Ojo con el lint del repo al escribirlo: las etiquetas largas chocan con el límite de columnas.
Pártelas en concatenación implícita **conservando el espacio final** de cada trozo (`"...de "`
`"infrastructure/"`), o saldrán palabras pegadas en el diagrama. Es un fallo invisible —el XML es
válido y el linter de layout pasa— así que hay un chequeo dedicado sobre el fuente:

```bash
python scripts/check_labels.py <script_generador>.py
```

### 4. Verificar

Los linters no sustituyen ver el diagrama. Es obligatorio cerrar así:

```bash
python scripts/check_layout.py docs/architecture.drawio   # nodos/etiquetas/flechas/texto/página
python scripts/check_labels.py <generador>.py             # etiquetas partidas sin espacio
```

Y luego, **como asistente no puedes renderizar el `.drawio`: pídele al usuario un export y espera
su confirmación.** Si el diagrama es multipágina, pídeselo explícitamente **con todas las páginas**
(*File → Export as → PNG* con **All Pages** marcado, o cambiando de pestaña antes de exportar): el
export por defecto saca solo la página activa, y es fácil creer que verificaste tres vistas cuando
te mandaron tres copias de la primera.

Revisar y editar el `.drawio` en VS Code con la extensión *Draw.io Integration*
(`hediet.vscode-drawio`). Confirmar con el usuario que los iconos rendericen y que no haya palabras
pegadas ni texto recortado — cosas que el linter no ve.

Alternativa sin scripts: escribir el XML a mano siguiendo `references/estilo.md` (útil para retoques
puntuales). Estructura mínima por página: `<mxfile><diagram name="…"><mxGraphModel><root>`
`<mxCell id="0"/><mxCell id="1" parent="0"/> … celdas … </root></mxGraphModel></diagram></mxfile>`.

## Estilo

Paleta, strings de estilo, edges, **reglas de layout para evitar traslapes** (fan-out/gather con
anclajes, almacenes pegados a su nodo) y los **patrones de composición** (serpentina, pasos
numerados, corredores reservados, color-por-capa en páginas de flujo) están en
**`references/estilo.md`**. Rasgo distintivo de la casa: edges `orthogonalEdgeStyle` con
`flowAnimation=1` y color `light-dark(...)` (theme-aware).

## Iconos (agnóstico de tecnología)

Las tecnologías varían por proyecto. **Regla: logo oficial de la tecnología; si no existe, glifo
genérico.** Detalle y ejemplos en **`references/iconos.md`**. Orden:

1. **Al generar, usa `glyph.icon(nombre, glifo_fallback)`**: aplica la regla completa en una
   llamada — logo oficial y, si esa tecnología no lo tiene, glifo genérico; devuelve `None` si no hay
   red, en vez de romper. Es el punto de entrada recomendado. **No le pases color a un logo de marca:**
   el tercer argumento es para los glifos genéricos, y en un logo apaga el arte multicolor.
2. **`glyph.logo(nombre)`** si quieres controlar el fallo. Prioriza el **arte a color**, que es lo
   que da vida al diagrama: devicon multicolor (`python`, `docker`, `postgresql`, `react`, `nodejs`,
   `kubernetes`, `fastapi`…) → producto Google Cloud, también multicolor (`vertex_ai`, `bigquery`,
   `cloud_run`…) → simple-icons teñido con el **hex oficial de la marca**. Lanza `KeyError` si
   ninguna fuente tiene el logo. Un icono negro en el render suele significar que se pasó un `color`
   por error, no que la fuente falle (detalle en `references/iconos.md`).
3. **`glyph.material(symbol, color)`** para el glifo genérico suelto (p. ej. Google ADK, Langfuse, un
   componente custom) — nunca una caja vacía. `python scripts/glyph.py list-suggested` mapea
   tipo→glifo.
4. **Librería nativa de draw.io** — más liviana, look distinto, riesgo de icono en blanco.
5. **Imágenes del usuario** — último recurso; al usarla **informar siempre** del peso extra, que
   son imágenes pegadas, el riesgo de PII en capturas y las licencias de terceros.

## Legibilidad (evitar traslapes) — obligatorio

El flujo debe leerse claro, sin flechas ni textos superpuestos. `references/estilo.md` tiene las
reglas (separación mínima, anclajes `exit`/`entry`, `points=` para rutear alrededor de nodos) y los
patrones de composición que suelen resolver el problema sin tocar waypoints. Antes de entregar, corre
el linter y **itera hasta que no queden problemas duros**:

```bash
python scripts/check_layout.py docs/architecture.drawio
```

Detecta once cosas. Ocho son traslapes: nodos superpuestos, etiquetas sobre nodos, flechas que
cruzan nodos, etiquetas de flecha sobre nodos, sobre el título de una zona o encimadas entre sí,
texto que desborda su caja y nodos fuera del área de página. Las otras tres son **economía**:
**cajas sobredimensionadas**, **etiquetas de caja muy largas** y **rojo disperso** fuera de una
zona de deuda — no rompen nada, pero son lo que separa un diagrama correcto de uno a la altura
del estándar de la casa. `drawio_kit.write()` ya lo ejecuta y avisa.

**El linter no ve todo.** No sabe de fuentes reales, iconos que no cargan ni palabras pegadas por un
literal mal partido. Un diagrama que pasa el linter puede seguir siendo ilegible: cierra siempre con
la verificación visual del paso 4.

## Leyenda (obligatorio)

Toda arquitectura entregada **debe incluir una leyenda descriptiva** — sin ella el diagrama no está
terminado. Un diagrama codifica significado en el color de las flechas y de las cajas; la leyenda es
lo que hace ese código legible para quien no lo dibujó. Ubícala en una franja al pie (o en una esquina
libre) y cubre, como mínimo:

- **Color de cada flecha**: qué relación representa. En el estilo de la casa (ver `EDGE` en
  `references/estilo.md`) el convenio es: **verde** = flujo de datos; **azul** = orquestación / control
  (quién invoca o ejecuta a quién); **gris punteada** = consumo de un servicio o recurso compartido
  (lectura/escritura). Si usas otros colores o relaciones, explícalos igual.
- **Color de cada caja**: qué tipo de componente es (p. ej. verde = paso determinista, azul =
  servicio/modelo LLM, rojo = orquestador, blanco = almacén de apoyo, amarillo = salida). Describe
  solo las categorías que realmente aparezcan en el diagrama.
- **Cualquier otra convención relevante**: iconos sueltos = fuentes/actores externos, que las flechas
  van animadas e indican el sentido del flujo, líneas punteadas vs. sólidas, etc.

Usa **`Page.legend(y, edges, chips, nota)`**, que ya dibuja las muestras como edges reales (mismo
`style`, así el color y la animación coinciden de verdad) y los chips con el `fillColor` de cada
arquetipo, resolviendo además el caso de las formas con etiqueta inferior. No la reimplementes: si
cada diagrama arma su leyenda a mano, dejan de parecerse entre sí, que es justo lo que la skill
evita. En multipágina, **repite la leyenda en cada página** — nadie garantiza que el lector entre por
la primera. Mantenla dentro del `pageHeight` y pásala por el linter como el resto.

## Reglas

- **Todos los conectores van animados** (`flowAnimation=1`); el kit lo garantiza en `EDGE`.
- **Incluye siempre una leyenda descriptiva** de colores de flecha y de caja (ver sección *Leyenda*);
  un diagrama sin leyenda está incompleto.
- **Nunca dibujes sin haber ofrecido opciones de encuadre** (paso 2) cuando el diagrama sale de un
  repositorio: la decisión de una página o varias es del usuario, no tuya.
- **El diagrama refleja el código, no la intención**; la deuda técnica se marca, no se esconde.
- **La salida por defecto es `docs/architecture.drawio`**, con las distintas vistas como páginas del
  mismo archivo; si ya existe, confirmar antes de sobrescribir.
- **El script generador es andamiaje**: por defecto no se versiona, porque regenerar pisa los ajustes
  manuales que la persona haga sobre el `.drawio`.
- **Un diagrama no está verificado hasta que el usuario confirma un export visual**, y en multipágina
  el export debe incluir todas las páginas.
- **Esquinas con radio fijo** (no la curva grande por defecto de `rounded=1`, que tapa el texto): dos
  niveles, ya incluidos en `STYLE` (`ARC` y `ARC_ZONE`) — cajas de componente `absoluteArcSize=1` (muy
  sutil) y contenedores/zonas azules punteados `absoluteArcSize=2` (esquina algo más marcada).
- Sin PII ni datos internos sensibles en etiquetas, notas o imágenes embebidas.
- Mantener el `.drawio` liviano (iconos SVG, no PNG pesados): el pre-commit típico bloquea > 500 KB.
- No prometer que rendericen los iconos sin que el usuario lo confirme en draw.io; si alguno sale en
  blanco, revisar el data URI (ver `references/iconos.md`).
