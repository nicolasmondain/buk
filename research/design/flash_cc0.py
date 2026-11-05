#!/usr/bin/env python3
"""Bibliothèque de flashs classiques importés de planches du domaine public (CC0).

  python3 research/design/flash_cc0.py            # importe tout dans skills/buk/assets/classiques/
  python3 research/design/flash_cc0.py rose ancre_usn

Les images sources (non versionnées) vont dans research/design/images/ sous les noms ci-dessous ;
URL et licences : research/design/SOURCES_CC0.md. Sans les images, les SVG déjà générés dans
skills/buk/assets/classiques/ restent utilisables tels quels.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "research" / "design" / "images"
OUT = ROOT / "skills" / "buk" / "assets" / "classiques"   # SVG : embarqués dans le skill
RENDUS = ROOT / "flashs" / "_classiques"                   # aperçus pour le README
SCRIPTS = ROOT / "skills" / "buk" / "scripts"

# nom : (image, échelle de la grille de repérage, (x0, y0, x1, y1) sur cette grille, largeur mm, titre)
# La grille = image réduite à 1000 px de côté max ; échelle = 1000 / plus grand côté d'origine.
CROPS = {
    "rose":               ("saam_C", .5208, (395, 340, 645, 745), 60, "Rose"),
    "hirondelle_friends": ("saam_C", .5208, (75, 335, 345, 685), 70, "Hirondelle FRIENDS"),
    "hirondelle":         ("saam_C", .5208, (668, 468, 912, 708), 65, "Hirondelle"),
    "croix_father":       ("saam_C", .5208, (412, 45, 622, 312), 60, "Croix FATHER"),
    "papillon":           ("saam_C", .5208, (80, 86, 362, 284), 70, "Papillon"),
    "dague_lune":         ("saam_A", .5208, (378, 58, 502, 292), 40, "Dague et lune"),
    "trois_mats":         ("saam_A", .5208, (382, 330, 595, 728), 60, "Trois-mâts"),
    "coeur_bouclier":     ("saam_E", .5208, (68, 103, 268, 330), 55, "Cœur bouclier"),
    "ancre_usn":          ("saam_E", .5208, (622, 378, 892, 718), 70, "Ancre U.S.N."),
    "dague_death":        ("saam_F", .5208, (400, 78, 568, 552), 45, "Death before dishonor"),
    "cartes_lucky":       ("saam_B", .5208, (638, 78, 952, 338), 80, "Cartes LUCKY"),
    "crane_dead_sport":   ("saam_B", .5208, (672, 398, 918, 692), 70, "Crâne DEAD SPORT"),
}


def importer(nom):
    im, sc, box, w, titre = CROPS[nom]
    src = IMAGES / f"{im}.jpg"
    if not src.exists():
        print(f"  ! {src.name} absente (voir SOURCES_CC0.md) — {nom} ignoré")
        return False
    OUT.mkdir(parents=True, exist_ok=True)
    crop = [str(round(v / sc)) for v in box]
    svg = OUT / f"{nom}.svg"
    subprocess.run([sys.executable, SCRIPTS / "buk_flash_import.py", src, "--crop", *crop, "--largeur-mm", str(w),
                    "--titre", titre, "-o", svg], check=True, capture_output=True)
    r = subprocess.run([sys.executable, SCRIPTS / "buk_validate.py", svg], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout)
    RENDUS.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, SCRIPTS / "buk_stencil.py", svg, "--preview-only", "--out", RENDUS / f"{nom}_rendu"],
                   check=True, capture_output=True)
    print(f"  {nom}: {svg.relative_to(ROOT)}")
    return True


if __name__ == "__main__":
    for nom in sys.argv[1:] or CROPS:
        importer(nom)
