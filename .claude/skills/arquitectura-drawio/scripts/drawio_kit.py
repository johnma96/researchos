"""drawio_kit — motor mínimo para generar diagramas .drawio en el estilo de la casa.

Portable y sin dependencias externas (solo stdlib). Emite XML mxGraph válido con:
  - IDs únicos por página (prefijo automático),
  - escapado XML y saltos de línea correctos en etiquetas,
  - tokens de estilo de la organización (paleta, cajas, edges),
  - soporte de iconos embebidos (data URI) con el patrón "caja + icono a la izquierda".

Uso típico:

    from drawio_kit import Diagram, STYLE, EDGE
    from glyph import logo                  # logo oficial de CUALQUIER tecnología

    d = Diagram()
    p = d.page("Arquitectura")
    a = p.node("Frontend", 40, 40, 170, 60, STYLE["card"], icon=logo("react"))
    b = p.node("Servicio", 260, 40, 170, 60, STYLE["llm"],  icon=logo("langchain"))
    p.edge(a, b, EDGE["flow"], "procesa", exit=(1, 0.5), entry=(0, 0.5))
    d.write("arquitectura.drawio")

Convenciones de estilo: ver references/estilo.md. Iconos: ver references/iconos.md.
"""

from __future__ import annotations

import collections
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

FONT = "#4B5259"  # texto primario de la casa
BLUE = "#4284F3"  # azul de marca (bordes / edges)

# Radio de esquina fijo (px) para las cajas redondeadas. Con `rounded=1` a secas
# draw.io usa una curva grande (proporcional al tamaño) que puede tapar el texto
# alineado a la izquierda o sacarlo por las esquinas; `absoluteArcSize=1` fija el
# radio en píxeles y `arcSize` lo controla. Ver references/estilo.md.
#   ARC       → cajas de componente: radio muy sutil (1 px).
#   ARC_ZONE  → contenedores/zonas azules punteados: esquina algo más marcada (2 px)
#               para que se note en las cajas grandes.
ARC = "arcSize=6;absoluteArcSize=1;"
ARC_ZONE = "arcSize=6;absoluteArcSize=2;"

# --- Arquetipos de nodo (copiar-pegar tal cual en draw.io con Ctrl+E) ---------
STYLE = {
    "banner": "rounded=0;whiteSpace=wrap;html=1;fillColor=#4DA1F5;strokeColor=none;"
    "shadow=1;fontColor=#ffffff;fontSize=15;fontStyle=1;align=center;verticalAlign=middle;",
    "card": f"rounded=1;{ARC}whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#dddddd;"
    f"shadow=1;strokeWidth=1;fontColor={FONT};fontSize=12;",
    "llm": f"rounded=1;{ARC}whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    f"shadow=1;fontColor={FONT};fontSize=12;",
    "det": f"rounded=1;{ARC}whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
    f"shadow=1;fontColor={FONT};fontSize=12;",
    "warn": f"rounded=1;{ARC}whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;"
    f"shadow=1;fontColor={FONT};fontSize=12;fontStyle=1;",
    "out": f"rounded=1;{ARC}whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
    f"shadow=1;fontColor={FONT};fontSize=12;",
    "gate": "rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;"
    f"shadow=1;fontColor={FONT};fontSize=11;",
    # Almacén/BD: cilindro compacto con la ETIQUETA DEBAJO (no dentro; así la elipse
    # superior no tacha el texto). Tamaño estándar ~120x50. No usar boundedLbl.
    "store": "shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#999999;"
    "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=center;align=center;"
    f"fontColor={FONT};fontSize=10;",
    "doc": "shape=document;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;"
    f"boundedLbl=1;fontColor={FONT};fontSize=11;",
    "user": "shape=mxgraph.ios7.icons.user;html=1;strokeColor=#0080F0;strokeWidth=2;"
    "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=center;align=center;"
    f"fontColor={FONT};fontSize=11;",
    "zone": f"rounded=1;{ARC_ZONE}whiteSpace=wrap;html=1;fillColor=none;strokeColor={BLUE};"
    f"dashed=1;verticalAlign=top;align=left;fontColor={BLUE};fontSize=13;fontStyle=1;"
    "spacingLeft=12;spacingTop=6;",
    "note": "text;whiteSpace=wrap;html=1;fontColor=#9E9E9E;fontSize=11;align=left;",
    "caption": f"text;whiteSpace=wrap;html=1;fontColor={FONT};"
    "fontSize=11;align=center;fontStyle=1;",
    # Icono suelto embebido (image= debe quedar de ÚLTIMO y sin ';' final)
    "_icon": "shape=image;html=1;imageAspect=0;aspect=fixed;image=%s",
}

# --- Edges: la firma de la casa es orthogonal + flowAnimation + theme-aware ----
# TODOS los conectores van ANIMADOS (flowAnimation=1). Es un rasgo obligatorio del
# estilo de la casa; ver references/estilo.md. Las variantes punteadas siguen animadas.
EDGE = {
    "flow": "edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;jettySize=auto;"
    "strokeColor=light-dark(#4284F3,#6671E3);strokeWidth=2;",
    "data": "edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;jettySize=auto;"
    "strokeColor=#66CC00;strokeWidth=2;",
    "warn": "edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;"
    "jettySize=auto;dashed=1;strokeColor=#b85450;strokeWidth=2;",
    "aux": "edgeStyle=orthogonalEdgeStyle;flowAnimation=1;rounded=0;html=1;"
    "jettySize=auto;dashed=1;strokeColor=#9E9E9E;strokeWidth=1;",
}


def _esc(text: str) -> str:
    """Escapa para atributo XML y convierte '\\n' en salto de línea de draw.io."""
    return escape(text or "").replace("\n", "&#xa;")


