---
description: Crée ou modifie un flash old school (noir, rouge, blanc) à partir d'un vrai flash
argument-hint: "<motif, taille, emplacement, texte> | modifier <nom> : <changement>"
---

Demande : $ARGUMENTS

Utilise l'agent **buk** (ou suis `skills/buk/SKILL.md`, section « Dessiner ou modifier le flash ») :

1. **Partir d'un vrai flash** : cherche le motif dans `skills/buk/assets/classiques/` (voir
   `flashs/_classiques/README.md`) et copie-le dans `flashs/<nom>/<nom>.svg`. Si la personne
   fournit un dessin : `/buk:import`. Pièces de `assets/composants/` seulement pour un élément
   simple manquant. Modification → repars du SVG existant.
2. Adapter : `Flash.depuis_svg(...)`, `masquer_forme(...)` pour effacer (ancien texte, détail),
   `lettrage(...)` / `banderole_texte(...)` pour le texte, puis `f.ecrire(...)`
   (exemple dans `skills/buk/references/IMPORT.md`). Taille et emplacement :
   `references/PLACEMENT.md` ; goûts : `references/PREFERENCES.md`.
3. `python3 skills/buk/scripts/buk_validate.py flashs/<nom>/<nom>.svg` (0 erreur ; les
   « Conseil » sont à considérer, pas obligatoires).
4. Boucle de `references/CRITIQUE.md` : `python3 skills/buk/scripts/buk_render.py
   flashs/<nom>/<nom>.svg`, regarde les 4 images, corrige les pires défauts (3 tours maximum).
5. Montre l'aperçu et propose `/buk:calques <nom>`.
