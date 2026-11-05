"""Bestiaire et grands motifs old school : panthère, serpent, flammes, toile d'araignée,
bateau, phare, pin-up. Mêmes conventions que buk_composants / buk_classiques.
Fiche : references/motifs/BESTIAIRE.md.
"""
from __future__ import annotations

import math

from buk_composants import Flash, P, reserve, rose


# --------------------------------------------------------------------------- outils

def _cubic(p0, p1, p2, p3, n=16):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
                    mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]))
    return out


def courbe(*segs, n=16):
    """Chaîne de Béziers cubiques [(p0,p1,p2,p3), (p3,p4,p5,p6), …] → liste de points."""
    pts = []
    for k, s in enumerate(segs):
        c = _cubic(*s, n=n)
        pts += c if k == 0 else c[1:]
    return pts


def poly(p: P, pts, close=True):
    p.M(*pts[0])
    for q in pts[1:]:
        p.L(*q)
    return p.Z() if close else p


def lisse(p: P, pts, pointes=(), tension=.5):
    """Contour fermé lissé (Catmull-Rom → Béziers) passant par `pts` ; les indices de `pointes`
    restent anguleux (pointes de touffes, d'oreilles, de flammes)."""
    n = len(pts)
    p.M(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        k1 = 0 if i in pointes else tension / 3
        k2 = 0 if (i + 1) % n in pointes else tension / 3
        c1 = (p1[0] + (p2[0] - p0[0]) * k1, p1[1] + (p2[1] - p0[1]) * k1)
        c2 = (p2[0] - (p3[0] - p1[0]) * k2, p2[1] - (p3[1] - p1[1]) * k2)
        p.C(*c1, *c2, *p2)
    return p.Z()


def bande(pts, largeur):
    """Contour d'une bande d'épaisseur variable le long d'une ligne de points.

    `largeur(t)` donne la demi-largeur pour t ∈ [0, 1]. Renvoie (bord gauche, bord droit).
    """
    g, d = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = largeur(i / (n - 1))
        g.append((x + nx * w, y + ny * w))
        d.append((x - nx * w, y - ny * w))
    return g, d


# --------------------------------------------------------------------------- panthère

def panthere(f: Flash, cx, cy, h, ang=0.0):
    """Tête de panthère de face, rictus, hauteur `h` mm.

    Sujet noir lu par ses réserves : touffes de joues dentelées, pelage du front et des joues en
    petits traits réservés, arcades qui plongent vers le nez (colère), yeux à pupille fendue,
    rides du rictus sur l'arête du nez, truffe cernée, coussinets à moustaches. Grande gueule
    rouge, crocs et rangées de dents blancs, langue ombrée vers la gorge.
    """
    def p():
        return P(cx, cy, h / 2, ang)

    # Silhouette lissée : oreilles en arrière, touffes de joues pointues, mâchoire ronde.
    droite = [(.3, -.7), (.58, -.95), (.7, -.62), (.8, -.44), (.93, -.25), (.84, -.17), (1.0, -.04), (.86, .03),
              (.96, .19), (.79, .21), (.84, .37), (.67, .38), (.58, .64), (.32, .87)]
    pts = [(0, -.68)] + droite + [(0, .95)] + [(-x, y) for x, y in reversed(droite)]
    pointes = {i for i, q in enumerate(pts) if q[0] and abs(q[0]) in (.58, .93, 1.0, .96, .84) and q[1] in (-.95, -.25, -.04, .19, .37)}
    tete = lisse(p(), pts, pointes)
    trous = []
    fourrure = []
    for s in (-1, 1):
        # Œil en colère : coin intérieur bas, coin extérieur haut.
        oeil = p().M(s * .12, -.2).C(s * .2, -.33, s * .38, -.42, s * .5, -.37).C(s * .42, -.25, s * .26, -.18, s * .12, -.2).Z()
        trous.append(str(oeil))
        f.add("noir-fin", p().M(s * .32, -.36).C(s * .345, -.33, s * .345, -.23, s * .32, -.2).C(s * .295, -.23, s * .295, -.33, s * .32, -.36).Z())
        f.add("rehauts", p().M(s * .37, -.33).C(s * .385, -.335, s * .395, -.32, s * .38, -.305).C(s * .365, -.305, s * .36, -.32, s * .37, -.33).Z())
        # Arcade qui plonge vers le nez, paupière.
        trous.append(str(reserve(p(), s * .08, -.3, s * .22, -.42, s * .42, -.52, s * .56, -.46, .022, .006)))
        # Oreille : intérieur rouge, touffe.
        oreille = p().M(s * .42, -.72).C(s * .5, -.8, s * .55, -.86, s * .57, -.88).C(s * .62, -.78, s * .64, -.7, s * .64, -.64).Z()
        trous.append(str(oreille))
        f.add("rouge", oreille)
        for k in range(3):
            fourrure.append(str(reserve(p(), s * (.5 + k * .04), -.66, s * (.52 + k * .04), -.72, s * (.53 + k * .03), -.76,
                                        s * (.54 + k * .03), -.8, .008, .002)))
        # Pelage des joues : traits courbes rayonnants.
        for k in range(6):
            y = -.15 + k * .085
            x = .58 + k * .02
            fourrure.append(str(reserve(p(), s * (x - .14), y - .02, s * (x - .06), y, s * x, y + .03, s * (x + .08), y + .02, .009, .002)))
        # Coussinets : trois rangées de points.
        for row in range(3):
            for k in range(3):
                x, y = .14 + k * .055 + row * .02, .15 + row * .045
                trous.append(str(p().M(s * x - .012, y).C(s * x - .012, y - .016, s * x + .012, y - .016, s * x + .012, y)
                                 .C(s * x + .012, y + .016, s * x - .012, y + .016, s * x - .012, y).Z()))
        # Moustaches (au-delà de la tête, en traits fins).
        for k, dy in enumerate((-.02, .05, .12)):
            f.add("details", p().M(s * .82, .14 + dy).C(s * .95, .1 + dy * 1.5, s * 1.05, .1 + dy * 2, s * 1.14, .12 + dy * 2.6))
    # Front : rangées de petits chevrons de pelage.
    for row, y in enumerate((-.62, -.54)):
        for k in range(-2 + row, 3 - row):
            x = k * .1
            fourrure.append(str(reserve(p(), x - .035, y - .02, x - .015, y + .01, x + .015, y + .01, x + .035, y - .02, .008, .003)))
    # Rides du rictus sur l'arête du nez.
    for k, y in enumerate((-.14, -.07, 0)):
        w = .1 + k * .02
        trous.append(str(reserve(p(), -w, y + .02, -w * .4, y - .025, w * .4, y - .025, w, y + .02, .014, .014)))
    # Truffe cernée de peau, philtrum.
    truffe = p().M(-.15, .05).C(-.06, .01, .06, .01, .15, .05).C(.11, .14, .05, .19, 0, .21).C(-.05, .19, -.11, .14, -.15, .05).Z()
    cerne = p().M(-.19, .04).C(-.07, -.03, .07, -.03, .19, .04).C(.14, .17, .06, .24, 0, .26).C(-.06, .24, -.14, .17, -.19, .04).Z()
    trous.append(f"{cerne} {truffe}")
    trous.append(str(reserve(p(), 0, .25, .0, .27, .0, .29, 0, .31, .012, .012)))
    # Gueule ouverte.
    gueule = p().M(-.46, .33).C(-.3, .28, -.12, .34, 0, .3).C(.12, .34, .3, .28, .46, .33) \
        .C(.4, .6, .2, .78, 0, .8).C(-.2, .78, -.4, .6, -.46, .33).Z()
    trous.append(str(gueule))
    f.add("noir", f"{tete} " + " ".join(trous + fourrure))
    f.add("contour", tete).add("contour", gueule)
    f.add("rouge", gueule)
    f.add("ombrage", p().M(-.44, .34).C(-.3, .3, -.12, .36, 0, .32).C(.12, .36, .3, .3, .44, .34)
          .C(.3, .48, -.3, .48, -.44, .34).Z(), direction=90 + ang)
    f.add("interieur", p().M(-.26, .62).C(-.16, .52, .16, .52, .26, .62))
    for s in (-1, 1):
        croc_h = p().M(s * .34, .31).C(s * .33, .42, s * .31, .52, s * .27, .58).C(s * .26, .48, s * .25, .38, s * .22, .31).Z()
        croc_b = p().M(s * .3, .7).C(s * .29, .62, s * .27, .56, s * .23, .52).C(s * .23, .6, s * .22, .66, s * .19, .73).Z()
        for c in (croc_h, croc_b):
            f.add("rehauts", c).add("details", c)
        for k in range(2):
            x = .06 + k * .07
            dent = p().M(s * x, .31).L(s * (x + .05), .32).L(s * (x + .025), .38).Z()
            f.add("rehauts", dent).add("details", dent)
            dent_b = p().M(s * (x - .01), .77).L(s * (x + .04), .75).L(s * (x + .015), .7).Z()
            f.add("rehauts", dent_b).add("details", dent_b)


# --------------------------------------------------------------------------- serpent

def serpent(f: Flash, cx, cy, h, ang=0.0, flip=False):
    """Serpent en S, anneaux rouge / noir / peau (palette buk), tête gueule ouverte en haut à
    gauche, langue fourchue rouge. `h` ≈ hauteur totale en mm."""
    S = h / 2

    def T(pt):
        x, y = pt
        if flip:
            x = -x
        a = math.radians(ang)
        return (cx + S * (x * math.cos(a) - y * math.sin(a)), cy + S * (x * math.sin(a) + y * math.cos(a)))

    centre = courbe(((.75, .95), (1.05, .7), (.7, .35), (.2, .4)),
                    ((.2, .4), (-.4, .45), (-.8, .1), (-.45, -.2)),
                    ((-.45, -.2), (-.05, -.48), (.55, -.48), (.2, -.62)), n=24)
    g, d = bande(centre, lambda t: .015 + .13 * min(1, t * 2.2) - (.03 if t > .92 else 0))
    corps = [T(q) for q in g + d[::-1]]
    f.add("contour", "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in corps) + " Z")
    # Anneaux sur le dos (du bord g jusqu'à la ligne du ventre m) : rouge large, noir, peau, noir.
    m = [(dq[0] + (gq[0] - dq[0]) * .32, dq[1] + (gq[1] - dq[1]) * .32) for gq, dq in zip(g, d)]
    n = len(centre)
    cycle = [("rouge", 5), ("noir", 2), (None, 2), ("noir", 2)]
    i, k = 0, 0
    while i < n - 3:
        layer, step = cycle[k % 4]
        j = min(n - 1, i + step)
        quad = [T(q) for q in g[i:j + 1] + m[i:j + 1][::-1]]
        dq = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in quad) + " Z"
        if layer:
            f.add(layer, dq)
        a1, b1 = T(g[j]), T(m[j])
        f.add("details", f"M{a1[0]:.2f} {a1[1]:.2f} L{b1[0]:.2f} {b1[1]:.2f}")
        i, k = j, k + 1
    # Ventre : bande de peau continue, écailles en échelle.
    ligne = [T(q) for q in m[1:-2]]
    f.add("interieur", "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in ligne))
    for i in range(2, len(centre) - 3):
        a1, b1 = T(m[i]), T(d[i])
        f.add("details", f"M{a1[0]:.2f} {a1[1]:.2f} L{b1[0]:.2f} {b1[1]:.2f}")
    f.add("ombrage", "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in [T(q) for q in m[1:-2]] +
                                       [T(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)) for a, b in zip(m[1:-2][::-1], d[1:-2][::-1])]) + " Z",
          direction=None)

    # Tête en coin, gueule grande ouverte, au bout du corps (repère u = axe de la tête).
    hx, hy = centre[-1]
    a0 = math.atan2(centre[-1][1] - centre[-5][1], centre[-1][0] - centre[-5][0])
    ux, uy = math.cos(a0), math.sin(a0)
    vx, vy = -uy, ux
    K = 1.95

    def L(u, v):
        u, v = u * K, v * K
        return T((hx + ux * u + vx * v, hy + uy * u + vy * v))

    def path(pts, close=True):
        return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + (" Z" if close else "")

    def lisse_pts(pts):
        q = P(0, 0, 1)
        lisse(q, pts)
        return str(q)
    sup = [L(-.04, .075), L(.06, .1), L(.15, .12), L(.22, .1), L(.3, .075), L(.36, .045), L(.34, .02), L(.2, .015), L(.05, .01)]
    inf = [L(.05, -.015), L(.16, -.04), L(.27, -.08), L(.3, -.1), L(.27, -.11), L(.15, -.09), L(.03, -.075), L(-.04, -.07)]
    bouche = [L(.05, -.0), L(.2, .015), L(.34, .02), L(.3, -.03), L(.27, -.08), L(.16, -.04)]
    for pts in (sup, inf):
        d = lisse_pts(pts)
        f.masquer_forme(d)
        f.add("noir", d).add("contour", d)
    f.add("rouge", path(bouche)).add("interieur", path(bouche, False))
    # Arcade, œil fendu, narine, écailles de la tête réservées.
    f.add("interieur", path([L(.1, .095), L(.15, .108), L(.21, .1)], False))
    ex, ey = L(.155, .075)
    r = .02 * S * K
    f.add("rehauts", f"M{ex - r:.2f} {ey:.2f} C{ex - r:.2f} {ey - r * 1.2:.2f} {ex + r:.2f} {ey - r * 1.2:.2f} {ex + r:.2f} {ey:.2f} "
                     f"C{ex + r:.2f} {ey + r * 1.2:.2f} {ex - r:.2f} {ey + r * 1.2:.2f} {ex - r:.2f} {ey:.2f} Z")
    px1, py1 = L(.155, .09)
    px2, py2 = L(.155, .06)
    f.add("details", f"M{px1:.2f} {py1:.2f} L{px2:.2f} {py2:.2f}")
    # Crochets (haut, recourbés) et langue fourchue qui sort de la gueule.
    for u0 in (.3, .22):
        croc = [L(u0, .018), L(u0 + .022, .016), L(u0 + .004, -.04)]
        f.add("rehauts", path(croc)).add("details", path(croc))
    langue = [L(.12, -.02), L(.32, -.03), L(.46, -.02), L(.53, .02), L(.48, -.035), L(.55, -.07), L(.46, -.05), L(.32, -.045), L(.12, -.035)]
    f.add("rouge", path(langue)).add("details", path(langue))


