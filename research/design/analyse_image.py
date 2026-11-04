#!/usr/bin/env python3
"""Mesures objectives sur une image de tatouage ou de flash, pour compléter le regard de Claude.

Ce que l'œil juge mal, le script le mesure :
  - proportions noir / rouge / clair (peau, papier) / autres couleurs ;
  - épaisseur des traits noirs (médiane et 90e centile, en % de la largeur du motif) ;
  - centre de gravité du noir (équilibre gauche/droite, haut/bas) ;
  - lisibilité en miniature (le motif réduit à 75 px garde-t-il sa silhouette ?).

Usage : python3 research/design/analyse_image.py image.jpg [--json]
Dépendances : pillow, numpy (opencv facultatif pour l'épaisseur des traits).
"""
from __future__ import annotations

import argparse
import json
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("pip install pillow numpy")


def classify(rgb: "np.ndarray") -> dict[str, "np.ndarray"]:
    r, g, b = (rgb[..., i].astype(float) for i in range(3))
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / (mx + 1e-6)
    lum = .2126 * r + .7152 * g + .0722 * b
    rouge = (r > 90) & (r > g * 1.6) & (r > b * 1.4) & (sat > .45)
    noir = (lum < 70) & ~rouge
    clair = (~noir) & (~rouge) & (lum > 150) & (sat < .45)
    autre = ~(noir | rouge | clair)
    return {"noir": noir, "rouge": rouge, "clair": clair, "autre": autre}


def stroke_widths(noir: "np.ndarray") -> tuple[float, float] | None:
    try:
        import cv2
    except ImportError:
        return None
    m = noir.astype("uint8") * 255
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 3)
    # Squelette approché : maxima locaux de la distance = demi-épaisseurs des traits.
    dil = cv2.dilate(dist, np.ones((3, 3), np.uint8))
    ridge = (dist > 0) & (dist >= dil)
    w = 2 * dist[ridge]
    if w.size == 0:
        return None
    return float(np.median(w)), float(np.percentile(w, 90))


def analyse(path: str) -> dict:
    img = Image.open(path).convert("RGB")
    a = np.asarray(img)
    cls = classify(a)
    motif = ~cls["clair"]
    ys, xs = np.nonzero(motif)
    if xs.size == 0:
        return {"fichier": path, "erreur": "aucun motif détecté (image trop claire ?)"}
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    bw = max(1, x1 - x0)
    crop = {k: v[y0:y1 + 1, x0:x1 + 1] for k, v in cls.items()}
    tot = crop["noir"].size
    ratios = {k: round(100 * float(v.sum()) / tot, 1) for k, v in crop.items()}
    ny, nx = np.nonzero(crop["noir"])
    cg = (round(float(nx.mean() / (x1 - x0 + 1)), 2), round(float(ny.mean() / (y1 - y0 + 1)), 2)) if nx.size else None
    sw = stroke_widths(crop["noir"])
    small = img.crop((x0, y0, x1 + 1, y1 + 1)).resize((75, max(1, round(75 * (y1 - y0 + 1) / (x1 - x0 + 1)))))
    sm = ~classify(np.asarray(small))["clair"]
    out = {
        "fichier": path,
        "taille_px": [int(img.width), int(img.height)],
        "proportions_pct": ratios,
        "centre_gravite_noir": cg,
        "traits_pct_largeur": {"mediane": round(float(100 * sw[0] / bw), 2), "p90": round(float(100 * sw[1] / bw), 2)} if sw else None,
        "miniature_remplissage_pct": round(100 * float(sm.mean()), 1),
    }
    notes = []
    if ratios["autre"] > 8:
        notes.append("couleurs hors palette buk présentes (bleu/vert/jaune…) : transposer en noir/rouge")
    if cg and abs(cg[0] - .5) > .15:
        notes.append("masse noire décentrée horizontalement : composition volontairement asymétrique ?")
    if out["miniature_remplissage_pct"] > 85:
        notes.append("en miniature le motif devient une tache : silhouette peu découpée")
    out["observations"] = notes
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = [analyse(p) for p in a.images]
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for r in res:
            print(f"{r['fichier']}")
            for k, v in r.items():
                if k != "fichier":
                    print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
