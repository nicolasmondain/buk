---
description: Pipeline de recherche YouTube → transcripts → notes → skill. Arguments : run (défaut) | status | synthese
argument-hint: "[run|status|synthese] [taille de lot]"
---

Mode demandé : `$ARGUMENTS` (vide = `run`, taille de lot par défaut 5).

## status
Lance `python3 research/scripts/harvest.py status` et `python3 research/scripts/coverage.py`,
puis résume en 5 lignes : vidéos cataloguées / transcrites / notées, thèmes manquants, verdict.

## run — boucle jusqu'à matière suffisante

1. Si `research/index.json` n'existe pas ou si `research/sources.yaml` a changé depuis :
   `python3 research/scripts/harvest.py list`.
2. `python3 research/scripts/coverage.py --quiet` → si la sortie commence par `STOP`, passe
   directement au mode **synthese**.
3. `python3 research/scripts/harvest.py fetch -n <lot>` (choisit d'abord les vidéos qui couvrent
   les thèmes non saturés).
4. Pour chaque transcript produit et pas encore noté (`research/transcripts/<id>.md` sans
   `research/notes/<id>.md`), lance l'agent **buk-transcript-miner** avec l'id — tous en parallèle,
   dans un seul message.
5. Quand ils ont fini : `python3 research/scripts/coverage.py` et affiche le tableau.
6. Reviens à l'étape 2. Arrête-toi aussi si `fetch` ne trouve plus de vidéo exploitable : dis
   alors quelles chaînes ou recherches ajouter dans `research/sources.yaml` pour les thèmes
   manquants.

Entre deux tours, donne une ligne d'avancement (notes, thèmes saturés, nouveauté récente).

## synthese
Lance l'agent **buk-synthese**. Ensuite, propose (sans le faire d'office) de supprimer
`research/transcripts/` puisque les notes suffisent désormais.