# --------------------------------------------------------------------------- flammes

def flammes(f: Flash, cx, cy, largeur, hauteur, n=5, ang=0.0):
    """Rangée de langues de feu posée sur (cx, cy) (base au centre), une seule silhouette.

    Rouge plein, whip noir qui monte depuis la base, une langue intérieure par flamme. Hauteurs
    alternées (la plus haute au centre), pointes qui se recourbent vers l'extérieur.
    """
    def p():
        return P(cx, cy, 1, ang)
    w = largeur / n
    hs = [hauteur * (.68 + .32 * (1 - abs(i - (n - 1) / 2) / ((n - 1) / 2 + 1e-9))) for i in range(n)]
    sil = p().M(-largeur / 2, 0)
    for i in range(n):
        x0 = -largeur / 2 + i * w
        side = -1 if i < (n - 1) / 2 else 1
        tip = (x0 + w * (.5 + side * .35), -hs[i])
        sil.C(x0 - w * .2, -hs[i] * .3, x0 + w * .6, -hs[i] * .45, x0 + w * .3, -hs[i] * .72)
        sil.C(x0 + w * .1, -hs[i] * .9, tip[0] - side * w * .45, -hs[i] * .92, *tip)
        valley_y = -min(hs[i], hs[i + 1] if i + 1 < n else 0) * .32 if i + 1 < n else 0
        sil.C(x0 + w * 1.05, -hs[i] * .7, x0 + w * .7, -hs[i] * .45, x0 + w, valley_y)
        f.add("interieur", p().M(x0 + w * .5, -hs[i] * .18).C(x0 + w * .35, -hs[i] * .38, x0 + w * .62, -hs[i] * .5,
                                                              x0 + w * (.5 + side * .12), -hs[i] * .66))
    sil.C(largeur * .58, hauteur * .12, largeur * .25, hauteur * .2, 0, hauteur * .2) \
        .C(-largeur * .25, hauteur * .2, -largeur * .58, hauteur * .12, -largeur / 2, 0).Z()
    f.add("rouge", sil).add("contour", sil)
    f.add("ombrage", p().M(-largeur / 2, 0).C(-largeur * .58, hauteur * .12, -largeur * .25, hauteur * .2, 0, hauteur * .2)
          .C(largeur * .25, hauteur * .2, largeur * .58, hauteur * .12, largeur / 2, 0)
          .C(largeur * .2, -hauteur * .12, -largeur * .2, -hauteur * .12, -largeur / 2, 0).Z(), direction=-90 + ang)


