#!/usr/bin/env python3
"""Génère l'aperçu couleur, les calques de transfert et la fiche technique d'un flash buk.

Exemples :
  python3 buk_stencil.py flash.svg --by needle
  python3 buk_stencil.py flash.svg --by technique --machine coil --mirror
  python3 buk_stencil.py flash.svg --by both --scale 1.2 --out calques/
  python3 buk_stencil.py flash.svg --preview-only

Sorties (dans <flash>_calques/ par défaut) :
  apercu.svg             rendu couleur sur peau
  calque-maitre.svg      le stencil à poser
  calque-aiguille-*.svg  un calque par aiguille + encre (--by needle|both)
  calque-technique-*.svg un calque par type d'ombrage (--by technique|both)
  fiche.html             fiche imprimable A4, échelle 1:1, avec réglages et gestes
  sequence.json          déroulé de séance lisible par l'agent
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from buk_lib import (PALETTE, SVG_NS, Design, Layer, clone, element_direction, fmt, label_point,
                     load_data, load_design, poly_area, shape_polygons, tag)
from buk_validate import validate

TECH_ORDER = ["bold-line", "lining", "whip", "pepper", "solid-black", "solid-red", "highlight-white"]
INK_FILL = {"noir": PALETTE["noir"], "rouge": PALETTE["rouge"], "blanc": PALETTE["blanc"]}


def q(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def new_svg(d: Design, scale: float = 1.0) -> ET.Element:
    vb = d.viewbox
    return ET.Element(q("svg"), {
        "width": f"{fmt(d.width_mm * scale)}mm", "height": f"{fmt(d.height_mm * scale)}mm",
        "viewBox": " ".join(fmt(v) for v in vb),
    })


def to_str(el: ET.Element) -> str:
    return ET.tostring(el, encoding="unicode")


def strip_meta(el: ET.Element) -> ET.Element:
    for e in el.iter():
        for k in [k for k in e.attrib if k.startswith("data-")]:
            del e.attrib[k]
    return el


# --------------------------------------------------------------------------- aperçu couleur

def preview_svg(d: Design, scale: float = 1.0) -> ET.Element:
    svg = new_svg(d, scale)
    defs = ET.SubElement(svg, q("defs"))
    pat = ET.SubElement(defs, q("pattern"), {"id": "poivre", "width": "1.2", "height": "1.2",
                                              "patternUnits": "userSpaceOnUse"})
    ET.SubElement(pat, q("circle"), {"cx": "0.3", "cy": "0.3", "r": "0.22", "fill": PALETTE["noir"]})
    ET.SubElement(pat, q("circle"), {"cx": "0.9", "cy": "0.9", "r": "0.18", "fill": PALETTE["noir"]})
    vb = d.viewbox
    ET.SubElement(svg, q("rect"), {"x": fmt(vb[0]), "y": fmt(vb[1]), "width": fmt(vb[2]),
                                   "height": fmt(vb[3]), "fill": PALETTE["peau"]})
    n = 0
    for L in d.layers:  # ordre du document = ordre d'empilement
        g = ET.SubElement(svg, q("g"), {"id": f"apercu-{L.id}"})
        for el in L.shapes:
            c = strip_meta(clone(el))
            if L.kind == "line":
                c.set("stroke", PALETTE["noir"]); c.set("fill", "none")
            elif L.technique == "whip":
                n += 1
                gid = f"whip{n}"
                ang = element_direction(el, L)
                if ang is None:
                    gr = ET.SubElement(defs, q("radialGradient"), {"id": gid})
                    stops = [("0", "0.05"), ("0.6", "0.35"), ("1", "0.95")]
                else:
                    a = math.radians(ang)
                    gr = ET.SubElement(defs, q("linearGradient"), {
                        "id": gid, "x1": fmt(0.5 - 0.5 * math.cos(a)), "y1": fmt(0.5 - 0.5 * math.sin(a)),
                        "x2": fmt(0.5 + 0.5 * math.cos(a)), "y2": fmt(0.5 + 0.5 * math.sin(a))})
                    stops = [("0", "1"), ("0.35", "0.7"), ("1", "0")]
                for off, op in stops:
                    ET.SubElement(gr, q("stop"), {"offset": off, "stop-color": PALETTE["noir"], "stop-opacity": op})
                c.set("fill", f"url(#{gid})"); c.set("stroke", "none")
            elif L.technique == "pepper":
                c.set("fill", "url(#poivre)"); c.set("stroke", "none")
            else:
                c.set("fill", INK_FILL.get(L.ink, PALETTE["noir"])); c.set("stroke", "none")
            g.append(c)
    return svg


# --------------------------------------------------------------------------- calques

def _zone_marks(parent: ET.Element, el: ET.Element, L: Layer, code: str, color: str):
    polys, _ = shape_polygons(el)
    if not polys:
        return
    x, y, margin = el.get("data-label-x"), el.get("data-label-y"), None
    if x is not None and y is not None:
        x, y = float(x), float(y)
        margin = 2.0
    else:
        x, y, margin = label_point(polys)
    area = sum(poly_area(p) for p in polys)
    size = max(1.6, min(3.2, 1.6 * max(margin, 0.5), math.sqrt(max(area, 0.1)) * 0.9))
    if code and area >= 6.0:
        t = ET.SubElement(parent, q("text"), {
            "x": fmt(x), "y": fmt(y + size * 0.36), "font-size": fmt(size), "text-anchor": "middle",
            "font-family": "Arial, Helvetica, sans-serif", "font-weight": "700", "fill": color})
        t.text = code
    ang = element_direction(el, L)
    if ang is not None and L.technique in ("whip", "pepper"):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        length = max(2.5, min(6.0, margin * 1.6 if margin else 4))
        sx, sy = x - ux * length / 2, y - uy * length / 2
        if code and area >= 6.0:  # la flèche passe à côté de la lettre
            sx, sy = sx - uy * size * 0.9, sy + ux * size * 0.9
        ex, ey = sx + ux * length, sy + uy * length
        ET.SubElement(parent, q("line"), {"x1": fmt(sx), "y1": fmt(sy), "x2": fmt(ex), "y2": fmt(ey),
                                          "stroke": color, "stroke-width": "0.3", "stroke-linecap": "round"})
        hx, hy = ex - ux * 1.0, ey - uy * 1.0
        ET.SubElement(parent, q("polygon"), {
            "points": f"{fmt(ex)},{fmt(ey)} {fmt(hx - uy * 0.55)},{fmt(hy + ux * 0.55)} {fmt(hx + uy * 0.55)},{fmt(hy - ux * 0.55)}",
            "fill": color})


def stencil_svg(d: Design, selected: list[Layer], techniques: dict, *, context: str = "none",
                mirror: bool = False, scale: float = 1.0) -> ET.Element:
    """context : none | faint (traits non sélectionnés en gris clair) | dotted (contour bold-line en pointillé)."""
    svg = new_svg(d, scale)
    vb = d.viewbox
    ET.SubElement(svg, q("rect"), {"x": fmt(vb[0]), "y": fmt(vb[1]), "width": fmt(vb[2]),
                                   "height": fmt(vb[3]), "fill": "#FFFFFF"})
    root = ET.SubElement(svg, q("g"))
    if mirror:
        root.set("transform", f"translate({fmt(2 * vb[0] + vb[2])},0) scale(-1,1)")
    sel_ids = {L.id for L in selected}
    others = [L for L in d.layers if L.id not in sel_ids]
    if context == "faint":
        g = ET.SubElement(root, q("g"), {"id": "contexte"})
        for L in others:
            for el in L.shapes:
                c = strip_meta(clone(el))
                c.set("fill", "none"); c.set("stroke", "#C9C9C9")
                c.set("stroke-width", "0.35" if L.kind == "line" else "0.2")
                if L.kind == "zone":
                    c.set("stroke-dasharray", "0.6 0.8")
                g.append(c)
    elif context == "dotted":
        g = ET.SubElement(root, q("g"), {"id": "reperes"})
        for L in others:
            if L.technique != "bold-line":
                continue
            for el in L.shapes:
                c = strip_meta(clone(el))
                c.set("fill", "none"); c.set("stroke", "#000000"); c.set("stroke-width", "0.25")
                c.set("stroke-dasharray", "0.4 1.6")
                g.append(c)
    for L in sorted(selected, key=lambda l: (l.kind != "zone", l.order)):
        g = ET.SubElement(root, q("g"), {"id": f"calque-{L.id}"})
        code = techniques.get(L.technique, {}).get("code", "")
        for el in L.shapes:
            c = strip_meta(clone(el))
            if L.kind == "line":
                c.set("fill", "none"); c.set("stroke", "#000000")
                g.append(c)
            else:
                c.set("fill", "none"); c.set("stroke", "#000000"); c.set("stroke-width", "0.25")
                c.set("stroke-dasharray", "0.8 0.8")
                g.append(c)
                _zone_marks(g, el, L, code, "#000000")
    return svg


def groups(d: Design, by: str) -> list[tuple[str, str, list[Layer]]]:
    """Renvoie [(clé fichier, titre, couches)] triés par ordre de séance."""
    buckets: dict[str, list[Layer]] = {}
    for L in d.layers:
        key = f"{L.needle}-{L.ink}" if by == "needle" else L.technique
        buckets.setdefault(key, []).append(L)
    out = []
    for key, layers in buckets.items():
        title = (f"{layers[0].needle} · encre {layers[0].ink}" if by == "needle" else key)
        out.append((key, title, layers))
    out.sort(key=lambda t: min(l.order for l in t[2]))
    return out


# --------------------------------------------------------------------------- fiche HTML

CSS = """
:root{--ink:#111;--red:#C1121F;--paper:#FBF6EC;--line:#d9cfbf;--muted:#6b6257}
*{box-sizing:border-box}
body{margin:0;background:#e9e2d4;color:var(--ink);font:13px/1.45 "Helvetica Neue",Arial,sans-serif}
.page{width:210mm;min-height:297mm;margin:12px auto;padding:12mm;background:var(--paper);
  box-shadow:0 2px 12px rgba(0,0,0,.15);position:relative}
h1,h2{font-family:Impact,"Arial Black","Helvetica Neue",sans-serif;letter-spacing:.04em;
  text-transform:uppercase;margin:0}
h1{font-size:30px}h2{font-size:20px;margin-bottom:2mm}
.rule{height:3px;background:var(--red);margin:3mm 0 4mm;box-shadow:0 3px 0 var(--ink)}
.meta{color:var(--muted);font-size:12px}
.row{display:flex;gap:8mm;align-items:flex-start}
.col{flex:1;min-width:0}
table{border-collapse:collapse;width:100%;font-size:11.5px}
th,td{border-bottom:1px solid var(--line);padding:1.6mm 1.4mm;text-align:left;vertical-align:top}
th{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.badge{display:inline-block;padding:0 1.8mm;border:1px solid currentColor;border-radius:2mm;
  font-size:10px;text-transform:uppercase;letter-spacing:.05em}
.seed{color:#9a6b00}.source{color:#1d6b34}
.ink{display:inline-block;width:3mm;height:3mm;border:1px solid #111;vertical-align:-0.4mm;margin-right:1mm}
.stencil{background:#fff;border:1px dashed #b9ae9c;display:inline-block;line-height:0}
.preview{max-width:100%;height:auto}
.preview svg{max-width:68mm;max-height:105mm;width:auto;height:auto}
ul{margin:1mm 0 2mm 4.5mm;padding:0}li{margin:.4mm 0}
.mat{font-size:11.5px;list-style:none;margin-left:0}
.k{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.06em;margin-top:2.4mm}
.ruler{margin-top:4mm}
.note{font-size:11px;color:var(--muted)}
.warn{color:var(--red);font-weight:600}
.step{font-family:Impact,"Arial Black",sans-serif;color:var(--red);font-size:26px;line-height:1;margin-right:3mm}
@media print{body{background:#fff}.page{margin:0;box-shadow:none;background:#fff;min-height:0;page-break-after:always}
  @page{size:A4;margin:0}}
"""

INK_SWATCH = {"noir": PALETTE["noir"], "rouge": PALETTE["rouge"], "blanc": PALETTE["blanc"]}


def esc(s) -> str:
    return html.escape(str(s))


def ruler_svg() -> str:
    ticks = "".join(
        f'<line x1="{i}" y1="0" x2="{i}" y2="{4 if i % 10 == 0 else 2}" stroke="#111" stroke-width="0.2"/>'
        for i in range(0, 51))
    return (f'<svg width="52mm" height="8mm" viewBox="-1 -0.5 52 8">{ticks}'
            f'<line x1="0" y1="0" x2="50" y2="0" stroke="#111" stroke-width="0.3"/>'
            f'<text x="25" y="7.2" font-size="2.6" text-anchor="middle" font-family="Arial">50 mm — à vérifier après impression</text></svg>')


def tech_block(layers: list[Layer], tech: dict, needles: dict, machine: str) -> str:
    L = layers[0]
    statut = tech.get("statut", "seed")
    badge = (f'<span class="badge source">sourcé ({len(tech.get("sources", []))})</span>' if statut == "sourcé"
             else '<span class="badge seed">seed · à ajuster</span>')
    volts = tech.get("tension_v", {})
    vtxt = " · ".join(f"{'<b>' if k == machine else ''}{k} {v} V{'</b>' if k == machine else ''}"
                      for k, v in volts.items())
    geste = "".join(f"<li>{esc(g)}</li>" for g in tech.get("geste", []))
    errs = "".join(f"<li>{esc(g)}</li>" for g in tech.get("erreurs", []))
    rows = "".join(
        f"<tr><td>{esc(l.id)}</td><td><b>{esc(l.needle)}</b> — {esc(needles.get(l.needle, {}).get('nom', ''))}"
        f" · 0,35 mm · {esc(needles.get(l.needle, {}).get('taper', ''))}</td>"
        f"<td><span class='ink' style='background:{INK_SWATCH.get(l.ink, '#111')}'></span>{esc(l.ink)}</td>"
        f"<td>{l.order}</td></tr>" for l in layers)
    return f"""
<div class="tech">
  <h2>{esc(tech.get('nom', L.technique))} {badge}</h2>
  <table>
    <tr><th>Couche</th><th>Aiguille</th><th>Encre</th><th>Ordre</th></tr>
    {rows}
  </table>
  <div class="k">Réglages (point de départ)</div>
  <div>Tension : {vtxt}<br>Course : {esc(tech.get('course_mm', '—'))} mm · Angle : {esc(tech.get('angle', '—'))}<br>
  Main : {esc(tech.get('vitesse_main', '—'))}</div>
  <div class="k">Geste</div><ul>{geste}</ul>
  <div class="k">Réussite</div><div>{esc(tech.get('reussite', ''))}</div>
  <div class="k">Si ça rate</div><ul>{errs}</ul>
</div>"""


def fiche_html(d: Design, report: dict, preview: str, master: str, sheets: list[dict],
               techniques: dict, needles: dict, machine: str, mirror: bool, scale: float) -> str:
    layers = sorted(d.layers, key=lambda l: l.order)
    rows = "".join(
        f"<tr><td><b>{L.order}</b></td><td>{esc(techniques.get(L.technique, {}).get('nom', L.technique))}"
        f"<div class='note'>{esc(L.id)}</div></td><td><b>{esc(L.needle)}</b></td>"
        f"<td><span class='ink' style='background:{INK_SWATCH.get(L.ink, '#111')}'></span>{esc(L.ink)}</td>"
        f"<td>{esc(techniques.get(L.technique, {}).get('tension_v', {}).get(machine, '—'))} V</td></tr>"
        for L in layers)
    carts: dict[str, list[str]] = {}
    for L in layers:
        carts.setdefault(f"{L.needle} ({L.ink})", []).append(L.id)
    cart_li = "".join(f"<li>☐ Cartouche <b>{esc(k)}</b> — {esc(', '.join(v))}</li>" for k, v in carts.items())
    inks = sorted({L.ink for L in layers}, key=["noir", "rouge", "blanc"].index)
    ink_li = "".join(f"<li>☐ Encre {esc(i)} (conforme REACH, n° de lot noté)</li>" for i in inks)
    warn = ""
    if d.width_mm * scale > 186 or d.height_mm * scale > 273:
        warn = "<p class='warn'>Le design dépasse la zone imprimable A4 : imprimer les calques en A3 (échelle 100 %).</p>"
    if any(L.ink == "rouge" for L in layers):
        warn += "<p class='warn'>Rouge présent : test cutané conseillé (pigment le plus allergisant).</p>"
    val = "".join(f"<li>{esc(w)}</li>" for w in report["avertissements"]) or "<li>Rien à signaler.</li>"
    ratios = report["infos"]["ratios_pct"]

    pages = [f"""
<section class="page">
  <h1>{esc(d.title)}</h1>
  <div class="meta">buk · fiche de séance · {date.today().isoformat()} · {fmt(d.width_mm * scale)} × {fmt(d.height_mm * scale)} mm
   {('· ' + esc(d.placement)) if d.placement else ''} · machine : {esc(machine)} {'· calques en MIROIR' if mirror else ''}</div>
  <div class="rule"></div>
  <div class="row">
    <div class="col" style="flex:0 0 68mm"><div class="preview">{preview}</div>
      <div class="note">Surfaces visibles ≈ noir {ratios['noir']} % · ombrage {ratios['ombrage']} % · rouge {ratios['rouge']} % · blanc {ratios['blanc']} % · peau {ratios['peau']} %</div>
    </div>
    <div class="col">
      <h2>Déroulé</h2>
      <table><tr><th>#</th><th>Étape</th><th>Aiguille</th><th>Encre</th><th>{esc(machine)}</th></tr>{rows}</table>
      <div class="k">Matériel</div>
      <ul class="mat">{cart_li}{ink_li}
        <li>☐ Papier transfert + solution de pose · rasoir jetable · antiseptique</li>
        <li>☐ Gants nitrile · film barrière · capsules · vaseline · abaisse-langues · sopalin</li>
        <li>☐ Savon/solution de nettoyage · gobelet d'eau de rinçage · collecteur DASRI · pansement</li></ul>
      {warn}
    </div>
  </div>
  <div class="k">Contrôle du design</div><ul>{val}</ul>
  <div class="k">Légende des calques</div>
  <div class="note">Trait plein = à tatouer · pointillé serré = limite de zone (ne pas ligner) ·
   pointillé espacé = repère de contour · W whip · P poivré · N noir plein · R rouge · B blanc · flèche = sens du coup de fouet.
   Les valeurs « seed » sont des points de départ : régler sur peau synthétique avant la peau.</div>
  <div class="ruler">{ruler_svg()}</div>
</section>
<section class="page">
  <h1>Calque maître</h1><div class="meta">À poser sur la peau · échelle 1:1 · imprimer à 100 %</div>
  <div class="rule"></div>
  <div class="stencil">{master}</div>
  <div class="ruler">{ruler_svg()}</div>
</section>"""]
    for sh in sheets:
        by_tech: dict[str, list[Layer]] = {}
        for L in sh["layers"]:
            by_tech.setdefault(L.technique, []).append(L)
        blocks = "".join(tech_block(ls, techniques.get(t, {}), needles, machine) for t, ls in by_tech.items())
        pages.append(f"""
<section class="page">
  <div class="row" style="align-items:center"><span class="step">{sh['step']}</span>
    <div><h1>{esc(sh['title'])}</h1><div class="meta">{esc(sh['kind_label'])} · fichier {esc(sh['file'])}</div></div></div>
  <div class="rule"></div>
  <div class="row">
    <div class="col" style="flex:0 0 auto"><div class="stencil">{sh['svg_faint']}</div>
      <div class="note">Gris = reste du dessin, pour se repérer.</div></div>
    <div class="col">{blocks}</div>
  </div>
</section>""")
    return (f"<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(d.title)} — calques</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>")


# --------------------------------------------------------------------------- main

def slug(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in s.lower()).strip("-")


def write_svg(path: Path, el: ET.Element):
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + to_str(el), encoding="utf-8")


def run(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg", help="flash au contrat buk")
    ap.add_argument("--by", choices=["needle", "technique", "both"], default="both",
                    help="découpage des calques : par aiguille, par technique d'ombrage, ou les deux")
    ap.add_argument("--out", help="dossier de sortie (défaut : <flash>_calques)")
    ap.add_argument("--mirror", action="store_true", help="calques en miroir (papier jet d'encre, voir CALQUES.md)")
    ap.add_argument("--scale", type=float, default=1.0, help="facteur d'échelle d'impression (1.0 = taille du design)")
    ap.add_argument("--machine", choices=["pen", "rotary", "coil"], default="pen")
    ap.add_argument("--preview-only", action="store_true", help="n'écrire que apercu.svg")
    ap.add_argument("--force", action="store_true", help="générer malgré des erreurs de validation")
    a = ap.parse_args(argv)

    report = validate(a.svg)
    if report["erreurs"] and not a.force:
        print("Le flash ne respecte pas le contrat buk :", file=sys.stderr)
        for e in report["erreurs"]:
            print(f"  - {e}", file=sys.stderr)
        print("Corriger le SVG (ou --force).", file=sys.stderr)
        return 1

    d = load_design(a.svg)
    techniques, needles = load_data()
    out = Path(a.out) if a.out else d.path.with_name(d.path.stem + "_calques")
    out.mkdir(parents=True, exist_ok=True)

    prev = preview_svg(d, a.scale)
    write_svg(out / "apercu.svg", prev)
    if a.preview_only:
        print(out / "apercu.svg")
        return 0

    master = stencil_svg(d, d.layers, techniques, mirror=a.mirror, scale=a.scale)
    write_svg(out / "calque-maitre.svg", master)

    modes = ["needle", "technique"] if a.by == "both" else [a.by]
    sheets = []
    for mode in modes:
        for i, (key, title, layers) in enumerate(groups(d, mode), 1):
            prefix = "aiguille" if mode == "needle" else "technique"
            fname = f"calque-{prefix}-{slug(key)}.svg"
            write_svg(out / fname, stencil_svg(d, layers, techniques, context="dotted",
                                               mirror=a.mirror, scale=a.scale))
            faint = stencil_svg(d, layers, techniques, context="faint", mirror=a.mirror, scale=a.scale)
            if mode == "technique":
                title = techniques.get(key, {}).get("nom", key)
            sheets.append({"step": min(l.order for l in layers), "title": title, "file": fname,
                           "kind_label": "calque par aiguille" if mode == "needle" else "calque par technique",
                           "layers": sorted(layers, key=lambda l: l.order), "svg_faint": to_str(faint)})

    (out / "fiche.html").write_text(
        fiche_html(d, report, to_str(preview_svg(d, 1.0)), to_str(master), sheets, techniques, needles,
                   a.machine, a.mirror, a.scale), encoding="utf-8")

    seq = [{
        "ordre": L.order, "couche": L.id, "technique": L.technique,
        "technique_nom": techniques.get(L.technique, {}).get("nom"), "aiguille": L.needle, "encre": L.ink,
        "tension_v": techniques.get(L.technique, {}).get("tension_v", {}).get(a.machine),
        "statut": techniques.get(L.technique, {}).get("statut"),
        "calque_aiguille": f"calque-aiguille-{slug(L.needle + '-' + L.ink)}.svg" if "needle" in modes else None,
        "calque_technique": f"calque-technique-{slug(L.technique)}.svg" if "technique" in modes else None,
    } for L in sorted(d.layers, key=lambda l: l.order)]
    (out / "sequence.json").write_text(json.dumps({
        "titre": d.title, "taille_mm": [d.width_mm * a.scale, d.height_mm * a.scale], "machine": a.machine,
        "miroir": a.mirror, "avertissements": report["avertissements"], "etapes": seq}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(f"Calques générés dans {out}/")
    for p in sorted(out.iterdir()):
        print(f"  {p.name}")
    for w in report["avertissements"]:
        print(f"  ATTENTION  {w}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
