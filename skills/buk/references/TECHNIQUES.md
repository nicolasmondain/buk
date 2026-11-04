# Techniques

> Statut : seed. Chaque technique a son équivalent structuré dans `assets/techniques.json`
> (c'est ce fichier que lisent les scripts pour remplir la fiche des calques).

## Le stretch (tension de peau) — avant tout le reste

Trois points : la main libre tend la peau en écartant deux doigts, la main qui tient la machine
tend le troisième côté avec son appui. Une peau bien tendue = trait net, encre qui rentre du
premier coup. Une peau molle = trait qui ondule et blowouts.

## Lining (traits) — `lining`, `bold-line`

- Commencer par le bas du dessin et par le côté opposé à la main qui travaille, pour ne pas
  effacer le stencil avec la main.
- **Tirer** le trait vers soi plutôt que le pousser ; poser l'aiguille, laisser la machine
  démarrer l'encrage, avancer d'une vitesse constante, sortir en douceur.
- Un trait = un passage, d'un seul mouvement le plus long possible. Les raccords se font en
  repartant **dans** le trait existant, pas bout à bout.
- Les grands cercles se font en plusieurs arcs en tournant la peau/le bras plutôt que le poignet.
- `bold-line` = contour extérieur à grosse aiguille (RL11–14) : un peu plus lent, même geste.
- Essuyer souvent (sopalin + vaseline/savon) pour voir le stencil.

Réussite : trait plein, régulier, bords nets après essuyage, pas de halo.

## Whip shading (ombrage au fouet) — `whip`

- Mouvement de pendule du poignet : on pique dans la zone sombre (contre le trait), on remonte
  en « fouettant », l'aiguille sort de la peau en fin de course. La densité diminue naturellement
  vers la fin du geste.
- Passages rapides et nombreux plutôt que lents et appuyés ; on construit la densité par couches.
- Le départ du geste est toujours le côté le plus sombre (le contour ou l'arête indiquée par la
  flèche du calque).
- Magnum arrondi (RM7–RM9) : dégradé doux ; round shader (RS7) pour les petites zones.

Réussite : dégradé continu du noir vers la peau, sans traînées ni ronds.

## Poivré / stipple — `pepper`

- Petits points obtenus en tapotant ou en avançant très vite avec une machine plus lente.
- Densité de points = valeur. Utile pour les textures (sable, ombre de banderole, fond).

## Noir plein — `solid-black`

- Petits cercles serrés qui se chevauchent (« packing »), ou passages croisés lents à la magnum.
- Commencer contre les traits avec une petite aiguille si la zone est étroite, puis grosse magnum
  pour le centre.
- Une zone pleine doit être **saturée au premier passage** : repasser dix fois abîme la peau.
- Vérifier en essuyant : pas de trous, pas de reflets de peau.

## Rouge plein — `solid-red`

- Même geste que le noir plein, main un peu plus lente : les couleurs rentrent moins facilement
  que le noir.
- Cartouche neuve, capsule propre, essuyer souvent le surplus de noir des traits pour ne pas
  « salir » le rouge.
- Remplir jusqu'au trait : le rouge doit toucher le contour, sans halo de peau.

## Rehauts blancs — `highlight-white`

- En tout dernier, petites virgules ou points (RL3–RL5), sur une zone déjà saturée de rouge ou de
  noir. Pas de repasses : un passage propre.
- Le blanc frais paraît toujours plus visible qu'une fois cicatrisé ; il ne faut pas « forcer ».

## Erreurs fréquentes

| Symptôme | Cause probable |
|---|---|
| Blowout (halo flou) | Trop profond, angle trop couché, peau mal tendue |
| Trait tremblé | Main trop lente, appui instable, café |
| Trait irrégulier/pâle | Profondeur trop faible, main trop rapide, pas assez d'encre dans la cartouche |
| Remplissage « troué » après cicatrisation | Passage trop rapide, peau gonflée, zone surtravaillée |
| Rouge qui grise | Noir poussé dans le rouge (essuyer, rincer, cartouche neuve) |