# --------------------------------------------------------------------------- toile d'araignée

def toile(f: Flash, cx, cy, r, rayons=8, tours=4, ang0=-90.0, ouverture=360.0, araignee=True):
    """Toile d'araignée centrée en (cx, cy), rayon `r` mm. `ouverture` < 360 pour une toile en
    éventail (coude, épaule). Fils en traits fins, tours affaissés vers le centre entre deux
    rayons, petite araignée noire suspendue."""
    full = ouverture >= 359
    n = rayons if full else rayons + 1
    angs = [ang0 + i * ouverture / (rayons if full else rayons) for i in range(n)]
    for a in angs:
        t = math.radians(a)
        f.add("interieur", f"M{cx:.2f} {cy:.2f} L{cx + r * math.cos(t):.2f} {cy + r * math.sin(t):.2f}")
    for k in range(1, tours + 1):
        rr = r * k / tours * .96
        pairs = list(zip(angs, angs[1:] + ([angs[0]] if full else [])))
        for a1, a2 in pairs:
            t1, t2 = math.radians(a1), math.radians(a2)
            x1, y1 = cx + rr * math.cos(t1), cy + rr * math.sin(t1)
            x2, y2 = cx + rr * math.cos(t2), cy + rr * math.sin(t2)
            tm = (t1 + t2) / 2 if abs(a2 - a1) < 180 else (t1 + t2) / 2 + math.pi
            sag = rr * .78
            mx, my = cx + sag * math.cos(tm), cy + sag * math.sin(tm)
            f.add("details", f"M{x1:.2f} {y1:.2f} Q{mx:.2f} {my:.2f} {x2:.2f} {y2:.2f}")
    if araignee:
        t = math.radians(angs[1] if len(angs) > 1 else ang0) + .25
        ax, ay = cx + r * .62 * math.cos(t), cy + r * .62 * math.sin(t)
        s = r * .07
        f.add("details", f"M{ax:.2f} {ay - s * 3:.2f} L{ax:.2f} {ay:.2f}")
        corps = P(ax, ay, s).M(0, -.6).C(.5, -.6, .55, .1, .45, .5).C(.35, 1.2, -.35, 1.2, -.45, .5) \
            .C(-.55, .1, -.5, -.6, 0, -.6).Z()
        f.add("noir-fin", corps)
        for sgn in (-1, 1):
            for k, (dy, ex, ey) in enumerate(((-.3, 1.3, -.9), (0, 1.5, -.2), (.3, 1.5, .6), (.55, 1.2, 1.3))):
                f.add("details", P(ax, ay, s).M(sgn * .4, dy).Q(sgn * (ex * .8), dy - .4, sgn * ex, ey))


