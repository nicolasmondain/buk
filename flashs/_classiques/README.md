# Bibliothèque de flashs classiques

Vrais flashs traditionnels de planches du domaine public (CC0 — Smithsonian American Art Museum ; détail dans `research/design/SOURCES_CC0.md`), convertis au contrat
buk par `skills/buk/scripts/buk_flash_import.py`. Les SVG vivent dans `skills/buk/assets/classiques/`
(ils partent avec le skill dans `dist/buk.zip`) ; ce dossier ne garde que les aperçus. Point de départ de tout nouveau flash : copier le
SVG dans `flashs/<nom>/`, adapter, valider, générer les calques.

| Flash | Fichier | État |
|---|---|---|
| Rose | `rose.svg` | prêt |
| Hirondelle FRIENDS | `hirondelle_friends.svg` | prêt (texte de banderole à reposer) |
| Hirondelle | `hirondelle.svg` | prêt |
| Papillon | `papillon.svg` | prêt |
| Dague et lune | `dague_lune.svg` | prêt |
| Trois-mâts | `trois_mats.svg` | prêt |
| Cœur bouclier | `coeur_bouclier.svg` | prêt |
| Ancre U.S.N. | `ancre_usn.svg` | prêt |
| Cartes LUCKY | `cartes_lucky.svg` | prêt |
| Croix FATHER | `croix_father.svg` | texte à reposer (`lettrage()`) |
| Death before dishonor | `dague_death.svg` | texte à reposer |
| Crâne DEAD SPORT | `crane_dead_sport.svg` | texte à reposer |

Régénérer : `python3 research/design/flash_cc0.py` (images sources dans `research/design/images/`).