class Page:
    """Una página (<diagram>) del archivo. No instanciar directo: usar Diagram.page()."""

    def __init__(self, name: str, prefix: str) -> None:
        self.name = name
        self.prefix = prefix
        self.cells: list[str] = []
        self._n = 0

    def _id(self, hint: str) -> str:
        self._n += 1
        return f"{self.prefix}-{hint}-{self._n}"

    def node(self, label, x, y, w, h, style, ident=None, icon=None) -> str:
        """Crea un nodo y devuelve su id. Si `icon` (data URI) se pasa, incrusta
        un icono 22x22 sobre el borde izquierdo y alinea la etiqueta a su derecha."""
        cid = f"{self.prefix}-{ident}" if ident else self._id("n")
        st = style + ("align=left;spacingLeft=32;" if icon else "")
        self.cells.append(
            f'<mxCell id="{cid}" value="{_esc(label)}" style="{escape(st)}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
        if icon:
            iid = self._id("ico")
            iy = y + (h - 22) / 2
            self.cells.append(
                f'<mxCell id="{iid}" value="" style="{escape(STYLE["_icon"] % icon)}" '
                f'vertex="1" parent="1"><mxGeometry x="{x + 6}" y="{iy}" width="22" '
                f'height="22" as="geometry"/></mxCell>'
            )
        return cid

    def edge(
        self, src, dst, style=EDGE["flow"], label="", exit=None, entry=None, points=None
    ) -> str:
        """Conecta dos nodos. `exit`/`entry` son (fx, fy) en [0,1] para fijar el
        punto de anclaje y evitar traslapes (fan-out/gather en peine). `points` es
        una lista de (x, y) absolutos: waypoints por los que se fuerza el ruteo
        (úsalo para sacar una flecha por encima/alrededor y no cruzar nodos)."""
        st = style
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        cid = self._id("e")
        if points:
            pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
            geo = (
                f'<mxGeometry relative="1" as="geometry">'
                f'<Array as="points">{pts}</Array></mxGeometry>'
            )
        else:
            geo = '<mxGeometry relative="1" as="geometry"/>'
        self.cells.append(
            f'<mxCell id="{cid}" value="{_esc(label)}" style="{escape(st)}" edge="1" '
            f'parent="1" source="{src}" target="{dst}">{geo}</mxCell>'
        )
        return cid

    def legend_edge(self, x1: float, x2: float, y: float, style: str) -> str:
        """Muestra de flecha para la leyenda: un edge SIN nodo origen/destino
        (`source`/`target`). mxGraph exige que un edge flotante declare sus
        extremos con `<mxPoint as="sourcePoint">`/`<mxPoint as="targetPoint">`;
        sin ese atributo `as=`, draw.io no sabe dónde dibujar la línea y la
        muestra no se ve (aunque el resto del diagrama sea válido)."""
        cid = self._id("lge")
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="{escape(style)}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1}" y="{y}" as="sourcePoint"/>'
            f'<mxPoint x="{x2}" y="{y}" as="targetPoint"/>'
            f"</mxGeometry></mxCell>"
        )
        return cid

    def _xml(self) -> str:
        body = "".join(self.cells)
        return (
            f'<diagram id="{escape(self.prefix)}" name="{escape(self.name)}">'
            f'<mxGraphModel dx="1400" dy="850" grid="1" gridSize="10" guides="1" '
            f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="1654" pageHeight="1169" math="0" shadow="0">'
            f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root>'
            f"</mxGraphModel></diagram>"
        )


class Diagram:
    """Archivo .drawio con una o más páginas."""

    def __init__(self) -> None:
        self.pages: list[Page] = []

    def page(self, name: str) -> Page:
        p = Page(name, f"p{len(self.pages) + 1}")
        self.pages.append(p)
        return p

    def xml(self) -> str:
        inner = "".join(p._xml() for p in self.pages)
        return (
            f'<mxfile host="app.diagrams.net" agent="drawio-kit" version="24.0.0">{inner}</mxfile>'
        )

    def write(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.xml())
        self.validate(path)
        size = len(self.xml())
        print(f"escrito: {path}  ({size} bytes, {size // 1024} KB)")
        if size > 500_000:
            print("  ⚠️  >500 KB: el pre-commit típico lo bloquea. Reduce iconos embebidos.")
        try:  # chequeo de legibilidad (no fatal)
            from check_layout import summarize

            rep = summarize(path)
            if rep["total"]:
                print(f"  ⚠️  check_layout: {rep['total']} posibles traslapes -> {rep['por_tipo']}")
                print(f"      detalle: python scripts/check_layout.py {path}")
            else:
                print("  ✓ check_layout: sin traslapes detectados")
        except Exception as exc:
            print(f"  (check_layout no ejecutado: {exc})")

    @staticmethod
    def validate(path: str) -> None:
        """Falla ruidosamente si el XML es inválido, hay IDs duplicados o edges rotos."""
        t = ET.parse(path)  # lanza si no es XML bien formado
        ids = [c.get("id") for c in t.iter("mxCell") if c.get("id") not in ("0", "1")]
        dups = [k for k, v in collections.Counter(ids).items() if v > 1]
        if dups:
            raise ValueError(f"IDs duplicados: {dups}")
        allids = {c.get("id") for c in t.iter("mxCell")}
        broken = [
            (c.get("id"), k, c.get(k))
            for c in t.iter("mxCell")
            if c.get("edge") == "1"
            for k in ("source", "target")
            if c.get(k) and c.get(k) not in allids
        ]
        if broken:
            raise ValueError(f"edges con extremos inexistentes: {broken}")
