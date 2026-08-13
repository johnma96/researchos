"""Plantilla de uso de drawio_kit — AGNÓSTICA de tecnología y MULTIPÁGINA.

Copia este patrón para cualquier stack (JS, Python, LangChain, ADK, cloud, ...). Muestra
las dos formas de página que cubren casi todo diagrama de arquitectura, y que conviene NO
mezclar en el mismo lienzo (ver el criterio de partición en SKILL.md):

    página 1 · vista ESTÁTICA  -> qué existe y quién depende de quién (capas, zonas)
    página 2 · vista DINÁMICA  -> qué pasa cuando ocurre X (secuencia numerada)

Si tu repositorio tiene un solo flujo y pocos componentes, una sola página es la respuesta
correcta: borra la segunda. Partir de más también hace daño.

    python ejemplo.py            # escribe ejemplo.drawio, lo valida y chequea el layout
"""

from drawio_kit import EDGE, STYLE, Diagram
from glyph import icon  # logo oficial a color -> glifo genérico -> None si no hay red

# Arquetipos usados en este ejemplo. Mantén el mapeo color->significado estable en todo
# el archivo: es lo que la leyenda promete al lector.
CARD, LLM, DET, STORE, ZONE = (
    STYLE["card"],
    STYLE["llm"],
    STYLE["det"],
    STYLE["store"],
    STYLE["zone"],
)

LEG_EDGES = [
    (EDGE["data"], "Flujo de datos — lo que se transforma y avanza al paso siguiente"),
    (EDGE["flow"], "Orquestación / control — quién invoca o ejecuta a quién"),
    (EDGE["aux"], "Consumo de un recurso o servicio compartido (lectura / escritura)"),
]
LEG_CHIPS = [
    (DET, "Paso determinista (lógica propia)"),
    (LLM, "Servicio LLM o sistema externo"),
    (CARD, "Adapter concreto sobre un SDK"),
    (STORE, "Almacén de datos"),
]
LEG_NOTA = (
    "Las flechas van animadas e indican el sentido del flujo. Los números marcan el orden de "
    "ejecución: el lector sigue la numeración y no necesita trazar las flechas. Cada caja lleva "
    "el logo oficial de su tecnología; las que no tienen logo usan un glifo genérico."
)

AG = icon("langchain", "smart_toy")
DB = icon("postgresql", "database")

d = Diagram()

# ── Página 1 · vista estática: qué existe y cómo se agrupa ────────────────────
p1 = d.page("1 · Componentes")
p1.banner(
    "Ejemplo — vista estática de componentes",
    "Qué existe y en qué capa vive. El recorrido en tiempo de ejecución está en la "
    "página «2 · Flujo».",
)
p1.zone("frontera del sistema", 40, 100, 1574, 210)
p1.node("Frontend\nReact", 80, 150, 190, 56, CARD, icon=icon("react", "code"))
p1.node("API\nFastAPI", 330, 150, 190, 56, CARD, icon=icon("fastapi", "api"))
p1.node("Agente\nLangChain", 580, 150, 190, 56, LLM, icon=icon("langchain", "smart_toy"))
# Langfuse no está en las fuentes de logos -> cae al glifo genérico "visibility"
p1.node("Langfuse\nobservabilidad", 830, 150, 190, 56, CARD, icon=icon("langfuse", "visibility"))
p1.node("PostgreSQL", 1090, 156, 150, 44, STORE)
p1.legend(370, LEG_EDGES, LEG_CHIPS, LEG_NOTA)

# ── Página 2 · vista dinámica: qué pasa cuando llega una petición ─────────────
# Secuencia numerada de izquierda a derecha; si no cupiera, se sigue en una fila de
# abajo bajando por la MISMA columna (serpentina), así ninguna flecha retrocede.
p2 = d.page("2 · Flujo")
p2.banner(
    "Ejemplo — flujo de una petición",
    "Cuatro pasos numerados. El color de cada caja indica su tipo (ver leyenda).",
)
s1 = p2.node("①  Frontend\nenvía la petición", 60, 140, 200, 56, CARD, icon=icon("react", "code"))
s2 = p2.node("②  API\nvalida y enruta", 380, 140, 200, 56, CARD, icon=icon("fastapi", "api"))
s3 = p2.node("③  Agente\nrazona y decide", 700, 140, 200, 56, LLM, icon=AG)
s4 = p2.node("④  PostgreSQL\npersiste el resultado", 1020, 140, 200, 56, DET, icon=DB)
p2.edge(s1, s2, EDGE["flow"], "POST /consulta", exit=(1, 0.5), entry=(0, 0.5))
p2.edge(s2, s3, EDGE["flow"], exit=(1, 0.5), entry=(0, 0.5))
p2.edge(s3, s4, EDGE["data"], "resultado", exit=(1, 0.5), entry=(0, 0.5))
p2.legend(300, LEG_EDGES, LEG_CHIPS, LEG_NOTA)

# En un repo real la salida por defecto es docs/architecture.drawio (ver SKILL.md);
# aquí se escribe al directorio actual por ser solo una plantilla de demostración.
d.write("ejemplo.drawio")
