---
image: t101-oiseau-ombrage-peau-synth.png
source: https://tattooing101.com/learn/styles/how-to-shade-american-traditional-tattoos/
motif: autre
support: peau-fraiche
mesures: {noir: 26.2, rouge: 0.0, clair: 52.5, autre: 21.3, trait_mediane_pct: 0.66}
---
Capture vidéo basse résolution (291 × 142 px) d'un tatouage en cours : tête d'oiseau à bec
crochu et plumes/feuilles à gauche, aiguille au contact de la peau. Qualité faible : on lit les
principes, pas les détails.

## Construction
Tête d'oiseau simple (contour rond, bec court, une volute en spirale sous la tête) ; à gauche,
des formes en feuille/plume déjà ombrées. Lecture limitée par la résolution.

## Hiérarchie des traits
Contour noir unique et régulier sur toutes les formes ; la volute intérieure est tracée au même
calibre que le contour (cohérent avec la règle « une seule épaisseur »).

## Noir et ombres
Moment intéressant : le tatoueur pose des **points noirs isolés** le long d'un trait (début de
whip poivré / packing) — on voit des points de tailles décroissantes qui partent du contour et
s'espacent. Sur les plumes de gauche, l'ombre déjà faite est **collée au contour** côté intérieur,
dense contre le trait et éclaircie vers le centre de la forme, d'un seul côté du trait. La partie
déjà ombrée (gauche) est nettement plus sombre que la tête (droite) : le fond est plus foncé que
le sujet.

## Couleur et lumière
Les ombres sont en gris-bleu (dilution/bleu, hors palette) : buk les transpose en **whip noir
sur peau**, sans gris dilué. La tête reste en peau nue à ce stade (la réserve est le clair).

## Ce que buk doit retenir
- L'ombre démarre exactement sur le trait, sans liseré de peau entre les deux.
- Le whip se lit comme des points qui s'espacent, pas comme un voile gris : la fin de l'ombre est
  granuleuse.
- Ce qui est derrière (plumes, feuillage) est ombré plus fort que le sujet au premier plan.

## Écart avec buk
Les zones `ombrage` des composants sont des formes fermées qui partent du trait (ex. rose : les
croissants sont construits sur la courbe du pétale) : le collage au trait est respecté dans la
géométrie. En revanche l'aperçu ne montre aucun grain (dégradé lisse), et le poivré de
`buk_stencil.py` est un motif de points **à densité constante** (`#poivre`, pas de 1,2 mm) qui ne
fait pas de transition. Gris-bleu : sans équivalent dans buk (palette stricte), et c'est voulu.
