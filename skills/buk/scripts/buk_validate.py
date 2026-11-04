#!/usr/bin/env python3
"""Vérifie qu'un flash respecte le contrat SVG buk et les règles old school.

Usage : python3 buk_validate.py design.svg [--json]
Code de sortie : 0 si aucune erreur (les avertissements n'empêchent pas), 1 sinon.
"""
from __future__ import annotations

import argparse
import json
import sys

from buk_lib import (INKS, PALETTE, coverage, load_data, load_design, poly_area, shape_polygons, tag)

ALLOWED_COLORS = {c.lower() for c in PALETTE.values()} | {"none", "black", "white", "#000", "#000000", "#fff"}
INK_BY_TECH = {
    "bold-line": "noir", "lining": "noir", "whip": "noir", "pepper": "noir",
    "solid-black": "noir", "solid-red": "rouge", "highlight-white": "blanc",
}


def validate(path: str) -> dict:
    techniques, needles = load_data()
    errors: list[str] = []
    warns: list[str] = []
    info: dict = {}
    d = load_design(path)
    root = d.root

    if not (root.get("width", "").endswith("mm") and root.get("height", "").endswith("mm")):
        errors.append("width/height de <svg> doivent être en mm (ex. width=\"80mm\").")
    if d.viewbox[2] <= 0 or d.viewbox[3] <= 0:
        errors.append("viewBox manquant ou invalide.")
    elif abs(d.viewbox[2] - d.width_mm) > 0.01 or abs(d.viewbox[3] - d.height_mm) > 0.01:
        errors.append("viewBox doit valoir 0 0 <largeur_mm> <hauteur_mm> (1 unité = 1 mm).")
    if not d.layers:
        errors.append("Aucune couche <g data-buk-kind=…> trouvée au premier niveau.")

    for el in root.iter():
        if tag(el) in ("image", "text", "foreignObject"):
            errors.append(f"<{tag(el)}> interdit : dessiner en chemins (lettrage compris).")

    for L in d.layers:
        where = f"couche « {L.id} »"
        if L.kind not in ("line", "zone"):
            errors.append(f"{where} : data-buk-kind doit être line ou zone.")
        tech = techniques.get(L.technique)
        if not tech:
            errors.append(f"{where} : data-technique « {L.technique} » inconnue ({', '.join(techniques)}).")
        elif tech["kind"] != L.kind:
            errors.append(f"{where} : la technique {L.technique} attend data-buk-kind={tech['kind']}.")
        nd = needles.get(L.needle)
        if not nd:
            errors.append(f"{where} : aiguille « {L.needle} » absente de assets/aiguilles.json.")
        if L.ink not in INKS:
            errors.append(f"{where} : data-ink « {L.ink} » refusé — noir, rouge ou blanc uniquement (palette buk).")
        elif L.technique in INK_BY_TECH and INK_BY_TECH[L.technique] != L.ink:
            errors.append(f"{where} : {L.technique} se fait en {INK_BY_TECH[L.technique]}, pas en {L.ink}.")
        if L.order < 1:
            errors.append(f"{where} : data-order doit être un entier ≥ 1.")
        if L.el.get("transform"):
            errors.append(f"{where} : pas de transform sur un <g> de couche.")
        if nd and L.kind == "line" and nd.get("famille") != "liner":
            warns.append(f"{where} : trait fait avec {L.needle} ({nd['famille']}) — un round liner est attendu.")
        if nd and tech and tech.get("aiguilles_conseillees") and L.needle not in tech["aiguilles_conseillees"]:
            warns.append(f"{where} : {L.needle} inhabituelle pour {L.technique} "
                         f"(conseillé : {', '.join(tech['aiguilles_conseillees'])}).")
        shapes = L.shapes
        if not shapes:
            warns.append(f"{where} : couche vide.")
        for el in shapes:
            for attr in ("fill", "stroke"):
                v = (el.get(attr) or "").lower()
                if v and v not in ALLOWED_COLORS and not v.startswith("url("):
                    errors.append(f"{where} : couleur {attr}={v} hors palette (noir #111111, rouge #C1121F, blanc #FFFFFF).")
            polys, closed = shape_polygons(el)
            if L.kind == "line":
                if not el.get("stroke") or el.get("stroke") == "none":
                    errors.append(f"{where} : un trait doit avoir un stroke.")
                sw = el.get("stroke-width")
                if nd and sw and "stroke_mm" in nd and abs(float(sw) - nd["stroke_mm"]) > 0.35:
                    warns.append(f"{where} : stroke-width {sw} mm loin de {nd['stroke_mm']} mm attendu pour {L.needle}.")
            else:
                if not closed:
                    errors.append(f"{where} : <{tag(el)}> de zone non fermé (terminer le chemin par Z).")
                area = sum(poly_area(p) for p in polys)
                if area < 1.0 and L.technique != "highlight-white":
                    warns.append(f"{where} : zone de {area:.1f} mm² — trop petite pour être remplie, en faire un trait ?")

    # Proportions visibles (échantillonnage : la zone du dessus gagne).
    sil = [L for L in d.layers if L.technique == "bold-line"]
    ratios = coverage(d) if not errors else {"noir": 0, "ombrage": 0, "rouge": 0, "blanc": 0, "peau": 0}
    info["ratios_pct"] = ratios
    if not errors:
        if ratios["noir"] < 12:
            warns.append(f"Noir plein ≈ {ratios['noir']} % du motif : le style en veut une vraie masse (≈ 20–40 %).")
        if ratios["rouge"] > 70:
            warns.append(f"Rouge ≈ {ratios['rouge']} % : réserver le rouge au sujet, ajouter du noir structurant.")
        if ratios["blanc"] > 5:
            warns.append(f"Blanc ≈ {ratios['blanc']} % : le blanc se limite à de petits rehauts.")
    if not sil:
        warns.append("Aucune couche bold-line : le contour extérieur épais est la signature du style.")
    configs = sorted({(L.needle, L.ink) for L in d.layers})
    info["configurations"] = [f"{n} / {i}" for n, i in configs]
    if len(configs) > 7:
        warns.append(f"{len(configs)} configurations aiguille/encre : simplifier (3 à 6 pour un flash).")
    info["taille_mm"] = [d.width_mm, d.height_mm]
    return {"fichier": str(path), "erreurs": errors, "avertissements": warns, "infos": info}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    a = ap.parse_args()
    r = validate(a.svg)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"buk validate — {r['fichier']}")
        print(f"  taille : {r['infos']['taille_mm'][0]} × {r['infos']['taille_mm'][1]} mm")
        print(f"  configurations : {', '.join(r['infos']['configurations'])}")
        print("  surfaces visibles (≈ %) : " + ", ".join(f"{k} {v}" for k, v in r["infos"]["ratios_pct"].items()))
        for e in r["erreurs"]:
            print(f"  ERREUR  {e}")
        for w in r["avertissements"]:
            print(f"  ATTENTION  {w}")
        print("  OK" if not r["erreurs"] else f"  {len(r['erreurs'])} erreur(s)")
    return 1 if r["erreurs"] else 0


if __name__ == "__main__":
    sys.exit(main())
