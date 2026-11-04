# Critique visuelle — buk regarde avant de montrer

Un tatoueur ne livre jamais un dessin qu'il n'a pas regardé de loin, de près, et en plissant les
yeux. buk fait pareil : **aucun flash n'est montré à la personne sans au moins un tour de
critique**. La personne voit le résultat, pas la critique (sauf si elle la demande).

## La boucle (2 à 3 tours, pas plus)

1. `python3 scripts/buk_render.py flash.svg` → `apercu.png`, `miniature.png`, `valeurs.png`,
   `planche.png`.
2. **Regarde les quatre images** (outil de lecture d'image) et réponds aux questions ci-dessous,
   pour toi.
3. Note les 1 à 3 défauts les plus graves — pas plus : on corrige le plus important d'abord.
4. Édite le SVG (ou les paramètres des pièces de `assets/composants/`), revalide, re-rends.
5. Arrête quand plus aucun défaut de niveau 1 ou 2 ne subsiste, ou après 3 tours (dis alors
   ce qui reste perfectible).

## Les questions, par ordre de gravité

**Niveau 1 — Lecture (`miniature.png`)**
- À 2 cm, reconnaît-on le sujet sans hésiter ? Sinon : silhouette à reprendre, pas les détails.
- Le contour extérieur est-il d'un seul tenant, plus épais que tout le reste ?
- Est-ce que ça ressemble à autre chose (pot, fraise, tache) ? Si oui, dis à quoi, et pourquoi.

**Niveau 2 — Valeurs (`valeurs.png`)**
- Trois valeurs nettes : noir plein, ombré, clair. Pas de bouillie grise.
- Le noir forme au moins une masse qui équilibre le dessin (pas tout d'un côté).
- La lumière (peau, rehauts) est là où l'œil doit aller en premier.

**Niveau 3 — Construction (`planche.png`)**
- Étape 1 : la silhouette seule tient-elle ? Étape 2 : chaque trait intérieur raconte-t-il une
  forme (pli, pétale, plume) ou est-il décoratif ? Supprime les décoratifs.
- Étape 3 : chaque ombre part d'un trait, d'un seul côté. Une ombre des deux côtés d'un trait
  aplatit la forme.
- Comparer à la fiche du motif (`references/motifs/`) : la grammaire est-elle respectée ?

**Niveau 4 — Finition (`apercu.png`)**
- Rien sous 2 mm, aucun écart < 1,5 mm entre traits parallèles.
- Les réserves (nervures, plumes, reflets) sont lisibles, pas des égratignures.
- Rehauts blancs : 2 à 6, petits, du même côté (une seule source de lumière, en haut à gauche
  par convention).

## Vocabulaire de critique

Nommer précisément le défaut aide à le corriger : *silhouette molle*, *contour qui s'éteint*,
*ombre flottante* (ne touche aucun trait), *ombre double* (des deux côtés d'un trait), *noir
orphelin* (petite tache noire isolée), *trait décoratif*, *zone bouchée* (trop de traits
rapprochés), *réserve illisible*, *lumière dispersée* (rehauts de plusieurs côtés),
*composition centrée morte* (tout est symétrique sans raison).

## Garder la trace

Après une session de dessin, si la personne a corrigé quelque chose que la critique aurait dû
voir, ajoute la leçon à `references/PREFERENCES.md` (goûts de la personne) ou à la fiche du
motif (règle générale). C'est comme ça que le goût de buk s'affine.
