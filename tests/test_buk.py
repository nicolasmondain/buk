"""Tests de bout en bout du skill buk (bibliothèque standard uniquement ; les tests de la
recherche sont ignorés si pyyaml n'est pas installé)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "buk" / "scripts"
FLASH = ROOT / "skills" / "buk" / "assets" / "flash" / "dague_coeur.svg"
sys.path.insert(0, str(SCRIPTS))

import buk_lib  # noqa: E402
from buk_validate import validate  # noqa: E402

try:
    import yaml  # noqa: F401
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


BAD = """<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
  <g id="z" data-buk-kind="zone" data-technique="solid-blue" data-needle="RX9" data-ink="bleu" data-order="0">
    <path fill="#0000FF" d="M5 5 L30 5 L30 30"/>
  </g>
</svg>"""


class TestGeometry(unittest.TestCase):
    def test_path_relative_and_absolute_agree(self):
        a, ca = buk_lib.path_subpaths("M0 0 L10 0 L10 10 Z")
        b, cb = buk_lib.path_subpaths("m0 0 l10 0 l0 10 z")
        self.assertEqual(a[0][:3], b[0][:3])
        self.assertTrue(ca[0] and cb[0])
        self.assertAlmostEqual(buk_lib.poly_area(a[0]), 50.0)

    def test_label_point_inside(self):
        polys, _ = buk_lib.path_subpaths("M0 0 L20 0 L20 4 L4 4 L4 20 L0 20 Z")  # L concave
        x, y, m = buk_lib.label_point(polys)
        self.assertTrue(buk_lib.inside((x, y), polys))
        self.assertGreater(m, 0)


class TestValidate(unittest.TestCase):
    def test_example_flash_is_valid(self):
        r = validate(FLASH)
        self.assertEqual(r["erreurs"], [], r["erreurs"])
        self.assertGreater(r["infos"]["ratios_pct"]["noir"], 10)

    def test_bad_flash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.svg"
            p.write_text(BAD, encoding="utf-8")
            errs = " ".join(validate(p)["erreurs"])
        for needle in ("mm", "solid-blue", "RX9", "bleu", "data-order", "hors palette", "non fermé"):
            self.assertIn(needle, errs)


class TestStencil(unittest.TestCase):
    def test_generates_all_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(SCRIPTS / "buk_stencil.py", FLASH, "--by", "both", "--out", tmp, "--mirror")
            self.assertEqual(r.returncode, 0, r.stderr)
            files = {p.name for p in Path(tmp).iterdir()}
            for f in ("fiche.html", "apercu.svg", "calque-maitre.svg", "sequence.json",
                      "calque-aiguille-rl11-noir.svg", "calque-technique-whip.svg"):
                self.assertIn(f, files)
            master = (Path(tmp) / "calque-maitre.svg").read_text(encoding="utf-8")
            self.assertIn("scale(-1,1)", master)
            self.assertIn('width="87.5mm"', master)
            self.assertNotIn("#C1121F", master.upper())  # un calque est en noir seulement
            seq = json.loads((Path(tmp) / "sequence.json").read_text(encoding="utf-8"))
            orders = [e["ordre"] for e in seq["etapes"]]
            self.assertEqual(orders, sorted(orders))
            self.assertEqual(seq["etapes"][0]["technique"], "bold-line")

    def test_refuses_invalid_design(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.svg"
            p.write_text(BAD, encoding="utf-8")
            self.assertEqual(run(SCRIPTS / "buk_stencil.py", p, "--out", tmp).returncode, 1)

    def test_scale(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(SCRIPTS / "buk_stencil.py", FLASH, "--by", "needle", "--scale", "2", "--out", tmp)
            self.assertIn('width="175mm"', (Path(tmp) / "calque-maitre.svg").read_text(encoding="utf-8"))


class TestComposants(unittest.TestCase):
    def test_motifs_are_valid_and_plates_build(self):
        sys.path.insert(0, str(ROOT / "skills" / "buk" / "assets" / "composants"))
        from buk_composants import Flash, rose, feuille, hirondelle, banderole, etoile_nautique, goutte
        from buk_planche import planche
        with tempfile.TemporaryDirectory() as tmp:
            f = Flash("Test", 170, 70)
            rose(f, 30, 30, 18); feuille(f, 12, 45, 14, angle=160)
            hirondelle(f, 100, 30, 30); banderole(f, 120, 165, 55, 9)
            etoile_nautique(f, 150, 22, 12); goutte(f, 60, 60, 2)
            p = Path(tmp) / "t.svg"
            f.ecrire(p)
            r = validate(p)
            self.assertEqual(r["erreurs"], [], r["erreurs"])
            self.assertIn("4 · Couleur", planche(p))


class TestClassiques(unittest.TestCase):
    def test_classics_valid_and_masking_cuts_behind(self):
        sys.path.insert(0, str(ROOT / "skills" / "buk" / "assets" / "composants"))
        from buk_composants import Flash
        from buk_classiques import (ancre, banderole_texte, carte, coeur, crane, dague, de,
                                    fer_a_cheval, lettrage, GLYPHES)
        f = Flash("T", 260, 90)
        fer_a_cheval(f, 20, 40, 36); de(f, 55, 40, 10); carte(f, 85, 40, 40, "A", "pique")
        ancre(f, 125, 40, 60); crane(f, 165, 40, 40); dague(f, 200, 45, 70); coeur(f, 235, 30, 30)
        lettrage(f, "".join(k for k in GLYPHES if k.isalnum())[:10], 130, 82, 7)
        n_rouge = len(f.couches["rouge"])
        banderole_texte(f, "MOM", 235, 30, 40)
        self.assertEqual(len(f.couches["rouge"]), n_rouge)  # le cœur est découpé, pas supprimé
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "c.svg"
            f.ecrire(p)
            r = validate(p)
            self.assertEqual(r["erreurs"], [], r["erreurs"])

    def test_alphabet_complete(self):
        sys.path.insert(0, str(ROOT / "skills" / "buk" / "assets" / "composants"))
        from buk_classiques import GLYPHES
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            self.assertIn(c, GLYPHES)


class TestData(unittest.TestCase):
    def test_every_recommended_needle_exists(self):
        techniques, needles = buk_lib.load_data()
        for k, t in techniques.items():
            for n in t["aiguilles_conseillees"]:
                self.assertIn(n, needles, f"{k} conseille {n} inconnue")


@unittest.skipUnless(HAS_YAML, "pyyaml absent")
class TestResearch(unittest.TestCase):
    def test_coverage_stops_when_saturated(self):
        sys.path.insert(0, str(ROOT / "research" / "scripts"))
        import coverage
        cfg = {"stop": {"min_videos": 2, "min_channels": 2, "window": 3, "novelty_threshold": 0.2},
               "themes": {"lining": {"required": True}, "whip": {"required": False}}}
        notes = [{"video_id": f"v{i}", "chaine": f"c{i}", "_file": f"v{i}.md",
                  "claims": [{"theme": "lining", "nouveau": True}]} for i in range(2)]
        self.assertTrue(coverage.compute(notes, cfg)["arreter"])
        self.assertFalse(coverage.compute(notes[:1], cfg)["arreter"])

    def test_vtt_cleaning(self):
        sys.path.insert(0, str(ROOT / "research" / "scripts"))
        try:
            import harvest
        except SystemExit:
            self.skipTest("yt-dlp absent")
        vtt = ("WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nhold the <c>machine</c>\n\n"
               "00:00:02.000 --> 00:00:04.000\nhold the machine\nlike a pen\n\n"
               "00:00:40.000 --> 00:00:42.000\nstretch the skin\n")
        txt = harvest.vtt_to_text(vtt)
        self.assertEqual(txt.count("hold the machine"), 1)
        self.assertIn("[00:40] stretch the skin", txt)


if __name__ == "__main__":
    unittest.main()
