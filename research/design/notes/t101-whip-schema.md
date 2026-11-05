---
image: t101-whip-schema.png
source: https://tattooing101.com/learn/styles/how-to-shade-american-traditional-tattoos/
motif: autre
support: flash
mesures: {noir: 5.0, rouge: 0.2, clair: 92.1, autre: 2.7, trait_mediane_pct: 0.44}
---
Schéma pédagogique (illustration vectorielle, pas un flash) : machine en coupe au-dessus d'une
bande de peau, et la trace laissée par un coup de whip. Mesures non pertinentes pour le style
(fond clair du schéma).

## Construction
Une seule forme utile : la trace du geste dans la peau, en **virgule couchée** — tête ronde et
pleine à gauche (point d'entrée vertical de l'aiguille), queue effilée qui remonte en arc vers la
droite et s'amincit jusqu'à disparaître (sortie de l'aiguille en fin de course).

## Hiérarchie des traits
Aucun contour sur la virgule : la trace est une masse, pas un trait. Ce qu'il faut lire, c'est que
la valeur sombre/claire vient de l'**épaisseur et de la densité** du dépôt, pas d'un gris.

## Noir et ombres
Le noir est concentré à l'entrée (tête de la virgule, « paraît plus sombre ») et s'éteint le long
de la courbe (« paraît plus clair »). La courbe est **asymétrique** : départ court et dense,
sortie longue et tirée. Le dégradé n'est pas linéaire : il reste plein sur le premier tiers, puis
chute vite.

## Couleur et lumière
Hors sujet (schéma). Le rouge n'apparaît que sur la machine. Retenir seulement : la peau qui
reste visible en fin de geste *est* le clair de l'ombre.

## Ce que buk doit retenir
- Un whip est un geste orienté : il a une tête dense collée au trait et une queue qui s'efface ;
  toute zone `ombrage` doit avoir un sens (`direction`), jamais un dégradé sans origine.
- Profil de densité : plein sur le premier tiers environ, puis chute rapide vers la peau — pas une
  rampe linéaire 100 % → 0 %.
- La sortie est courbe (arc qui remonte), donc la limite claire d'une zone de whip est un bord
  irrégulier et effiloché, pas une ligne nette parallèle au trait.

## Écart avec buk
`buk_stencil.py` rend une zone `whip` par un `linearGradient` lisse (opacité 1 → 0,7 à 35 % →
0) : le profil « plein puis chute » est déjà approché, mais le rendu reste un gris continu, alors
que le schéma décrit un dépôt qui se raréfie (voir la note du poivré). Les zones sans `direction`
reçoivent un dégradé radial sombre au bord : c'est un whip sans sens de geste, à proscrire dans
les composants.
