#!/usr/bin/env python3
"""Transforme une photo / un croquis en base SVG au contrat buk (à redessiner ensuite).

Détecte les masses sombres (→ zone solid-black), le rouge (→ zone solid-red) et la silhouette
(→ trait bold-line). Le résultat n'est jamais un flash fini : c'est un calque de travail que buk
simplifie et redessine selon DESIGN_OLD_SCHOOL.md.

Usage : python3 buk_trace.py croquis.jpg --width-mm 80 [--out base.svg] [--no-red]
Dépendances : opencv-python-headless, numpy (pip install -r requirements-trace.txt)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover
    sys.exit("buk_trace a besoin d'OpenCV : pip install opencv-python-headless numpy")

PX_PER_MM = 10


def contours_to_path(mask: "np.ndarray", eps_mm: float, min_area_mm2: float) -> str:
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cnts:
        if cv2.contourArea(c) < min_area_mm2 * PX_PER_MM ** 2:
            continue
        a = cv2.approxPolyDP(c, eps_mm * PX_PER_MM, True).reshape(-1, 2) / PX_PER_MM
        if len(a) < 3:
            continue
        parts.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in a) + " Z")
    return " ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--width-mm", type=float, default=80)
    ap.add_argument("--out")
    ap.add_argument("--no-red", action="store_true", help="ne pas chercher de rouge")
    ap.add_argument("--simplify", type=float, default=0.35, help="tolérance de simplification en mm")
    a = ap.parse_args()

    img = cv2.imread(a.image)
    if img is None:
        sys.exit(f"Impossible de lire {a.image}")
    h, w = img.shape[:2]
    W = int(a.width_mm * PX_PER_MM)
    H = int(h * W / w)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    _, dark = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    red = np.zeros_like(dark)
    if not a.no_red:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red = cv2.inRange(hsv, (0, 90, 60), (10, 255, 255)) | cv2.inRange(hsv, (170, 90, 60), (180, 255, 255))
        red = cv2.morphologyEx(red, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        dark = cv2.bitwise_and(dark, cv2.bitwise_not(red))
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    silhouette = cv2.morphologyEx(dark | red, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    sil_cnts, _ = cv2.findContours(silhouette, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sil_paths = []
    for c in sil_cnts:
        if cv2.contourArea(c) < 20 * PX_PER_MM ** 2:
            continue
        pts = cv2.approxPolyDP(c, a.simplify * 2 * PX_PER_MM, True).reshape(-1, 2) / PX_PER_MM
        sil_paths.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z")

    wmm, hmm = W / PX_PER_MM, H / PX_PER_MM
    black_d = contours_to_path(dark, a.simplify, 1.5)
    red_d = contours_to_path(red, a.simplify, 2.0)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{wmm:g}mm" height="{hmm:g}mm" '
           f'viewBox="0 0 {wmm:g} {hmm:g}" data-buk-title="{Path(a.image).stem} (tracé)">',
           "  <!-- Base automatique : à simplifier et redessiner avant de générer les calques. -->"]
    if red_d:
        out.append('  <g id="trace-rouge" data-buk-kind="zone" data-technique="solid-red" data-needle="RM11" '
                   f'data-ink="rouge" data-order="5">\n    <path fill="#C1121F" fill-rule="evenodd" d="{red_d}"/>\n  </g>')
    if black_d:
        out.append('  <g id="trace-noir" data-buk-kind="zone" data-technique="solid-black" data-needle="RM13" '
                   f'data-ink="noir" data-order="4">\n    <path fill="#111111" fill-rule="evenodd" d="{black_d}"/>\n  </g>')
    if sil_paths:
        out.append('  <g id="trace-contour" data-buk-kind="line" data-technique="bold-line" data-needle="RL11" '
                   'data-ink="noir" data-order="1">\n' + "\n".join(
                       f'    <path fill="none" stroke="#111111" stroke-width="1.4" stroke-linecap="round" '
                       f'stroke-linejoin="round" d="{d}"/>' for d in sil_paths) + "\n  </g>")
    out.append("</svg>")
    dest = Path(a.out) if a.out else Path(a.image).with_suffix(".trace.svg")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
