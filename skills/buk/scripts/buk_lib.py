"""Bibliothèque commune buk : lecture du SVG au contrat buk, géométrie approchée, données.

Aucune dépendance hors bibliothèque standard Python (>= 3.9).
"""
from __future__ import annotations

import copy
import json
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
NS = {"svg": SVG_NS}

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

PALETTE = {
    "noir": "#111111",
    "rouge": "#C1121F",
    "blanc": "#FFFFFF",
    "peau": "#F1D3B3",
}
INKS = ("noir", "rouge", "blanc")
SHAPES = ("path", "circle", "ellipse", "polygon", "polyline", "line", "rect")


def tag(el: ET.Element) -> str:
    return el.tag.split("}", 1)[-1]


def load_json(name: str) -> dict:
    with open(ASSETS / name, encoding="utf-8") as fh:
        return json.load(fh)


def load_data() -> tuple[dict, dict]:
    return load_json("techniques.json")["techniques"], load_json("aiguilles.json")["aiguilles"]


# --------------------------------------------------------------------------- géométrie

_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARITY = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7, "Z": 0}


def _bez(p0, p1, p2, p3, steps=8):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        out.append((
            mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
            mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1],
        ))
    return out


def path_subpaths(d: str) -> tuple[list[list[tuple[float, float]]], list[bool]]:
    """Échantillonne un attribut `d` en polylignes. Renvoie (sous-chemins, fermé?)."""
    toks = _TOKEN.findall(d or "")
    subs: list[list[tuple[float, float]]] = []
    closed: list[bool] = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    last_ctrl = None
    i = 0
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                if subs:
                    closed[-1] = True
                    subs[-1].append(start)
                cur = start
                last_ctrl = None
                continue
        if cmd is None:
            raise ValueError("chemin sans commande initiale")
        n = _ARITY[cmd.upper()]
        vals = [float(v) for v in toks[i:i + n]]
        if len(vals) < n:
            break
        i += n
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if C == "M":
            cur = (ox + vals[0], oy + vals[1])
            start = cur
            subs.append([cur])
            closed.append(False)
            cmd = "l" if rel else "L"  # coordonnées suivantes implicites = lineto
            last_ctrl = None
            continue
        if not subs:
            subs.append([cur])
            closed.append(False)
        pts = subs[-1]
        if C == "L":
            cur = (ox + vals[0], oy + vals[1]); pts.append(cur); last_ctrl = None
        elif C == "H":
            cur = ((cur[0] if rel else 0) + vals[0], cur[1]); pts.append(cur); last_ctrl = None
        elif C == "V":
            cur = (cur[0], (cur[1] if rel else 0) + vals[0]); pts.append(cur); last_ctrl = None
        elif C == "C":
            p1 = (ox + vals[0], oy + vals[1]); p2 = (ox + vals[2], oy + vals[3]); p3 = (ox + vals[4], oy + vals[5])
            pts.extend(_bez(cur, p1, p2, p3)); cur = p3; last_ctrl = p2
        elif C == "S":
            p1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) if last_ctrl else cur
            p2 = (ox + vals[0], oy + vals[1]); p3 = (ox + vals[2], oy + vals[3])
            pts.extend(_bez(cur, p1, p2, p3)); cur = p3; last_ctrl = p2
        elif C == "Q":
            q = (ox + vals[0], oy + vals[1]); p3 = (ox + vals[2], oy + vals[3])
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts.extend(_bez(cur, p1, p2, p3)); cur = p3; last_ctrl = q
        elif C == "T":
            q = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) if last_ctrl else cur
            p3 = (ox + vals[0], oy + vals[1])
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts.extend(_bez(cur, p1, p2, p3)); cur = p3; last_ctrl = q
        elif C == "A":
            cur = (ox + vals[5], oy + vals[6]); pts.append(cur); last_ctrl = None
    return subs, closed


def _f(el, name, default=0.0):
    v = el.get(name)
    if v is None:
        return default
    return float(re.sub(r"[a-z%]+$", "", v.strip()))


def shape_polygons(el: ET.Element) -> tuple[list[list[tuple[float, float]]], bool]:
    """Polygones approchés d'une forme SVG et indicateur « fermée »."""
    t = tag(el)
    if t == "path":
        subs, closed = path_subpaths(el.get("d", ""))
        return subs, bool(closed) and all(closed)
    if t in ("circle", "ellipse"):
        cx, cy = _f(el, "cx"), _f(el, "cy")
        rx = _f(el, "r") if t == "circle" else _f(el, "rx")
        ry = _f(el, "r") if t == "circle" else _f(el, "ry")
        return [[(cx + rx * math.cos(a * math.pi / 16), cy + ry * math.sin(a * math.pi / 16)) for a in range(33)]], True
    if t == "rect":
        x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
        return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]], True
    if t in ("polygon", "polyline"):
        nums = [float(n) for n in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)", el.get("points", ""))]
        pts = list(zip(nums[::2], nums[1::2]))
        if t == "polygon" and pts:
            pts.append(pts[0])
        return [pts], t == "polygon"
    if t == "line":
        return [[(_f(el, "x1"), _f(el, "y1")), (_f(el, "x2"), _f(el, "y2"))]], False
    return [], False


