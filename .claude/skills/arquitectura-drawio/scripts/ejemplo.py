"""Plantilla de uso de drawio_kit — AGNÓSTICA de tecnología.

Muestra el flujo de iconos recomendado: intentar el LOGO OFICIAL de cada tecnología
con `logo(...)` y, si no existe, caer a un GLIFO GENÉRICO con `material(...)`.
Copie este patrón para cualquier stack (JS, Python, LangChain, ADK, cloud, ...).

    python ejemplo.py            # escribe ejemplo.drawio, lo valida y chequea el layout
"""

from drawio_kit import EDGE, STYLE, Diagram

try:
    from glyph import logo, material

    def icon(name, fallback_glyph, color=None):
        """Logo oficial de `name`; si no existe, el glifo genérico `fallback_glyph`."""
        try:
            return logo(name, color)
        except Exception:
            return material(fallback_glyph, color or "#5f6368")
except Exception as exc:  # sin red -> degradar sin iconos (no romper)
    print(f"(aviso: sin iconos, sigo sin ellos: {exc})")

    def icon(name, fallback_glyph, color=None):
        return None


def istyle(uri, fs=11):
    return (
        (
            f"shape=image;html=1;imageAspect=0;aspect=fixed;verticalLabelPosition=bottom;"
            f"verticalAlign=top;labelPosition=center;align=center;fontColor=#4B5259;"
            f"fontSize={fs};image={uri}"
        )
        if uri
        else STYLE["card"]
    )


d = Diagram()
p = d.page("Ejemplo")
p.node(
    "Arquitectura de ejemplo — plantilla drawio_kit (agnóstica de tecnología)",
    40,
    20,
    900,
    40,
    STYLE["banner"],
)
p.node("Aplicación", 40, 90, 920, 330, STYLE["zone"], ident="app")

# Cada nodo usa el logo oficial de su tecnología; los que no lo tienen, un glifo genérico.
front = p.node("Frontend", 70, 150, 150, 60, STYLE["card"], icon=icon("react", "code", "#61DAFB"))
api = p.node("API", 280, 150, 150, 60, STYLE["card"], icon=icon("fastapi", "api", "#009688"))
agent = p.node(
    "Agente LangChain", 490, 150, 160, 60, STYLE["llm"], icon=icon("langchain", "smart_toy")
)
# Langfuse NO está en las fuentes de logos -> cae al glifo genérico "visibility"
obs = p.node(
    "Langfuse\n(observabilidad)",
    720,
    152,
    160,
    56,
    STYLE["card"],
    icon=icon("langfuse", "visibility", "#1a73e8"),
)
# Componente custom sin logo -> glifo genérico "code"
worker = p.node(
    "Worker propio", 280, 270, 150, 56, STYLE["card"], icon=icon("__custom__", "code", "#cc0000")
)
# Base de datos: cilindro estándar (etiqueta debajo)
db = p.node("PostgreSQL", 520, 280, 120, 50, STYLE["store"])

p.edge(front, api, EDGE["flow"], exit=(1, 0.5), entry=(0, 0.5))
p.edge(api, agent, EDGE["flow"], exit=(1, 0.5), entry=(0, 0.5))
p.edge(agent, obs, EDGE["flow"], exit=(1, 0.5), entry=(0, 0.5))
p.edge(agent, db, EDGE["data"], exit=(0.5, 1), entry=(0.5, 0))
p.edge(api, worker, EDGE["flow"], exit=(0.5, 1), entry=(0.5, 0))

d.write("ejemplo.drawio")
