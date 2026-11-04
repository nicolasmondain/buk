# Pièces d'assemblage

Toutes dans `assets/composants/buk_composants.py`. Chaque pièce se pose par un point, une taille
et un angle ; le `Flash` range les chemins dans les bonnes couches (aiguille, encre, ordre).

| Pièce | Appel | Règles |
|---|---|---|
| Feuille | `feuille(f, x, y, longueur, angle, flip)` | Noir plein, nervure centrale + 2–3 latérales réservées en peau, orientées vers la pointe. Attachée par sa base à un bord. |
| Goutte | `goutte(f, x, y, s)` | Rouge, contour fin, reflet blanc côté lumière. Par 2–3, tailles différentes. |
| Banderole | `banderole(f, x1, x2, y, h, pli)` | Bande cintrée en peau (pour le lettrage), queues en aronde décalées vers le bas, replis en noir plein, ombre côté bande. Hauteur ≥ 9 mm si lettrage. |
| Étoile nautique | `etoile_nautique(f, x, y, r)` | Chaque branche moitié noire, moitié rouge, toujours dans le même sens de rotation. |
| Réserve | `reserve(P(...), x0, y0, ..., x3, y3, w0, w1)` | Bande de peau effilée le long d'une courbe, à ajouter au chemin d'une zone noire (plumes, nervures, reflets). |
| Rose | `rose(f, x, y, r)` | Voir `ROSE.md`. |
| Hirondelle | `hirondelle(f, x, y, L, ang, flip)` | Voir `HIRONDELLE.md`. |
| Lettrage, banderole à texte | `lettrage(...)`, `banderole_texte(...)` | Voir `LETTRAGE.md` (dans `buk_classiques.py`). |
| Fer à cheval, dés, cartes, enseignes, ancre, crâne, cœur, dague | voir `CLASSIQUES.md` | Dans `buk_classiques.py`. |
| Masque | `f.masquer(x1, y1, x2, y2)` | Découpe ce qui est déjà dessiné sous un élément posé devant. |

## Composer un flash

```python
import sys; sys.path.insert(0, "skills/buk/assets/composants")
from buk_composants import Flash, rose, feuille, banderole
f = Flash("Rose et banderole", 80, 80, placement="avant-bras")
feuille(f, 22, 50, 18, angle=160); feuille(f, 58, 50, 18, angle=20)
rose(f, 40, 38, 20)
banderole(f, 8, 72, 66, 11)
f.ecrire("flashs/rose/rose.svg")
```

Ordre d'appel = ordre d'empilement *à l'intérieur d'une couche* ; entre couches, l'ordre est
fixe (rouge, ombrage, noir, rehauts, puis traits). Pour qu'une feuille passe « derrière » la
rose, place sa base sur le bord de la silhouette plutôt qu'à l'intérieur.

## À venir

Voir la fin de `CLASSIQUES.md`. Chaque nouvelle pièce = une fonction + une fiche + une planche
validée par la boucle de `CRITIQUE.md`.
