"""check_layout — linter de legibilidad para diagramas .drawio.

Detecta lo que hace ilegible un diagrama y que draw.io no valida por ti:
  1. NODOS superpuestos (cajas/iconos que se pisan).
  2. ETIQUETAS que invaden otro nodo (incluye la etiqueta al pie de un icono
     que cae sobre el nodo de abajo).
  3. FLECHAS que cruzan un nodo que no es su origen/destino (heurístico: ruteo
     ortogonal aproximado según exit/entry).
  4. ETIQUETAS DE FLECHA que caen dentro de un nodo ajeno.

Es una heurística (el ruteo real de draw.io difiere), pero atrapa los problemas
gruesos de traslape. Los contenedores/zonas se excluyen (contienen a otros por diseño).

CLI:
    python check_layout.py archivo.drawio          # reporta y sale !=0 si hay traslapes duros

Como librería:
    from check_layout import check
    issues = check("archivo.drawio")   # -> lista de dicts {tipo, pagina, detalle}
"""

from __future__ import annotations

import re
import sys
from xml.etree import ElementTree as ET

MIN_AREA = 90  # px² de intersección para contar un traslape de cajas
LABEL_LH = 15  # alto estimado por línea de etiqueta al pie de un icono


def _sk(style: str) -> dict:
    d = {}
    for t in (style or "").split(";"):
        if "=" in t:
            k, v = t.split("=", 1)
            d[k] = v
        elif t:
            d[t] = ""
    return d


def _is_container(d: dict) -> bool:
    return "dashed" in d and d.get("fillColor") == "none" and d.get("shape", "") == ""


def _label(cell) -> str:
    return re.sub(r"<[^>]+>", "", cell.get("value") or "")


def _footprint(cell, d, geo):
    """(x,y,w,h) del nodo, ampliado con la banda de etiqueta al pie si es un icono
    con verticalLabelPosition=bottom (esa etiqueta ocupa espacio bajo el icono)."""
    x, y, w, h = geo
    label = _label(cell)
    if label and d.get("verticalLabelPosition") == "bottom":
        lines = label.count("\n") + (cell.get("value") or "").count("&#xa;") + 1
        lw = max(w * 1.7, 90)
        lh = LABEL_LH * lines
        nx = x + w / 2 - lw / 2
        return (min(x, nx), y, max(w, lw), h + lh)
    return (x, y, w, h)


def _inter(a, b) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return ix * iy


def _seg_hits_rect(p, q, rect, margin=2.0) -> bool:
    """¿El segmento axis-aligned p-q entra en rect (con margen para no contar roces)?"""
    rx, ry, rw, rh = rect[0] + margin, rect[1] + margin, rect[2] - 2 * margin, rect[3] - 2 * margin
    if rw <= 0 or rh <= 0:
        return False
    x1, y1 = p
    x2, y2 = q
    if abs(y1 - y2) < 0.5:  # horizontal
        lo, hi = sorted((x1, x2))
        return ry <= y1 <= ry + rh and lo < rx + rw and hi > rx
    if abs(x1 - x2) < 0.5:  # vertical
        lo, hi = sorted((y1, y2))
        return rx <= x1 <= rx + rw and lo < ry + rh and hi > ry
    return False


def _route(p0, p1, ex):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    if ex in (0.0, 1.0):  # sale horizontal
        return [p0, (mx, p0[1]), (mx, p1[1]), p1]
    return [p0, (p0[0], my), (p1[0], my), p1]


