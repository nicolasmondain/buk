#!/usr/bin/env python3
"""Planche de construction d'un flash : le même dessin en 4 étapes, côte à côte.

  1 Silhouette (contour bold-line) · 2 Traits (+ lining) · 3 Noir et ombres · 4 Couleur

Sert à montrer comment un motif se construit (références motifs/, apprentissage) et à
critiquer un design étape par étape : si l'étape 1 ne se lit pas, rien ne la sauvera ensuite.

Usage : python3 buk_planche.py flash.svg [--out planche.svg] [--titre "Rose"]
"""
from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

from buk_lib import PALETTE, SVG_NS, fmt, load_design
from buk_stencil import preview_svg, to_str

ETAPES = [
    ("1 · Silhouette", {"bold-line"}),
    ("2 · Traits", {"bold-line", "lining"}),
    ("3 · Noir et ombres", {"bold-line", "lining", "whip", "pepper", "solid-black"}),
    ("4 · Couleur", None),
]


def planche(svg_path: str, titre: str | None = None) -> str:
    d = load_design(svg_path)
    W, H = d.viewbox[2], d.viewbox[3]
    gap, head, foot = W * .08, max(H * .3, 4 * W * .016 * 3.2), H * .06
    total_w = 4 * W + 5 * gap
    total_h = H + head + foot
    fs = max(H * .09, total_w * .014)
    parts = []
    for i, (label, keep) in enumerate(ETAPES):
        dd = copy.copy(d)
        dd.layers = [L for L in d.layers if keep is None or L.technique in keep]
        pv = preview_svg(dd)
        x = gap + i * (W + gap)
        pv.set("x", fmt(x)); pv.set("y", fmt(head)); pv.set("width", fmt(W)); pv.set("height", fmt(H))
        parts.append(to_str(pv))
        parts.append( f'<text x="{fmt(x + W / 2)}" y="{fmt(head - H * .045)}" text-anchor="middle" '
                     f'font-family="Helvetica, Arial, sans-serif" font-size="{fmt(fs * .62)}" fill="#111">{label}</text>')
    t = titre or d.title
    return (f'<svg xmlns="{SVG_NS}" width="{fmt(total_w)}mm" height="{fmt(total_h)}mm" '
            f'viewBox="0 0 {fmt(total_w)} {fmt(total_h)}">'
            f'<rect width="100%" height="100%" fill="#FBF6EC"/>'
            f'<text x="{fmt(gap)}" y="{fmt(fs * 1.25)}" font-family="Impact, Arial Black, sans-serif" '
            f'font-size="{fmt(fs)}" fill="#111">{t.upper()}</text>'
            f'<rect x="{fmt(gap)}" y="{fmt(fs * 1.6)}" width="{fmt(total_w - 2 * gap)}" height="{fmt(H * .008)}" fill="{PALETTE["rouge"]}"/>'
            + "".join(parts) + "</svg>")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--out")
    ap.add_argument("--titre")
    a = ap.parse_args()
    out = Path(a.out) if a.out else Path(a.svg).with_suffix(".planche.svg")
    out.write_text(planche(a.svg, a.titre), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
