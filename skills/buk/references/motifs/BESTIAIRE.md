# Bestiaire, marine et pin-up

Pièces dans `assets/composants/buk_bestiaire.py` ; planches `flashs/_motifs/bestiaire.svg` et
`marine_pinup.svg`. Outils communs : `courbe()` (chaîne de Béziers → points), `bande()` (corps
d'épaisseur variable le long d'une courbe), `poly()`.

## Leçon de la v2 : pourquoi la v1 faisait « dessin d'enfant »

La v1 de la panthère et du serpent était lisible mais naïve : formes géométriques
simples, aucun dessin intérieur, silhouettes en segments droits, une seule épaisseur partout.
Un flash traditionnel tient par **la densité du dessin intérieur** et **la hiérarchie** :
- de la **texture structurée** : pelage en petits traits réservés, plumes une à une, écailles ;
- un **contour lissé** (`lisse()`) avec des **pointes franches** aux bons endroits (touffes,
  oreilles, griffes), jamais des segments droits ;
- deux épaisseurs : contour des masses au RL11, détails (plumes, écailles) au RL7/RL5 ;
- des **superpositions** propres : `Flash.masquer_forme(d)` efface les traits de derrière.
Avant de livrer un animal, comparer à la v1 (planche avant/après) : si le dessin intérieur ne
raconte pas la matière (poil, plume, écaille), ce n'est pas fini.

## Panthère — `panthere(f, x, y, h)`
- Tête de face en rictus. Silhouette lissée à **touffes de joues en pointe**, oreilles couchées
  à intérieur rouge et poils.
- Sujet noir lu par ses réserves : **pelage** (chevrons au front, traits rayonnants aux joues),
  **arcades qui plongent vers le nez** (colère), yeux à pupille fendue, **rides du rictus** sur
  l'arête, truffe cernée de peau, coussinets en points, moustaches qui débordent.
- Grande gueule rouge ombrée vers la gorge, crocs haut et bas, incisives.

## Aigle
Retiré (trop complexe pour un rendu propre point par point). Pour un aigle, partir d'un vrai
flash importé (`buk_flash_import.py`) et le simplifier.

## Serpent — `serpent(f, x, y, h, flip)`
- Corps en S construit par `bande()`. **Ventre en peau continu, écailles en échelle** ; anneaux
  corail (rouge large, noir, peau, noir) **sur le dos seulement**.
- **Tête de profil** au bout d'un cou qui tourne (une tête vue de dessus se lit mal) : mâchoires
  lissées, gueule rouge, crochets blancs, arcade, œil, narine, langue fourchue qui sort.

## Flammes — `flammes(f, x, y, largeur, hauteur, n)`
- Une **seule silhouette** de langues qui ondulent, pointes recourbées vers l'extérieur, la plus
  haute au centre ; une langue intérieure par flamme ; whip noir qui monte depuis la base.
- Servent de fond (cœur en flammes, crâne en flammes) : poser les flammes d'abord, le sujet ensuite.

## Toile d'araignée — `toile(f, x, y, r, ouverture=360)`
- Rayons + tours **affaissés vers le centre**, traits fins ; araignée noire suspendue à un fil.
- `ouverture=180` ou `90` (avec `ang0`) pour la toile de coude ou d'épaule.

## Trois-mâts — `bateau(f, x, y, longueur)`
- Coque noire à **sabords réservés**, **liston rouge** (réservé dans le noir, sinon il disparaît),
  trois mâts, trois voiles carrées par mât gonflées avec whip côté vent, flammes rouges en tête,
  vagues en volutes et mer légère (pas de bloc rectangulaire).
- Les voiles de mâts voisins ne doivent pas se toucher.

## Phare — `phare(f, x, y, h)`
- Tour effilée à **bandes rouges / peau**, ombre côté droit, galerie et dôme noirs, lanterne en
  peau avec rehaut blanc, faisceaux en traits, rochers noirs à réserves, vagues.

## Pin-up — `pinup(f, x, y, h, fleur=True)`
- Portrait tête et épaules, **habillée** : buk dessine la pin-up classique des planches de
  marins (coiffure à boucles, rouge à lèvres, rose dans les cheveux), jamais de nu ni de pose
  suggestive, et jamais le portrait d'une personne réelle.
- Chevelure noire à boucles réservées, visage en peau sous la frange, paupières baissées à cils,
  lèvres rouges avec reflet, rose découpée dans le noir des cheveux (sinon le noir la recouvre).

## Règle commune

Tout élément rouge posé sur une masse noire doit être **réservé** dans le noir (trou dans la
zone noire) : les couches s'empilent rouge → ombre → noir, donc un rouge sous un noir disparaît.
Défaut constaté deux fois (liston du bateau, rose de la pin-up).