# --------------------------------------------------------------------------- bateau

def bateau(f: Flash, cx, cy, l, ang=0.0):
    """Trois-mâts sous voiles, longueur `l` mm, proue à droite. Coque noire à sabords réservés,
    liston rouge, voiles en peau gonflées avec whip côté vent, flammes rouges en tête de mât,
    vagues en volutes."""
    def p():
        return P(cx, cy, l / 2, ang)
    coque = p().M(-.9, .3).L(.95, .22).L(1.05, .16).C(.9, .45, .7, .62, .4, .66).L(-.65, .66).C(-.8, .6, -.88, .45, -.9, .3).Z()
    sabords = " ".join(str(p().M(x - .025, .4).L(x + .025, .4).L(x + .025, .45).L(x - .025, .45).Z())
                       for x in (-.6, -.42, -.24, -.06, .12, .3, .48))
    liston = p().M(-.86, .31).L(.95, .23).L(.91, .27).L(-.85, .35).Z()
    f.add("noir", f"{coque} {sabords} {liston}").add("contour", coque)
    f.add("rouge", liston)
    f.add("interieur", p().M(-.87, .35).L(.9, .27))
    mats = [(-.5, -.9), (.05, -1.05), (.55, -.85)]
    for x, top in mats:
        f.add("contour", p().M(x, .3).L(x, top))
        flamme = p().M(x, top).C(x - .08, top - .02, x - .16, top + .02, x - .22, top - .02).C(x - .16, top + .04, x - .08, top + .06, x, top + .05).Z()
        f.add("rouge", flamme).add("details", flamme)
        y = top + .1
        largeur = .13
        for k in range(3):  # trois voiles carrées par mât, plus larges vers le bas
            h = .22 + k * .02
            w = largeur + k * .035
            voile = p().M(x - w, y).L(x + w, y).C(x + w + .06, y + h * .4, x + w + .06, y + h * .7, x + w, y + h) \
                .L(x - w, y + h).C(x - w + .07, y + h * .7, x - w + .07, y + h * .4, x - w, y).Z()
            f.add("contour", voile)
            f.add("ombrage", p().M(x - w, y).C(x - w + .07, y + h * .4, x - w + .07, y + h * .7, x - w, y + h)
                  .L(x - w + .1, y + h).C(x - w + .15, y + h * .7, x - w + .15, y + h * .4, x - w + .1, y).Z(),
                  direction=0 + ang)
            f.add("details", p().M(x - w + .03, y + h * .5).C(x - .05, y + h * .58, x + .05, y + h * .58, x + w + .04, y + h * .5))
            y += h + .03
    # Mer : vagues en volutes sous la coque.
    for i, x in enumerate((-.95, -.55, -.15, .25, .65)):
        vague = p().M(x, .62).C(x + .08, .5, x + .26, .5, x + .3, .6).C(x + .3, .66, x + .22, .66, x + .2, .6) \
            .C(x + .24, .74, x + .4, .74, x + .42, .64)
        f.add("interieur", vague)
    mer = p().M(-.9, .68).C(-.5, .64, -.1, .72, .3, .67).C(.6, .63, .85, .7, 1.0, .66) \
        .C(.7, .74, .3, .74, 0, .74).C(-.4, .74, -.7, .74, -.9, .68).Z()
    f.add("ombrage", mer, direction=-90 + ang)


