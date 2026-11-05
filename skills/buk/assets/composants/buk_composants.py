"""Bibliothèque de pièces old school pour construire des flashs au contrat buk.

Chaque pièce renvoie des chemins SVG en coordonnées absolues (mm). Les pièces ne savent rien
des couches : c'est le `Flash` qui range chaque chemin dans la bonne couche (technique, aiguille,
encre, ordre). Toutes les fonctions sont paramétrées par un centre, une taille et un angle, pour
qu'une rose, une feuille ou une banderole se recompose à n'importe quelle échelle.

Usage minimal :
    from buk_composants import Flash, rose, feuille
    f = Flash("Rose", 60, 60, placement="mollet")
    rose(f, 30, 28, 18)
    feuille(f, 14, 44, 14, angle=200)
    f.ecrire("rose.svg")
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from buk_lib import inside, path_subpaths  # noqa: E402

NOIR, ROUGE, BLANC = "#111111", "#C1121F", "#FFFFFF"

# Couches standard d'un flash buk : id -> (kind, technique, aiguille, encre, ordre, empilement)
COUCHES = {
    "ombrage":   ("zone", "whip",            "RM9",  "noir",  3, 2),
    "rouge":     ("zone", "solid-red",       "RM11", "rouge", 5, 1),
    "noir":      ("zone", "solid-black",     "RM13", "noir",  4, 3),
    "noir-fin":  ("zone", "solid-black",     "RS9",  "noir",  4, 3),
    "rehauts":   ("zone", "highlight-white", "RL5",  "blanc", 6, 4),
    "contour":   ("line", "bold-line",       "RL11", "noir",  1, 6),
    "interieur": ("line", "lining",          "RL7",  "noir",  2, 5),
    "details":   ("line", "lining",          "RL5",  "noir",  2, 5),
    "lettre-ombre": ("line", "lining",       "RL9",  "noir",  2, 5.5),
    "lettre":    ("line", "bold-line",       "RL14", "noir",  1, 7),
}
STROKE = {"contour": 1.4, "interieur": 1.0, "details": 0.8, "lettre": 1.7, "lettre-ombre": 1.2}
FILL = {"ombrage": NOIR, "rouge": ROUGE, "noir": NOIR, "noir-fin": NOIR, "rehauts": BLANC}


# --------------------------------------------------------------------------- géométrie

def rot(x, y, ang, cx=0.0, cy=0.0):
    a = math.radians(ang)
    return (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))


class P:
    """Constructeur de chemin dans un repère local (unité = `s` mm), tourné de `ang` autour de (cx, cy)."""

    def __init__(self, cx, cy, s=1.0, ang=0.0, flip=False):
        self.cx, self.cy, self.s, self.ang, self.flip = cx, cy, s, ang, flip
        self.d = []

    def _p(self, x, y):
        if self.flip:
            x = -x
        X, Y = rot(x * self.s, y * self.s, self.ang)
        return f"{self.cx + X:.2f} {self.cy + Y:.2f}"

    def M(self, x, y):
        self.d.append("M" + self._p(x, y)); return self

    def L(self, x, y):
        self.d.append("L" + self._p(x, y)); return self

    def C(self, x1, y1, x2, y2, x, y):
        self.d.append("C" + " ".join((self._p(x1, y1), self._p(x2, y2), self._p(x, y)))); return self

    def Q(self, x1, y1, x, y):
        self.d.append("Q" + " ".join((self._p(x1, y1), self._p(x, y)))); return self

    def Z(self):
        self.d.append("Z"); return self

    def __str__(self):
        return " ".join(self.d)


# --------------------------------------------------------------------------- flash

def reserve(pt, x0, y0, x1, y1, x2, y2, x3, y3, w0=.012, w1=.004):
    """Bande de peau effilée le long d'une courbe de Bézier (repère local d'un `P`).

    S'ajoute au chemin d'une zone noire : avec fill-rule evenodd, elle devient une réserve
    (séparation de plumes, nervure, reflet). Largeurs w0 -> w1 en unités locales.
    """
    pts = []
    for i in range(13):
        t = i / 12
        mt = 1 - t
        x = mt**3 * x0 + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t**3 * x3
        y = mt**3 * y0 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t**3 * y3
        dx = 3 * mt * mt * (x1 - x0) + 6 * mt * t * (x2 - x1) + 3 * t * t * (x3 - x2)
        dy = 3 * mt * mt * (y1 - y0) + 6 * mt * t * (y2 - y1) + 3 * t * t * (y3 - y2)
        n = math.hypot(dx, dy) or 1
        pts.append((x, y, -dy / n, dx / n, w0 + (w1 - w0) * t))
    pt.M(pts[0][0] + pts[0][2] * pts[0][4], pts[0][1] + pts[0][3] * pts[0][4])
    for x, y, nx, ny, w in pts[1:]:
        pt.L(x + nx * w, y + ny * w)
    for x, y, nx, ny, w in reversed(pts):
        pt.L(x - nx * w, y - ny * w)
    return pt.Z()


class Flash:
    def __init__(self, titre, largeur_mm, hauteur_mm, placement=""):
        self.titre, self.w, self.h, self.placement = titre, largeur_mm, hauteur_mm, placement
        self.couches = {k: [] for k in COUCHES}
        self.aiguilles = {}
        self.directions = {}

    def add(self, couche, d, direction=None):
        """Ajoute un chemin à une couche. `direction` (degrés) = sens du whip pour cette zone."""
        self.couches[couche].append((str(d), direction))
        return self

    @classmethod
    def depuis_svg(cls, chemin):
        """Charge un flash existant (importé ou dessiné) pour le retoucher avec les pièces buk.

        Chaque couche du SVG est rangée dans la couche standard correspondante ; on peut ensuite
        `masquer(...)` une zone (ancien lettrage), ajouter `lettrage(...)`, des gouttes, etc.
        """
        import xml.etree.ElementTree as ET
        tech2couche = {"bold-line": "contour", "lining": "interieur", "solid-red": "rouge", "solid-black": "noir",
                       "whip": "ombrage", "pepper": "ombrage", "highlight-white": "rehauts"}
        root = ET.parse(chemin).getroot()
        vb = [float(v) for v in root.get("viewBox").split()]
        f = cls(root.get("data-buk-title", Path(chemin).stem), vb[2], vb[3], root.get("data-buk-placement", ""))
        for g in root:
            tech = g.get("data-technique")
            if tech not in tech2couche:
                continue
            couche = tech2couche[tech]
            if couche == "interieur" and g.get("data-needle") == "RL5":
                couche = "details"
            for el in g.iter():
                if el.tag.endswith("path") and el.get("d"):
                    dirv = el.get("data-direction")
                    f.add(couche, el.get("d"), float(dirv) if dirv else None)
        return f

    def masquer(self, x1, y1, x2, y2):
        """Découpe tout ce qui a déjà été dessiné dans le rectangle (x1, y1)-(x2, y2).

        À appeler juste avant de poser un élément « devant » dont l'intérieur est en peau
        (banderole, carte…) : sans ça, le rouge et les traits de derrière transparaîtraient,
        sur l'aperçu comme sur le calque.
        """
        regions = [  # 4 régions convexes disjointes qui forment l'extérieur du rectangle
            [(0, 1, -y1)],                                   # y <= y1
            [(0, -1, y2)],                                   # y >= y2
            [(0, -1, y1), (0, 1, -y2), (1, 0, -x1)],          # y1<y<y2 et x <= x1
            [(0, -1, y1), (0, 1, -y2), (-1, 0, x2)],          # y1<y<y2 et x >= x2
        ]

        def clip(poly, a, b, c):
            out = []
            n = len(poly)
            for i in range(n):
                p1, p2 = poly[i], poly[(i + 1) % n]
                v1, v2 = a * p1[0] + b * p1[1] + c, a * p2[0] + b * p2[1] + c
                if v1 <= 0:
                    out.append(p1)
                if (v1 <= 0) != (v2 <= 0):
                    t = v1 / (v1 - v2)
                    out.append((p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])))
            return out

        def dedans(x, y):
            return x1 < x < x2 and y1 < y < y2

        def fmtp(pts, close):
            return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + (" Z" if close else "")

        for cid, items in self.couches.items():
            kind = COUCHES[cid][0]
            new = []
            for d, direction in items:
                subs, closed = path_subpaths(d)
                pts = [q for sp in subs for q in sp]
                if not pts or (max(q[0] for q in pts) <= x1 or min(q[0] for q in pts) >= x2
                               or max(q[1] for q in pts) <= y1 or min(q[1] for q in pts) >= y2):
                    new.append((d, direction))  # ne touche pas le rectangle : intact
                    continue
                if kind == "zone":
                    parts = []
                    for reg in regions:
                        for sp in subs:
                            poly = sp[:-1] if len(sp) > 1 and sp[0] == sp[-1] else sp
                            for hp in reg:
                                poly = clip(poly, *hp)
                                if len(poly) < 3:
                                    break
                            if len(poly) >= 3:
                                parts.append(fmtp(poly, True))
                    if parts:
                        new.append((" ".join(parts), direction))
                else:
                    runs = []
                    for sp, cl in zip(subs, closed):
                        dense = []
                        for (ax, ay), (bx, by) in zip(sp, sp[1:]):
                            n = max(1, int(math.hypot(bx - ax, by - ay) / .25))
                            dense += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
                        if sp:
                            dense.append(sp[-1])
                        run = []
                        for pt in dense:
                            if dedans(*pt):
                                if len(run) > 1:
                                    runs.append(run)
                                run = []
                            else:
                                run.append(pt)
                        if len(run) > 1:
                            runs.append(run)
                    if runs:
                        new.append((" ".join(fmtp(r, False) for r in runs), direction))
            self.couches[cid] = new
        return self

    def masquer_forme(self, d):
        """Efface les TRAITS déjà dessinés à l'intérieur de la forme `d` (chemin fermé).

        Pour superposer des formes : plume sur plume, anneau sur dague, mèche sur visage. Les zones
        ne sont pas découpées (sous une forme noire elles sont de toute façon couvertes ; pour une
        forme en peau posée devant, combiner avec `masquer` rectangulaire ou réserver).
        """
        polys = [sp for sp in path_subpaths(str(d))[0] if len(sp) > 2]
        if not polys:
            return self
        xs = [q[0] for sp in polys for q in sp]
        ys = [q[1] for sp in polys for q in sp]
        bx1, bx2, by1, by2 = min(xs), max(xs), min(ys), max(ys)

        def dedans(x, y):
            return bx1 < x < bx2 and by1 < y < by2 and inside((x, y), polys)

        for cid, items in self.couches.items():
            if COUCHES[cid][0] != "line":
                continue
            new = []
            for dd, direction in items:
                subs, _ = path_subpaths(dd)
                runs = []
                for sp in subs:
                    dense = []
                    for (ax, ay), (bx, by) in zip(sp, sp[1:]):
                        n = max(1, int(math.hypot(bx - ax, by - ay) / .2))
                        dense += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
                    if sp:
                        dense.append(sp[-1])
                    run = []
                    for pt in dense:
                        if dedans(*pt):
                            if len(run) > 1:
                                runs.append(run)
                            run = []
                        else:
                            run.append(pt)
                    if len(run) > 1:
                        runs.append(run)
                if runs:
                    new.append((" ".join("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in r) for r in runs), direction))
            self.couches[cid] = new
        return self

    def aiguille(self, couche, code):
        self.aiguilles[couche] = code
        return self

    def svg(self) -> str:
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:g}mm" height="{self.h:g}mm" '
               f'viewBox="0 0 {self.w:g} {self.h:g}" data-buk-title="{self.titre}"'
               + (f' data-buk-placement="{self.placement}"' if self.placement else "") + ">"]
        for cid, (kind, tech, needle, ink, order, _) in sorted(COUCHES.items(), key=lambda kv: kv[1][5]):
            items = self.couches[cid]
            if not items:
                continue
            needle = self.aiguilles.get(cid, needle)
            out.append(f'  <g id="{cid}" data-buk-kind="{kind}" data-technique="{tech}" '
                       f'data-needle="{needle}" data-ink="{ink}" data-order="{order}">')
            for d, direction in items:
                dd = f' data-direction="{direction:g}"' if direction is not None else ""
                if kind == "line":
                    out.append(f'    <path fill="none" stroke="{NOIR}" stroke-width="{STROKE[cid]}" '
                               f'stroke-linecap="round" stroke-linejoin="round" d="{d}"/>')
                else:
                    out.append(f'    <path fill="{FILL[cid]}" fill-rule="evenodd"{dd} d="{d}"/>')
            out.append("  </g>")
        out.append("</svg>")
        return "\n".join(out) + "\n"

    def ecrire(self, chemin):
        Path(chemin).write_text(self.svg(), encoding="utf-8")
        return chemin


# --------------------------------------------------------------------------- pièces

def goutte(f: Flash, cx, cy, s, ang=0.0):
    """Goutte de sang : rouge, contour fin, reflet blanc. `s` ≈ demi-largeur en mm."""
    p = P(cx, cy, s, ang).M(0, -1.6).C(.2, -.9, 1, -.3, 1, .2).C(1, .8, .55, 1.1, 0, 1.1) \
        .C(-.55, 1.1, -1, .8, -1, .2).C(-1, -.3, -.2, -.9, 0, -1.6).Z()
    f.add("rouge", p).add("interieur", p)
    f.add("rehauts", P(cx, cy, s, ang).M(.35, -.15).C(.62, -.05, .62, .35, .45, .45)
          .C(.38, .25, .32, .05, .35, -.15).Z())


def feuille(f: Flash, cx, cy, longueur, angle=0.0, flip=False):
    """Feuille old school : noir plein, nervure centrale et 3 nervures latérales réservées en peau.

    (cx, cy) = point d'attache sur la tige ; la feuille pointe dans la direction `angle`
    (0 = vers la droite). Les nervures sont des trous dans le noir (règle pair-impair), pas des
    traits : sur la peau, ce sont des lignes de réserve.
    """
    L = longueur
    out = P(cx, cy, L, angle - 90, flip)  # repère local : la feuille pousse vers +y
    out.M(0, 0).C(.32, .12, .42, .5, 0, 1).C(-.36, .55, -.34, .14, 0, 0).Z()
    nerv = P(cx, cy, L, angle - 90, flip)
    nerv.M(.015, .08).C(.06, .4, .04, .7, 0, .9).C(-.035, .7, -.06, .4, -.015, .08).Z()
    for t, side in ((.28, 1), (.44, -1), (.6, 1)):
        nerv.M(side * .025, t).Q(side * .1, t + .07, side * .15, t + .2).Q(side * .08, t + .1, side * .025, t + .045).Z()
    f.add("noir", f"{out} {nerv}")
    f.add("contour", P(cx, cy, L, angle - 90, flip).M(0, 0).C(.32, .12, .42, .5, 0, 1)
          .C(-.36, .55, -.34, .14, 0, 0).Z())


def rose(f: Flash, cx, cy, r, ombre=True):
    """Rose traditionnelle vue de 3/4 haut, rayon `r` mm (cf. references/motifs/ROSE.md).

    Construction :
      1. silhouette festonnée : 2 lobes arrière (encoche au centre), 2 pétales latéraux à pointe
         roulée, 2 lobes bas ;
      2. coupe : ouverture en haut (bord arrière + lèvre avant), cœur en spirale de « C » ;
      3. pétales avant : deux courbes en S qui enveloppent la coupe, lèvre basse ;
      4. plis des pétales latéraux ;
      5. ombre : fond de coupe en noir plein, whip sous chaque lèvre et à la base de chaque
         pétale — toujours d'un seul côté du trait.
    """
    def p():
        return P(cx, cy, r)

    sil = (p().M(-.38, -.55).C(-.5, -.88, -.1, -.97, 0, -.68).C(.12, -.97, .56, -.9, .45, -.55)
           .C(.78, -.64, 1.0, -.36, .9, -.04).C(1.0, .27, .86, .56, .6, .62)
           .C(.55, .87, .24, .97, .04, .83).C(-.2, 1.0, -.62, .9, -.62, .62)
           .C(-.9, .56, -1.02, .2, -.9, -.07).C(-.99, -.4, -.72, -.64, -.38, -.55).Z())
    f.add("rouge", sil)
    f.add("contour", sil)

    # Coupe : bord arrière + lèvre avant.
    back = p().M(-.42, -.38).C(-.35, -.64, .35, -.64, .42, -.38)
    lip = p().M(-.42, -.38).C(-.38, -.1, .38, -.1, .42, -.38)
    f.add("contour", back).add("contour", lip)
    # Cœur : deux « C » emboîtés.
    f.add("interieur", p().M(.26, -.42).C(.2, -.55, -.18, -.55, -.22, -.42).C(-.26, -.3, .02, -.26, .1, -.36))
    f.add("details", p().M(.04, -.42).C(.0, -.47, -.1, -.46, -.1, -.4))
    # Pétales avant en S + lèvre basse.
    f.add("interieur", p().M(-.42, -.36).C(-.62, -.12, -.6, .2, -.33, .33))
    f.add("interieur", p().M(.42, -.36).C(.72, .0, .5, .46, .04, .47).C(-.1, .47, -.16, .38, -.07, .32))
    f.add("interieur", p().M(-.62, .62).C(-.32, .46, .3, .46, .6, .62))
    # Plis des pétales latéraux et de l'arrière.
    f.add("interieur", p().M(-.9, -.07).C(-.76, -.05, -.64, .02, -.58, .12))
    f.add("interieur", p().M(.9, -.04).C(.76, -.02, .65, .05, .6, .14))
    f.add("details", p().M(0, -.68).C(-.02, -.62, .0, -.58, .04, -.55))

    if ombre:
        f.add("noir-fin", p().M(-.42, -.38).C(-.35, -.64, .35, -.64, .42, -.38)
              .C(.3, -.5, -.3, -.5, -.42, -.38).Z())
        f.add("ombrage", p().M(-.42, -.36).C(-.38, -.1, .38, -.1, .42, -.36)
              .C(.42, .02, -.42, .02, -.42, -.36).Z(), direction=90)
        f.add("ombrage", p().M(-.42, -.4).C(-.35, -.64, .35, -.64, .42, -.4)
              .C(.38, -.78, -.38, -.78, -.42, -.4).Z(), direction=-90)
        f.add("ombrage", p().M(-.61, .61).C(-.31, .45, .29, .45, .59, .61)
              .C(.3, .3, -.3, .3, -.61, .61).Z(), direction=-90)
        f.add("ombrage", p().M(-.9, -.07).C(-.76, -.05, -.64, .02, -.58, .12)
              .C(-.66, .26, -.84, .2, -.9, -.07).Z(), direction=135)
        f.add("ombrage", p().M(.9, -.04).C(.76, -.02, .65, .05, .6, .14)
              .C(.68, .28, .86, .22, .9, -.04).Z(), direction=45)
        f.add("ombrage", p().M(-.33, .33).C(-.6, .2, -.62, -.12, -.42, -.34)
              .C(-.5, -.05, -.45, .2, -.33, .33).Z(), direction=0)
        f.add("ombrage", p().M(.04, .47).C(.5, .46, .72, .0, .43, -.33)
              .C(.58, .02, .42, .36, .04, .47).Z(), direction=180)
    f.add("rehauts", p().M(-.42, -.7).C(-.34, -.82, -.18, -.84, -.1, -.78).C(-.2, -.77, -.3, -.73, -.37, -.65)
          .C(-.42, -.64, -.45, -.67, -.42, -.7).Z())
    f.add("rehauts", p().M(.72, -.42).C(.8, -.38, .86, -.28, .86, -.18).C(.82, -.26, .76, -.33, .7, -.38)
          .C(.68, -.4, .69, -.43, .72, -.42).Z())


def banderole(f: Flash, x1, x2, y, h, pli=6.0):
    """Banderole horizontale de x1 à x2, hauteur h, extrémités repliées avec queue d'aronde.

    Le fond reste en peau (pour le lettrage) ; les replis sont en noir plein, le dessous des plis
    est ombré.
    """
    cy = y
    top, bot = cy - h / 2, cy + h / 2
    # Bande centrale légèrement cintrée.
    band = (f"M{x1 + pli:.2f} {top:.2f} C{(x1 + x2) / 2 - 10:.2f} {top - 2:.2f} {(x1 + x2) / 2 + 10:.2f} {top - 2:.2f} "
            f"{x2 - pli:.2f} {top:.2f} L{x2 - pli:.2f} {bot:.2f} C{(x1 + x2) / 2 + 10:.2f} {bot - 2:.2f} "
            f"{(x1 + x2) / 2 - 10:.2f} {bot - 2:.2f} {x1 + pli:.2f} {bot:.2f} Z")
    f.add("contour", band)
    for side in (-1, 1):
        xe = x1 if side < 0 else x2
        xi = x1 + pli if side < 0 else x2 - pli
        # Queue (dépasse en bas, découpée en V).
        ya, yb = top + h * .35, bot + h * .35
        tail = (f"M{xi:.2f} {ya:.2f} L{xe:.2f} {ya:.2f} L{xe - side * h * .3:.2f} {(ya + yb) / 2:.2f} "
                f"L{xe:.2f} {yb:.2f} L{xi:.2f} {yb:.2f} Z")
        f.add("contour", tail)
        # Départ de la queue en noir plein : le ruban passe derrière la bande.
        rentre = (f"M{xi:.2f} {ya:.2f} L{xi + side * pli * .45:.2f} {ya:.2f} "
                  f"L{xi + side * pli * .45:.2f} {yb:.2f} L{xi:.2f} {yb:.2f} Z")
        f.add("noir-fin", rentre)
        f.add("interieur", f"M{xi + side * pli * .45:.2f} {ya:.2f} L{xi + side * pli * .45:.2f} {yb:.2f}")


def etoile_nautique(f: Flash, cx, cy, r, ang=-90):
    """Étoile nautique à 5 branches : chaque branche moitié noire, moitié rouge."""
    ri = r * .42
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else ri
        a = math.radians(ang + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    contour = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    f.add("contour", contour)
    for i in range(5):
        tip = pts[2 * i]
        left, right = pts[2 * i - 1], pts[2 * i + 1]
        f.add("noir", f"M{cx:.2f} {cy:.2f} L{left[0]:.2f} {left[1]:.2f} L{tip[0]:.2f} {tip[1]:.2f} Z")
        f.add("rouge", f"M{cx:.2f} {cy:.2f} L{tip[0]:.2f} {tip[1]:.2f} L{right[0]:.2f} {right[1]:.2f} Z")
        f.add("interieur", f"M{cx:.2f} {cy:.2f} L{tip[0]:.2f} {tip[1]:.2f}")


def hirondelle(f: Flash, cx, cy, L, ang=0.0, flip=False):
    """Hirondelle traditionnelle en piqué, tête à gauche, envergure ≈ `L` mm.

    Grammaire (cf. references/motifs/HIRONDELLE.md) : ailes repliées vers l'arrière (jamais
    ouvertes à plat), queue nettement fourchue (le trait le plus reconnaissable), gorge rouge,
    ventre en peau réservée, dos et ailes en noir plein avec plumes séparées par des réserves,
    œil = un point noir avec un reflet. `flip=True` la retourne (pour une paire en vis-à-vis).
    """
    def p():
        return P(cx, cy, L, ang, flip)

    # Aile haute (vers l'arrière et le haut), bord de fuite festonné en 3 plumes.
    aile_h = (p().M(-.18, -.08).C(-.05, -.3, .3, -.5, .62, -.58).C(.52, -.48, .48, -.42, .46, -.38)
              .C(.5, -.36, .5, -.3, .38, -.27).C(.42, -.24, .4, -.18, .28, -.17)
              .C(.3, -.12, .24, -.06, .12, -.06).Z())
    # Aile basse (vers l'arrière et le bas).
    aile_b = (p().M(-.1, .1).C(.05, .25, .3, .42, .55, .5).C(.48, .38, .46, .34, .43, .3)
              .C(.46, .26, .42, .2, .32, .2).C(.34, .15, .28, .12, .16, .12).Z())
    # Corps : tête ronde, gorge, ventre, attache de queue.
    corps = (p().M(-.62, -.02).C(-.6, -.16, -.42, -.2, -.32, -.12).C(-.12, -.1, .12, -.04, .3, .04)
             .C(.12, .14, -.12, .16, -.3, .12).C(-.45, .12, -.6, .1, -.62, -.02).Z())
    # Queue fourchue : deux longues plumes.
    queue = (p().M(.26, .02).C(.45, .0, .7, -.08, .88, -.12).C(.72, -.02, .55, .06, .46, .08)
             .C(.6, .14, .76, .22, .86, .32).C(.66, .26, .45, .18, .26, .1).Z())
    bec = p().M(-.62, -.05).L(-.74, -.02).L(-.61, .02).Z()
    # Zones de couleur.
    gorge = p().M(-.6, .02).C(-.52, .1, -.4, .12, -.3, .12).C(-.32, .03, -.42, -.02, -.48, -.04).C(-.54, -.04, -.58, -.02, -.6, .02).Z()
    calotte = p().M(-.62, -.02).C(-.6, -.16, -.42, -.2, -.32, -.12).C(-.4, -.1, -.5, -.09, -.62, -.04).Z()
    dos = p().M(-.32, -.12).C(-.12, -.1, .12, -.04, .3, .04).C(.1, -.01, -.12, -.04, -.32, -.12).Z()
    plumes_h = [(.12, -.07, .22, -.2, .36, -.33, .52, -.45), (.27, -.18, .34, -.26, .42, -.32, .5, -.37),
                (.0, -.09, .1, -.14, .16, -.17, .22, -.19)]
    plumes_b = [(.16, .13, .26, .22, .36, .3, .47, .36), (.0, .11, .1, .15, .16, .17, .22, .18)]
    plumes_q = [(.42, .07, .55, .04, .68, -.02, .8, -.08), (.42, .11, .55, .15, .68, .21, .78, .27)]
    for zone, ps in ((aile_h, plumes_h), (aile_b, plumes_b), (queue, plumes_q)):
        d = str(zone)
        for c in ps:
            d += " " + str(reserve(p(), *c))
        f.add("noir", d)
    for z in (calotte, dos, bec):
        f.add("noir", z)
    f.add("rouge", gorge)
    for z in (aile_h, aile_b, corps, queue, bec):
        f.add("contour", z)
    # Œil + reflet, ligne de gorge.
    oeil = p().M(-.5, -.035).C(-.5, -.06, -.455, -.06, -.455, -.035).C(-.455, -.01, -.5, -.01, -.5, -.035).Z()
    f.add("noir-fin", oeil).add("details", oeil)
    f.add("rehauts", p().M(-.473, -.045).C(-.473, -.052, -.462, -.052, -.462, -.045).C(-.462, -.038, -.473, -.038, -.473, -.045).Z())
    f.add("interieur", p().M(-.6, .02).C(-.52, .1, -.4, .12, -.3, .12))
    f.add("ombrage", p().M(-.3, .12).C(-.12, .16, .12, .14, .26, .06).C(.1, .1, -.12, .11, -.3, .12).Z(), direction=-90)
