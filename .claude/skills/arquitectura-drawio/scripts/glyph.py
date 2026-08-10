"""glyph — resolución de iconos de tecnología para draw.io (AGNÓSTICO de stack).

Las arquitecturas usan tecnologías variadas según el proyecto (GCP, AWS, Azure,
LangChain, Langfuse, Google ADK, React, Node, Python, Docker, Kubernetes, ...).
Regla: SIEMPRE el logo OFICIAL de la tecnología; si no existe, un glifo genérico.
Todo se resuelve a data URI URL-encoded (embebible con `shape=image`). Solo stdlib;
cachea cada SVG en el temp del sistema.

Entradas:
  - logo(name, color)        -> LOGO OFICIAL (punto de entrada recomendado). Prueba, en
                                orden: marca (simple-icons, ~3000 logos) y producto Google
                                Cloud (gcp_icon). Sirve para cualquier tecnología.
  - simple_icon(slug, color) -> logo de marca puntual (simple-icons).
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
import os
import sys
import tempfile
import urllib.parse
import urllib.request

SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons/icons/{}.svg"
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


def material(symbol: str, color: str = "#5f6368") -> str:
    """Glifo genérico de fallback (Material Symbols). Ver SUGGESTED para nombres útiles."""
    return _uri(_fetch(MATERIAL.format(symbol)), color)


def globe(color: str = "#5f6368") -> str:
    return material("language", color)


def logo(name: str, color: str | None = None) -> str:
    """Logo OFICIAL de una tecnología (punto de entrada agnóstico de stack).

    Prueba, en orden: (1) marca en simple-icons (langchain, langfuse, react, nodejs,
    python, docker, kubernetes, awslambda, microsoftazure, ...) y (2) producto Google
    Cloud (gcp_icon: vertex_ai, bigquery, cloud_run, ...). Si NO hay logo oficial, lanza
    KeyError sugiriendo un glifo genérico con material() — nunca inventa un icono.
    """
    try:
        return simple_icon(name, color)
    except Exception:
        pass
    try:  # gcp_icon vive en la misma carpeta de la skill
        from gcp_icon import data_uri as _gcp

        return _gcp(name)
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
