---
description: Convertit un vrai dessin (planche du domaine public, ton croquis) en flash buk
argument-hint: "<image> [x0 y0 x1 y1] [largeur mm] [titre]"
---

Arguments : $ARGUMENTS

1. Vérifie les droits : domaine public (CC0), dessin de la personne, ou licence qui l'autorise.
   Une image de blog, d'Instagram, de Pinterest ou d'un artiste vivant ne s'importe pas (analyse
   seulement). Une image de banque d'images (Magnific/Freepik…) va dans `flashs/prive/<nom>/`,
   jamais dans le dépôt (voir `skills/buk/references/IMPORT.md`).
2. Si aucun cadrage n'est donné, regarde l'image (réduite à 1000 px avec une grille) et propose
   la boîte du motif.
3. `python3 skills/buk/scripts/buk_flash_import.py <image> --crop x0 y0 x1 y1 --largeur-mm <L>
   --titre "<titre>" -o flashs/<nom>/<nom>.svg`
4. `python3 skills/buk/scripts/buk_validate.py flashs/<nom>/<nom>.svg`, puis
   `python3 skills/buk/scripts/buk_render.py flashs/<nom>/<nom>.svg` et regarde le résultat à côté
   de l'original. Corrige (lettrage à reposer, zones mal colorées) selon `IMPORT.md`.
5. Propose `/buk:calques <nom>`.
