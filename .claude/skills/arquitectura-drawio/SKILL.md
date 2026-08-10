---
name: arquitectura-drawio
description: Genera y edita diagramas de arquitectura en draw.io (.drawio) con el estilo visual de la organización — paleta, cajas por categoría, edges ortogonales animados theme-aware y logos oficiales de la tecnología que sea (GCP, AWS, Azure, LangChain, React, Node, Python, Docker…) con glifo genérico de fallback. Agnóstica del stack. Usar cuando se pida crear, rediseñar o exportar una arquitectura/diagrama en draw.io, o convertir una descripción o boceto en un .drawio con el look de la casa.
---

# Arquitecturas draw.io con el estilo de la organización

Skill **portable y transversal**: para llevarla a otro repo, copiar la carpeta
`.claude/skills/arquitectura-drawio/` completa. Los scripts son solo stdlib de Python; `gcp_icon.py`
descarga iconos desde URLs públicas de Google (internet una vez, luego cacheado).

## Principio

Un `.drawio` es XML de mxGraph (texto plano). Lo mejor es **generarlo directamente** con el motor
`scripts/drawio_kit.py`, que ya trae los tokens de estilo de la casa, asegura IDs únicos, escapa el
XML y valida el resultado. No hace falta ningún MCP ni servicio online.

## Flujo de trabajo

1. **Entender la arquitectura**: nodos, capas, flujos, qué herramienta es cada nodo. Si es ambiguo,
   preguntar antes de dibujar.
2. **Generar** con `drawio_kit` (ver `scripts/ejemplo.py` como plantilla). Escribir un script corto
   en el scratchpad que:
   - agregue `scripts/` de esta skill a `sys.path` e importe `Diagram, STYLE, EDGE` y, para
     iconos, `glyph.logo` (logo oficial de cualquier tecnología) y `glyph.material` (fallback);
   - defina nodos con coordenadas en grilla y edges con **anclajes explícitos**
     (`exit=`/`entry=`) — clave para que no se traslapen las flechas;
   - llame `Diagram.write(ruta)`, que valida (IDs únicos, edges íntegros, XML) y avisa si supera 500 KB.
3. **Agregar la leyenda** (obligatorio, ver sección *Leyenda*): un bloque que explique qué significa
   cada color de flecha y de caja antes de dar por terminado el diagrama.
4. **Revisar** abriendo el `.drawio` en VS Code con la extensión *Draw.io Integration*
   (`hediet.vscode-drawio`). Iterar con el usuario y confirmar que los iconos rendericen.

Alternativa sin scripts: escribir el XML a mano siguiendo `references/estilo.md` (útil para retoques
puntuales). Estructura mínima por página: `<mxfile><diagram name="…"><mxGraphModel><root>`
`<mxCell id="0"/><mxCell id="1" parent="0"/> … celdas … </root></mxGraphModel></diagram></mxfile>`.

## Estilo

Paleta, strings de estilo, edges y **reglas de layout para evitar traslapes** (fan-out/gather con
anclajes, almacenes pegados a su nodo) están en **`references/estilo.md`**. Rasgo distintivo de la
casa: edges `orthogonalEdgeStyle` con `flowAnimation=1` y color `light-dark(...)` (theme-aware).

## Iconos (agnóstico de tecnología)

Las tecnologías varían por proyecto. **Regla: logo oficial de la tecnología; si no existe, glifo
genérico.** Detalle y ejemplos en **`references/iconos.md`**. Orden:

1. **Logo oficial** — `from glyph import logo; logo(nombre, color)`. Punto de entrada único que
   resuelve marcas (simple-icons: `langchain`, `react`, `nodejs`, `python`, `docker`, `awslambda`,
   `microsoftazure`…) y productos Google Cloud (`vertex_ai`, `bigquery`, `cloud_run`…).
2. **Glifo genérico de fallback** — si `logo()` no encuentra la tecnología (p. ej. Google ADK,
   Langfuse, un componente custom), usa `glyph.material(symbol, color)` en vez de una caja vacía
   (`python scripts/glyph.py list-suggested` mapea tipo→glifo).
3. **Librería nativa de draw.io** — más liviana, look distinto, riesgo de icono en blanco.
4. **Imágenes del usuario** — último recurso; al usarla **informar siempre** del peso extra, que
   son imágenes pegadas, el riesgo de PII en capturas y las licencias de terceros.

## Legibilidad (evitar traslapes) — obligatorio

El flujo debe leerse claro, sin flechas ni textos superpuestos. `references/estilo.md` tiene las
reglas (separación mínima, anclajes `exit`/`entry`, `points=` para rutear alrededor de nodos). Antes
de entregar, corre el linter y **itera hasta que no queden traslapes duros**:

```bash
python scripts/check_layout.py <archivo>.drawio    # nodos/etiquetas/flechas superpuestos
```

`drawio_kit.write()` ya lo ejecuta y avisa. Confirma también visualmente en draw.io.

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

Dibuja las muestras de flecha como edges reales (con su mismo `style`) para que el color y la animación
coincidan con el diagrama, y usa chips de color con el `fillColor`/`strokeColor` de cada arquetipo de
caja. Mantén la leyenda dentro del `pageHeight` y pásala por el linter como el resto.

## Reglas

- **Todos los conectores van animados** (`flowAnimation=1`); el kit lo garantiza en `EDGE`.
- **Incluye siempre una leyenda descriptiva** de colores de flecha y de caja (ver sección *Leyenda*);
  un diagrama sin leyenda está incompleto.
- **Esquinas con radio fijo** (no la curva grande por defecto de `rounded=1`, que tapa el texto): dos
  niveles, ya incluidos en `STYLE` (`ARC` y `ARC_ZONE`) — cajas de componente `absoluteArcSize=1` (muy
  sutil) y contenedores/zonas azules punteados `absoluteArcSize=2` (esquina algo más marcada).
- Sin PII ni datos internos sensibles en etiquetas, notas o imágenes embebidas.
- Mantener el `.drawio` liviano (iconos SVG, no PNG pesados): el pre-commit típico bloquea > 500 KB.
- No prometer que rendericen los iconos sin que el usuario lo confirme en draw.io; si alguno sale en
  blanco, revisar el data URI (ver `references/iconos.md`).
