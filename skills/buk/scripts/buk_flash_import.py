#!/usr/bin/env python3
"""Convertit un motif d'une planche de flash (photo/scan) en flash au contrat buk.

C'est la façon recommandée de faire un flash de qualité : partir d'un VRAI dessin traditionnel
(planche du domaine public, croquis de la personne) plutôt que de dessiner point par point.

Ce que fait le script :
  1. détecte l'encre noire, le rouge, le bleu et le vert sur le papier (espace Lab) ;
  2. trait de plume → squelette → lignes centrales lissées, épaisseur d'aiguille (lining RL7) ;
  3. silhouette extérieure → contour épais lissé (bold-line RL11) ;
  4. aplats : rouge → solid-red ; noir épais et vert → solid-black (le vert n'existe pas chez
     buk) ; bleu → whip (le bleu des vieux flashs devient de l'ombrage noir) ;
  5. écrit un SVG en mm au contrat buk (validé par buk_validate.py).

Usage :
  python3 buk_flash_import.py planche.jpg --crop x0 y0 x1 y1 --largeur-mm 70 --titre "Rose" -o rose.svg
  (--crop en pixels de l'image d'origine ; --apercu pour un PNG de contrôle)

Dépendances : opencv-contrib (ximgproc) ou scikit-image, numpy.
À n'utiliser que sur des images dont on a le droit : domaine public (CC0), ses propres dessins.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover
    sys.exit("pip install opencv-contrib-python-headless numpy")

NOIR, ROUGE = "#111111", "#C1121F"


# --------------------------------------------------------------------------- masques

def masques(img, trait_px=5):
    """Renvoie (traits, noir_plein, rouge, bleu, vert).

    Les traits de plume sont isolés par un « black-hat » sur la luminance : ce qui est plus
    sombre que son voisinage immédiat, que le fond soit le papier ou un aplat rouge.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.int16)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    # Tout est mesuré par rapport au papier (jaune, brun, crème…) : couleur médiane des pixels clairs.
    clair = L > np.percentile(L, 55)
    paper, pA, pB = float(np.median(L[clair])), float(np.median(A[clair])), float(np.median(B[clair]))
    dA, dB = A - pA, B - pB
    k = max(9, int(trait_px * 3) | 1)
    bh = cv2.morphologyEx(L.astype(np.uint8), cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    # Seuil d'Otsu sur la réponse black-hat : sépare le trait du grain du papier.
    vals = bh[bh > 4].astype(np.uint8)
    otsu = cv2.threshold(vals.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0] if vals.size else 20
    seuil = max(16, otsu)
    rouge = (dA > 18) & (dA > np.abs(dB) * .45)
    traits = (bh > seuil) | ((bh > seuil * .7) & rouge)
    noir_plein = (L < paper * .4) & (dA < 16)
    bleu = (dB < -9) & (dA < 8) & (L < paper * .95) & (L > paper * .3)
    vert = (dA < -8) & (L < paper * .95) & (L > paper * .3)
    return traits, noir_plein, rouge, bleu, vert


def nettoie(m, ouv=2, ferm=3, aire_min=30):
    m = m.astype(np.uint8) * 255
    if ferm:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((ferm, ferm), np.uint8))
    if ouv:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((ouv, ouv), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= aire_min:
            out[lab == i] = 255
    return out


def sans_bord(m, marge=3, part=.2):
    """Supprime les composantes qui touchent le bord du cadre (œillets, motif voisin coupé)."""
    m = m.astype(np.uint8)
    if m.max() == 1:
        m = m * 255
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    h, w = m.shape
    out = m.copy()
    if n <= 1:
        return out
    grand = stats[1:, cv2.CC_STAT_AREA].max()
    for i in range(1, n):
        x, y, ww, hh, aire = stats[i]
        touche = x <= marge or y <= marge or x + ww >= w - marge or y + hh >= h - marge
        if touche and aire < part * grand:  # petit morceau coupé par le cadre : pas le motif
            out[lab == i] = 0
    return out


def _zhang_suen(m):
    """Squelettisation Zhang-Suen en numpy pur (secours sans opencv-contrib ni scikit-image)."""
    img = (m > 0).astype(np.uint8)
    img = np.pad(img, 1)
    while True:
        changed = False
        for step in (0, 1):
            P = img
            p2, p3, p4 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:]
            p5, p6, p7 = P[2:, 2:], P[2:, 1:-1], P[2:, :-2]
            p8, p9 = P[1:-1, :-2], P[:-2, :-2]
            c = P[1:-1, 1:-1]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(x.astype(np.int16) for x in nb)
            seq = nb + [p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.int16) for i in range(8))
            if step == 0:
                cond = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                cond = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            rm = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & cond
            if rm.any():
                img[1:-1, 1:-1][rm] = 0
                changed = True
        if not changed:
            break
    return (img[1:-1, 1:-1] * 255).astype(np.uint8)


