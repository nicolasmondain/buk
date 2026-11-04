# Calques de transfert (stencils)

## Ce que génère `buk_stencil.py`

| Calque | Contenu | Usage |
|---|---|---|
| **Maître** | Tous les traits à leur épaisseur + contours de zones en pointillés fins + code lettre | Celui qu'on pose sur la peau |
| **Par aiguille** (`--by needle`) | Tout ce qui se fait avec une même aiguille | Carte de travail pour chaque cartouche |
| **Par technique** (`--by technique`) | Tout ce qui se fait avec un même type d'ombrage | Carte de travail par geste |

Codes lettres posés au centre des zones :

| Code | Technique |
|---|---|
| `W` | Whip (ombrage noir) — une flèche indique le sens du fouet si `data-direction` est défini |
| `P` | Poivré |
| `N` | Noir plein |
| `R` | Rouge plein |
| `B` | Blanc (rehaut) |

Conventions graphiques sur le calque : **trait plein** = à tatouer ; **pointillé fin** = limite de
zone, à ne pas tatouer comme un trait.

## Papiers et impression

| Méthode | Miroir ? | Réglage buk |
|---|---|---|
| Imprimante thermique + papier thermique 4 feuilles | Non | Imprimer le SVG du calque (ou la page de la fiche) à 100 % |
| Papier hectographique, décalque à la main (on repasse au stylo sur la feuille blanche) | Non | Imprimer sur papier normal, poser dessous, repasser |
| Papier transfert pour jet d'encre / encre stencil imprimée face au contact de la peau | **Souvent oui** | `--mirror` — vérifier la notice du papier |

Règle de contrôle : s'il y a du lettrage, il doit se lire **à l'endroit sur la peau**. Faire un
essai sur papier avant la peau.

Impression : toujours à **100 % / taille réelle** (désactiver « ajuster à la page »). La fiche
contient une règle de contrôle de 50 mm : la mesurer après impression.

## Pose du stencil

1. Peau rasée, désinfectée, sèche.
2. Solution de transfert (stencil primer) en couche fine, attendre qu'elle devienne collante.
3. Poser le calque bien à plat, appuyer du centre vers les bords sans glisser, retirer d'un seul
   geste.
4. Laisser sécher 10 à 20 minutes (plus le stencil sèche, mieux il résiste à l'essuyage).
5. Raté ou de travers : nettoyer (alcool / savon), attendre que la peau sèche, recommencer.

## Taille et échelle

`--scale 1.2` agrandit tout le design (traits compris) ; prévoir que les aiguilles du calque
restent celles de la fiche : au-delà de ±25 %, buk recommande de revoir les aiguilles
(contour plus épais pour une grande pièce, détails supprimés pour une petite).
