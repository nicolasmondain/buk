# Classiques : grammaire de chaque motif

Pièces dans `assets/composants/buk_classiques.py` ; planches dans `flashs/_motifs/`
(`classiques`, `coeur_dague`, `compositions`). Chaque pièce : `piece(f, cx, cy, taille, ang=…)`.

## Fer à cheval — `fer_a_cheval(f, x, y, h)`
- **Ouverture vers le haut** (il garde la chance) ; vers le bas, il la verse : ne l'inverser que
  si la personne le demande.
- Bande épaisse (≈ 40 % du rayon), **éponges** coupées net, **6 étampures** (trous de clous)
  en noir sur la rainure, 3 de chaque côté.
- Bande en peau, whip sur la moitié droite depuis le bord extérieur, reflet blanc à gauche.
- Défaut constaté v1 : bande trop fine et éponges en pointe → ressemblait à un aimant.

## Dés — `de(f, x, y, arete, faces=(dessus, gauche, droite))`
- Vue de 3/4 haut, **trois faces visibles**. Dessus en peau, face gauche en peau avec whip,
  **face droite en noir plein avec points blancs** : c'est ce contraste qui fait lire un dé.
- Par paire, tailles et angles légèrement différents, valeurs différentes (souvent 7 ou 11 au total).

## Cartes — `carte(f, x, y, h, valeur, enseigne)` · `enseigne(f, kind, x, y, s)`
- Ratio 0,7, coins arrondis, **index** (lettre + petite enseigne) en haut à gauche et retourné en
  bas à droite, grande enseigne au centre (≈ 30 % de la hauteur).
- Enseignes : cœur et carreau en **rouge**, pique et trèfle en **noir**.
- Ombre portée de la carte sur la peau (droite et bas) pour le volume.
- **Ne pas faire se chevaucher deux cartes** : leur intérieur est en peau, celle de derrière
  transparaîtrait. Les poser en éventail, côte à côte.

## Ancre marine — `ancre(f, x, y, h)`
- Organeau (anneau) en haut, **jas** (barre) en noir plein avec boules et reflet, verge et bras
  **d'un seul contour**, **pattes en fer de lance** dans le prolongement des bras.
- Whip de gauche à droite sur la verge et les bras.
- Avec banderole : la passer **sur la verge, sous le jas**, jamais sur les bras (ce sont eux qui
  font reconnaître l'ancre). Classique : HOLD FAST.
- Défaut constaté v1 : pattes en flèches renflées, plantées de travers.

## Crâne — `crane(f, x, y, h)`
- De face : calotte large, pommettes marquées, mâchoire étroite.
- **Orbites et nez (cœur inversé) en noir plein**, reflet blanc dans chaque orbite.
- Dents : une bande, une ligne d'occlusion, 5 séparations.
- Whip aux tempes, sous les pommettes et sous la mâchoire ; la peau fait le blanc de l'os.

## Cœur — `coeur(f, x, y, largeur)`
- Rouge plein, **croissant noir le long du bord bas-gauche** prolongé par un whip, virgule
  blanche en haut à droite.
- Avec dague : la **garde au-dessus du cœur**, la lame qui le traverse.
- Avec banderole (MOM) : banderole devant, sur le tiers bas du cœur.

## Dague — `dague(f, x, y, longueur, ang)`
- Pommeau et garde en noir plein, poignée avec bagues, lame avec arête centrale et whip sur une
  moitié. Elle souligne l'axe du membre : la poser dans l'axe de l'avant-bras ou du tibia.

## Composer avec une banderole devant

`banderole_texte(..., devant=True)` (par défaut) **découpe** tout ce qui a déjà été dessiné
sous la bande et les queues (`Flash.masquer`). Ordre d'appel : d'abord ce qui est derrière,
ensuite la banderole. Le même `f.masquer(x1, y1, x2, y2)` sert pour tout élément rectangulaire
posé devant.

## Encore à faire

Panthère, aigle, serpent, flammes, toile d'araignée, bateau, phare, pin-up, lune. Chacun : une
fonction, une entrée ici, une planche passée par la boucle de `CRITIQUE.md`.
