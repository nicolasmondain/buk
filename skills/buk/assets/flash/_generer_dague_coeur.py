#!/usr/bin/env python3
"""Génère dague_coeur.svg (flash d'exemple). Gardé pour montrer comment construire un flash
au contrat buk par programme ; un flash peut aussi être écrit à la main."""
from pathlib import Path

S = 1.25          # échelle : 1 unité de dessin = 1,25 mm
W, H = 70, 106    # taille de dessin avant échelle


def p(x, y):
    return f"{x * S:.2f} {y * S:.2f}"


def path(*cmds, close=True):
    out = []
    for c in cmds:
        if isinstance(c, str):
            out.append(c)
        else:
            out.append(p(*c))
    return " ".join(out) + (" Z" if close else "")


HEART = path("M", (35, 74), "C", (22, 64), (10, 56), (10, 45), "C", (10, 37), (16, 32), (23, 32),
             "C", (29, 32), (33, 36), (35, 40), "C", (37, 36), (41, 32), (47, 32),
             "C", (54, 32), (60, 37), (60, 45), "C", (60, 56), (48, 64), (35, 74))
# Croissant noir plein le long du bord bas-gauche, et dégradé whip qui le prolonge vers l'intérieur.
CRESCENT_BLACK = path("M", (35, 74), "C", (22, 64), (10, 56), (10, 45), "C", (10, 41), (11.5, 37.5), (14, 35.5),
                      "C", (12.6, 42), (14.5, 50), (21, 56.5), "C", (26, 61.5), (31, 66.5), (35, 70.3))
CRESCENT_WHIP = path("M", (35, 70.3), "C", (31, 66.5), (26, 61.5), (21, 56.5), "C", (14.5, 50), (12.6, 42), (14, 35.5),
                     "C", (16, 34), (18, 33.4), (19.5, 33.4), "C", (18.5, 41), (21, 48.5), (27, 54.5),
                     "C", (30.5, 58), (33.5, 61.5), (35, 64))
COMMA = path("M", (49, 36), "C", (52.5, 36), (55.5, 38.6), (56, 42.6), "C", (54.2, 40.4), (51.6, 38.6), (49, 38),
             "C", (48.1, 37.7), (48.1, 36.2), (49, 36))

BLADE_SHADE_TOP = path("M", (31.5, 24), "L", (35, 24), "L", (35, 40), "L", (34, 38.27), "L", (33, 36.91),
                       "L", (32, 35.8), "L", (31.5, 35.33))
BLADE_SHADE_BOT = path("M", (31.5, 71.33), "L", (32, 71.71), "L", (33, 72.47), "L", (34, 73.23), "L", (35, 74),
                       "L", (35, 96), "L", (31.5, 82))
GRIP = path("M", (32.6, 10.6), "L", (32.2, 19.8), "L", (37.8, 19.8), "L", (37.4, 10.6))
GUARD = path("M", (21, 19.8), "L", (49, 19.8), "L", (49, 24), "L", (21, 24))


def drop(cx, cy, s):
    return path("M", (cx, cy - s * 1.6), "C", (cx + s * .2, cy - s * .9), (cx + s, cy - s * .3), (cx + s, cy + s * .2),
                "C", (cx + s, cy + s * .8), (cx + s * .55, cy + s * 1.1), (cx, cy + s * 1.1),
                "C", (cx - s * .55, cy + s * 1.1), (cx - s, cy + s * .8), (cx - s, cy + s * .2),
                "C", (cx - s, cy - s * .3), (cx - s * .2, cy - s * .9), (cx, cy - s * 1.6))


DROPS = [(35, 101.5, 1.8), (21, 70, 2.2), (50, 75, 2.0)]


def circle(cx, cy, r, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<circle cx="{cx * S:.2f}" cy="{cy * S:.2f}" r="{r * S:.2f}" {attrs}/>'


def d(dpath, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<path {attrs} d="{dpath}"/>'


LINE = dict(fill="none", stroke="#111111", stroke_linecap="round", stroke_linejoin="round")
RED, BLACK, WHITE = "#C1121F", "#111111", "#FFFFFF"


def layer(id_, kind, tech, needle, ink, order, body, direction=None):
    extra = f' data-direction="{direction}"' if direction is not None else ""
    return (f'  <g id="{id_}" data-buk-kind="{kind}" data-technique="{tech}" data-needle="{needle}" '
            f'data-ink="{ink}" data-order="{order}"{extra}>\n    ' + "\n    ".join(body) + "\n  </g>")


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * S:g}mm" height="{H * S:g}mm" '
       f'viewBox="0 0 {W * S:g} {H * S:g}" data-buk-title="Dague et cœur" data-buk-placement="avant-bras">',
       "  <!-- Zones d'abord (empilement de l'aperçu), traits ensuite. L'ordre de séance = data-order. -->",
       layer("ombrage-lame", "zone", "whip", "RM7", "noir", 3,
             [d(BLADE_SHADE_TOP, fill=BLACK), d(BLADE_SHADE_BOT, fill=BLACK)], direction=0),
       layer("rouge", "zone", "solid-red", "RM11", "rouge", 5,
             [d(HEART, fill=RED)] + [d(drop(*t), fill=RED) for t in DROPS]),
       layer("ombrage-coeur", "zone", "whip", "RM9", "noir", 3,
             [d(CRESCENT_WHIP, fill=BLACK)], direction=-45),
       layer("noir-plein", "zone", "solid-black", "RS9", "noir", 4,
             [d(CRESCENT_BLACK, fill=BLACK), d(GRIP, fill=BLACK), d(GUARD, fill=BLACK),
              circle(35, 7.5, 3.2, fill=BLACK), circle(19, 21.9, 1.9, fill=BLACK), circle(51, 21.9, 1.9, fill=BLACK)]),
       layer("rehauts", "zone", "highlight-white", "RL5", "blanc", 6,
             [d(COMMA, fill=WHITE), circle(34, 6.4, 0.75, fill=WHITE)]
             + [circle(cx + s * .38, cy - s * .05, s * .28, fill=WHITE) for cx, cy, s in DROPS]),
       layer("contour", "line", "bold-line", "RL11", "noir", 1, [
           d(HEART, stroke_width="1.4", **LINE),
           d(path("M", (31.5, 24), "L", (31.5, 35.33), close=False), stroke_width="1.4", **LINE),
           d(path("M", (38.5, 24), "L", (38.5, 35.33), close=False), stroke_width="1.4", **LINE),
           d(path("M", (31.5, 71.33), "L", (31.5, 82), "L", (35, 96), "L", (38.5, 82), "L", (38.5, 71.33), close=False),
             stroke_width="1.4", **LINE),
           d(GUARD, stroke_width="1.4", **LINE), d(GRIP, stroke_width="1.4", **LINE),
           circle(35, 7.5, 3.2, stroke_width="1.4", **LINE),
           circle(19, 21.9, 1.9, stroke_width="1.4", **LINE), circle(51, 21.9, 1.9, stroke_width="1.4", **LINE)]),
       layer("interieur", "line", "lining", "RL7", "noir", 2, [
           d(path("M", (35, 24), "L", (35, 40), close=False), stroke_width="1.0", **LINE),
           d(path("M", (35, 74), "L", (35, 93), close=False), stroke_width="1.0", **LINE)]
           + [d(drop(*t), stroke_width="1.0", **LINE) for t in DROPS]),
       "</svg>"]

Path(__file__).with_name("dague_coeur.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
print("dague_coeur.svg écrit")
