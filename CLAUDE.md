# buk — consignes pour Claude dans ce repo

- Langue du projet : **français** (docs, messages, noms de couches). Code et noms de fichiers
  sans accents.
- Le skill est `skills/buk/` (lien `.claude/skills/buk`). Pour toute demande de tatouage,
  utilise l'agent `buk` ou suis `skills/buk/SKILL.md`.
- Palette stricte : noir, rouge, blanc. Style strictement old school.
- Les scripts du skill restent **sans dépendance** hors bibliothèque standard Python ≥ 3.9.
  Exceptions : OpenCV/numpy dans `buk_trace.py` et `buk_flash_import.py` (squelette de secours en
  numpy pur), rsvg/cairosvg/Chrome pour `buk_render.py`, yt-dlp/pyyaml/pillow dans `research/`.
- Toutes les commandes s'appellent `buk:` (commandes Claude : `.claude/commands/buk/*.md` →
  `/buk:flash`…) ou `buk-` (agents, cibles make).
- **Partir de vrais flashs** (`skills/buk/assets/classiques/`, import d'images CC0 ou de la
  personne). Jamais d'import d'images protégées (blogs, Pinterest, artistes vivants, banques
  d'images dans le dépôt public).
- Ne jamais versionner `research/transcripts/` ; les notes sont des paraphrases (aucune citation
  longue).
- Après toute modification de scripts, de JSON ou du flash d'exemple : `make buk-test` puis
  `make buk-demo` (le flash d'exemple et ses calques sont versionnés).
- Valeurs techniques : toujours des plages « point de départ » ; le champ `statut` (`seed` /
  `sourcé`) est mis à jour uniquement lors d'une synthèse de la recherche (`/buk:research synthese`,
  agent `buk-synthese`).
- `SECURITE.md` ne peut qu'être renforcé, jamais assoupli.
