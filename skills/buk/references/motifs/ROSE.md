# Rose traditionnelle

Pièce : `rose(f, cx, cy, r)` dans `assets/composants/buk_composants.py` · feuilles : `feuille()`.
Planche : `python3 scripts/buk_planche.py` sur un flash qui l'utilise.

## Construction

1. **Silhouette festonnée**, légèrement plus large que haute : deux lobes arrière avec une
   encoche au centre, deux pétales latéraux à pointe roulée, deux lobes bas. Jamais un cercle :
   un contour régulier donne un pot ou une fraise (défaut constaté sur la v1 de buk).
2. **La coupe** en haut : bord arrière + lèvre avant qui forment une ouverture en amande. Le
   cœur est fait de deux « C » emboîtés, pas d'une spirale mathématique.
3. **Les pétales avant** : deux courbes en S **asymétriques** qui enveloppent la coupe ; l'une
   finit par un crochet roulé. Deux courbes symétriques forment une boule (défaut v2).
4. **La lèvre basse** sépare les pétales avant des lobes bas.
5. **Les plis latéraux** : un trait court qui part de la pointe roulée vers le centre.

## Noir et ombres

- Fond de la coupe : croissant de **noir plein** contre le bord arrière — c'est la zone la plus
  sombre de la rose ; le cœur doit rester lisible devant.
- Whip **sous chaque lèvre** et **à la base de chaque pétale**, toujours d'un seul côté du
  trait : l'ombre part du trait vers l'intérieur du pétale qui passe dessous.
- Densité : les ombres doivent compter comme une **valeur** à part entière. Test : dans
  `valeurs.png`, elles doivent apparaître en noir/gris franc. Sur la v3 de buk elles
  disparaissaient → allonger les zones (jusqu'au tiers du pétale) et démarrer en noir plein.
- Ne pas ombrer les deux côtés d'un même trait : la forme s'aplatit.

## Feuilles

Deux ou trois, en **noir plein** avec nervure centrale réservée en peau et 2–3 nervures
latérales courtes orientées vers la pointe. Attachées au bord de la rose (jamais flottantes),
orientées en éventail vers l'extérieur ; une feuille plus petite en haut casse la symétrie.

## Couleur

Rouge plein sur toute la rose. Rehauts : une virgule sur le lobe arrière gauche, un trait sur la
pointe droite (lumière en haut à gauche). En old school buk : pas de vert, les feuilles sont noires.

## Erreurs typiques

Silhouette ronde · spirale centrale perdue dans un aplat noir · pétales avant symétriques ·
ombres timides · feuilles qui flottent ou couvrent les pétales · nervures en « arêtes de poisson ».

## Sources

Principes repris et reformulés depuis le guide de dessin traditionnel de
[Tattooing 101](https://tattooing101.com/learn/guides/draw-traditional/) (construction à partir
de formes simples, ombre d'un seul côté du trait, réserves blanches) et son guide
[d'ombrage traditionnel](https://tattooing101.com/learn/styles/how-to-shade-american-traditional-tattoos/)
(arrière-plan plus sombre que le premier plan).
