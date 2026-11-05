---
image: t101-rose-rouge-peau.png
source: https://tattooing101.com/learn/guides/draw-traditional/ (fichier https://tattooing101.com/wp-content/uploads/2022/03/rose-traditional-tattoo.png)
motif: rose
support: peau-cicatrisee
mesures: {noir: 25.4, rouge: 37.9, clair: 11.9, autre: 24.8, trait_mediane_pct: 0.84}
---
Note de support : **même tatouage, même photo** que `t101-rose-peau-bras.png` (cou, même oreille,
mêmes feuilles), mais **retouché** : les réserves de peau des pétales ont été repeintes en rouge
plat (rouge un peu différent, bord net de retouche, liseré rouge en haut de l'image). Ce n'est
pas un état de cicatrisation ni un autre tatouage. Inutile comme référence de dessin ; très utile
comme **comparaison A/B avec/sans réserves**.

## Construction
Identique à `t101-rose-peau-bras.md` (3 étages, coupe à « doigts », grands pétales asymétriques,
composition verticale). Sans les réserves, les bords roulés ne se lisent plus : les doubles traits
semblent des contours parasites et les pétales se fondent les uns dans les autres.

## Hiérarchie des traits
Les traits sont les mêmes, mais privés de la bande claire qui les accompagnait ils ne suffisent
plus à séparer les plans : le trait seul ne crée pas la profondeur, c'est le couple trait +
réserve qui la crée.

## Noir et ombres
Noir inchangé (25,4 % contre 25,9 %). Les whips à la base des pétales restent, mais sans clair
à l'autre bout du pétale, ils ne forment plus un modelé : on lit un rouge assombri par endroits
plutôt qu'un volume.

## Couleur et lumière
- Rouge 37,9 % au lieu de 29,2 %, clair 11,9 % au lieu de 17,9 % : la retouche transforme ~6 % de
  la surface de réserve en rouge.
- L'analyse conclut que **la miniature devient une tache** (remplissage 88,9 %) alors que la
  version avec réserves passe le test (83,8 %). Les réserves de bord de pétale sont ce qui garde la
  rose lisible de loin.
- Plus aucune source de lumière lisible.

## Ce que buk doit retenir
- Les réserves de bord de pétale ne sont pas une finition : sans elles, la rose échoue au test de
  lisibilité en miniature. Les traiter comme une couche obligatoire de la rose.
- Viser pour une rose rouge un ordre de grandeur de **15 à 20 % de clair** dans la surface de la
  fleur (point de départ, mesuré sur un seul exemple) ; sous ~12 %, elle se lit comme une tache.
- Utiliser cette paire comme test de non-régression visuelle : une rose buk dont on retire les
  rehauts ne doit pas ressembler à la version « avec » ; si c'est le cas, les rehauts sont trop
  timides.

## Écart avec buk
La rose actuelle de `buk_composants.rose()` (deux petits rehauts) est plus proche de cette version
retouchée que de l'original : majoritairement rouge, peu de clair. C'est l'écart le plus net mis
en évidence par la paire.
