# Iconos de tecnología — regla y orden de preferencia

Cada proyecto usa tecnologías distintas: GCP, AWS, Azure, LangChain, Langfuse, Google ADK,
React, Node, Python, TypeScript, Docker, Kubernetes, PostgreSQL, FastAPI, etc. La skill es
**agnóstica del stack**.

> **Regla:** para cada componente usa SIEMPRE el **logo oficial de la tecnología** que representa;
> si no existe, cae al **glifo genérico**. Nunca inventes un icono ni dejes una caja vacía.

## Al generar: `icon()` — la regla completa en una llamada (recomendado)

```python
from glyph import icon

p.node("Frontend React", x, y, w, h, STYLE["card"], icon=icon("react", "code"))
p.node("PostgreSQL",     x, y, w, h, STYLE["card"], icon=icon("postgresql", "database"))
p.node("Google ADK",     x, y, w, h, STYLE["llm"],  icon=icon("adk", "smart_toy"))
p.node("Worker propio",  x, y, w, h, STYLE["card"], icon=icon("__worker__", "code"))
```

`icon(name, fallback, color)` intenta el **logo oficial** y, si esa tecnología no lo tiene, cae al
**glifo genérico** `fallback`. Si no hay red devuelve `None` y el kit dibuja la caja sin icono, en
vez de romper la generación. Para forzar el glifo sin intentar el logo, usa un `name` que no exista
como marca (convención: `"__mi_componente__"`).

> **No le pases `color` a un logo de marca salvo que quieras forzarlo.** El tercer argumento existe
> para los glifos genéricos, donde el color codifica la categoría. En un logo, pasar color **apaga el
> arte multicolor**: se salta devicon y tiñe la silueta de simple-icons de un solo tono.
> `icon("python", "code")` da el logo azul-y-amarillo real; `icon("python", "code", "#3776AB")` da
> una silueta plana azul.

## Por qué un icono sale a color o en negro

Los diagramas apagados casi siempre vienen de aquí: **simple-icons es monocromo por diseño**. Cada
logo es un único `<path>` sin `fill`, así que renderiza NEGRO salvo que se le pase un color, y aun
así queda plano. Es un set de siluetas de marca, no de logos a color.

`logo()` prueba las fuentes en este orden, para que el color sea lo normal y el negro la excepción:

| Orden | Fuente | Aspecto | Cobertura |
|---|---|---|---|
| 1 | **devicon** `original` | **Multicolor**, con degradados | Stack clásico: python, docker, postgresql, react, nodejs, kubernetes, fastapi, googlecloud… |
| 2 | **gcp_icon** | **Multicolor** (arte oficial de Google) | Productos Google Cloud: vertex_ai, bigquery, cloud_run… |
| 3 | **simple-icons + `brand_hex()`** | Monocromo, pero en el **color oficial de la marca** | ~3300 marcas: telegram `#26A5E4`, huggingface `#FFD21E`, pydantic `#E92063`… |

El paso 3 solo queda oscuro cuando el color de marca **es** oscuro: Anthropic es `#191919`, así que
su logo es casi negro por definición y está bien así.

```bash
python scripts/glyph.py logo python      # devicon multicolor
python scripts/glyph.py logo telegram    # simple-icons teñido con su #26A5E4
```

**Peso:** el arte multicolor pesa entre 2 y 3 veces más que la silueta (python 1,6 → 3,1 KB; docker
2,0 → 5,6 KB; postgresql 5,7 → 10,6 KB), porque lleva varios `path` y a veces degradados. Teñir un
simple-icons no cuesta nada (+25 bytes). En un diagrama normal la diferencia son unas decenas de KB,
muy lejos del límite de 500 KB; si alguna vez aprieta, la palanca es reducir iconos repetidos, no
volver al monocromo.

## 1ª opción por dentro — logo oficial de la tecnología

Si quieres controlar el fallo tú mismo:

```python
from glyph import logo
p.node("LangChain service", x, y, w, h, istyle(logo("langchain")))
p.node("Frontend React",    x, y, w, h, istyle(logo("react")))   # multicolor
p.node("PostgreSQL",        x, y, w, h, istyle(logo("postgresql")))
p.node("Vertex AI",         x, y, w, h, istyle(logo("vertex_ai")))   # cae a producto GCP
```

