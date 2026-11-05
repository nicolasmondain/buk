# Importer un vrai flash

`scripts/buk_flash_import.py` convertit un motif d'une planche (scan ou photo d'un dessin) en
flash au contrat buk. C'est la voie principale pour un dessin de qualité.

## Ce que fait le script

| Étape | Méthode | Résultat buk |
|---|---|---|
| Papier | couleur médiane des pixels clairs (jaune, crème, brun) ; tout est mesuré par rapport à lui | — |
| Trait de plume | « black-hat » (plus sombre que son voisinage, même sur un aplat rouge), squelette, raccord des bouts coupés, lissage | `lining` RL5, 0,8 mm |
| Silhouette | union de tout ce qui est dessiné, trous bouchés, contour lissé | `bold-line` RL11, 1,4 mm |
| Aplats | chaque région fermée par les traits prend la couleur qui y domine et se remplit jusque sous le trait | rouge → `solid-red` ; noir épais et vert → `solid-black` ; bleu → `whip` |
| Nettoyage | petits morceaux coupés par le cadre et aplats noirs au bord (œillets de planche) supprimés | — |

## Cadrage

- Cadre serré autour du motif avec ~3 % de marge ; aucun morceau du motif voisin.
- Repérer les coordonnées sur une version réduite de la planche à 1000 px avec une grille
  (voir `research/design/flash_cc0.py`, qui garde l'échelle et la boîte de chaque motif).

## Après l'import : retouches habituelles

1. `buk_render.py` puis la boucle de `CRITIQUE.md`.
2. **Lettrage** : les petites lettres manuscrites (banderoles) sortent souvent déformées. Les
   effacer et reposer le texte avec `lettrage()` / `banderole_texte()` de
   `assets/composants/buk_classiques.py`.
3. **Couleurs** : le bleu des vieux flashs devient de l'ombrage noir ; le vert devient noir plein.
   Vérifier que ça reste lisible ; sinon passer la zone en peau.
4. **Taille** : en dessous de ~5 cm, les hachures fines des feuilles se bouchent : les supprimer.

## Ce qu'on importe, ce qu'on n'importe pas

Domaine public (CC0 : Smithsonian, Met, catégories Wikimedia Commons), dessins de la personne,
flashs achetés avec licence d'usage. Jamais une image de blog, d'Instagram ou d'un artiste vivant
sans son accord : on l'analyse (principes), on ne la recopie pas.
