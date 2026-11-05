---
image: t101-crane-etape2.jpg
source: https://tattooing101.com/learn/guides/draw-traditional/
motif: crâne
support: flash
mesures: {noir: 5.1, rouge: 0.0, clair: 94.2, autre: 0.6, trait_mediane_pct: 1.27}
---
## Construction
Étape d'ébauche : deux volumes seulement. Un grand cercle légèrement plus large que haut pour la
boîte crânienne, et un ovale plus petit (environ 60 % de la largeur du cercle) posé en bas,
**décalé vers la droite** et chevauchant le bas du cercle sur environ un tiers de sa hauteur. Ce
décalage suffit à installer une vue de trois quarts tournée vers la droite : le visage (orbites,
nez, mâchoire) se logera dans l'ovale et la partie basse droite du cercle, la nuque restant à
gauche. Aucun axe de symétrie n'est tracé à ce stade.

## Hiérarchie des traits
Un seul trait, déjà à l'épaisseur finale (≈ 1,3 % de la largeur), pour des formes qui seront
ensuite passées en gris clair comme guides. Rien d'intérieur.

## Noir et ombres
Aucun.

## Couleur et lumière
Aucune ; le blanc est le fond.

## Ce que buk doit retenir
- Bâtir le crâne par **deux masses** : sphère crânienne + ovale facial plus petit qui chevauche le
  bas de la sphère. Le rapport et le décalage de l'ovale fixent l'orientation (centré = face,
  décalé = trois quarts).
- Le volume crânien domine : la face n'occupe que le tiers bas de la hauteur totale environ, la
  calotte les deux tiers.

## Écart avec buk
`crane()` (buk_classiques.py) dessine d'un seul tenant une silhouette symétrique de face, sans
logique de deux masses ; il n'existe pas de variante trois quarts. Le paramètre `ang` ne fait que
tourner le dessin dans le plan, il ne change pas la vue.
