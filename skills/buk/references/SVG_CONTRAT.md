# Contrat SVG d'un flash buk

Les scripts ne savent lire que ce format. `buk_validate.py` le vérifie.

## Racine

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     width="80mm" height="100mm" viewBox="0 0 80 100"
     data-buk-title="Dague et cœur" data-buk-placement="avant-bras">
```

- `width`/`height` en **mm** et `viewBox` en mm : 1 unité = 1 mm. C'est ce qui garantit
  l'impression à l'échelle 1:1.
- Coordonnées **absolues** dans les `d` de chemins (M, L, C, Q, H, V, Z en majuscules) : les
  scripts calculent les centres de zones à partir des points.

## Couches

Chaque élément dessiné vit dans un `<g>` de couche, enfant direct de `<svg>` :

```xml
<g id="contour" data-buk-kind="line" data-technique="lining"
   data-needle="RL11" data-ink="noir" data-order="1"> … </g>
```

| Attribut | Valeurs | Rôle |
|---|---|---|
| `data-buk-kind` | `line` · `zone` | `line` = trait à tatouer (stroke) ; `zone` = surface à remplir ou ombrer |
| `data-technique` | `lining` · `bold-line` · `whip` · `pepper` · `solid-black` · `solid-red` · `highlight-white` | Clé dans `assets/techniques.json` |
| `data-needle` | code de `assets/aiguilles.json` (`RL3` … `RL14`, `RS5` … `RS9`, `RM5` … `RM15`, `M7` … `M15`) | Aiguille de la couche |
| `data-ink` | `noir` · `rouge` · `blanc` | Encre |
| `data-order` | entier ≥ 1 | Ordre de passage dans la séance |
| `data-direction` | (optionnel, `whip`) angle en degrés, 0 = vers la droite, 90 = vers le bas | Sens du coup de fouet, dessiné en flèche sur le calque |

Règles :

- Couches `line` : éléments avec `stroke`, `fill="none"`, `stroke-linecap="round"`,
  `stroke-linejoin="round"`. Épaisseur `stroke-width` en mm cohérente avec l'aiguille
  (voir tableau ci-dessous).
- Couches `zone` : éléments fermés (`path` terminé par `Z`, `circle`, `ellipse`, `polygon`),
  sans contour. Une zone repose **à l'intérieur** des traits : elle peut déborder sous le trait,
  jamais au-delà.
- Une zone `whip` porte un `fill` noir ; l'aperçu la rend en dégradé.
- Optionnel sur une zone : `data-label-x` / `data-label-y` pour placer le code lettre du calque.
- Ordre recommandé : `lining`/`bold-line` (1–2), `whip`/`pepper` (3), `solid-black` (4),
  `solid-red` (5), `highlight-white` (6).
- Pas de `<image>`, pas de `<text>` dans les couches (le lettrage est dessiné en chemins),
  pas de `transform` sur les `<g>` de couche (autorisé sur les éléments enfants).

## Épaisseur de trait ↔ aiguille (aperçu)

| Aiguille | stroke-width (mm) |
|---|---|
| RL3 | 0.6 |
| RL5 | 0.8 |
| RL7 | 1.0 |
| RL9 | 1.2 |
| RL11 | 1.4 |
| RL14 | 1.7 |

## Squelette minimal

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="60mm" height="60mm" viewBox="0 0 60 60"
     data-buk-title="Cœur" data-buk-placement="mollet">
  <g id="rouge" data-buk-kind="zone" data-technique="solid-red" data-needle="RM11"
     data-ink="rouge" data-order="5">
    <path fill="#C1121F" d="M30 52 C10 38 6 26 12 18 C18 10 27 12 30 20 C33 12 42 10 48 18 C54 26 50 38 30 52 Z"/>
  </g>
  <g id="contour" data-buk-kind="line" data-technique="bold-line" data-needle="RL11"
     data-ink="noir" data-order="1">
    <path fill="none" stroke="#111111" stroke-width="1.4" stroke-linecap="round"
          stroke-linejoin="round"
          d="M30 52 C10 38 6 26 12 18 C18 10 27 12 30 20 C33 12 42 10 48 18 C54 26 50 38 30 52 Z"/>
  </g>
</svg>
```

L'ordre des `<g>` dans le fichier est l'ordre d'empilement de l'aperçu (zones d'abord, traits
au-dessus) ; l'ordre de séance, lui, vient de `data-order`.