def check(path: str) -> list[dict]:
    t = ET.parse(path)
    issues: list[dict] = []
    for diag in t.iter("diagram"):
        page = diag.get("name", "?")
        geo, sty, val, kind = {}, {}, {}, {}
        for c in diag.iter("mxCell"):
            g = c.find("mxGeometry")
            if c.get("vertex") == "1" and g is not None and g.get("width"):
                style = c.get("style", "")
                # icono-overlay decorativo (kit node(icon=): imagen sin etiqueta sobre
                # una tarjeta) -> no es un nodo propio, no cuenta para traslapes.
                if "shape=image" in style and not (c.get("value") or "").strip():
                    continue
                gid = c.get("id")
                geo[gid] = tuple(float(g.get(k, 0)) for k in ("x", "y", "width", "height"))
                d = _sk(style)
                sty[gid] = d
                val[gid] = c
                kind[gid] = (
                    "container"
                    if _is_container(d)
                    else ("text" if style.startswith("text;") else "node")
                )

        # 1 y 2: traslape de nodos / etiquetas (excluye contenedores)
        solid = [i for i in geo if kind[i] != "container"]
        fp = {i: _footprint(val[i], sty[i], geo[i]) for i in solid}
        for i, a in enumerate(solid):
            for b in solid[i + 1 :]:
                area = _inter(fp[a], fp[b])
                if area > MIN_AREA:
                    ta, tb = kind[a], kind[b]
                    typ = "etiqueta-sobre-nodo" if "text" in (ta, tb) else "nodos-superpuestos"
                    issues.append(
                        {
                            "tipo": typ,
                            "pagina": page,
                            "detalle": f"«{_label(val[a])[:22]}» ∩ «{_label(val[b])[:22]}» "
                            f"(~{int(area)} px²)",
                        }
                    )

        # 3 y 4: flechas que cruzan nodos / etiquetas de flecha dentro de un nodo
        def point(gid, fx, fy, geo=geo):  # geo=geo: enlaza el geo de ESTA página (B023)
            x, y, w, h = geo[gid]
            return x + fx * w, y + fy * h

        for c in diag.iter("mxCell"):
            if c.get("edge") != "1":
                continue
            s, tg = c.get("source"), c.get("target")
            if s not in geo or tg not in geo:
                continue
            d = _sk(c.get("style", ""))
            ex = float(d.get("exitX", 0.5))
            p0 = point(s, ex, float(d.get("exitY", 0.5)))
            p1 = point(tg, float(d.get("entryX", 0.5)), float(d.get("entryY", 0.5)))
            wps = [
                (float(mp.get("x")), float(mp.get("y")))
                for mp in c.findall("./mxGeometry/Array/mxPoint")
            ]
            pts = [p0, *wps, p1] if wps else _route(p0, p1, ex)
            for gid in geo:
                if gid in (s, tg) or kind[gid] == "container":
                    continue
                if any(_seg_hits_rect(pts[k], pts[k + 1], geo[gid]) for k in range(len(pts) - 1)):
                    issues.append(
                        {
                            "tipo": "flecha-cruza-nodo",
                            "pagina": page,
                            "detalle": f"edge «{_label(val[s])[:16]}»→«{_label(val[tg])[:16]}» "
                            f"cruza «{_label(val[gid])[:20]}»",
                        }
                    )
            if c.get("value"):
                mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
                for gid in geo:
                    if gid in (s, tg) or kind[gid] == "container":
                        continue
                    gx, gy, gw, gh = geo[gid]
                    if gx <= mid[0] <= gx + gw and gy <= mid[1] <= gy + gh:
                        issues.append(
                            {
                                "tipo": "etiqueta-flecha-sobre-nodo",
                                "pagina": page,
                                "detalle": f"etiqueta «{_label(c)[:16]}» "
                                f"cae en «{_label(val[gid])[:20]}»",
                            }
                        )
    return issues


def summarize(path: str) -> dict:
    issues = check(path)
    counts: dict[str, int] = {}
    for it in issues:
        counts[it["tipo"]] = counts.get(it["tipo"], 0) + 1
    return {"total": len(issues), "por_tipo": counts, "issues": issues}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python check_layout.py archivo.drawio")
        sys.exit(2)
    res = summarize(sys.argv[1])
    if not res["total"]:
        print("✓ check_layout: sin traslapes detectados")
        sys.exit(0)
    print(f"⚠ check_layout: {res['total']} posibles problemas de legibilidad")
    for tipo, n in sorted(res["por_tipo"].items(), key=lambda kv: -kv[1]):
        print(f"  {n:3}  {tipo}")
    print("---")
    for it in res["issues"][:40]:
        print(f"  [{it['tipo']}] {it['detalle']}")
    # traslapes duros -> exit !=0 (útil como gate en iteración)
    hard = {"nodos-superpuestos", "flecha-cruza-nodo"}
    sys.exit(1 if any(it["tipo"] in hard for it in res["issues"]) else 0)