def squelette(m):
    if hasattr(cv2, "ximgproc"):
        return cv2.ximgproc.thinning(m, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
    try:
        from skimage.morphology import skeletonize
        return (skeletonize(m > 0) * 255).astype(np.uint8)
    except ImportError:
        return _zhang_suen(m)


# --------------------------------------------------------------------------- géométrie

NB = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def polylignes(sk):
    """Squelette (pixels) → liste de polylignes, coupées aux jonctions."""
    ys, xs = np.nonzero(sk)
    pts = set(zip(xs.tolist(), ys.tolist()))

    def voisins(p):
        x, y = p
        return [(x + dx, y + dy) for dx, dy in NB if (x + dx, y + dy) in pts]
    deg = {p: len(voisins(p)) for p in pts}
    vus = set()
    lignes = []

    def marche(a, b):
        ligne = [a, b]
        vus.add(frozenset((a, b)))
        prev, cur = a, b
        while deg[cur] == 2:
            nxt = [q for q in voisins(cur) if q != prev and frozenset((cur, q)) not in vus]
            if not nxt:
                break
            vus.add(frozenset((cur, nxt[0])))
            prev, cur = cur, nxt[0]
            ligne.append(cur)
        return ligne
    for p in pts:
        if deg[p] != 2:
            for q in voisins(p):
                if frozenset((p, q)) not in vus:
                    lignes.append(marche(p, q))
    for p in pts:  # boucles fermées sans extrémité
        for q in voisins(p):
            if frozenset((p, q)) not in vus:
                lignes.append(marche(p, q))
    return lignes


def raccorde(lignes, gap, angle_max=55):
    """Relie les bouts de polylignes proches et à peu près alignés (trait de plume coupé).

    Glouton : toutes les paires de bouts candidates sont triées par distance une seule fois.
    """
    cosmax = math.cos(math.radians(angle_max))

    def dirn(pl, fin):
        a, b = (pl[-1], pl[max(0, len(pl) - 6)]) if fin else (pl[0], pl[min(len(pl) - 1, 5)])
        dx, dy = a[0] - b[0], a[1] - b[1]
        n = math.hypot(dx, dy) or 1
        return dx / n, dy / n
    ends = []
    for i, pl in enumerate(lignes):
        for fin in (False, True):
            ends.append((i, fin, pl[-1] if fin else pl[0], dirn(pl, fin)))
    cand = []
    cell = {}
    for k, (_, _, p, _) in enumerate(ends):
        cell.setdefault((int(p[0] // gap), int(p[1] // gap)), []).append(k)
    for k, (i, fa, pa, da) in enumerate(ends):
        cx, cy = int(pa[0] // gap), int(pa[1] // gap)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for m in cell.get((cx + dx, cy + dy), []):
                    j, fb, pb, db = ends[m]
                    if m <= k or j == i:
                        continue
                    d = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
                    if d == 0 or d > gap:
                        continue
                    ux, uy = (pb[0] - pa[0]) / d, (pb[1] - pa[1]) / d
                    if da[0] * ux + da[1] * uy > cosmax and -(db[0] * ux + db[1] * uy) > cosmax:
                        cand.append((d, k, m))
    cand.sort()
    # Chaque bout ne sert qu'une fois : les lignes forment des chemins (ou des boucles).
    lien = {}
    for _, k, m in cand:
        if k in lien or m in lien:
            continue
        lien[k], lien[m] = m, k
    n = len(lignes)
    vus = set()

    def parcourt(start, premier_bout):
        """premier_bout : 0 si la ligne est prise dans son sens, 1 si inversée."""
        chaine, cur, entree = [], start, premier_bout
        while cur not in vus:
            vus.add(cur)
            pl = lignes[cur] if entree == 0 else lignes[cur][::-1]
            chaine += pl
            sortie = 2 * cur + (1 - entree)
            if sortie not in lien:
                break
            m = lien[sortie]
            cur, entree = m // 2, m % 2
        return chaine
    out = []
    for i in range(n):  # chemins : partir d'une ligne dont un bout est libre
        if i in vus:
            continue
        if 2 * i not in lien:
            out.append(parcourt(i, 0))
        elif 2 * i + 1 not in lien:
            out.append(parcourt(i, 1))
    for i in range(n):  # boucles restantes
        if i not in vus:
            out.append(parcourt(i, 0))
    return out


def adoucit(pl, w=5):
    """Moyenne glissante sur les points (efface le tremblé du squelette), bouts conservés."""
    if len(pl) <= w:
        return pl
    a = np.array(pl, float)
    k = np.ones(w) / w
    xs = np.convolve(np.pad(a[:, 0], w // 2, mode="edge"), k, mode="valid")
    ys = np.convolve(np.pad(a[:, 1], w // 2, mode="edge"), k, mode="valid")
    out = list(zip(xs.tolist(), ys.tolist()))
    out[0], out[-1] = pl[0], pl[-1]
    return out


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b - a
    n = np.hypot(*ab) or 1e-9
    d = [abs(ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / n for p in pts[1:-1]]
    i = int(np.argmax(d)) + 1
    if d[i - 1] > eps:  # noqa: SIM108
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def lisse_d(pts, ferme=False, k=1 / 6):
    """Polyligne → chemin de Béziers (Catmull-Rom). Coordonnées déjà en mm."""
    if len(pts) < 2:
        return ""
    if ferme and pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    f = lambda p: f"{p[0]:.2f} {p[1]:.2f}"  # noqa: E731
    d = ["M" + f(pts[0])]
    rng = range(n) if ferme else range(n - 1)
    for i in rng:
        p0 = pts[i - 1] if (ferme or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (ferme or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d.append("C" + " ".join((f(c1), f(c2), f(p2))))
    if ferme:
        d.append("Z")
    return " ".join(d)


def contours_zone(m, s, eps_px):
    """Masque → chemin (avec trous, evenodd) en mm."""
    cnts, _ = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cnts:
        if cv2.contourArea(c) < 25:
            continue
        a = cv2.approxPolyDP(c, eps_px, True).reshape(-1, 2)
        if len(a) < 3:
            continue
        parts.append(lisse_d([(x * s, y * s) for x, y in a.tolist()], ferme=True))
    return " ".join(parts)


# --------------------------------------------------------------------------- conversion

def convertir(img, largeur_mm, titre, placement="", trait_mm=0.8, contour_mm=1.4):
    h0, w0 = img.shape[:2]
    up = max(1.0, 900 / max(h0, w0))  # travailler à ~900 px pour un squelette propre
    img = cv2.resize(img, (round(w0 * up), round(h0 * up)), interpolation=cv2.INTER_CUBIC)
    img = cv2.bilateralFilter(img, 7, 40, 7)
    h, w = img.shape[:2]
    s = largeur_mm / w  # mm par pixel
    traits, noir_plein, rouge, bleu, vert = masques(img, trait_px=4 * up)
    lignes = nettoie(traits, ouv=0, ferm=5, aire_min=int(40 * up))
    lignes = sans_bord(lignes)
    noir_plein = sans_bord(noir_plein.astype(np.uint8) * 255, part=10) > 0  # un aplat noir au bord = œillet
    epais = nettoie(noir_plein, ouv=7, ferm=3, aire_min=int(300 * up))
    lignes = cv2.subtract(lignes, cv2.dilate(epais, np.ones((3, 3), np.uint8), iterations=2))
    ink = cv2.bitwise_or(lignes, epais)
    dist = cv2.distanceTransform(lignes, cv2.DIST_L2, 5)
    trait_px = float(np.percentile(dist[dist > 0], 75) * 2) if (dist > 0).any() else 3.0

    rouge_m = nettoie((sans_bord(rouge) > 0) | ((cv2.dilate(rouge.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & (lignes > 0)),
                      ouv=3, ferm=9, aire_min=int(60 * up))
    bleu_m = nettoie(bleu & ~(rouge_m > 0) & ~noir_plein, ouv=3, ferm=7, aire_min=int(80 * up))
    vert_m = nettoie(vert & ~(rouge_m > 0) & ~noir_plein, ouv=3, ferm=7, aire_min=int(80 * up))
    noir_m = cv2.bitwise_or(epais, vert_m)

    # Silhouette : tout ce qui est dessiné, trous bouchés.
    tout = cv2.bitwise_or(cv2.bitwise_or(ink, rouge_m), cv2.bitwise_or(bleu_m, vert_m))
    tout = cv2.morphologyEx(tout, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    sil_c, _ = cv2.findContours(tout, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sil_c = [c for c in sil_c if cv2.contourArea(c) > 0.01 * h * w]
    sil = np.zeros_like(tout)
    cv2.drawContours(sil, sil_c, -1, 255, -1)
    bord = np.zeros_like(tout)
    cv2.drawContours(bord, sil_c, -1, 255, int(max(6, trait_px * 3.2)))

    # Trait intérieur : squelette des lignes, hors bord de silhouette (déjà au contour épais).
    sk = squelette(lignes)
    sk[bord > 0] = 0
    traits = []
    pls = [pl for pl in polylignes(sk) if len(pl) >= 4]
    pls = raccorde(pls, gap=trait_px * 3.5)
    for pl in pls:
        if len(pl) < max(10, trait_px * 3.5):
            continue
        court = len(pl) < trait_px * 14  # lettres, petits détails : moins lisser
        pl = rdp(adoucit(pl, 3 if court else 7), 1.0 if court else 1.6)
        traits.append(lisse_d([(x * s, y * s) for x, y in pl]))
    sil_d = []
    for c in sil_c:
        c2 = adoucit([tuple(q) for q in c.reshape(-1, 2).tolist()], 9)
        a = cv2.approxPolyDP(np.array(c2, np.float32).reshape(-1, 1, 2), 1.8, True).reshape(-1, 2)
        sil_d.append(lisse_d([(x * s, y * s) for x, y in a.tolist()], ferme=True))

    # Aplats : chaque région fermée par les traits prend la couleur qui y domine et se remplit
    # entièrement, jusque sous les traits (comme un remplissage au tatouage).
    barriere = cv2.dilate(cv2.bitwise_or(lignes, bord // 255 * 0 + cv2.subtract(cv2.dilate(sil, np.ones((3, 3), np.uint8)), sil)),
                          np.ones((3, 3), np.uint8))
    libre = cv2.bitwise_and(sil, cv2.bitwise_not(barriere))
    n, lab = cv2.connectedComponents(libre, connectivity=4)
    sous = int(max(2, trait_px * .9))
    pleins = {"rouge": np.zeros_like(sil), "ombrage": np.zeros_like(sil), "noir": np.zeros_like(sil)}
    for i in range(1, n):
        reg = lab == i
        aire = int(reg.sum())
        if aire < 20:
            continue
        parts = {"rouge": (rouge_m[reg] > 0).mean(), "ombrage": (bleu_m[reg] > 0).mean(),
                 "noir": ((vert_m[reg] > 0) | (epais[reg] > 0)).mean()}
        k, v = max(parts.items(), key=lambda kv: kv[1])
        if v >= .35:
            pleins[k][reg] = 255
    zone = {}
    for k, m in pleins.items():
        m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=sous)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        if k == "noir":
            m = cv2.bitwise_or(m, epais)
        elif k == "rouge":  # secours : le rouge peint, même si les traits ne ferment pas la zone
            m = cv2.bitwise_or(m, cv2.morphologyEx(rouge_m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
        zone[k] = contours_zone(cv2.bitwise_and(m, sil), s, 1.4)

    H = h * s
    g = []

    def layer(id_, kind, tech, needle, ink_, order, body):
        if body:
            g.append(f'  <g id="{id_}" data-buk-kind="{kind}" data-technique="{tech}" data-needle="{needle}" '
                     f'data-ink="{ink_}" data-order="{order}">\n' + "\n".join(body) + "\n  </g>")
    layer("rouge", "zone", "solid-red", "RM11", "rouge", 5,
          [f'    <path fill="{ROUGE}" fill-rule="evenodd" d="{zone["rouge"]}"/>'] if zone["rouge"] else [])
    layer("ombrage", "zone", "whip", "RM9", "noir", 3,
          [f'    <path fill="{NOIR}" fill-rule="evenodd" d="{zone["ombrage"]}"/>'] if zone["ombrage"] else [])
    layer("noir", "zone", "solid-black", "RM13", "noir", 4,
          [f'    <path fill="{NOIR}" fill-rule="evenodd" d="{zone["noir"]}"/>'] if zone["noir"] else [])
    style = 'fill="none" stroke="#111111" stroke-linecap="round" stroke-linejoin="round"'
    layer("interieur", "line", "lining", "RL5", "noir", 2,
          [f'    <path {style} stroke-width="{trait_mm}" d="{d}"/>' for d in traits])
    layer("contour", "line", "bold-line", "RL11", "noir", 1,
          [f'    <path {style} stroke-width="{contour_mm}" d="{d}"/>' for d in sil_d])
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur_mm:g}mm" height="{H:.1f}mm" '
            f'viewBox="0 0 {largeur_mm:g} {H:.1f}" data-buk-title="{titre}"'
            + (f' data-buk-placement="{placement}"' if placement else "") + ">")
    return head + "\n" + "\n".join(g) + "\n</svg>\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--largeur-mm", type=float, default=70)
    ap.add_argument("--titre", default="Flash importé")
    ap.add_argument("--placement", default="")
    ap.add_argument("--trait-mm", type=float, default=0.8)
    ap.add_argument("--contour-mm", type=float, default=1.4)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    img = cv2.imread(a.image)
    if img is None:
        sys.exit(f"Image illisible : {a.image}")
    if a.crop:
        x0, y0, x1, y1 = a.crop
        img = img[y0:y1, x0:x1]
    svg = convertir(img, a.largeur_mm, a.titre, a.placement, a.trait_mm, a.contour_mm)
    out = Path(a.out) if a.out else Path(a.image).with_suffix(".buk.svg")
    out.write_text(svg, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
