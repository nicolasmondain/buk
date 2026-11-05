---
image: t101-packing-schema.png
source: https://tattooing101.com/learn/styles/how-to-shade-american-traditional-tattoos/
motif: autre
support: flash
mesures: {noir: 12.2, rouge: 0.0, clair: 85.3, autre: 2.6, trait_mediane_pct: 0.53}
---
Schéma pédagogique sur fond crème : deux vignettes du même noir plein, vu de près et vu de loin.

## Construction
À gauche, quelques boucles ovales qui se chevauchent (le geste : petits cercles serrés, lents,
contrôlés). À droite, le résultat à distance : une tache noire pleine au **bord légèrement
dentelé**, sans aucun trou.

## Hiérarchie des traits
Pas de contour : la masse noire se suffit. Le bord irrégulier de la vignette « de loin » vient des
cercles, il n'est pas dessiné.

## Noir et ombres
Le message : un noir plein est **opaque et homogène** à l'échelle de lecture, quelle que soit la
façon dont il est construit. Aucune réserve, aucun reflet de peau à l'intérieur.

## Couleur et lumière
Hors sujet (schéma monochrome).

## Ce que buk doit retenir
- Le noir plein (`noir`, `noir-fin`) est un aplat sans trou ni grain : dans l'aperçu, ne jamais
  le texturer ; la texture est réservée au whip/poivré.
- Une zone `solid-black` doit être assez large pour être « packée » en petits cercles : éviter les
  noirs pleins en filet très fin (en dessous de ~1,5 mm, c'est un trait, pas un noir plein).
- Le bord d'un noir plein suit un trait ou une forme nette ; ce n'est pas lui qui fait la
  transition vers la peau (c'est le whip qui s'en charge, cf. note whip).

## Écart avec buk
Conforme : `TECHNIQUES.md` décrit déjà le packing et l'aperçu rend `solid-black` en aplat. Écart
possible côté composants : quelques zones `noir-fin` très étroites (croissants, liserés) qui, à
la taille d'un flash, sont plus des traits épais que des noirs packés ; à surveiller avec un
seuil de largeur minimale dans `buk_validate.py`.
