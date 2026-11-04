"""Classiques old school : lettrage block, banderole à texte, fer à cheval, dés, cartes,
ancre marine, cœur, dague, crâne.

Mêmes conventions que buk_composants : chaque pièce se pose par un centre, une taille et un
angle, et range ses chemins dans les couches standard d'un `Flash`.
Fiches : references/motifs/LETTRAGE.md et references/motifs/CLASSIQUES.md.
"""
from __future__ import annotations

import math
import re

from buk_composants import Flash, P, rot

# --------------------------------------------------------------------------- lettrage

# Squelettes de capitales « block » sur une grille 4 × 6 (y vers le bas). Tracés au RL14
# (trait épais = corps de la lettre) avec une ombre portée décalée en bas à droite.
GLYPHES = {
    "A": "M0 6 L2 0 L4 6 M0.75 3.9 L3.25 3.9",
    "B": "M0 6 L0 0 L2.5 0 C3.9 0 3.9 3 2.5 3 L0 3 M2.5 3 C4.2 3 4.2 6 2.5 6 L0 6",
    "C": "M4 1.1 C3.3 -0.3 0 -0.3 0 3 C0 6.3 3.3 6.3 4 4.9",
    "D": "M0 0 L0 6 L1.7 6 C4.3 6 4.3 0 1.7 0 L0 0",
    "E": "M4 0 L0 0 L0 6 L4 6 M0 3 L3 3",
    "F": "M4 0 L0 0 L0 6 M0 3 L3 3",
    "G": "M4 1.1 C3.3 -0.3 0 -0.3 0 3 C0 6.3 4 6.4 4 3.6 L2.3 3.6",
    "H": "M0 0 L0 6 M4 0 L4 6 M0 3 L4 3",
    "I": "M2 0 L2 6 M0.8 0 L3.2 0 M0.8 6 L3.2 6",
    "J": "M4 0 L4 4.2 C4 6.5 0.3 6.5 0 4.5",
    "K": "M0 0 L0 6 M4 0 L0 3.6 M1.5 2.6 L4 6",
    "L": "M0 0 L0 6 L4 6",
    "M": "M0 6 L0 0 L2 3.4 L4 0 L4 6",
    "N": "M0 6 L0 0 L4 6 L4 0",
    "O": "M2 0 C-0.6 0 -0.6 6 2 6 C4.6 6 4.6 0 2 0 Z",
    "P": "M0 6 L0 0 L2.5 0 C4.2 0 4.2 3.4 2.5 3.4 L0 3.4",
    "Q": "M2 0 C-0.6 0 -0.6 6 2 6 C4.6 6 4.6 0 2 0 Z M2.5 4.3 L4.2 6.3",
    "R": "M0 6 L0 0 L2.5 0 C4.2 0 4.2 3.4 2.5 3.4 L0 3.4 M2.1 3.4 L4 6",
    "S": "M3.9 1 C3.3 -0.3 0.2 -0.3 0.2 1.6 C0.2 3.3 3.9 2.6 3.9 4.4 C3.9 6.4 0.6 6.4 0 5",
    "T": "M0 0 L4 0 M2 0 L2 6",
    "U": "M0 0 L0 4 C0 6.6 4 6.6 4 4 L4 0",
    "V": "M0 0 L2 6 L4 0",
    "W": "M0 0 L1 6 L2 2.4 L3 6 L4 0",
    "X": "M0 0 L4 6 M4 0 L0 6",
    "Y": "M0 0 L2 3 L4 0 M2 3 L2 6",
    "Z": "M0 0 L4 0 L0 6 L4 6",
    "0": "M2 0 C0 0 0 6 2 6 C4 6 4 0 2 0 Z",
    "1": "M0.9 1.2 L2.4 0 L2.4 6 M0.9 6 L3.9 6",
    "2": "M0.2 1.3 C0.8 -0.4 3.9 -0.4 3.8 1.8 C3.7 3.4 0.4 4.6 0 6 L4 6",
    "3": "M0.2 0.9 C1 -0.4 4 -0.3 3.8 1.6 C3.7 2.7 2.5 3 1.6 3 C2.7 3 4 3.3 4 4.6 C4 6.4 0.8 6.4 0 5.2",
    "4": "M3 6 L3 0 L0 4.2 L4 4.2",
    "5": "M3.8 0 L0.6 0 L0.3 2.8 C2.2 1.9 4 2.6 4 4.3 C4 6.4 0.8 6.4 0 5.2",
    "6": "M3.6 0.6 C2.4 -0.4 0 0 0 3.4 C0 6.4 4 6.6 4 4.2 C4 2.2 1 2 0.1 3.6",
    "7": "M0 0 L4 0 L1.5 6",
    "8": "M2 3 C-0.1 3 0 0 2 0 C4 0 4.1 3 2 3 C-0.3 3 -0.3 6 2 6 C4.3 6 4.3 3 2 3 Z",
    "9": "M3.9 2.6 C3 4 0 3.8 0 1.9 C0 -0.5 4 -0.6 4 2.4 C4 5.8 1.6 6.4 0.4 5.4",
    "&": "M4 6 L1 1.8 C0.3 0.6 1 0 1.8 0 C2.6 0 3.2 0.7 2.6 1.7 L0.4 4 C-0.4 5.2 0.4 6.2 1.6 6.1 C2.6 6 3.4 5 3.8 3.8",
    "!": "M2 0 L2 4 M2 5.8 L2 6",
    "'": "M2 0 L1.6 1.6",
    "-": "M0.8 3.4 L3.2 3.4",
    ".": "M2 5.8 L2 6",
}
AVANCE, ESPACE = 4.0, 2.6  # largeur de glyphe et espace entre lettres, en unités de grille