def poly_area(pts) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def inside(pt, polys) -> bool:
    """Règle pair-impair sur l'ensemble des sous-polygones (gère les trous)."""
    x, y = pt
    c = False
    for poly in polys:
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
                c = not c
    return c


def _seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def label_point(polys) -> tuple[float, float, float]:
    """Point intérieur le plus éloigné des bords (recherche sur grille). Renvoie (x, y, marge)."""
    pts = [p for poly in polys for p in poly]
    if not pts:
        return 0, 0, 0
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    segs = [(a, b) for poly in polys for a, b in zip(poly, poly[1:])]
    best = ((x0 + x1) / 2, (y0 + y1) / 2, 0.0)
    n = 24
    for i in range(n + 1):
        for j in range(n + 1):
            p = (x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * j / n)
            if not inside(p, polys):
                continue
            d = min(_seg_dist(p, a, b) for a, b in segs) if segs else 0
            if d > best[2]:
                best = (p[0], p[1], d)
    return best


# --------------------------------------------------------------------------- design

@dataclass
class Layer:
    el: ET.Element
    id: str
    kind: str
    technique: str
    needle: str
    ink: str
    order: int
    direction: float | None = None

    @property
    def shapes(self) -> list[ET.Element]:
        return [e for e in self.el.iter() if tag(e) in SHAPES]


@dataclass
class Design:
    path: Path
    root: ET.Element
    width_mm: float
    height_mm: float
    viewbox: tuple[float, float, float, float]
    title: str
    placement: str
    layers: list[Layer] = field(default_factory=list)


def _mm(v: str | None) -> float | None:
    if not v:
        return None
    m = re.fullmatch(r"\s*([\d.]+)\s*mm\s*", v)
    if m:
        return float(m.group(1))
    m = re.fullmatch(r"\s*([\d.]+)\s*cm\s*", v)
    return float(m.group(1)) * 10 if m else None


def load_design(path: str | Path) -> Design:
    path = Path(path)
    root = ET.parse(path).getroot()
    vb = tuple(float(v) for v in re.split(r"[ ,]+", root.get("viewBox", "0 0 0 0").strip()))
    w, h = _mm(root.get("width")), _mm(root.get("height"))
    d = Design(
        path=path, root=root,
        width_mm=w or (vb[2] if len(vb) == 4 else 0),
        height_mm=h or (vb[3] if len(vb) == 4 else 0),
        viewbox=vb if len(vb) == 4 else (0, 0, 0, 0),
        title=root.get("data-buk-title", path.stem),
        placement=root.get("data-buk-placement", ""),
    )
    for g in root:
        if tag(g) != "g" or g.get("data-buk-kind") is None:
            continue
        try:
            order = int(g.get("data-order", "0"))
        except ValueError:
            order = 0
        dirv = g.get("data-direction")
        d.layers.append(Layer(
            el=g, id=g.get("id", f"couche{len(d.layers) + 1}"),
            kind=g.get("data-buk-kind", ""), technique=g.get("data-technique", ""),
            needle=g.get("data-needle", ""), ink=g.get("data-ink", ""), order=order,
            direction=float(dirv) if dirv not in (None, "") else None,
        ))
    return d


def coverage(d: "Design", step: float = 0.8) -> dict[str, float]:
    """Proportions visibles (%) par échantillonnage : la zone la plus haute dans le document gagne.

    Base = points couverts par une zone ou intérieurs à un contour bold-line fermé.
    Catégories : noir (solid-black), ombrage (whip, pepper), rouge, blanc, peau.
    """
    cat_of = {"solid-black": "noir", "whip": "ombrage", "pepper": "ombrage",
              "solid-red": "rouge", "highlight-white": "blanc"}
    zones = []   # (catégorie, polys, bbox) dans l'ordre d'empilement
    outlines = []
    for L in d.layers:
        for el in L.shapes:
            polys, closed = shape_polygons(el)
            pts = [p for poly in polys for p in poly]
            if not pts or not closed:
                continue
            bb = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
            if L.kind == "zone" and L.technique in cat_of:
                zones.append((cat_of[L.technique], polys, bb))
            elif L.technique == "bold-line":
                outlines.append((polys, bb))
    counts = {"noir": 0, "ombrage": 0, "rouge": 0, "blanc": 0, "peau": 0}
    vx, vy, vw, vh = d.viewbox
    y = vy + step / 2
    while y < vy + vh:
        x = vx + step / 2
        while x < vx + vw:
            hit = None
            for cat, polys, bb in reversed(zones):
                if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and inside((x, y), polys):
                    hit = cat
                    break
            if hit is None and any(bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and inside((x, y), polys)
                                   for polys, bb in outlines):
                hit = "peau"
            if hit:
                counts[hit] += 1
            x += step
        y += step
    total = sum(counts.values()) or 1
    return {k: round(100 * v / total, 1) for k, v in counts.items()}


def element_direction(el: ET.Element, layer: Layer) -> float | None:
    v = el.get("data-direction")
    return float(v) if v not in (None, "") else layer.direction


def clone(el: ET.Element) -> ET.Element:
    return copy.deepcopy(el)


def fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")
