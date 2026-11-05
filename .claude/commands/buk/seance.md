---
description: Guide une séance de tatouage pas à pas à partir des calques d'un flash
argument-hint: "<nom du flash>"
---

Flash : $ARGUMENTS

Utilise l'agent **buk**. Lis `skills/buk/references/SECURITE.md` et
`skills/buk/references/SEANCE.md`, puis `flashs/<nom>/calques/sequence.json` (génère les calques
d'abord s'ils n'existent pas).

Guide **une étape à la fois** et attends la confirmation de la personne avant la suivante :
poste → peau et stencil → chaque étape de `sequence.json` dans l'ordre → fin de séance et soins.
À chaque étape de piquage, donne : calque, aiguille, encre, réglage pour sa machine, geste,
critère de réussite, quoi faire si ça rate (depuis `skills/buk/assets/techniques.json`).
Signale clairement les valeurs encore au statut « seed ».
