#!/usr/bin/env python3
"""Régénère les flashs d'exemple des pièces et leurs planches de construction (make motifs)."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from buk_composants import (Flash, banderole, etoile_nautique, feuille, goutte,  # noqa: E402
                            hirondelle, rose)
from buk_bestiaire import bateau, flammes, panthere, phare, pinup, serpent, toile  # noqa: E402
from buk_classiques import (ancre, banderole_texte, carte, coeur, crane, dague, de,  # noqa: E402
                            fer_a_cheval, lettrage)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[3] / "flashs" / "_motifs"
OUT.mkdir(parents=True, exist_ok=True)

R, cx, cy = 20, 35, 30
f = Flash("Rose", 70, 62, placement="mollet")
feuille(f, cx - .78 * R, cy + .62 * R, 18, angle=160)
feuille(f, cx + .74 * R, cy + .64 * R, 18, angle=20)
feuille(f, cx + .76 * R, cy - .62 * R, 13, angle=-40)
rose(f, cx, cy, R)
f.ecrire(OUT / "rose.svg")

f = Flash("Hirondelles", 150, 60, placement="poitrine")
hirondelle(f, 42, 30, 38, ang=-12, flip=True)
hirondelle(f, 108, 30, 38, ang=12)
f.ecrire(OUT / "hirondelles.svg")

f = Flash("Pièces", 170, 60)
banderole(f, 8, 72, 30, 11, pli=7)
etoile_nautique(f, 96, 30, 19)
feuille(f, 124, 40, 22, angle=-60)
feuille(f, 140, 44, 16, angle=-110, flip=True)
for x, y, s in ((156, 18, 2.6), (160, 33, 2.0), (154, 46, 3.0)):
    goutte(f, x, y, s)
f.ecrire(OUT / "pieces.svg")

f = Flash("Classiques", 250, 80)
fer_a_cheval(f, 22, 40, 40)
de(f, 58, 30, 11, faces=(5, 3, 6)); de(f, 70, 56, 9, faces=(1, 4, 2), ang=14)
carte(f, 100, 40, 44, "A", "pique", ang=-8); carte(f, 136, 42, 44, "K", "coeur", ang=8)
ancre(f, 176, 40, 62)
crane(f, 222, 40, 44)
f.ecrire(OUT / "classiques.svg")

f = Flash("Cœur, dague et enseignes", 150, 70)
coeur(f, 30, 34, 44)
dague(f, 75, 35, 62, ang=20)
from buk_classiques import enseigne  # noqa: E402
for i, k in enumerate(("coeur", "carreau", "pique", "trefle")):
    enseigne(f, k, 110 + (i % 2) * 22, 22 + (i // 2) * 26, 8)
f.ecrire(OUT / "coeur_dague.svg")

f = Flash("Lettrage", 170, 62)
lettrage(f, "ABCDEFGHIJKLM", 85, 12, 9)
lettrage(f, "NOPQRSTUVWXYZ", 85, 31, 9)
lettrage(f, "0123456789 & !", 85, 50, 9)
f.ecrire(OUT / "lettrage.svg")

f = Flash("Compositions", 230, 104)
dague(f, 40, 50, 88)
coeur(f, 40, 61, 50)
banderole_texte(f, "MOM", 40, 74, 62)
ancre(f, 118, 48, 70)
banderole_texte(f, "HOLD FAST", 118, 40, 70)
fer_a_cheval(f, 193, 30, 40)
banderole_texte(f, "LUCKY", 193, 50, 52)
de(f, 180, 78, 9, faces=(6, 1, 4), ang=-10); de(f, 206, 80, 9, faces=(3, 5, 2), ang=12)
f.ecrire(OUT / "compositions.svg")

f = Flash("Bestiaire", 240, 100)
panthere(f, 52, 50, 76)
serpent(f, 140, 54, 76)
flammes(f, 206, 76, 50, 40)
f.ecrire(OUT / "bestiaire.svg")

f = Flash("Marine et pin-up", 260, 90)
toile(f, 32, 45, 30)
bateau(f, 105, 52, 72)
phare(f, 170, 45, 74)
pinup(f, 226, 46, 70)
f.ecrire(OUT / "marine_pinup.svg")

scripts = HERE.parent.parent / "scripts"
for name in ("rose", "hirondelles", "pieces", "classiques", "coeur_dague", "lettrage", "compositions", "bestiaire", "marine_pinup"):
    svg = OUT / f"{name}.svg"
    r = subprocess.run([sys.executable, scripts / "buk_validate.py", svg], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout)
    subprocess.run([sys.executable, scripts / "buk_stencil.py", svg, "--preview-only",
                    "--out", OUT / f"{name}_rendu"], check=True, capture_output=True)
    subprocess.run([sys.executable, scripts / "buk_planche.py", svg, "--out", OUT / f"{name}.planche.svg"],
                   check=True, capture_output=True)
    print(OUT / f"{name}.svg")
