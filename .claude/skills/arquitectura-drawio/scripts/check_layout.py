"""check_layout — linter de legibilidad para diagramas .drawio.

Detecta lo que hace ilegible un diagrama y que draw.io no valida por ti:
  1. NODOS superpuestos (cajas/iconos que se pisan).
  2. ETIQUETAS que invaden otro nodo (incluye la etiqueta al pie de un icono
     que cae sobre el nodo de abajo).
  3. FLECHAS que cruzan un nodo que no es su origen/destino (heurístico: ruteo
     ortogonal aproximado según exit/entry).
  4. ETIQUETAS DE FLECHA que caen dentro de un nodo ajeno.
  5. ETIQUETAS DE FLECHA sobre el TÍTULO de un contenedor/zona: el contenedor se
     excluye de (3) y (4) porque contiene a otros por diseño, pero su título vive
     en una banda de ~26 px arriba y ahí sí se pisa (bug real: el título quedó
     como «infrastructure/ — SDK[Atom XML]erno»).
  6. ETIQUETAS DE FLECHA ENCIMADAS entre sí: varios edges que cruzan el mismo
     carril colocan su etiqueta a la misma altura y se solapan.
  7. TEXTO QUE DESBORDA su caja: la etiqueta necesita más líneas de las que caben,
     así que draw.io la recorta o la derrama fuera del borde.
  8. NODOS FUERA DEL ÁREA DE PÁGINA (pageWidth/pageHeight): se ven en el lienzo
     pero se pierden al exportar a PNG/PDF con el recorte de página.
  9. CAJAS SOBREDIMENSIONADAS y 10. ETIQUETAS DE CAJA MUY LARGAS: no son traslapes,
     son economía. Una caja el doble de grande de lo normal gasta el espacio de tres
     componentes, y eso baja el número de nodos hasta dejar el diagrama incompleto
     para un lector técnico. Se reportan como mediana por página, no caja por caja.
 11. ROJO DISPERSO: el rojo marca deuda; concentrado en una zona rotulada se lee como
     sección, rociado sobre el flujo hace que el sistema entero parezca averiado.

Las PALABRAS PEGADAS ("dependiendo deinfrastructure/") no se detectan aquí sino en
`check_labels.py`, que lee el SCRIPT generador: sobre el .drawio ya solo queda texto
plano y no hay forma fiable de distinguir un error de un identificador CamelCase.

Es una heurística (el ruteo real de draw.io difiere), pero atrapa los problemas
gruesos de traslape. Los contenedores/zonas se excluyen de (1) a (4) por diseño;
para las etiquetas de flecha, la posición se estima sobre la polilínea ruteada
(incluidos los waypoints), no sobre el punto medio recto origen-destino.

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
ZONE_TITLE_H = 26  # banda superior de un contenedor donde se dibuja su título
ZONE_TITLE_CW = 7.4  # ancho estimado por carácter del título de un contenedor (fontSize 13, bold)
EDGE_LBL_CW = 6.4  # ancho estimado por carácter de una etiqueta de flecha
EDGE_LBL_H = 16  # alto estimado de una línea de etiqueta de flecha
# Métricas de texto dentro de una caja, por fontSize: (ancho medio de carácter, alto de línea).
# Son estimaciones de la fuente por defecto de draw.io (Helvetica); van holgadas a propósito
# para no llenar el reporte de falsos positivos por un par de píxeles.
TEXT_METRICS = {10: (5.5, 14), 11: (6.0, 15), 12: (6.5, 16), 13: (7.2, 17), 15: (8.2, 19)}
BOX_PAD = 16  # padding horizontal dentro de una caja con borde
ICON_PAD = 32  # desplazamiento extra que mete node(icon=) con spacingLeft=32

# ── Estándar de economía de caja (references/estilo.md) ──────────────────────────────
# Medido sobre los diagramas de referencia de la organización: caja de componente con
# mediana 176-200 x 52-56 px y etiqueta de 30-45 caracteres. Cajas más grandes con más
# texto no añaden información: gastan el espacio de tres componentes y bajan el número de
# nodos, que es lo que vuelve un diagrama incompleto para un lector técnico. Los umbrales
# van por encima del máximo de la referencia para avisar solo cuando la desviación es real.
BOX_W_MAX, BOX_H_MAX = 220, 70  # mediana por página a partir de la cual se avisa
BOX_LBL_MAX = 55  # mediana de caracteres por etiqueta de caja
# Caja suelta tan grande que se reporta aparte. Holgado a propósito: una rejilla de ítems
# de deuda o de notas rotuladas legítimamente usa cajas anchas, y ya la pesca la mediana.
BOX_W_ATIP, BOX_H_ATIP = 420, 130
BANNER_FILL = "#4da1f5"  # relleno del banner de la casa (no es un componente)
# Rojo = deuda/alerta. Concentrado en una zona rotulada se lee como sección; rociado sobre
# el flujo hace que el sistema entero parezca averiado. Se avisa por encima de esta fracción.
RED_MAX_FRAC = 0.25
RED_FILLS = {"#f8cecc", "#fdf3f3"}
RE_ZONA_DEUDA = re.compile(r"deuda|debt|pendiente|sin implementar|no implementad", re.I)


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
    """¿Es una zona/contenedor (contiene otros nodos por diseño)?

    Primero el marcador explícito que pone `Page.zone()`; la heurística vieja queda
    solo como respaldo para XML escrito a mano. Confiar únicamente en la heurística
    excluía en silencio de TODOS los chequeos a cualquier anotación punteada sin relleno."""
    if d.get("kitRole") == "zone":
        return True
    return "dashed" in d and d.get("fillColor") == "none" and d.get("shape", "") == ""


def _text_overflows(cell, d, geo) -> tuple[bool, int, int]:
    """¿La etiqueta necesita más alto del que tiene la caja? -> (desborda, necesita, hay).

    Las formas con `verticalLabelPosition=bottom` (cilindros, actores) dibujan el texto
    FUERA de la caja, así que nunca desbordan por dentro."""
    _, _, w, h = geo
    label = _label(cell).replace("&#xa;", "\n")
    if not label.strip() or d.get("verticalLabelPosition") == "bottom":
        return (False, 0, int(h))
    cw, lh = TEXT_METRICS.get(int(d.get("fontSize", 12)), (6.5, 16))
    es_texto_suelto = d.get("_bare_text", False)  # nodo `text;` sin borde: no lleva padding
    pad = (0 if es_texto_suelto else BOX_PAD) + (ICON_PAD if d.get("spacingLeft") == "32" else 0)
    util = max(w - pad, 40)
    lineas = sum(max(1, -(-len(ln) * cw // util)) for ln in label.split("\n"))
    necesita = int(lineas * lh + (0 if es_texto_suelto else 8))
    return (necesita > h, necesita, int(h))


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


def _path_midpoint(pts):
    """Punto al 50 % de la LONGITUD de la polilínea ruteada — que es donde draw.io
    dibuja la etiqueta de un edge con `relative=1`. Usar el punto medio recto
    origen→destino (como se hacía antes) da una posición muy distinta en cuanto el
    edge tiene waypoints, y deja pasar etiquetas que en el render sí se pisan."""
    segs = [
        (pts[i], pts[i + 1], abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]))
        for i in range(len(pts) - 1)
    ]
    total = sum(s[2] for s in segs)
    if total == 0:
        return pts[0]
    walked = 0.0
    for (ax, ay), (bx, by), ln in segs:
        if walked + ln >= total / 2:
            t = 0 if ln == 0 else (total / 2 - walked) / ln
            return (ax + (bx - ax) * t, ay + (by - ay) * t)
        walked += ln
    return pts[-1]


def _es_componente(d: dict) -> bool:
    """¿Es una caja de componente del diagrama (y no cromo: banner, zona, leyenda, nota)?

    Todos los arquetipos de componente de `STYLE` llevan `shadow=1`; el cromo no. Los
    elementos que reutilizan un estilo de arquetipo pero no son componentes (el banner,
    los chips de la leyenda) van marcados con `kitRole`, así que basta con excluirlos.
    El color de banner de la casa se reconoce además por su relleno, para que los diagramas
    hechos antes del marcador —o escritos a mano copiando `estilo.md`— tampoco lo cuenten."""
    return (
        d.get("shadow") == "1"
        and not d.get("kitRole")
        and not d.get("shape")
        and not d.get("_bare_text")
        and (d.get("fillColor") or "").lower() != BANNER_FILL
    )


def _mediana(xs):
    return sorted(xs)[len(xs) // 2] if xs else 0


def _edge_label_box(text: str, mid):
    """Caja aproximada que ocupa la etiqueta de una flecha, centrada en `mid`."""
    lines = text.split("\n") or [""]
    w = max(len(ln) for ln in lines) * EDGE_LBL_CW
    h = EDGE_LBL_H * len(lines)
    return (mid[0] - w / 2, mid[1] - h / 2, w, h)


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
                d["_bare_text"] = style.startswith("text;")
                sty[gid] = d
                val[gid] = c
                kind[gid] = (
                    "container"
                    if _is_container(d)
                    else ("text" if style.startswith("text;") else "node")
                )

        # 7 y 8: texto que no cabe en su caja / nodos fuera del área de página
        modelo = diag.find("mxGraphModel")
        pw = float(modelo.get("pageWidth", 1654)) if modelo is not None else 1654
        ph = float(modelo.get("pageHeight", 1169)) if modelo is not None else 1169
        for gid, (gx, gy, gw, gh) in geo.items():
            if gx < 0 or gy < 0 or gx + gw > pw or gy + gh > ph:
                issues.append(
                    {
                        "tipo": "nodo-fuera-de-pagina",
                        "pagina": page,
                        "detalle": f"«{_label(val[gid])[:24]}» en ({gx:.0f},{gy:.0f}) "
                        f"{gw:.0f}x{gh:.0f} excede {pw:.0f}x{ph:.0f}",
                    }
                )
            if kind[gid] == "container":
                continue
            desborda, necesita, hay = _text_overflows(val[gid], sty[gid], geo[gid])
            if desborda:
                issues.append(
                    {
                        "tipo": "texto-desborda-caja",
                        "pagina": page,
                        "detalle": f"«{_label(val[gid])[:24]}» necesita ~{necesita} px "
                        f"de alto y tiene {hay}",
                    }
                )

        # 9, 10 y 11: economía de caja y uso del rojo (agregados por página, no por caja,
        # para que el reporte sea accionable en vez de una lista de 50 líneas).
        comps = [i for i in geo if _es_componente(sty[i])]
        if comps:
            anchos = [geo[i][2] for i in comps]
            altos = [geo[i][3] for i in comps]
            largos = [len(_label(val[i]).replace("&#xa;", "\n")) for i in comps]
            mw, mh, ml = _mediana(anchos), _mediana(altos), _mediana(largos)
            if mw > BOX_W_MAX or mh > BOX_H_MAX:
                issues.append(
                    {
                        "tipo": "caja-sobredimensionada",
                        "pagina": page,
                        "detalle": f"caja de componente mediana {mw:.0f}x{mh:.0f}; el estándar "
                        f"de la casa es ~180x56. Con cajas así caben {len(comps)} componentes "
                        f"donde cabrían ~{int(len(comps) * (mw * mh) / (180 * 56))}",
                    }
                )
            if ml > BOX_LBL_MAX:
                issues.append(
                    {
                        "tipo": "etiqueta-de-caja-muy-larga",
                        "pagina": page,
                        "detalle": f"mediana de {ml} caracteres por caja (estándar 30-45); "
                        f"lleva el detalle a la etiqueta de flecha, a la zona o a la nota al pie",
                    }
                )
            for i in comps:
                _, _, w, h = geo[i]
                if w > BOX_W_ATIP or h > BOX_H_ATIP:
                    issues.append(
                        {
                            "tipo": "caja-sobredimensionada",
                            "pagina": page,
                            "detalle": f"«{_label(val[i])[:24]}» mide {w:.0f}x{h:.0f} — "
                            f"¿es un componente o una nota disfrazada?",
                        }
                    )
            zonas_deuda = [
                geo[i]
                for i in geo
                if kind[i] == "container" and RE_ZONA_DEUDA.search(_label(val[i]) or "")
            ]
            rojos = [i for i in comps if (sty[i].get("fillColor") or "").lower() in RED_FILLS]
            sueltos = [
                i
                for i in rojos
                if not any(_inter(geo[i], z) > 0.5 * geo[i][2] * geo[i][3] for z in zonas_deuda)
            ]
            if sueltos and len(sueltos) > RED_MAX_FRAC * len(comps):
                issues.append(
                    {
                        "tipo": "rojo-disperso",
                        "pagina": page,
                        "detalle": f"{len(sueltos)} de {len(comps)} cajas en rojo fuera de una "
                        f"zona de deuda ({len(sueltos) / len(comps) * 100:.0f}%): el flujo entero "
                        f"se lee como averiado. Concentra el rojo en una zona rotulada",
                    }
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

        edge_labels: list[tuple[str, tuple]] = []
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
            if _label(c).strip():
                text = _label(c).replace("&#xa;", "\n")
                mid = _path_midpoint(pts)
                box = _edge_label_box(text, mid)
                edge_labels.append((text, box))
                for gid in geo:
                    # OJO: aquí NO se excluyen `s` ni `tg`. La etiqueta de una flecha se
                    # dibuja en el punto medio del recorrido, que casi siempre cae en el
                    # HUECO entre sus dos extremos; si ese hueco es más angosto que la
                    # etiqueta, esta se monta sobre las cajas que conecta. Es el traslape
                    # más frecuente de todos y excluir los extremos lo hacía invisible.
                    gx, gy, gw, gh = geo[gid]
                    if kind[gid] == "container":
                        # el cuerpo del contenedor es zona de paso legítima; su TÍTULO no.
                        # El título es corto y va alineado a la izquierda: acotar el rect al
                        # ancho real del texto evita falsos positivos en el resto de la banda.
                        title = _label(val[gid])
                        tw = min(gw, len(title) * ZONE_TITLE_CW + 24)
                        if title and _inter(box, (gx, gy, tw, ZONE_TITLE_H)) > 0:
                            issues.append(
                                {
                                    "tipo": "etiqueta-flecha-sobre-titulo-zona",
                                    "pagina": page,
                                    "detalle": f"etiqueta «{text[:16]}» pisa el título "
                                    f"«{_label(val[gid])[:26]}»",
                                }
                            )
                    # Se compara la CAJA de la etiqueta contra el nodo, no solo su punto
                    # medio: una etiqueta de 130 px centrada justo en el borde de una caja
                    # la invade sin que su centro llegue a caer dentro.
                    elif _inter(box, (gx, gy, gw, gh)) > MIN_AREA:
                        propio = " (extremo de la propia flecha: el hueco es muy angosto)"
                        issues.append(
                            {
                                "tipo": "etiqueta-flecha-sobre-nodo",
                                "pagina": page,
                                "detalle": f"etiqueta «{text[:16]}» invade "
                                f"«{_label(val[gid])[:20]}»"
                                f"{propio if gid in (s, tg) else ''}",
                            }
                        )

        # 6: etiquetas de flecha encimadas entre sí (varios edges en el mismo carril)
        for i, (ta, ba) in enumerate(edge_labels):
            for tb, bb in edge_labels[i + 1 :]:
                if _inter(ba, bb) > MIN_AREA:
                    issues.append(
                        {
                            "tipo": "etiquetas-flecha-encimadas",
                            "pagina": page,
                            "detalle": f"«{ta[:20]}» ∩ «{tb[:20]}»",
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
    # Problemas duros -> exit !=0 (útil como gate en iteración). "nodo-fuera-de-pagina" entra
    # aquí porque es geometría exacta, no heurística: el nodo se pierde al exportar.
    # "texto-desborda-caja" queda fuera a propósito: la métrica de texto es estimada y no
    # conviene que un par de píxeles bloqueen la iteración — pero hay que atenderlo igual.
    hard = {
        "nodos-superpuestos",
        "flecha-cruza-nodo",
        "nodo-fuera-de-pagina",
        "etiqueta-flecha-sobre-nodo",
    }
    sys.exit(1 if any(it["tipo"] in hard for it in res["issues"]) else 0)