`logo(name, color)` prueba las tres fuentes de la tabla de arriba en orden, priorizando el arte a
color. Si ninguna tiene el logo, lanza un error que te guía al glifo genérico (no inventa iconos).
`color` es opcional y, si lo pasas, **salta devicon** y tiñe la silueta de simple-icons: úsalo solo
cuando quieras un color concreto por encima del arte de marca.

- Slugs típicos (sirven igual en devicon y simple-icons): `langchain`, `react`, `nodejs`, `typescript`, `python`, `docker`,
  `kubernetes`, `fastapi`, `postgresql`, `redis`, `awslambda`, `amazonsqs`, `microsoftazure`,
  `apache`, `openai`, `huggingface`. Catálogo completo: <https://simpleicons.org>.
- Productos GCP: `vertex_ai`, `bigquery`, `cloud_run`, `cloud_storage`, `cloud_vision_api`,
  `data_loss_prevention_api`, ... (`python scripts/gcp_icon.py --list`).

CLI para explorar/obtener un data URI:

```bash
python scripts/glyph.py logo langchain          # logo oficial (marca o producto GCP)
python scripts/glyph.py logo vertex_ai
```

Detalle técnico: el data URI es **URL-encoded** (no base64) y `image=` va **de último** en el
`style`, **sin `;` final** (así el `;base64` no rompe el parser de estilos de draw.io). `drawio_kit`
ya lo maneja al pasar `icon=`. El mismo patrón aplica a cualquier proveedor: bajar el SVG oficial,
URL-encode, `shape=image`.

## Fallback — glifo genérico (cuando NO hay logo oficial)

Muchas tecnologías nuevas o de nicho no tienen logo en las fuentes (p. ej. **Google ADK**,
**Langfuse**), igual que los componentes **custom** (un microservicio propio, una cola interna).
En esos casos NO dejes la caja vacía: rellena con un glifo genérico apropiado de Material Symbols
(Apache-2.0), coloreado según su categoría:

```python
from glyph import material
p.node("Orquestador ADK", x, y, w, h, istyle(material("smart_toy", "#1a73e8")))
p.node("Langfuse (observabilidad)", x, y, w, h, istyle(material("visibility")))
p.node("MicroComponent", x, y, w, h, istyle(material("code", "#cc0000")))
```

Glifos sugeridos por tipo (`python scripts/glyph.py list-suggested`): `code` (código/microservicio),
`deployed_code` (paquete), `smart_toy` (agente/ADK), `neurology` (modelo/IA), `api` (endpoint),
`database` (almacén), `forum` (cola), `bolt` (evento), `hub` (integración/orquestador), `settings`
(proceso), `dns` (servidor), `language`/`globe()` (internet), `lock` (auth), `person` (usuario).

## 2ª opción — librería nativa de draw.io

Formas vectoriales de la librería del proveedor en draw.io (p. ej. `mxgraph.gcp2.hexIcon` con
`prIcon=<producto>`; *More Shapes → …*). Es lo **más liviano** (cero KB embebidos) y diffeable,
pero el look difiere del arte oficial y hay riesgo de icono en blanco si el nombre/`prIcon` no
existe en esa versión. Usar cuando el peso importe más que la fidelidad, o sin acceso a la fuente.

## 3ª opción — imágenes provistas por el usuario (informar SIEMPRE)

Si el usuario aporta sus propios iconos (PNG/SVG: capturas, assets internos, logos de terceros), se
embeben como `shape=image`, pero **siempre hay que informarle** de:

- el **peso extra** en el `.drawio` (y el límite de 500 KB del pre-commit típico);
- que son **imágenes pegadas** (raster/opacas), no vectores de librería ni logos oficiales;
- que **no deben contener PII ni datos internos sensibles** — una captura puede filtrar información;
- posibles **restricciones de licencia** de logos de terceros.

Es el último recurso, cuando la tecnología no está en las fuentes oficiales ni aplica un glifo.
