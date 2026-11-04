---
# EXEMPLE DE FORMAT — fichier ignoré par coverage.py (nom commençant par « _ »).
# Une note = une vidéo. Nom du fichier : <video_id>.md
video_id: EXEMPLE0001
titre: "Titre exact de la vidéo"
chaine: "Nom de la chaîne"
url: https://www.youtube.com/watch?v=EXEMPLE0001
langue: en
note_le: 2026-11-04
pertinence: haute          # haute | moyenne | faible (faible = vidéo peu utile, on le dit)
themes: [lining, aiguilles]
claims:
  # Une affirmation = une idée technique, reformulée en français avec tes mots (≤ 30 mots,
  # jamais de citation longue). `t` = horodatage dans la vidéo pour vérification.
  - theme: lining
    claim: "Le contour se fait en tirant la machine vers soi, peau tendue en trois points."
    valeurs: {}
    t: "02:10"
    accord: confirme       # confirme | nuance | contredit | nouveau (par rapport aux références actuelles)
    nouveau: false         # true si l'idée n'existe encore dans aucune note ni référence
  - theme: aiguilles
    claim: "Pour un contour de pièce moyenne, l'auteur utilise une 11RL en 0,35 mm long taper."
    valeurs: {aiguille: RL11, diametre_mm: 0.35, taper: LT}
    t: "04:45"
    accord: confirme
    nouveau: false
  - theme: reglages-machine
    claim: "Sur sa rotative, l'auteur ligne autour de 8,5 V et baisse d'environ 1 V pour ombrer."
    valeurs: {technique: lining, machine: rotary, tension_v: 8.5}
    t: "05:30"
    accord: nuance
    nouveau: true
---

Résumé en 2–4 phrases, paraphrasé : ce que la vidéo apporte, et ses limites (ex. : montre le
geste mais ne donne aucun réglage).
