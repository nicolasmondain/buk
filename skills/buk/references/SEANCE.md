# Déroulé d'une séance

buk guide une étape à la fois. À chaque étape il donne : **calque**, **aiguille**, **encre**,
**réglage**, **geste**, **critère de réussite**, **quoi faire si ça rate**. Il attend que la
personne confirme avant de passer à la suivante.

## 0. Avant le jour J

- [ ] Design validé, calques et `fiche.html` imprimés (voir `CALQUES.md`).
- [ ] Liste de matériel cochée (la fiche la génère à partir des couches du design).
- [ ] Test d'allergie au rouge fait si première fois.
- [ ] Entraînement sur peau synthétique avec le **même** design et les **mêmes** aiguilles.

## 1. Poste (15–20 min)

Désinfecter, filmer, sortir cartouches et capsules, remplir les capsules, régler l'alimentation
(voir `SECURITE.md` et `MACHINE.md`). Machine testée à vide pour chaque tension prévue.

## 2. Peau et stencil (20–30 min)

Raser, désinfecter, poser le **calque maître**, laisser sécher. Vérifier placement et sens de
lecture du lettrage dans un miroir et en direct.

## 3. Étapes de piquage — dans l'ordre `data-order`

| # | Étape | Calque | Aiguille type | Encre |
|---|---|---|---|---|
| 1 | Contour extérieur | `bold-line` | RL11 | noir |
| 2 | Traits intérieurs et détails | `lining` | RL7 / RL5 | noir |
| — | *Pause : essuyer, laisser le stencil intact, nettoyer la zone* | | | |
| 3 | Ombrage | `whip` / `pepper` | RM9 / RL3 | noir |
| 4 | Noir plein | `solid-black` | RM13 | noir |
| — | *Changer de cartouche, rincer, essuyer le noir* | | | |
| 5 | Rouge | `solid-red` | RM11 | rouge |
| 6 | Rehauts | `highlight-white` | RL5 | blanc |

Les calques de zones (`whip`, `solid-*`) servent de **carte** : on les garde à côté pour savoir où
remplir, ou on les repose sur la peau (cicatrisée) pour une seconde séance. On ne re-décalque pas
par-dessus une peau fraîchement tatouée.

Pour chaque étape, buk va chercher dans `assets/techniques.json` la section correspondante et la
restitue : réglage, geste, critère de réussite, erreurs.

## 4. Fin de séance

Nettoyage doux (savon neutre), contrôle des manques, retouche immédiate seulement si la peau le
permet, film / pansement, explication des soins (voir `SECURITE.md`). Noter lots d'encres,
aiguilles et réglages réellement utilisés dans la fiche pour la prochaine fois.

## 5. Retouche (4 à 6 semaines après)

Comparer avec la fiche, reposer le calque de zone si nécessaire, repasser uniquement les manques.
