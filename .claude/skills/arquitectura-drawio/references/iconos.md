# Iconos de tecnología — regla y orden de preferencia

Cada proyecto usa tecnologías distintas: GCP, AWS, Azure, LangChain, Langfuse, Google ADK,
React, Node, Python, TypeScript, Docker, Kubernetes, PostgreSQL, FastAPI, etc. La skill es
**agnóstica del stack**.

> **Regla:** para cada componente usa SIEMPRE el **logo oficial de la tecnología** que representa;
> si no existe, cae al **glifo genérico**. Nunca inventes un icono ni dejes una caja vacía.

## 1ª opción — logo oficial de la tecnología (recomendado)

Punto de entrada único en `scripts/glyph.py`, sirve para cualquier tecnología:

```python
from glyph import logo
p.node("LangChain service", x, y, w, h, istyle(logo("langchain")))
p.node("Frontend React",    x, y, w, h, istyle(logo("react", "#61DAFB")))
p.node("PostgreSQL",        x, y, w, h, istyle(logo("postgresql")))
p.node("Vertex AI",         x, y, w, h, istyle(logo("vertex_ai")))   # cae a producto GCP
```

`logo(name, color)` prueba, en orden: **marca** (simple-icons, ~3000 logos oficiales) y luego
**producto Google Cloud** (`gcp_icon`). Si ninguno tiene el logo, lanza un error que te guía al
glifo genérico (no inventa iconos). `color` es opcional (respeta el color de marca).

- Slugs de marca típicos: `langchain`, `react`, `nodejs`, `typescript`, `python`, `docker`,
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
