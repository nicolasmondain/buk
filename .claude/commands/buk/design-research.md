---
description: Développe le sens artistique de buk à partir de blogs et d'images old school
argument-hint: "[collecter|analyser|appliquer]"
---

Mode : `$ARGUMENTS` (vide = `collecter` puis `analyser`).

## collecter
1. Lis `research/design/sources_design.yaml`. Pour chaque source de priorité 1 puis 2, ouvre la
   page (WebFetch) et repère les images utiles (étapes de construction, schémas d'ombrage,
   photos de tatouages traditionnels nets, idéalement cicatrisés).
2. Télécharge-les (curl) dans `research/design/images/` avec un nom parlant
   (`t101-rose-etape6.jpg`) et ajoute une ligne `nom ; url de l'image ; url de la page` dans
   `research/design/images/sources.txt`. 30 images maximum par session. Ce dossier n'est pas
   versionné : ce sont les images de leurs auteurs.
3. Note en 3–5 lignes par page les principes écrits (reformulés) dans
   `research/design/notes/_pages.md`.

## analyser
Lance l'agent **buk-flash-analyst** par lots de 3–4 images, plusieurs lots en parallèle. Puis
affiche `research/design/SYNTHESE.md`.

## appliquer
Pour chaque proposition de `SYNTHESE.md` validée par la personne : modifie la fiche motif et/ou
la pièce dans `assets/composants/buk_composants.py`, régénère la planche du motif, passe la
boucle de `skills/buk/references/CRITIQUE.md` (buk_render.py + regarder les images) et montre
l'avant/après.
