"""gcp_icon — resuelve iconos OFICIALES de Google Cloud a data URI para draw.io.

Descarga los sets públicos de Google (sin login), extrae el SVG del producto,
lo convierte a data URI URL-encoded y lo devuelve. Sin dependencias externas
(solo stdlib). Cachea los ZIP en el temp del sistema para no re-descargar.

CLI:
    python gcp_icon.py vertex_ai              # imprime el data URI
    python gcp_icon.py --list                 # lista los nombres disponibles
    python gcp_icon.py cloud vision           # match difuso por palabras

Como librería:
    from gcp_icon import data_uri
    uri = data_uri("cloud_dlp")               # -> "data:image/svg+xml,%3Csvg..."

Fuente: https://cloud.google.com/icons (descargas públicas de Google).
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile

# ZIP oficiales. 'core' = estilo actual (productos insignia); 'legacy' = set
# completo (216 SVG, incluye Document AI, Vision, DLP, etc.).
ZIPS = {
    "core": "https://services.google.com/fh/files/misc/core-products-icons.zip",
    "legacy": "https://services.google.com/fh/files/misc/google-cloud-legacy-icons.zip",
}
CACHE = os.path.join(tempfile.gettempdir(), "gcp_drawio_icons")


def _norm(s: str) -> str:
    """Normaliza un nombre para comparar: minúsculas, solo alfanumérico."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _ensure() -> dict[str, bytes]:
    """Descarga (si hace falta) y devuelve {nombre_svg_sin_ext: bytes_svg}.
    Prefiere el SVG de 'core' sobre 'legacy' cuando el mismo producto está en ambos."""
    os.makedirs(CACHE, exist_ok=True)
    svgs: dict[str, bytes] = {}
    for key in ("legacy", "core"):  # core al final => pisa a legacy (estilo actual gana)
        local = os.path.join(CACHE, f"{key}.zip")
        if not os.path.exists(local):
            req = urllib.request.Request(ZIPS[key], headers={"User-Agent": "drawio-kit"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            with open(local, "wb") as fh:
                fh.write(data)
        with zipfile.ZipFile(local) as z:
            for info in z.infolist():
                if info.filename.lower().endswith(".svg"):
                    base = os.path.splitext(os.path.basename(info.filename))[0]
                    # normaliza variantes: "CloudRun-512-color-rgb" -> "cloudrun"
                    clean = re.sub(r"[-_](512|color|rgb|blue|dark|light)\b", "", base, flags=re.I)
                    svgs[_norm(clean)] = z.read(info.filename)
    return svgs


def _find(name: str, svgs: dict[str, bytes]) -> bytes:
    key = _norm(name)
    if key in svgs:
        return svgs[key]
    # match difuso: todas las palabras del query aparecen en el nombre del svg
    words = [w for w in re.split(r"[^a-z0-9]+", name.lower()) if w]
    cands = [k for k in svgs if all(w in k for w in words)]
    if len(cands) == 1:
        return svgs[cands[0]]
    if not cands:
        raise KeyError(f"icono no encontrado: {name!r}. Prueba `--list`.")
    raise KeyError(f"{name!r} es ambiguo: {sorted(cands)[:10]}")


def data_uri(name: str) -> str:
    """Devuelve el data URI URL-encoded del SVG del producto (embebible en draw.io)."""
    svg = _find(name, _ensure()).decode("utf-8")
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


def available() -> list[str]:
    return sorted(_ensure().keys())


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
    elif args[0] == "--list":
        for n in available():
            print(n)
    else:
        print(data_uri(" ".join(args)))
