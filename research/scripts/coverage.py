#!/usr/bin/env python3
"""Mesure si la recherche vidéo a réuni assez de matière, et décide s'il faut continuer.

  python3 research/scripts/coverage.py           # tableau + écrit research/coverage.md
  python3 research/scripts/coverage.py --json    # sortie machine
  python3 research/scripts/coverage.py --quiet   # une ligne

Code de sortie : 0 = assez de matière (arrêter la transcription), 2 = continuer.
Les notes dont le nom commence par « _ » (exemples) sont ignorées.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]


def read_note(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    try:
        _, fm, _ = text.split("---", 2)
        data = yaml.safe_load(fm) or {}
    except Exception as exc:  # note mal formée : signalée, pas bloquante
        print(f"  ! note illisible {path.name}: {exc}", file=sys.stderr)
        return None
    data["_file"] = path.name
    return data


def load_notes(notes_dir: Path) -> list[dict]:
    notes = [read_note(p) for p in sorted(notes_dir.glob("*.md")) if not p.name.startswith("_")]
    notes = [n for n in notes if n]
    notes.sort(key=lambda n: str(n.get("note_le", "")) + n["_file"])
    return notes


def compute(notes: list[dict], cfg: dict) -> dict:
    stop = cfg["stop"]
    themes = {k: {"required": bool(v.get("required")), "videos": set(), "channels": set(), "claims": 0,
                  "accords": {"confirme": 0, "nuance": 0, "contredit": 0, "nouveau": 0}}
              for k, v in cfg["themes"].items()}
    unknown = set()
    for n in notes:
        for c in n.get("claims") or []:
            th = c.get("theme")
            if th not in themes:
                unknown.add(str(th))
                continue
            t = themes[th]
            t["videos"].add(n.get("video_id"))
            if n.get("chaine"):  # une chaîne inconnue ne compte pas comme chaîne distincte
                t["channels"].add(n.get("chaine"))
            t["claims"] += 1
            acc = c.get("accord")
            if acc in t["accords"]:
                t["accords"][acc] += 1
    out_t = {}
    for k, t in themes.items():
        sat = len(t["videos"]) >= stop["min_videos"] and len(t["channels"]) >= stop["min_channels"]
        out_t[k] = {"required": t["required"], "videos": len(t["videos"]), "chaines": len(t["channels"]),
                    "claims": t["claims"], "accords": t["accords"], "sature": sat}
    recent = notes[-stop["window"]:]
    rc = [c for n in recent for c in (n.get("claims") or [])]
    novelty = (sum(1 for c in rc if c.get("nouveau")) / len(rc)) if rc else 1.0
    req = [k for k, v in out_t.items() if v["required"]]
    all_sat = all(out_t[k]["sature"] for k in req)
    dried = len(notes) >= stop["window"] and novelty < stop["novelty_threshold"]
    capped = len(notes) >= stop.get("max_videos", 10**9)
    reason = ("tous les thèmes requis sont saturés" if all_sat else
              f"nouveauté tarie ({novelty:.0%} sur les {stop['window']} dernières notes)" if dried else
              f"plafond de {stop['max_videos']} vidéos atteint" if capped else None)
    return {"notes": len(notes), "nouveaute_recente": round(novelty, 3), "arreter": bool(reason),
            "raison": reason, "themes": out_t, "themes_inconnus": sorted(unknown),
            "manquants": [k for k in req if not out_t[k]["sature"]]}


def report_md(r: dict) -> str:
    rows = "\n".join(
        f"| {k} | {'oui' if v['required'] else 'non'} | {v['videos']} | {v['chaines']} | {v['claims']} | "
        f"{v['accords']['confirme']}/{v['accords']['nuance']}/{v['accords']['contredit']}/{v['accords']['nouveau']} | "
        f"{'✅' if v['sature'] else '…'} |" for k, v in r["themes"].items())
    verdict = (f"**Arrêter la transcription** : {r['raison']}." if r["arreter"] else
               f"**Continuer** — thèmes requis non saturés : {', '.join(r['manquants']) or '—'}.")
    return (f"# Couverture de la recherche\n\n_Généré par coverage.py — ne pas éditer._\n\n"
            f"{r['notes']} notes · nouveauté récente {r['nouveaute_recente']:.0%}\n\n{verdict}\n\n"
            f"| Thème | Requis | Vidéos | Chaînes | Affirmations | conf./nuance/contre/nouv. | Saturé |\n"
            f"|---|---|---|---|---|---|---|\n{rows}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--notes", default=str(ROOT / "notes"))
    ap.add_argument("--themes", default=str(ROOT / "themes.yaml"))
    a = ap.parse_args()
    with open(a.themes, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    r = compute(load_notes(Path(a.notes)), cfg)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    elif a.quiet:
        print(("STOP — " + r["raison"]) if r["arreter"] else f"CONTINUER — manquants : {', '.join(r['manquants'])}")
    else:
        md = report_md(r)
        print(md)
        if Path(a.notes) == ROOT / "notes":
            (ROOT / "coverage.md").write_text(md, encoding="utf-8")
    return 0 if r["arreter"] else 2


if __name__ == "__main__":
    sys.exit(main())
