#!/usr/bin/env python3
"""Collecte des vidéos YouTube et de leurs transcripts pour nourrir le skill buk.

  python3 research/scripts/harvest.py list            # catalogue les vidéos (index.json)
  python3 research/scripts/harvest.py fetch -n 5      # transcrit les 5 vidéos les plus utiles
  python3 research/scripts/harvest.py status          # résumé du catalogue
  python3 research/scripts/harvest.py skip <id> "raison"

`fetch` refuse de continuer si coverage.py déclare la recherche terminée (sauf --force) :
c'est ce qui arrête la transcription une fois la matière suffisante.

Les transcripts vont dans research/transcripts/ (ignoré par git : ce sont les paroles des
auteurs, on ne les redistribue pas). Seules les notes paraphrasées de research/notes/ sont
versionnées.

Dépendances : yt-dlp, pyyaml (pip install -r requirements.txt)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    from yt_dlp import YoutubeDL
except ImportError:  # pragma: no cover
    sys.exit("Installer les dépendances : pip install -r requirements.txt  (yt-dlp, pyyaml)")

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.json"
TRANSCRIPTS = ROOT / "transcripts"
NOTES = ROOT / "notes"


def load_yaml(name: str) -> dict:
    with open(ROOT / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"videos": {}, "channels": {}}


def save_index(idx: dict) -> None:
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def ydl(extra: dict | None = None) -> YoutubeDL:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": "in_playlist",
            "ignoreerrors": True}
    opts.update(extra or {})
    return YoutubeDL(opts)


def guess_themes(title: str, themes: dict) -> list[str]:
    t = title.lower()
    return [k for k, v in themes.items() if any(kw.lower() in t for kw in v.get("keywords", []))]


# --------------------------------------------------------------------------- list

def resolve_channel(name: str) -> str | None:
    with ydl({"extract_flat": True}) as y:
        info = y.extract_info(f"ytsearch5:{name}", download=False) or {}
    for e in info.get("entries") or []:
        if e and (e.get("channel") or "").lower() == name.lower() and e.get("channel_url"):
            return e["channel_url"]
    for e in info.get("entries") or []:
        if e and e.get("channel_url"):
            return e["channel_url"]
    return None


def add_entry(idx, e, source, priority, themes, limits):
    if not e or not e.get("id") or len(e["id"]) != 11:
        return False
    dur = e.get("duration") or 0
    if dur and (dur < limits["min_duration_s"] or dur > limits["max_duration_s"]):
        return False
    vid = e["id"]
    if vid in idx["videos"]:
        v = idx["videos"][vid]
        v["sources"] = sorted(set(v.get("sources", [])) | {source})
        v["priority"] = min(v.get("priority", 3), priority)
        return False
    title = e.get("title") or ""
    idx["videos"][vid] = {
        "id": vid, "title": title, "channel": e.get("channel") or e.get("uploader") or "",
        "url": f"https://www.youtube.com/watch?v={vid}", "duration_s": dur, "priority": priority,
        "sources": [source], "themes_guess": guess_themes(title, themes), "status": "pending",
    }
    return True


def cmd_list(args) -> int:
    cfg, th = load_yaml("sources.yaml"), load_yaml("themes.yaml")["themes"]
    limits = cfg.get("limits", {})
    idx = load_index()
    added = 0
    for ch in cfg.get("channels") or []:
        url = ch.get("url") or idx["channels"].get(ch["name"], {}).get("url")
        if not url:
            url = resolve_channel(ch["name"])
            if not url:
                print(f"  ! chaîne introuvable : {ch['name']}")
                continue
        idx["channels"][ch["name"]] = {"url": url, "resolved_by": "config" if ch.get("url") else "search"}
        with ydl({"playlistend": limits.get("videos_per_channel", 60)}) as y:
            info = y.extract_info(url.rstrip("/") + "/videos", download=False) or {}
        n = sum(add_entry(idx, e, f"chaîne:{ch['name']}", ch.get("priority", 2), th, limits)
                for e in info.get("entries") or [])
        added += n
        print(f"  {ch['name']}: +{n} vidéos ({url})")
    for s in cfg.get("searches") or []:
        with ydl() as y:
            info = y.extract_info(f"ytsearch{limits.get('results_per_search', 15)}:{s['query']}", download=False) or {}
        n = sum(add_entry(idx, e, f"recherche:{s['query']}", s.get("priority", 2), th, limits)
                for e in info.get("entries") or [])
        added += n
        print(f"  « {s['query']} »: +{n}")
    save_index(idx)
    print(f"{added} nouvelles vidéos, {len(idx['videos'])} au catalogue → {INDEX.relative_to(ROOT.parent)}")
    return 0


# --------------------------------------------------------------------------- fetch

def vtt_to_text(vtt: str, chunk_s: int = 30) -> str:
    """VTT (y compris sous-titres auto « roulants ») → texte horodaté par tranches."""
    out, seen, cur_t, buf = [], set(), None, []

    def ts(h, m, s):
        return int(h) * 3600 + int(m) * 60 + float(s)

    t = 0.0
    for line in vtt.splitlines():
        m = re.match(r"(\d+):(\d\d):(\d\d\.\d+)\s+-->", line) or re.match(r"()(\d\d):(\d\d\.\d+)\s+-->", line)
        if m:
            t = ts(m.group(1) or 0, m.group(2), m.group(3))
            continue
        if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in line:
            continue
        txt = re.sub(r"<[^>]+>", "", line).strip()
        if not txt or txt in seen:
            continue
        seen.add(txt)
        if cur_t is None or t - cur_t >= chunk_s:
            if buf:
                out.append(f"[{int(cur_t // 60):02d}:{int(cur_t % 60):02d}] " + " ".join(buf))
            cur_t, buf = t, []
        buf.append(txt)
    if buf:
        out.append(f"[{int(cur_t // 60):02d}:{int(cur_t % 60):02d}] " + " ".join(buf))
    return "\n".join(out)


def fetch_subs(vid: str, langs: list[str]) -> tuple[str | None, str | None]:
    with tempfile.TemporaryDirectory() as tmp:
        opts = {"writesubtitles": True, "writeautomaticsub": True, "subtitlesformat": "vtt",
                "subtitleslangs": langs + [f"{l}-orig" for l in langs], "outtmpl": f"{tmp}/%(id)s.%(ext)s",
                "extract_flat": False}
        with ydl(opts) as y:
            y.download([f"https://www.youtube.com/watch?v={vid}"])
        files = sorted(Path(tmp).glob(f"{vid}*.vtt"))
        for lang in langs:  # préférence : sous-titres de la langue demandée, manuels puis auto
            for f in files:
                if re.search(rf"\.{lang}(-orig)?\.vtt$", f.name):
                    return vtt_to_text(f.read_text(encoding="utf-8", errors="ignore")), lang
        if files:
            return vtt_to_text(files[0].read_text(encoding="utf-8", errors="ignore")), files[0].suffixes[-2][1:]
    return None, None


def coverage_says_stop() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("coverage.py")), "--quiet"],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def unsaturated_themes() -> set[str]:
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("coverage.py")), "--json"],
                       capture_output=True, text=True)
    try:
        data = json.loads(r.stdout)
        return {k for k, v in data["themes"].items() if not v["sature"]}
    except Exception:
        return set()


def cmd_fetch(args) -> int:
    stop, msg = coverage_says_stop()
    if stop and not args.force:
        print("Recherche terminée — on n'a plus besoin de transcrire.\n" + msg)
        return 0
    cfg = load_yaml("sources.yaml")
    langs = cfg.get("limits", {}).get("languages", ["fr", "en"])
    idx = load_index()
    need = unsaturated_themes()
    pend = [v for v in idx["videos"].values() if v["status"] == "pending"]
    pend.sort(key=lambda v: (-len(set(v["themes_guess"]) & need) if need else 0, v["priority"],
                             -len(v["themes_guess"])))
    TRANSCRIPTS.mkdir(exist_ok=True)
    done = 0
    for v in pend:
        if done >= args.n:
            break
        text, lang = fetch_subs(v["id"], langs)
        if not text or len(text) < 400:
            v["status"] = "no-transcript"
            print(f"  - {v['id']} sans sous-titres exploitables : {v['title'][:60]}")
            continue
        head = (f"---\nvideo_id: {v['id']}\ntitre: {json.dumps(v['title'], ensure_ascii=False)}\n"
                f"chaine: {json.dumps(v['channel'], ensure_ascii=False)}\nurl: {v['url']}\nlangue: {lang}\n"
                f"themes_devines: {json.dumps(v['themes_guess'], ensure_ascii=False)}\n"
                f"recupere: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n---\n\n")
        (TRANSCRIPTS / f"{v['id']}.md").write_text(head + text + "\n", encoding="utf-8")
        v["status"] = "transcribed"
        v["lang"] = lang
        done += 1
        print(f"  + {v['id']} [{lang}] {v['channel']} — {v['title'][:70]}")
    save_index(idx)
    print(f"{done} transcript(s) prêts dans research/transcripts/ → lancer l'agent transcript-miner.")
    return 0


def cmd_status(args) -> int:
    idx = load_index()
    by = {}
    for v in idx["videos"].values():
        by[v["status"]] = by.get(v["status"], 0) + 1
    print(json.dumps({"videos": len(idx["videos"]), "par_statut": by, "chaines": list(idx["channels"])},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_mark(args) -> int:
    idx = load_index()
    if args.id not in idx["videos"]:
        sys.exit(f"{args.id} absent du catalogue")
    idx["videos"][args.id]["status"] = args.status
    if args.reason:
        idx["videos"][args.id]["reason"] = args.reason
    save_index(idx)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    f = sub.add_parser("fetch")
    f.add_argument("-n", type=int, default=5)
    f.add_argument("--force", action="store_true", help="transcrire même si la couverture est atteinte")
    f.set_defaults(fn=cmd_fetch)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    for name, status in (("skip", "skipped"), ("noted", "noted")):
        m = sub.add_parser(name)
        m.add_argument("id")
        m.add_argument("reason", nargs="?")
        m.set_defaults(fn=cmd_mark, status=status)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
