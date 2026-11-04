---
description: Dessine ou modifie un flash old school (noir, rouge, blanc) au contrat buk
argument-hint: "<description du motif, taille, emplacement> | modifier <nom> : <changement>"
---

Demande : $ARGUMENTS

Utilise l'agent **buk** (ou suis directement `skills/buk/SKILL.md`, section « Dessiner ou
modifier le flash ») :

1. Nouveau motif → `flashs/<nom>/<nom>.svg` ; modification → édite le SVG existant.
2. Respecte `references/DESIGN_OLD_SCHOOL.md` et `references/SVG_CONTRAT.md`.
3. Passe `references/CHECKLIST_DESIGN.md`, puis
   `python3 skills/buk/scripts/buk_validate.py flashs/<nom>/<nom>.svg` (0 erreur).
4. `python3 skills/buk/scripts/buk_stencil.py flashs/<nom>/<nom>.svg --preview-only --out flashs/<nom>/calques`
   et montre `apercu.svg`.
5. Termine en proposant `/buk-calques <nom>`.
