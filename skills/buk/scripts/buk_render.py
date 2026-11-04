#!/usr/bin/env python3
"""Les yeux de buk : rend un flash en images pour que Claude le regarde et le critique.

Produit, dans <flash>_rendu/ :
  apercu.png      le flash couleur sur peau (taille confortable à l'écran)
  miniature.png   le flash réduit à ~2 cm de large : test de lisibilité de la silhouette
  valeurs.png     niveaux de gris à fort contraste : test des trois valeurs (noir / ombre / clair)
  planche.png     les 4 étapes de construction (silhouette, traits, noir, couleur)

Moteur de rendu, dans l'ordre : rsvg-convert (brew install librsvg), cairosvg (pip), Chrome /
Chromium en mode headless. Usage : python3 buk_render.py flash.svg [--out dossier]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from buk_planche import planche
from buk_stencil import preview_svg, to_str
from buk_lib import load_design

CHROMES = ["google-chrome", "chromium", "chromium-browser",
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium"]


def render(svg_text: str, png: Path, width_px: int) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as fh:
        fh.write(svg_text)
        src = fh.name
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", str(width_px), src, "-o", str(png)], check=True)
        return
    try:
        import cairosvg
        cairosvg.svg2png(url=src, write_to=str(png), output_width=width_px)
        return
    except ImportError:
        pass
    for c in CHROMES:
        exe = shutil.which(c) or (c if Path(c).exists() else None)
        if exe:
            html = Path(src).with_suffix(".html")
            html.write_text(f"<html><body style='margin:0'><img src='{Path(src).name}' "
                            f"style='width:{width_px}px;display:block'></body></html>", encoding="utf-8")
            subprocess.run([exe, "--headless=new", "--disable-gpu", f"--screenshot={png}",
                            f"--window-size={width_px},{width_px * 2}", "--hide-scrollbars",
                            html.as_uri()], check=True, capture_output=True)
            return
    sys.exit("Aucun moteur de rendu : brew install librsvg  (ou pip install cairosvg)")


def valeurs_svg(svg_text: str) -> str:
    """Filtre niveaux de gris + contraste : on juge les valeurs sans être distrait par le rouge."""
    flt = ('<defs><filter id="v" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/>'
           '<feComponentTransfer><feFuncR type="discrete" tableValues="0 .55 .55 .55 .8 .8 1 1"/>'
           '<feFuncG type="discrete" tableValues="0 .55 .55 .55 .8 .8 1 1"/><feFuncB type="discrete" tableValues="0 .55 .55 .55 .8 .8 1 1"/>'
           '</feComponentTransfer></filter></defs>')
    head, rest = svg_text.split(">", 1)
    return f'{head}>{flt}<g filter="url(#v)">{rest.rsplit("</svg>", 1)[0]}</g></svg>'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--out")
    a = ap.parse_args()
    d = load_design(a.svg)
    out = Path(a.out) if a.out else d.path.with_name(d.path.stem + "_rendu")
    out.mkdir(parents=True, exist_ok=True)
    pv = to_str(preview_svg(d))
    render(pv, out / "apercu.png", 700)
    # 2 cm de large vus sur un écran ≈ 75 px : au-delà, le détail n'existe pas à distance.
    render(pv, out / "miniature.png", 75)
    render(valeurs_svg(pv), out / "valeurs.png", 500)
    render(planche(a.svg), out / "planche.png", 1400)
    for f in ("apercu.png", "miniature.png", "valeurs.png", "planche.png"):
        print(out / f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
