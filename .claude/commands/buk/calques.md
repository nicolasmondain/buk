---
description: Génère les calques de transfert et la fiche technique d'un flash
argument-hint: "<nom du flash> [needle|technique|both] [--mirror] [--machine pen|rotary|coil] [--scale 1.0]"
---

Arguments : $ARGUMENTS

1. Retrouve le flash : `flashs/<nom>/<nom>.svg` (ou le chemin donné).
2. Si le type de papier transfert n'est pas connu, demande-le une fois (thermique, hectographique
   à la main, jet d'encre) : il décide de `--mirror` (voir `skills/buk/references/CALQUES.md`).
   Demande aussi la machine si inconnue (stylo par défaut).
3. `python3 skills/buk/scripts/buk_stencil.py flashs/<nom>/<nom>.svg --by <mode> --out flashs/<nom>/calques [options]`
   (mode par défaut : `both`).
4. Résume : nombre de calques, liste des cartouches (depuis `sequence.json`), avertissements, et
   le chemin de `fiche.html` à imprimer à 100 % (vérifier la règle de 50 mm).