def _glyph_points(cmds: str):
    """Découpe un glyphe en sous-chemins de points (courbes conservées en commandes)."""
    toks = re.findall(r"[MLCZ]|-?\d*\.?\d+", cmds)
    out, i, cmd = [], 0, None
    while i < len(toks):
        if toks[i] in "MLCZ":
            cmd = toks[i]; i += 1
            if cmd == "Z":
                out.append(("Z", ())); continue
        n = {"M": 2, "L": 2, "C": 6}[cmd]
        out.append((cmd, tuple(float(v) for v in toks[i:i + n]))); i += n
    return out


def largeur_texte(texte: str, hauteur: float) -> float:
    s = hauteur / 6
    n = len(texte)
    return (n * AVANCE + max(0, n - 1) * ESPACE - sum(AVANCE - 1.2 for c in texte if c == " ")) * s


def lettrage(f: Flash, texte: str, cx, cy, hauteur, ang=0.0, arc=0.0, ombre=False):
    """Texte en capitales block, centré sur (cx, cy), hauteur de capitale `hauteur` mm.

    `arc` > 0 cintre la ligne vers le haut (flèche en mm au centre), pour suivre une banderole.
    Hauteur ≥ 7 mm : corps au RL14 (option `ombre=True` : filet d'ombre RL9 décalé — à l'essai il
    fait « baver » le texte, donc désactivé par défaut). En dessous (index de carte…) : RL7 seul.
    """
    texte = texte.upper()
    s = hauteur / 6
    total = largeur_texte(texte, hauteur)
    x = -total / 2
    fort = hauteur >= 7
    dec = s * .78  # décalage de l'ombre portée : un filet détaché, séparé de la lettre par de la peau
    for c in texte:
        if c == " ":
            x += 1.2 * s + ESPACE * s
            continue
        g = GLYPHES.get(c)
        if g is None:
            x += AVANCE * s + ESPACE * s
            continue

        def tp(gx, gy, dx=0.0, dy=0.0):
            lx = x + gx * s
            ly = -hauteur / 2 + gy * s - (arc * (1 - (2 * lx / total) ** 2) if total else 0)
            X, Y = rot(lx + dx, ly + dy, ang)
            return f"{cx + X:.2f} {cy + Y:.2f}"

        for layer, dx, dy in ((("lettre-ombre", dec, dec),) if (ombre and fort) else ()) + \
                ((("lettre" if fort else "interieur"), 0.0, 0.0),):
            d = []
            for cmd, v in _glyph_points(g):
                if cmd == "Z":
                    d.append("Z")
                elif cmd == "C":
                    d.append("C" + " ".join(tp(v[k], v[k + 1], dx, dy) for k in (0, 2, 4)))
                else:
                    d.append(cmd + tp(v[0], v[1], dx, dy))
            f.add(layer, " ".join(d))
        x += AVANCE * s + ESPACE * s


