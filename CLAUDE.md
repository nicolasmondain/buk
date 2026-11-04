# buk — consignes pour Claude dans ce repo

- Langue du projet : **français** (docs, messages, noms de couches). Code et noms de fichiers
  sans accents.
- Le skill est `skills/buk/` (lien `.claude/skills/buk`). Pour toute demande de tatouage,
  utilise l'agent `buk` ou suis `skills/buk/SKILL.md`.
- Palette stricte : noir, rouge, blanc. Style strictement old school.
- Les scripts du skill restent **sans dépendance** hors bibliothèque standard Python ≥ 3.9.
  OpenCV n'est autorisé que dans `buk_trace.py`, yt-dlp/pyyaml que dans `research/`.
- Ne jamais versionner `research/transcripts/` ; les notes sont des paraphrases (aucune citation
  longue).
- Après toute modification de scripts, de JSON ou du flash d'exemple : `make test` puis
  `make demo` (le flash d'exemple et ses calques sont versionnés).
- Valeurs techniques : toujours des plages « point de départ » ; le champ `statut` (`seed` /
  `sourcé`) est mis à jour uniquement par l'agent `buk-synthese`.
- `SECURITE.md` ne peut qu'être renforcé, jamais assoupli.
