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
            "type=\"file\"",
            "type=\"submit\"",
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
        self.assertIn(">Talent application<", home)
        self.assertIn(">Client planning note<", home)
        self.assertIn("Connecting talent across East and West", home)
        self.assertIn("North America, South America, Japan, Europe, and the Middle East", home)
        for title in (
            "Maquia: When the Promised Flower Blooms",
            "Penguin Highway",
            "Ryoma! The Prince of Tennis",
            "Millennium Actress",
            "A Silent Voice",
        ):
            self.assertIn(title, home)
        self.assertIn("https://henryfinn.com", home)
        self.assertIn("Henry Finn is a co-founder of Anistar.", home)
        self.assertIn("https://www.elevenarts.net/", home)
        self.assertIn("https://www.instagram.com/eleven_arts/", home)
        self.assertIn("Founder and CEO of ELEVEN ARTS.", home)
        self.assertIn("ELEVEN ARTS is a separate company.", home)
        self.assertIn("https://www.instagram.com/eleven_arts/", home)
        self.assertNotIn("https://www.elevenarts.net/</a>", home)
        for internal in (
            "no offices there",
            "does not call Ko",
            "Wikipedia",
            "privacy notice",
            "named studio",
            "no monitored inbox",
        ):
            self.assertNotIn(internal, home, internal)
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
        self.assertIn('name="email"', apply)
        self.assertIn('type="email"', apply)
        self.assertNotIn("name=\"email\"", plan)
        self.assertNotIn('type="email"', plan)
        self.assertNotIn("name=\"age\"", apply)
        self.assertNotIn('type="file"', apply)
        self.assertIn("data-brief-list", plan)
        self.assertNotIn("data-brief-list", apply)
        self.assertIn(">Prepare application<", apply)
        self.assertIn(">Copy application<", apply)
        self.assertIn(">Prepare a copy<", plan)
        self.assertIn("Join Anistar's founding talent roster", apply)
        self.assertIn(
            "This preview lets you prepare and copy your application. Online submission is not available yet. Nothing is sent.",
            apply,
        )
        self.assertIn("Selected ELEVEN ARTS releases", apply)
        self.assertNotIn("Wikipedia", apply)
        self.assertIn("Maquia: When the Promised Flower Blooms", apply)
        script = (ROOT / "app.js").read_text()
        for phrase in ("fetch(", "XMLHttpRequest", "sendBeacon", "mailto:", "gtag", "supabase", "plausible"):
            self.assertNotIn(phrase, script)
        self.assertIn("anistar-brief", script)
        self.assertIn("localStorage", script)
        self.assertIn("ANISTAR TALENT APPLICATION", script)
        self.assertIn("ANISTAR PLANNING NOTE", script)
        self.assertIn("Nothing was sent. Anistar did not receive this note.", script)
        talent_fn = script.split("ANISTAR TALENT APPLICATION")[1].split("].join")[0]
        self.assertNotIn("getB()", talent_fn)
        plan_fn = script.split("ANISTAR PLANNING NOTE")[1].split("].join")[0]
        self.assertIn("getB()", plan_fn)

    def test_visual_system_sources(self):
        css = (ROOT / "styles.css").read_text()
        for color in ("#FBF4E8", "#1B174D", "#FCCE77", "#FA7590"):
            self.assertIn(color, css)
        self.assertNotIn("#B5121B", css)
        self.assertNotIn("#14110F", css)
        for phrase in ("gradient", "backdrop-filter", "box-shadow", "@keyframes", "Inter", "Geist", "system-ui"):
            self.assertNotIn(phrase, css)
        html = (ROOT / "index.html").read_text()
        self.assertIn("family=Newsreader", html)
        self.assertIn("family=IBM+Plex+Sans", html)
        self.assertIn("family=Noto+Serif+JP", html)
        for phrase in ("family=Inter", "family=Geist", "Bodoni", "Shippori", "Roboto"):
            self.assertNotIn(phrase, html)

    def test_logo_asset_is_the_supplied_file(self):
        import hashlib
        from PIL import Image

        source = ROOT / "img" / "logo" / "anistar-logo-source.png"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, "dd7f7b0188033b6e51a3b9c831513555b4406a1391d7139655527438e5c6bd3d")
        lockup = Image.open(ROOT / "img" / "logo" / "anistar-lockup.png")
        symbol = Image.open(ROOT / "img" / "logo" / "anistar-symbol.png")
        self.assertEqual(lockup.mode, "RGBA")
        self.assertEqual(symbol.mode, "RGBA")
        self.assertEqual(lockup.size, (1275, 859))
        self.assertEqual(symbol.size, (796, 653))
        self.assertEqual(lockup.getpixel((0, 0))[3], 0)
        self.assertEqual(symbol.getpixel((0, 0))[3], 0)
        home = (ROOT / "index.html").read_text()
        self.assertIn('alt="Anistar"', home)
        self.assertIn("/img/logo/anistar-lockup.png", home)
        self.assertNotIn("/img/logo/anistar-symbol.png", home)
        self.assertNotIn('class="hero-mark"', home)
        self.assertNotIn("favicon.svg", home)

    def test_public_illustrations_are_credited(self):
        home = (ROOT / "index.html").read_text()
        credits = (ROOT / "credits" / "index.html").read_text()
        for path in (
            "/img/talent/wondercon-xmen.jpg",
            "/img/talent/wondercon-xmen.webp",
            "/img/talent/drawing-tablet.jpg",
            "/img/talent/evo-players.jpg",
        ):
            self.assertIn(path, home)
            self.assertTrue((ROOT / path.lstrip("/")).is_file())
        self.assertIn("Not Anistar talent.", home)
        self.assertIn("Convention cosplay at WonderCon 2019.", home)
        for url in (
            "https://commons.wikimedia.org/wiki/File:WonderCon_2019_-_90s_X-Men_(1)_(47451008372).jpg",
            "https://commons.wikimedia.org/wiki/File:Penciling_on_Wacom_Cintiq_13HD_by_David_Revoy.jpg",
            "https://commons.wikimedia.org/wiki/File:Melee_It_On_Me_-_Super_Smash_Bros._Melee_players_at_Evo_2014.jpg",
            "https://creativecommons.org/licenses/by-sa/2.0/",
            "https://creativecommons.org/licenses/by/4.0/",
        ):
            self.assertIn(url, credits)
        self.assertIn("No model release is held by Anistar.", credits)
        self.assertIn("not an endorsement", credits)

    def test_browser_shortlist_and_forms(self):
        chrome = "/usr/bin/google-chrome-stable"
        if not Path(chrome).exists():
            self.skipTest("chrome is not installed")
        subprocess.check_call(["node", str(ROOT / "tests" / "browser_flows.mjs")], cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