# --------------------------------------------------------------------------- phare

def phare(f: Flash, cx, cy, h, ang=0.0):
    """Phare sur son rocher, hauteur `h` mm : tour effilée à bandes rouges, galerie et dôme noirs,
    lanterne en peau avec rehaut blanc, faisceaux, rochers noirs, vagues."""
    def p():
        return P(cx, cy, h / 2, ang)
    yb, yt, wb, wt = .62, -.42, .2, .13

    def xw(y):
        return wt + (wb - wt) * (y - yt) / (yb - yt)
    tour = p().M(-wb, yb).L(-wt, yt).L(wt, yt).L(wb, yb).Z()
    f.add("contour", tour)
    ys = [yt + (yb - yt) * k / 5 for k in range(6)]
    for k in range(5):
        if k % 2 == 0:
            y1, y2 = ys[k], ys[k + 1]
            f.add("rouge", p().M(-xw(y1), y1).L(xw(y1), y1).L(xw(y2), y2).L(-xw(y2), y2).Z())
        f.add("interieur", p().M(-xw(ys[k + 1]), ys[k + 1]).L(xw(ys[k + 1]), ys[k + 1]))
    f.add("ombrage", p().M(.04, yt).L(wt, yt).L(wb, yb).L(.06, yb).Z(), direction=180 + ang)
    porte = p().M(-.04, yb).L(-.04, .52).C(-.04, .48, .04, .48, .04, .52).L(.04, yb).Z()
    f.add("noir-fin", porte)
    galerie = p().M(-.2, yt).L(.2, yt).L(.2, yt - .05).L(-.2, yt - .05).Z()
    f.add("noir", galerie).add("contour", galerie)
    lanterne = p().M(-.1, yt - .05).L(.1, yt - .05).L(.1, -.66).L(-.1, -.66).Z()
    f.add("contour", lanterne)
    for x in (-.035, .035):
        f.add("details", p().M(x, yt - .05).L(x, -.66))
    f.add("rehauts", p().M(-.07, -.52).L(-.04, -.52).L(-.04, -.6).L(-.07, -.6).Z())
    dome = p().M(-.13, -.66).L(.13, -.66).C(.12, -.76, .05, -.8, 0, -.8).C(-.05, -.8, -.12, -.76, -.13, -.66).Z()
    f.add("noir", dome).add("contour", dome)
    f.add("contour", p().M(0, -.8).L(0, -.88))
    for s in (-1, 1):  # faisceaux
        for dy in (-.12, 0, .12):
            f.add("details", p().M(s * .16, -.56 + dy * .3).L(s * .55, -.56 + dy * 1.6))
    rochers = (p().M(-.55, .78).C(-.5, .6, -.35, .55, -.22, .6).C(-.18, .5, -.05, .52, 0, .58)
               .C(.08, .5, .25, .52, .3, .62).C(.42, .56, .55, .65, .58, .78).Z())
    f.add("noir", str(rochers) + " " + str(reserve(p(), -.45, .7, -.38, .65, -.3, .64, -.24, .66, .012, .006))
          + " " + str(reserve(p(), .32, .7, .38, .66, .44, .67, .5, .72, .012, .006)))
    f.add("contour", rochers)
    for x in (-.85, -.6, .6, .35):
        f.add("interieur", p().M(x, .8).C(x + .06, .7, x + .18, .7, x + .2, .78).C(x + .2, .82, x + .14, .82, x + .13, .78))


