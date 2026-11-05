# Calques de transfert (stencils)

Histoire du stencil (celluloïd gravé, charbon et vaseline, thermofax) : `HISTOIRE_STENCILS.md`.

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
2. Solution de transfert (stencil primer) en **couche fine**, attendre qu'elle devienne collante.
3. Poser le calque bien à plat, **appuyer fermement** du centre vers les bords sans glisser.
4. Retirer **lentement en partant d'un coin**. Un papier transfert translucide permet de voir
   pendant le retrait les zones qui n'ont pas pris (bulles, manques) : reposer avant qu'il soit
   trop tard.
5. Laisser sécher 10 à 20 minutes (plus le stencil sèche, mieux il résiste à l'essuyage).
6. **Dernier contrôle avant l'aiguille** : emplacement, angle, taille sur la zone réelle, accords
   avec les tatouages voisins et les courbes du corps. C'est le dernier moment où tout se corrige.
7. Raté ou de travers : nettoyer (alcool / savon), attendre que la peau sèche, recommencer.

### Entraînement

- Sur peau synthétique, un **déodorant en stick** peut remplacer la solution de transfert.
- Tracer le flash plusieurs fois à la main (papier, puis peau synthétique) avant le premier
  stencil : la mémoire du geste compte autant que le calque.
- Une impression jet d'encre ordinaire d'un dessin au trait fonctionne avec le fluide de stencil ;
  le thermique est préférable dès que le dessin a des épaisseurs variées.

Sources : [Colin Tattoo — Traditional tattoo stencils](https://colintattoo.com/traditional-tattoo-stencils/)
(reformulé) et `HISTOIRE_STENCILS.md`.

## Pendant le tatouage : garder le stencil

- **Tamponner** l'excès d'encre plutôt que frotter : chaque essuyage frotté éclaircit le calque.
  On ne frotte que là où le stencil ne sert plus.
- Ordonner le travail pour essuyer le moins possible les zones encore à faire (ligner d'abord ce
  que la main risque d'effacer).
- Si le stencil s'efface ou devient illisible : tatouer d'abord ce dont on est sûr, avec la
  référence imprimée à portée — ne jamais deviner.
- Stencil **simple** : la forme générale et les limites de zones, pas chaque point ni chaque hachure.
  Un stencil trop chargé devient illisible dès le premier essuyage (c'est pourquoi les calques buk
  marquent les zones par des pointillés et des codes plutôt que de tout dessiner).
- Surface très courbe : quelques fentes dans le papier l'aident à épouser la forme.

## Taille et échelle

`--scale 1.2` agrandit tout le design (traits compris) ; prévoir que les aiguilles du calque
restent celles de la fiche : au-delà de ±25 %, buk recommande de revoir les aiguilles
(contour plus épais pour une grande pièce, détails supprimés pour une petite).
