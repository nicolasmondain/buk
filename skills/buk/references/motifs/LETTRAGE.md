# Lettrage old school

Pièce : `lettrage(f, texte, cx, cy, hauteur, ang=0, arc=0)` et `banderole_texte(f, texte, cx, cy,
largeur)` dans `assets/composants/buk_classiques.py`. Alphabet : A–Z, 0–9, `& ! ' - .`
(planche : `flashs/_motifs/lettrage.svg`).

## Règles

- **Capitales block uniquement**, larges, sans empattement fin : c'est le lettrage des peintres
  d'enseignes, celui qui se lit encore dans 30 ans. Pas de cursive fine, pas de minuscules.
- **Hauteur de capitale ≥ 7 mm** → corps au RL14 (1,7 mm). En dessous, la pièce bascule en RL7
  (index de carte, petites dates) : à réserver aux éléments secondaires.
- **Espacement généreux** : l'encre s'étale avec les années ; les lettres serrées se soudent.
  L'alphabet de buk laisse 2/3 de chasse entre lettres — ne pas le resserrer.
- **Texte court** : 1 à 3 mots (MOM, TRUE LOVE, HOLD FAST, LUCKY, un prénom, une date).
- Sur une banderole, le texte suit la courbe (`arc`) et laisse une marge à chaque bout ;
  `banderole_texte` calcule la taille et refuse de descendre sous une banderole de 13,5 mm de haut.

## Ombre portée

Le style classique pose une ombre noire décalée en bas à droite. Sur des lettres **noires**,
une ombre noire se fond dans la lettre, et un filet décalé fait « baver » le texte (essayé et
écarté sur la v1 de buk). L'ombre portée demande des lettres à **corps clair** (contour noir,
intérieur peau ou rouge) : à développer. En attendant, le lettrage buk est plein noir, sans ombre.

## Erreurs typiques

Lettres trop petites ou trop fines · texte trop long pour la banderole · lettres qui touchent les
bords de la bande · ombre qui double le trait · mélange de styles de lettres.