def banderole_texte(f: Flash, texte: str, cx, cy, largeur, hauteur=None, pli=None, devant=True):
    """Banderole horizontale centrée en (cx, cy) avec son texte (taille adaptée).

    `devant=True` : la banderole passe devant ce qui est déjà dessiné (découpé dessous).
    """
    from buk_composants import banderole
    h = hauteur or max(13.5, largeur * .16)
    pli = pli or h * .65
    if devant:
        x1, x2, top, bot = cx - largeur / 2, cx + largeur / 2, cy - h / 2, cy + h / 2
        f.masquer(x1 + pli, top - 1.6, x2 - pli, bot)
        f.masquer(x1, top + h * .35, x1 + pli, bot + h * .35)
        f.masquer(x2 - pli, top + h * .35, x2, bot + h * .35)
    banderole(f, cx - largeur / 2, cx + largeur / 2, cy, h, pli=pli)
    utile = largeur - 2 * pli - 2 * h * .45
    ht = min(h * .54, 6 * utile / max(1e-6, largeur_texte(texte, 6)))
    lettrage(f, texte, cx, cy - 1.0, ht, arc=1.4)


# --------------------------------------------------------------------------- cœur et dague

def coeur(f: Flash, cx, cy, w, ang=0.0, ombre=True):
    """Cœur traditionnel, largeur `w` mm : rouge, croissant noir + whip bas-gauche, virgule blanche."""
    def p():
        return P(cx, cy, w / 50, ang)
    contour = (p().M(0, 21).C(-13, 11, -25, 3, -25, -8).C(-25, -16, -19, -21, -12, -21)
               .C(-6, -21, -2, -17, 0, -13).C(2, -17, 6, -21, 12, -21)
               .C(19, -21, 25, -16, 25, -8).C(25, 3, 13, 11, 0, 21).Z())
    f.add("rouge", contour).add("contour", contour)
    if ombre:
        f.add("noir-fin", p().M(0, 21).C(-13, 11, -25, 3, -25, -8).C(-25, -12, -23.5, -15.5, -21, -17.5)
              .C(-22.4, -11, -20.5, -3, -14, 3.5).C(-9, 8.5, -4, 13.5, 0, 17.3).Z())
        f.add("ombrage", p().M(0, 17.3).C(-4, 13.5, -9, 8.5, -14, 3.5).C(-20.5, -3, -22.4, -11, -21, -17.5)
              .C(-19, -19, -17, -19.6, -15.5, -19.6).C(-16.5, -12, -14, -4.5, -8, 1.5)
              .C(-4.5, 5, -1.5, 8.5, 0, 11).Z(), direction=-45 + ang)
    f.add("rehauts", p().M(14, -17).C(17.5, -17, 20.5, -14.4, 21, -10.4).C(19.2, -12.6, 16.6, -14.4, 14, -15)
          .C(13.1, -15.3, 13.1, -16.8, 14, -17).Z())


def dague(f: Flash, cx, cy, L, ang=0.0):
    """Dague verticale (pointe vers le bas à ang=0), longueur totale `L` mm, centre au milieu.

    Pommeau et garde en noir plein, lame avec arête centrale et whip sur la moitié gauche,
    reflet blanc sur le pommeau.
    """
    def p():
        return P(cx, cy, L / 100, ang)
    pommeau = p().M(0, -50).C(3.5, -50, 4.6, -47, 4.6, -45.5).C(4.6, -43, 2.5, -41.5, 0, -41.5) \
        .C(-2.5, -41.5, -4.6, -43, -4.6, -45.5).C(-4.6, -47, -3.5, -50, 0, -50).Z()
    poignee = p().M(-2.6, -41.5).L(-3.2, -24).L(3.2, -24).L(2.6, -41.5).Z()
    garde = (p().M(-17, -24).C(-19.5, -24, -21, -22.5, -21, -21).C(-21, -19.5, -19.5, -18, -17, -18)
             .L(17, -18).C(19.5, -18, 21, -19.5, 21, -21).C(21, -22.5, 19.5, -24, 17, -24).Z())
    lame = p().M(-5, -18).L(-5, 32).L(0, 50).L(5, 32).L(5, -18).Z()
    f.add("noir", pommeau).add("noir", garde).add("noir-fin", poignee)
    for z in (lame, garde, poignee, pommeau):
        f.add("contour", z)
    f.add("interieur", p().M(0, -18).L(0, 46))
    f.add("ombrage", p().M(-5, -18).L(0, -18).L(0, 50).L(-5, 32).Z(), direction=0 + ang)
    for y in (-37, -32.5, -28):  # bagues de la poignée réservées en peau
        f.add("noir-fin", p().M(-2.9, y).L(2.9, y).L(2.9, y + 1.2).L(-2.9, y + 1.2).Z())
    f.add("rehauts", p().M(-1.8, -47.6).C(-1.2, -48.6, .4, -48.8, 1.2, -48.2).C(.2, -47.9, -.8, -47.4, -1.4, -46.6)
          .C(-1.9, -46.6, -2.1, -47.1, -1.8, -47.6).Z())


