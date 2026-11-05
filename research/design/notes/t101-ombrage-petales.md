---
image: t101-ombrage-petales.png
source: https://tattooing101.com/learn/guides/draw-traditional/
motif: rose
support: peau-cicatrisee
mesures: {noir: 44.6, rouge: 7.3, clair: 27.7, autre: 20.4, trait_mediane_pct: 0.38}
---
Diptyque pédagogique (deux photos de tatouages cicatrisés annotées de flèches) : à gauche une
dague + rose + banderole sur avant-bras, à droite une rose seule avec feuilles sur bras. Les
mesures sont faussées par le fond noir de la photo de gauche (44,6 % de noir) et la peau/le
décor photographique (20 % « autre ») : ne pas les comparer aux flashs.

## Construction
Rose de droite : silhouette festonnée, cœur en spirale fermé par une coupe, deux rangs de
pétales qui s'emboîtent (un rang intérieur serré autour du cœur, un rang extérieur plus large
dont les pétales se chevauchent). Silhouette plus large que haute, nettement non circulaire.
Banderole de gauche : bande qui s'enroule sur elle-même ; le revers est la partie qui fuit.

## Hiérarchie des traits
Contour unique, épais et régulier sur tout le motif ; les plis intérieurs (bords de pétales,
spirale) sont du même trait. Aucun trait décoratif « dans » les pétales : c'est l'ombre qui
porte le volume.

## Noir et ombres
Ce que les flèches désignent : l'ombre noire est placée **sur le pétale qui passe dessous**,
collée au bord du pétale qui le recouvre, et seulement de ce côté-là. Résultat : chaque
recouvrement se lit comme un plan. Même logique sur la banderole : le revers qui s'éloigne
de l'œil est assombri, la face qui vient vers nous reste claire. Les ombres sont courtes
(un quart à un tiers du pétale) et ne se rejoignent pas toutes : on voit le rouge entre deux
zones sombres.

## Couleur et lumière
Rouge sur le corps des pétales, mais les bords externes des pétales du rang intérieur sont
éclaircis (rose pâle / peau) : la lumière est sur les arêtes, le noir dans les creux.
Feuilles vert foncé avec nervure claire (chez buk : noir plein + nervure en réserve) ; petites
touches jaunes en « rayons » derrière la rose (chez buk : rouge ou à supprimer).

## Ce que buk doit retenir
- L'ombre se pose sur le plan qui passe dessous, collée au trait du plan qui recouvre, jamais
  sur le plan du dessus.
- Un élément qui s'enroule (banderole, pétale roulé) : assombrir la face qui s'éloigne.
- Arête claire / creux sombre : chaque pétale a un bord éclairci et une base ombrée.

## Écart avec buk
Dans `rose()` de `buk_composants.py`, le rendu (`flashs/_motifs/rose_rendu/apercu.svg`) est un
rouge uniforme avec des ombres très discrètes : aucun bord de pétale éclairci, donc les plans
ne se séparent que par le trait. Sur la banderole, buk met le départ de queue en noir plein
(bon) mais n'ombre pas le revers dans la longueur de la bande.