# --------------------------------------------------------------------------- pin-up

def pinup(f: Flash, cx, cy, h, ang=0.0, fleur=True):
    """Portrait de pin-up (tête et épaules), hauteur `h` mm. Chevelure noire à boucles réservées,
    visage en peau, paupières baissées à cils, lèvres rouges, rose dans les cheveux."""
    def p():
        return P(cx, cy, h / 2, ang)
    cheveux = (p().M(-.3, .12).C(-.52, .0, -.56, -.45, -.42, -.66).C(-.3, -.86, .1, -.95, .3, -.8)
               .C(.5, -.66, .56, -.3, .44, -.05).C(.5, .2, .46, .38, .36, .45)
               .C(.32, .2, .3, .02, .3, -.08).C(.32, -.3, .2, -.5, 0, -.52)
               .C(-.2, -.5, -.28, -.3, -.28, -.1).C(-.28, .0, -.28, .08, -.3, .12).Z())
    boucles = " ".join(str(reserve(p(), *c, .014, .004)) for c in (
        (-.38, -.55, -.3, -.7, -.12, -.78, .05, -.74),
        (.1, -.84, .28, -.78, .4, -.6, .42, -.4),
        (-.45, -.35, -.48, -.2, -.42, -.05, -.34, .02),
        (.42, -.2, .44, -.05, .42, .1, .38, .25)))
    rx, ry = (float(v) for v in p()._p(.3, -.62).split())
    rr = h * .1
    trou = P(rx, ry, rr * 1.02).M(-1, 0).C(-1, -.56, 1, -.56, 1, 0).C(1, .56, -1, .56, -1, 0).Z()
    trou = P(rx, ry, rr * 1.0).M(-1, 0).C(-1, -1.1, 1, -1.1, 1, 0).C(1, 1.1, -1, 1.1, -1, 0).Z()
    f.add("noir", f"{cheveux} {boucles}" + (f" {trou}" if fleur else "")).add("contour", cheveux)
    # Visage (ovale ouvert en haut, sous la frange) et cou, épaules.
    f.add("contour", p().M(-.28, -.1).C(-.3, .12, -.2, .32, 0, .36).C(.2, .32, .3, .12, .3, -.08))
    f.add("contour", p().M(-.12, .32).L(-.13, .52).C(-.3, .58, -.5, .62, -.62, .78))
    f.add("contour", p().M(.12, .32).L(.13, .52).C(.3, .58, .5, .62, .62, .78))
    f.add("ombrage", p().M(-.12, .34).L(.12, .34).L(.12, .44).C(.04, .42, -.04, .42, -.12, .44).Z(), direction=-90 + ang)
    for s in (-1, 1):  # yeux mi-clos, sourcils
        f.add("interieur", p().M(s * .05, -.1).C(s * .1, -.13, s * .18, -.13, s * .22, -.08))
        f.add("noir-fin", p().M(s * .06, -.1).C(s * .1, -.12, s * .17, -.12, s * .21, -.08).C(s * .17, -.09, s * .1, -.09, s * .06, -.1).Z())
        for k in range(3):
            x = s * (.14 + k * .035)
            f.add("details", p().M(x, -.105 + k * .005).L(x + s * .025, -.135 + k * .008))
        f.add("details", p().M(s * .05, -.2).C(s * .1, -.25, s * .18, -.25, s * .23, -.19))
    f.add("details", p().M(-.01, -.05).C(.02, .02, .02, .06, -.02, .08))
    levres = p().M(-.1, .17).C(-.05, .14, -.02, .13, 0, .15).C(.02, .13, .05, .14, .1, .17) \
        .C(.06, .23, -.06, .23, -.1, .17).Z()
    f.add("rouge", levres).add("interieur", levres)
    f.add("details", p().M(-.09, .17).C(-.03, .18, .03, .18, .09, .17))
    f.add("rehauts", p().M(.02, .195).C(.035, .19, .05, .195, .055, .2).C(.04, .205, .03, .205, .02, .195).Z())
    if fleur:
        rose(f, rx, ry, rr)