# --------------------------------------------------------------------------- fer à cheval

def fer_a_cheval(f: Flash, cx, cy, h, ang=0.0):
    """Fer à cheval ouverture vers le haut (porte-bonheur), hauteur `h` mm.

    Bande en peau avec whip sur la moitié droite, 6 étampures (trous de clous) en noir, éponges
    (extrémités) élargies, reflet blanc sur la gauche.
    """
    def pt(r_x, r_y, t):
        return r_x * math.cos(math.radians(t)), .08 + r_y * math.sin(math.radians(t))

    def p():
        return P(cx, cy, h / 2.2, ang)

    t0, t1 = -52, 232
    ri_x, ri_y = .52, .6
    ts = [t0 + (t1 - t0) * i / 40 for i in range(41)]
    pp = p()
    pp.M(*pt(1, 1.08, ts[0]))
    for t in ts[1:]:
        pp.L(*pt(1, 1.08, t))
    for t in reversed(ts):
        pp.L(*pt(ri_x, ri_y, t))
    pp.Z()
    bande = str(pp)
    f.add("contour", bande)
    # Ombre : moitié droite, depuis le bord extérieur.
    sh = p()
    tsr = [t0 + (100 - t0) * i / 20 for i in range(21)]
    sh.M(*pt(1, 1.08, tsr[0]))
    for t in tsr[1:]:
        sh.L(*pt(1, 1.08, t))
    for t in reversed(tsr):
        sh.L(*pt(.8, .87, t))
    f.add("ombrage", sh.Z(), direction=-135 + ang)
    # Ligne médiane (rainure) et étampures.
    rain = p()
    rain.M(*pt(.76, .84, t0 + 10))
    for i in range(1, 31):
        rain.L(*pt(.76, .84, t0 + 10 + (t1 - t0 - 20) * i / 30))
    f.add("details", rain)
    for t in (-25, 10, 45, 135, 170, 205):
        x, y = pt(.76, .84, t)
        f.add("noir-fin", P(cx, cy, h / 2.2, ang).M(x - .06, y - .065).L(x + .06, y - .065)
              .L(x + .06, y + .065).L(x - .06, y + .065).Z())
    f.add("rehauts", p().M(*pt(.93, 1.0, 150)).C(*pt(.96, 1.03, 165), *pt(.96, 1.03, 185), *pt(.93, 1.0, 200))
          .L(*pt(.89, .96, 195)).C(*pt(.91, .98, 182), *pt(.91, .98, 168), *pt(.89, .96, 155)).Z())


# --------------------------------------------------------------------------- dés

PIPS = {1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 3: [(.25, .25), (.5, .5), (.75, .75)],
        4: [(.27, .27), (.73, .27), (.27, .73), (.73, .73)],
        5: [(.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)],
        6: [(.27, .2), (.27, .5), (.27, .8), (.73, .2), (.73, .5), (.73, .8)]}


