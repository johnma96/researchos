"""check_labels — detecta etiquetas mal partidas en el SCRIPT que genera un diagrama.

Las etiquetas de un diagrama son textos largos y chocan con el límite de columnas del
repo (ruff/flake8). Al partirlas en concatenación implícita es fácil perder el espacio
final de un trozo, y draw.io las muestra pegadas:

    "... dependiendo de "   "infrastructure/"  ->  "dependiendo de infrastructure/"   OK
    "... dependiendo de"    "infrastructure/"  ->  "dependiendo deinfrastructure/"    MAL

Es un fallo invisible: el XML es válido, el layout no se traslapa y el linter de
legibilidad pasa; solo se ve al mirar el diagrama renderizado. Este chequeo lo atrapa en
el fuente, que es donde la información existe (sobre el .drawio ya solo hay texto plano y
`deinfrastructure` no se distingue de un identificador legítimo).

CLI:
    python check_labels.py build_mi_diagrama.py       # sale !=0 si encuentra algo

Como librería:
    from check_labels import check
    problemas = check("build_mi_diagrama.py")   # -> [(línea, izquierda, derecha)]
"""

from __future__ import annotations

import pathlib
import re
import sys

# Una línea que es EXACTAMENTE un literal de string (posiblemente con coma final).
_LITERAL = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"(,?)\s*$')

# Finales/inicios donde la concatenación sin espacio es intencional y correcta:
# un token de estilo (`fillColor=#fff;`), un salto de línea explícito, un guion de
# palabra partida, o el trozo derecho empieza por puntuación.
_FIN_OK = (" ", "\\n", "-", "(", ";", ":", "/", "=")
_INI_OK = (" ", "\\n", ")", ",", ".", ";", ":", "/")


def check(path: str) -> list[tuple[int, str, str]]:
    lineas = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    fallos: list[tuple[int, str, str]] = []
    for i in range(len(lineas) - 1):
        a, b = _LITERAL.match(lineas[i]), _LITERAL.match(lineas[i + 1])
        if not (a and b):
            continue
        if a.group(2):  # coma final -> son argumentos distintos, no se concatenan
            continue
        izq, der = a.group(1), b.group(1)
        if not izq or not der:
            continue
        if izq.endswith(_FIN_OK) or der.startswith(_INI_OK):
            continue
        fallos.append((i + 1, izq, der))
    return fallos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python check_labels.py <script_generador>.py [...]")
        sys.exit(2)
    total = 0
    for archivo in sys.argv[1:]:
        for linea, izq, der in check(archivo):
            total += 1
            print(f"{archivo}:{linea}  «…{izq[-24:]}» + «{der[:24]}…»")
            print(f"{' ' * len(archivo)}   -> quedaría «{izq[-14:]}{der[:14]}»")
    if total:
        print(f"\n⚠ {total} etiqueta(s) partida(s) sin espacio de separación.")
        print('  Añade el espacio al FINAL del trozo izquierdo: "…de " "infrastructure/"')
        sys.exit(1)
    print("✓ check_labels: etiquetas bien partidas")
