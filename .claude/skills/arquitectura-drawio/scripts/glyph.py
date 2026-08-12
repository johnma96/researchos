"""glyph — resolución de iconos de tecnología para draw.io (AGNÓSTICO de stack).

Las arquitecturas usan tecnologías variadas según el proyecto (GCP, AWS, Azure,
LangChain, Langfuse, Google ADK, React, Node, Python, Docker, Kubernetes, ...).
Regla: SIEMPRE el logo OFICIAL de la tecnología; si no existe, un glifo genérico.
Todo se resuelve a data URI URL-encoded (embebible con `shape=image`). Solo stdlib;
cachea cada SVG en el temp del sistema.

Entradas:
  - icon(name, fallback, color) -> RECOMENDADO al generar: logo oficial y, si no existe,
                                glifo genérico; None si no hay red. Nunca lanza.
  - logo(name, color)        -> LOGO OFICIAL (lanza KeyError si no existe). Prefiere el
                                arte A COLOR: devicon (multicolor) -> producto Google Cloud
                                (multicolor) -> simple-icons teñido con el hex OFICIAL de
                                la marca. Solo sale negro si el color de marca lo es.
  - devicon(slug)            -> logo multicolor (devicon). Cubre el stack clásico.
  - brand_hex(slug)          -> color oficial de una marca (#RRGGBB) según simple-icons.
  - simple_icon(slug, color) -> logo de marca puntual (simple-icons, monocromo).
  - material(symbol, color)  -> GLIFO GENÉRICO de fallback (code, database, api, hub,
                                settings, smart_toy...) vía Material Symbols (Apache-2.0).
                                Úsalo cuando NO haya logo oficial (p. ej. Google ADK, un
                                componente custom).
  - globe(color)             -> globo/Internet (atajo de material('language')).

CLI:
    python glyph.py logo langchain              # logo oficial (marca o producto GCP)
    python glyph.py logo vertex_ai              # cae a producto Google Cloud
    python glyph.py brand awslambda "#FF9900"
    python glyph.py glyph code "#cc0000"        # glifo genérico </>
    python glyph.py list-suggested              # glifos genéricos por tipo
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons/icons/{}.svg"
SIMPLE_META = "https://cdn.jsdelivr.net/npm/simple-icons/_data/simple-icons.json"
DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{0}/{0}-{1}.svg"
DEVICON_VARIANTS = ("original", "plain")  # "original" es el arte a color; "plain", silueta
MATERIAL = "https://cdn.jsdelivr.net/npm/@material-symbols/svg-400/outlined/{}.svg"
CACHE = os.path.join(tempfile.gettempdir(), "drawio_glyphs")

# Glifos genéricos sugeridos según el tipo de componente (Material Symbols).
SUGGESTED = {
    "código / microservicio / componente": "code",
    "componente desplegable / paquete": "deployed_code",
    "agente / kit de agentes (p. ej. ADK)": "smart_toy",
    "API / endpoint genérico": "api",
    "base de datos / almacén": "database",
    "cola / mensajería": "forum",
    "evento / trigger": "bolt",
    "red / hub / integración / orquestador": "hub",
    "configuración / proceso": "settings",
    "servidor / DNS": "dns",
    "internet / web (globo)": "language",
    "seguridad / auth": "lock",
    "usuario / actor": "person",
    "modelo / IA": "neurology",
}


def _fetch(url: str) -> str:
    os.makedirs(CACHE, exist_ok=True)
    local = os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest()[:16] + ".svg")
    if not os.path.exists(local):
        req = urllib.request.Request(url, headers={"User-Agent": "drawio-kit"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(local, "wb") as fh:
            fh.write(data)
    with open(local, encoding="utf-8") as fh:
        return fh.read()


def _uri(svg: str, color: str | None) -> str:
    if color:  # el path hereda el fill puesto en el <svg>
        svg = svg.replace("<svg ", f'<svg fill="{color}" ', 1)
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


def simple_icon(slug: str, color: str | None = None) -> str:
    """Logo de marca (simple-icons). `slug` p.ej.: awslambda, amazonsqs, microsoftazure,
    apache. `color` opcional (hex) para colorizar; por defecto negro."""
    return _uri(_fetch(SIMPLE.format(slug)), color)


def devicon(slug: str) -> str:
    """Logo A COLOR de una tecnología (devicon, variante `original`).

    simple-icons es monocromo por diseño: cada logo es un `<path>` sin `fill`, así que
    sale NEGRO salvo que se le pase un color, y aun así queda plano. devicon publica el
    arte oficial multicolor (degradados incluidos) para el stack clásico de desarrollo
    —python, docker, postgresql, react, nodejs, googlecloud, kubernetes…— que es lo que
    da vida al diagrama. No cubre marcas nuevas o de nicho: ahí hay que caer a
    simple-icons coloreado con el hex de marca."""
    ultimo: Exception | None = None
    for variante in DEVICON_VARIANTS:
        try:
            return _uri(_fetch(DEVICON.format(slug, variante)), None)
        except Exception as exc:
            ultimo = exc
    raise KeyError(f"devicon no tiene {slug!r}") from ultimo


def brand_hex(slug: str) -> str | None:
    """Color oficial de una marca según los metadatos de simple-icons (#RRGGBB).

    Sirve para que un logo monocromo salga al menos en SU color y no en negro. El JSON
    (~3300 marcas) se descarga una vez y queda cacheado como el resto."""
    try:
        datos = json.loads(_fetch(SIMPLE_META))
    except Exception:
        return None
    iconos = datos["icons"] if isinstance(datos, dict) else datos
    for entrada in iconos:
        propio = entrada.get("slug") or _slug(entrada.get("title", ""))
        if propio == slug.lower():
            return "#" + entrada["hex"]
    return None


def _slug(titulo: str) -> str:
    """Slug de simple-icons a partir del título (regla simple: minúsculas y alfanuméricos)."""
    return re.sub(r"[^a-z0-9]", "", titulo.lower())


def material(symbol: str, color: str = "#5f6368") -> str:
    """Glifo genérico de fallback (Material Symbols). Ver SUGGESTED para nombres útiles."""
    return _uri(_fetch(MATERIAL.format(symbol)), color)


def globe(color: str = "#5f6368") -> str:
    return material("language", color)


def icon(name: str, fallback: str = "code", color: str | None = None) -> str | None:
    """Resolución de icono **a prueba de fallos** — el punto de entrada para generar.

    Aplica la regla de la skill en una sola llamada: intenta el LOGO OFICIAL de `name`
    y, si esa tecnología no tiene logo, cae al GLIFO GENÉRICO `fallback`. Si tampoco hay
    red (primera ejecución sin conectividad), devuelve None en vez de romper: el kit
    dibuja entonces la caja sin icono y el diagrama sigue siendo válido.

    Es lo que antes cada script copiaba de ejemplo.py; vive aquí para que la caída a
    glifo sea idéntica en todos los diagramas.

        p.node("Frontend", x, y, w, h, STYLE["card"], icon=icon("react", "code"))
        p.node("Google ADK", x, y, w, h, STYLE["llm"], icon=icon("adk", "smart_toy"))

    Para forzar el glifo sin intentar el logo, pasa un `name` que no exista como marca
    (convención: "__mi_componente__").
    """
    try:
        return logo(name, color)
    except Exception:
        pass
    try:
        return material(fallback, color or "#5f6368")
    except Exception as exc:  # sin red: degradar, no romper
        print(f"(aviso glyph: sin icono para {name!r} ni glifo {fallback!r}: {exc})")
        return None


def logo(name: str, color: str | None = None) -> str:
    """Logo OFICIAL de una tecnología (punto de entrada agnóstico de stack).

    **Prefiere el arte a color**, que es lo que da vida al diagrama:

    1. devicon `original` — multicolor, con degradados (python, docker, postgresql,
       react, nodejs, googlecloud, kubernetes, fastapi...).
    2. producto Google Cloud vía gcp_icon — también multicolor (vertex_ai, bigquery...).
    3. simple-icons teñido con el hex OFICIAL de la marca — cubre ~3300 marcas, pero es
       monocromo por diseño; al menos sale en su color y no en negro.

    Si se pasa `color` explícito se respeta y se salta el paso 1: quien pide un color
    concreto quiere ese color. Si NO hay logo oficial en ninguna fuente lanza KeyError
    para que caigas a un glifo genérico — nunca inventa un icono.
    """
    if color is None:  # sin color pedido -> se prefiere el arte multicolor
        try:
            return devicon(name)
        except Exception:
            pass
    try:  # gcp_icon vive en la misma carpeta de la skill; sus iconos ya son a color
        from gcp_icon import data_uri as _gcp

        return _gcp(name)
    except Exception:
        pass
    try:
        # simple-icons es monocromo: si no se pidió color, se tiñe con el hex OFICIAL de la
        # marca en vez de dejarlo en negro, que es lo que apagaba los diagramas.
        return simple_icon(name, color or brand_hex(name))
    except Exception:
        pass
    raise KeyError(
        f"sin logo oficial para {name!r}. Usa un glifo genérico de fallback, p. ej. "
        f"material('code'|'hub'|'database'|'smart_toy', color). Ver `list-suggested`."
    )


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "list-suggested":
        for k, v in SUGGESTED.items():
            print(f"  {v:16} <- {k}")
    elif a[0] == "logo":
        print(logo(a[1], a[2] if len(a) > 2 else None))
    elif a[0] == "brand":
        print(simple_icon(a[1], a[2] if len(a) > 2 else None))
    elif a[0] == "glyph":
        print(material(a[1], a[2] if len(a) > 2 else "#5f6368"))
    else:
        print(
            "uso: glyph.py [logo <name> [color] | brand <slug> [color] | "
            "glyph <symbol> [color] | list-suggested]"
        )