def de(f: Flash, cx, cy, a, faces=(5, 3, 6), ang=0.0):
    """Dé vu en perspective (3 faces : dessus, gauche, droite), arête `a` mm.

    Dessus en peau, face gauche en peau avec whip, face droite en noir plein avec points blancs :
    le contraste qui fait lire un dé à distance.
    """
    k = .87

    def q(x, y):
        X, Y = rot(x * a, y * a, ang)
        return cx + X, cy + Y

    def poly(pts):
        return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in (q(*p) for p in pts)) + " Z"

    top = [(0, -1), (k, -.5), (0, 0), (-k, -.5)]
    left = [(-k, -.5), (0, 0), (0, 1), (-k, .5)]
    right = [(0, 0), (k, -.5), (k, .5), (0, 1)]
    f.add("noir", poly(right))
    f.add("ombrage", poly([(-k, .1), (0, .6), (0, 1), (-k, .5)]), direction=-90 + ang)
    f.add("contour", poly([(0, -1), (k, -.5), (k, .5), (0, 1), (-k, .5), (-k, -.5)]))
    f.add("interieur", poly(top))
    f.add("interieur", "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in (q(0, 0), q(0, 1))))
    faces_def = [  # origine, U, V
        ((0, -1), (k, .5), (-k, .5), faces[0], "noir-fin"),
        ((-k, -.5), (k, .5), (0, 1), faces[1], "noir-fin"),
        ((0, 0), (k, -.5), (0, 1), faces[2], "rehauts"),
    ]
    for (ox, oy), (ux, uy), (vx, vy), n, layer in faces_def:
        for u, v in PIPS[n]:
            x, y = ox + u * ux + v * vx, oy + u * uy + v * vy
            r = .085
            f.add(layer, P(*q(x, y), a, ang).M(-r, 0).C(-r, -r * .55, r, -r * .55, r, 0)
                  .C(r, r * .55, -r, r * .55, -r, 0).Z())


# --------------------------------------------------------------------------- cartes

def enseigne(f: Flash, kind: str, cx, cy, s, ang=0.0, couche=None):
    """Symbole de carte : coeur, carreau (rouges), pique, trefle (noirs). `s` = demi-hauteur mm."""
    p = P(cx, cy, s, ang)
    if kind == "coeur":
        p.M(0, 1).C(-.55, .5, -1, .15, -1, -.3).C(-1, -.7, -.7, -.95, -.45, -.95).C(-.2, -.95, -.05, -.8, 0, -.6) \
            .C(.05, -.8, .2, -.95, .45, -.95).C(.7, -.95, 1, -.7, 1, -.3).C(1, .15, .55, .5, 0, 1).Z()
    elif kind == "carreau":
        p.M(0, -1).C(.25, -.6, .45, -.3, .72, 0).C(.45, .3, .25, .6, 0, 1).C(-.25, .6, -.45, .3, -.72, 0) \
            .C(-.45, -.3, -.25, -.6, 0, -1).Z()
    elif kind == "pique":
        p.M(0, -1).C(.3, -.55, 1, -.25, 1, .22).C(1, .62, .5, .78, .12, .45).L(.32, 1).L(-.32, 1).L(-.12, .45) \
            .C(-.5, .78, -1, .62, -1, .22).C(-1, -.25, -.3, -.55, 0, -1).Z()
    else:  # trefle
        p.M(0, -1).C(.45, -1, .55, -.45, .3, -.22).C(.7, -.5, 1.1, -.1, .9, .25).C(.75, .55, .35, .5, .15, .3) \
            .L(.3, 1).L(-.3, 1).L(-.15, .3).C(-.35, .5, -.75, .55, -.9, .25).C(-1.1, -.1, -.7, -.5, -.3, -.22) \
            .C(-.55, -.45, -.45, -1, 0, -1).Z()
    rouge = kind in ("coeur", "carreau")
    f.add(couche or ("rouge" if rouge else "noir-fin"), p)
    f.add("details" if s < 4 else "contour", p)


def carte(f: Flash, cx, cy, h, valeur="A", kind="pique", ang=0.0):
    """Carte à jouer (h = hauteur mm, ratio 0,7) : fond peau, index coin + grande enseigne."""
    w = h * .7
    r = h * .06

    def q(x, y):
        X, Y = rot(x, y, ang)
        return f"{cx + X:.2f} {cy + Y:.2f}"
    hw, hh = w / 2, h / 2
    d = (f"M{q(-hw + r, -hh)} L{q(hw - r, -hh)} Q{q(hw, -hh)} {q(hw, -hh + r)} L{q(hw, hh - r)} "
         f"Q{q(hw, hh)} {q(hw - r, hh)} L{q(-hw + r, hh)} Q{q(-hw, hh)} {q(-hw, hh - r)} "
         f"L{q(-hw, -hh + r)} Q{q(-hw, -hh)} {q(-hw + r, -hh)} Z")
    f.add("contour", d)
    # Ombre portée de la carte sur la peau (à droite et en bas) : donne le volume.
    f.add("ombrage", (f"M{q(hw, -hh + r * 2)} L{q(hw + h * .05, -hh + r * 2 + h * .04)} "
                      f"L{q(hw + h * .05, hh + h * .04)} L{q(-hw + r * 2, hh + h * .04)} L{q(-hw + r * 2, hh)} "
                      f"L{q(hw - r, hh)} Q{q(hw, hh)} {q(hw, hh - r)} Z"), direction=180 + ang)
    big = h * .15
    X, Y = rot(0, h * .02, ang)
    enseigne(f, kind, cx + X, cy + Y, big, ang)
    ih = max(4.5, h * .1)
    for sx, sy, a2 in ((-1, -1, 0), (1, 1, 180)):
        X, Y = rot(sx * (hw - ih * .55), sy * (hh - ih * .75), ang)
        lettrage(f, valeur, cx + X, cy + Y, ih, ang=ang + a2, ombre=False)
        X, Y = rot(sx * (hw - ih * .55), sy * (hh - ih * 1.95), ang)
        enseigne(f, kind, cx + X, cy + Y, ih * .38, ang + a2)


# --------------------------------------------------------------------------- ancre

def ancre(f: Flash, cx, cy, h, ang=0.0):
    """Ancre marine, hauteur `h` mm : organeau, jas (barre) noir, verge et bras d'un seul tenant
    ombrés au whip, pattes (flèches) en noir plein."""
    def p():
        return P(cx, cy, h / 2, ang)
    w = .065
    R1, R2, oy = .8, .66, .05

    def arc(r, t):
        return r * math.cos(math.radians(t)), oy + r * math.sin(math.radians(t))
    tin = math.degrees(math.acos(w / R2))  # angle où le cercle intérieur croise la verge
    a0, a1 = 28, 152
    b = p().M(-w, -.66).L(-w, oy + math.sqrt(R2 ** 2 - w ** 2))
    for i in range(1, 13):
        b.L(*arc(R2, (180 - tin) + (a1 - (180 - tin)) * i / 12))
    for i in range(0, 25):
        b.L(*arc(R1, a1 - (a1 - a0) * i / 24))
    for i in range(0, 13):
        b.L(*arc(R2, a0 + (tin - a0) * i / 12))
    b.L(w, -.66).Z()
    f.add("ombrage", b, direction=0 + ang)
    f.add("contour", b)
    f.add("interieur", p().M(0, -.62).L(0, .78))
    # Pattes : fers de lance dans le prolongement de chaque bras.
    for t, sgn in ((a0, 1), (a1, -1)):
        xm, ym = arc((R1 + R2) / 2, t)
        tr = math.radians(t)
        tx, ty = (math.sin(tr), -math.cos(tr)) if sgn > 0 else (-math.sin(tr), math.cos(tr))
        if ty > 0:
            tx, ty = -tx, -ty
        nx, ny = -ty, tx
        L1, W1 = .24, .085
        base = (xm - tx * .04, ym - ty * .04)
        apex = (xm + tx * L1, ym + ty * L1)
        patte = (p().M(base[0] + nx * .05, base[1] + ny * .05)
                 .L(base[0] + nx * W1 * 1.5 + tx * .03, base[1] + ny * W1 * 1.5 + ty * .03).L(*apex)
                 .L(base[0] - nx * W1 * 1.5 + tx * .03, base[1] - ny * W1 * 1.5 + ty * .03)
                 .L(base[0] - nx * .05, base[1] - ny * .05).Z())
        f.add("noir", patte).add("contour", patte)
    # Jas : barre horizontale en noir plein avec boules, devant la verge.
    jas = (p().M(-.44, -.76).L(.44, -.76).C(.5, -.76, .52, -.7, .52, -.705).C(.52, -.66, .5, -.66, .44, -.66)
           .L(-.44, -.66).C(-.5, -.66, -.52, -.66, -.52, -.705).C(-.52, -.7, -.5, -.76, -.44, -.76).Z())
    f.add("noir", jas).add("contour", jas)
    for sgn in (-1, 1):
        boule = p().M(sgn * .5, -.775).C(sgn * .58, -.775, sgn * .6, -.71, sgn * .6, -.71) \
            .C(sgn * .6, -.65, sgn * .56, -.635, sgn * .5, -.635).C(sgn * .44, -.635, sgn * .42, -.67, sgn * .42, -.705) \
            .C(sgn * .42, -.74, sgn * .44, -.775, sgn * .5, -.775).Z()
        f.add("noir", boule).add("contour", boule)
    tete = p().M(-w, -.88).L(w, -.88).L(w, -.76).L(-w, -.76).Z()
    f.add("noir", tete).add("contour", tete)
    anneau = p().M(0, -1).C(.09, -1, .11, -.95, .11, -.94).C(.11, -.9, .08, -.88, 0, -.88) \
        .C(-.08, -.88, -.11, -.9, -.11, -.94).C(-.11, -.95, -.09, -1, 0, -1).Z()
    f.add("contour", anneau)
    f.add("rehauts", p().M(-.38, -.735).L(-.1, -.735).L(-.1, -.718).L(-.38, -.718).Z())


# --------------------------------------------------------------------------- crâne

def crane(f: Flash, cx, cy, h, ang=0.0):
    """Crâne de face, hauteur `h` mm : orbites et nez en noir plein, dents, pommettes, whip aux
    tempes et sous les pommettes. La peau fait le blanc de l'os."""
    def p():
        return P(cx, cy, h / 1.72, ang)
    tete = (p().M(0, -1).C(.56, -1, .82, -.6, .8, -.2).C(.79, .06, .7, .2, .6, .28).L(.52, .44)
            .C(.5, .62, .32, .72, 0, .72).C(-.32, .72, -.5, .62, -.52, .44).L(-.6, .28)
            .C(-.7, .2, -.79, .06, -.8, -.2).C(-.82, -.6, -.56, -1, 0, -1).Z())
    f.add("contour", tete)
    for sgn in (-1, 1):
        orbite = (p().M(sgn * .08, -.12).C(sgn * .1, -.3, sgn * .3, -.34, sgn * .45, -.26)
                  .C(sgn * .58, -.18, sgn * .56, .04, sgn * .4, .1).C(sgn * .26, .15, sgn * .07, .08, sgn * .08, -.12).Z())
        f.add("noir", orbite).add("contour", orbite)
        f.add("ombrage", p().M(sgn * .8, -.2).C(sgn * .82, -.6, sgn * .56, -1, 0, -1)
              .C(sgn * .45, -.88, sgn * .64, -.55, sgn * .62, -.2).Z(), direction=(0 if sgn > 0 else 180) + 180 + ang)
        f.add("interieur", p().M(sgn * .6, .24).C(sgn * .5, .2, sgn * .4, .24, sgn * .3, .34))
        f.add("ombrage", p().M(sgn * .6, .26).C(sgn * .5, .22, sgn * .4, .26, sgn * .3, .36)
              .C(sgn * .42, .36, sgn * .5, .36, sgn * .53, .42).Z(), direction=90 + ang)
        f.add("rehauts", p().M(sgn * .3, -.2).C(sgn * .36, -.24, sgn * .43, -.22, sgn * .46, -.17)
              .C(sgn * .4, -.19, sgn * .35, -.19, sgn * .3, -.16).Z())
    nez = p().M(0, .12).C(.03, .17, .12, .26, .07, .32).C(.04, .34, .02, .31, 0, .28) \
        .C(-.02, .31, -.04, .34, -.07, .32).C(-.12, .26, -.03, .17, 0, .12).Z()
    f.add("noir", nez).add("contour", nez)
    # Dents : bande, ligne d'occlusion et séparations.
    f.add("interieur", p().M(-.34, .42).C(-.2, .46, .2, .46, .34, .42))
    f.add("interieur", p().M(-.33, .54).C(-.2, .57, .2, .57, .33, .54))
    for x in (-.24, -.12, 0, .12, .24):
        f.add("details", p().M(x, .44 + abs(x) * -.05).L(x, .66 - abs(x) * .25))
    f.add("ombrage", p().M(-.52, .44).C(-.5, .62, -.32, .72, 0, .72).C(.32, .72, .5, .62, .52, .44)
          .C(.42, .56, .3, .64, 0, .65).C(-.3, .64, -.42, .56, -.52, .44).Z(), direction=-90 + ang)
