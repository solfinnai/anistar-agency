import html
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import gen
from site_config import LICENSE_NUMBER, LICENSE_STATUS, STATUS
from taxonomy import T


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def pages():
    paths = [
        ROOT / "index.html",
        ROOT / "404.html",
        ROOT / "talent" / "index.html",
        ROOT / "book" / "index.html",
        ROOT / "apply" / "index.html",
        ROOT / "credits" / "index.html",
    ]
    paths += [ROOT / "talent" / slug(division) / "index.html" for division, _, _ in T]
    return paths


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gen.main()

    def test_taxonomy_routes_and_talent_categories(self):
        self.assertEqual(len(T), 16)
        self.assertEqual(sum(len(categories) for _, _, categories in T), 135)
        for division, _, categories in T:
            text = (ROOT / "talent" / slug(division) / "index.html").read_text()
            self.assertIn(f"<h1>{html.escape(division)}</h1>", text)
            for name, _desc, _roles in categories:
                self.assertIn(f'id="{slug(name)}"', text)
                self.assertIn(f'data-brief="{name.replace("&", "&amp;")}"', text)
        esports = (ROOT / "talent" / "esports-pro-gaming" / "index.html").read_text()
        studios = (ROOT / "talent" / "game-development-talent" / "index.html").read_text()
        self.assertIn("Esports Teams &amp; Orgs", esports)
        self.assertIn("Teams and organizations are talent categories.", esports)
        self.assertIn("Indie Game Developers &amp; Studios", studios)
        self.assertIn("A studio is a talent category", studios)
        roster = (ROOT / "talent" / "index.html").read_text()
        self.assertEqual(roster.count("brief-add"), 135)

    def test_status_founders_and_no_false_claims(self):
        self.assertEqual(LICENSE_STATUS, "forming")
        self.assertEqual(LICENSE_NUMBER, "")
        banned = [
            "Book talent",
            "hello@anistar.agency",
            "hire through",
            "Apply for representation",
            "mailto:",
            "Labor Code",
            "privacy policy",
            "Terms of",
            "we will reply",
            "California",
            "licensed",
            "0N1",
            "Animori",
            "Unicorn Studios",
            "type=\"email\"",
            "type=\"file\"",
            "type=\"submit\"",
            "<img",
            "filemark",
        ]
        for path in pages():
            text = path.read_text()
            self.assertIn(STATUS, text, path)
            self.assertIn('data-license-status="forming"', text, path)
            self.assertNotIn("data-inquiry-email", text, path)
            for phrase in banned:
                self.assertNotIn(phrase, text, f"{path} contains {phrase}")
            self.assertNotRegex(text, r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        home = (ROOT / "index.html").read_text()
        self.assertIn(">Explore talent categories<", home)
        self.assertIn(">Talent interest<", home)
        self.assertIn(">Client planning note<", home)
        self.assertIn("https://henryfinn.com", home)
        self.assertIn("Henry Finn is a co-founder of Anistar.", home)
        self.assertIn("https://www.elevenarts.net/", home)
        self.assertIn("https://www.instagram.com/eleven_arts/", home)
        self.assertIn("He leads ELEVEN ARTS.", home)
        self.assertIn("does not recruit through the ELEVEN ARTS Instagram account.", home)
        self.assertFalse((ROOT / "privacy" / "index.html").exists())
        self.assertFalse((ROOT / "terms" / "index.html").exists())

    def test_forms_are_copy_only_and_distinct(self):
        apply = (ROOT / "apply" / "index.html").read_text()
        plan = (ROOT / "book" / "index.html").read_text()
        self.assertIn('id="apply-form"', apply)
        self.assertIn('id="inquiry-form"', plan)
        self.assertIn('data-nosend="true"', apply)
        self.assertIn('data-nosend="true"', plan)
        self.assertIn("onsubmit=\"event.preventDefault()\"", apply)
        self.assertIn("onsubmit=\"event.preventDefault()\"", plan)
        self.assertIn("Nothing is sent.", apply)
        self.assertIn("Nothing is sent.", plan)
        self.assertIn("not a representation agreement", apply)
        self.assertIn("I am 18 or older.", apply)
        self.assertIn("cannot book talent", plan)
        self.assertNotIn("name=\"email\"", apply)
        self.assertNotIn("name=\"email\"", plan)
        self.assertNotIn("name=\"age\"", apply)
        self.assertIn("data-brief-list", plan)
        self.assertNotIn("data-brief-list", apply)
        self.assertIn(">Prepare a copy<", apply)
        self.assertIn(">Prepare a copy<", plan)
        script = (ROOT / "app.js").read_text()
        for phrase in ("fetch(", "XMLHttpRequest", "sendBeacon", "mailto:", "gtag", "supabase", "plausible"):
            self.assertNotIn(phrase, script)
        self.assertIn("anistar-brief", script)
        self.assertIn("localStorage", script)
        self.assertIn("ANISTAR TALENT INTEREST NOTE", script)
        self.assertIn("ANISTAR PLANNING NOTE", script)
        self.assertIn("Nothing was sent. Anistar did not receive this note.", script)
        talent_fn = script.split("ANISTAR TALENT INTEREST NOTE")[1].split("].join")[0]
        self.assertNotIn("getB()", talent_fn)
        plan_fn = script.split("ANISTAR PLANNING NOTE")[1].split("].join")[0]
        self.assertIn("getB()", plan_fn)

    def test_visual_system_sources(self):
        css = (ROOT / "styles.css").read_text()
        self.assertIn("#F3EEE4", css)
        self.assertIn("#14110F", css)
        self.assertIn("#B5121B", css)
        for phrase in ("gradient", "backdrop-filter", "box-shadow", "@keyframes", "Inter", "Geist", "system-ui"):
            self.assertNotIn(phrase, css)
        html = (ROOT / "index.html").read_text()
        self.assertIn("family=Newsreader", html)
        self.assertIn("family=IBM+Plex+Sans", html)
        self.assertIn("family=Noto+Serif+JP", html)
        for phrase in ("family=Inter", "family=Geist", "Bodoni", "Shippori", "Roboto"):
            self.assertNotIn(phrase, html)

    def test_browser_shortlist_and_forms(self):
        chrome = "/usr/bin/google-chrome-stable"
        if not Path(chrome).exists():
            self.skipTest("chrome is not installed")
        subprocess.check_call(["node", str(ROOT / "tests" / "browser_flows.mjs")], cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
