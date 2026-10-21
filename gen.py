import csv, html, json, os, re, urllib.parse
from taxonomy import T
from site_config import BASE, INQUIRY_EMAIL, FOUNDERS

slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = lambda s: html.escape(s, quote=True)

FOOTER_JP = "アニメ、マンガ、コミック、ゲームのタレント事務所"
COVER_JP = "アニメ、コスプレ、クリエイターの事務所"
WORD_JP = "アニスター"

META = {
    "Creators & Artists": {
        "jp": "絵と漫画",
        "lede": "Illustrators, mangaka, comic and webtoon artists, character designers, and the people who ink, color, and letter.",
        "cap": "Illustration, manga, comics, and the desk the page is made on.",
    },
    "Animation & Production Craft": {
        "jp": "アニメーション制作",
        "lede": "Key animators, in-betweeners, directors, storyboard artists, background painters, compositors, Live2D riggers, and editors.",
        "cap": "From key animation to the edit.",
    },
    "Voice & Performance": {
        "jp": "声優",
        "lede": "English dub actors, Japanese seiyuu, game voice actors, ADR directors, motion-capture performers, and 2.5D stage actors.",
        "cap": "A voice actor, a seiyuu, or a booth session.",
    },
    "Music & Audio": {
        "jp": "音楽",
        "lede": "Anisong singers, composers, idol performers, sound designers, Vocaloid producers, utaite, and live ensembles.",
        "cap": "A singer, a composer, or a live ensemble.",
    },
    "Writing & Story": {
        "jp": "物語",
        "lede": "Manga and comic writers, light novel authors, anime screenwriters, game and visual novel writers, and editors.",
        "cap": "Scripts, novels, and series composition.",
    },
    "Localization & Translation": {
        "jp": "翻訳",
        "lede": "Manga translators, anime subtitlers, game localizers, interpreters, and cultural consultants.",
        "cap": "Translation for manga, anime, and games.",
    },
    "Cosplay & Fashion": {
        "jp": "コスプレ",
        "lede": "Guest cosplayers, masquerade judges, costume and prop makers, wig stylists, photographers, and j-fashion talent.",
        "cap": "Guest cosplay, a maker, or the photographer.",
    },
    "Models & Brand Faces": {
        "jp": "モデル",
        "lede": "Fashion and commercial models, booth and product models, ambassadors, and promo talent for launches.",
        "cap": "Faces for print, booths, and campaigns.",
    },
    "Streamers, VTubers & Creators": {
        "jp": "配信",
        "lede": "Gaming streamers, VTubers, watch-along hosts, YouTubers, podcasters, and people who cover collecting, travel, and community.",
        "cap": "A streamer or a VTuber, on camera or off.",
    },
    "Esports & Pro Gaming": {
        "jp": "eスポーツ",
        "lede": "Pro players, fighting-game competitors, casters, coaches, and whole teams. Teams and organizations are roster talent.",
        "cap": "Players, casters, and whole teams.",
    },
    "Game Development Talent": {
        "jp": "ゲーム開発",
        "lede": "Designers, programmers, artists, producers, and indie studios. A studio is roster talent, the same as a solo developer.",
        "cap": "People who make the games.",
    },
    "Celebrities, Hosts & Ambassadors": {
        "jp": "司会",
        "lede": "Hosts, panel moderators, media personalities, and crossover guests for shows and launches.",
        "cap": "Hosts, moderators, and guests.",
    },
    "Events & Conventions": {
        "jp": "イベント",
        "lede": "Guests of honor, signing talent, featured artist-alley exhibitors, dancers, mascot performers, and workshop teachers.",
        "cap": "The convention itself.",
    },
    "Media, Critics & Educators": {
        "jp": "メディア",
        "lede": "Critics, games journalists, historians, art teachers, Japanese language teachers, and researchers.",
        "cap": "Critics, teachers, and reporters.",
    },
    "IP, Licensing & Business": {
        "jp": "ライセンス",
        "lede": "Original IP creators, licensing people, imprint editors, producers, marketers, and managers who already work in this field.",
        "cap": "Licensing, publishing, and original IP.",
    },
    "Emerging & Tech": {
        "jp": "新しい技術",
        "lede": "Disclosed AI-assisted creators, VR and virtual production artists, and figure designers.",
        "cap": "VR, virtual production, and disclosed AI-assisted work.",
    },
}

LEADS = {"Creators & Artists", "Voice & Performance", "Cosplay & Fashion"}
FEATURED = [
    ("Cosplay & Fashion", "3 / 4", "f-cos", "Guest cosplayers, masquerade judges, costume and prop makers, wig stylists, and cosplay photographers. Conventions book them. So do brands, when a character has to stand in the room."),
    ("Voice & Performance", "1 / 1", "f-voice", "English dub actors, Japanese seiyuu, game voice actors, and ADR directors. Also motion-capture performers, narrators, and actors in 2.5D musicals."),
    ("Creators & Artists", "2 / 3", "f-art", "Illustrators, mangaka, comic artists, character designers, and the benches behind them: backgrounds, tones, inks, color, letters."),
    ("Streamers, VTubers & Creators", "4 / 5", "f-stream", "Gaming streamers, independent VTubers, VTuber units, and watch-along hosts. Also the channels that stay with a series after the episode airs."),
    ("Music & Audio", "16 / 9", "f-music", "Anisong singers, composers for anime and games, idol performers, utaite, and ensembles that play this music live."),
]
ROSTER_PHOTOS = {0, 6, 12}

names = [d for d, _, _ in T]
missing = [n for n in names if n not in META]
assert not missing, missing

ORG = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Anistar Agency",
    "url": BASE + "/",
    "logo": BASE + "/favicon.svg",
    "description": "Talent agency for anime, cosplay, and creator talent, and for manga, comics, and games.",
    "founder": [
        {"@type": "Person", "name": f["name"], "jobTitle": f["role"], "sameAs": [f["link"]]}
        for f in FOUNDERS
    ],
}


def jp_text():
    blobs = [FOOTER_JP, COVER_JP, WORD_JP, "表紙", "創業者", "ロスター"]
    blobs += [m["jp"] for m in META.values()]
    seen = []
    for blob in blobs:
        for ch in blob:
            if ord(ch) > 127 and ch not in seen:
                seen.append(ch)
    return "".join(seen)


def font_links():
    latin = "https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,500;0,6..96,600;1,6..96,500;1,6..96,600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&display=swap"
    jp = "https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap&text=" + urllib.parse.quote(jp_text())
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="{latin}" rel="stylesheet">'
        f'<link href="{jp}" rel="stylesheet">'
    )


NAV = [
    ("/talent/", "Roster", "roster"),
    ("/#agency", "Agency", "agency"),
    ("/book/", "Book talent", "book"),
    ("/apply/", "Apply", "apply"),
]


def nav_html(current):
    parts = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == current else ""
        parts.append(f'<a href="{href}"{cur}>{label}</a>')
    return "".join(parts)


def head(title, desc, path, current="", extra_ld=(), body_class=""):
    url = BASE + path
    lds = "".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
        for x in (ORG,) + tuple(extra_ld)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#fbfbf8">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Anistar Agency">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{font_links()}
<link rel="stylesheet" href="/styles.css">
{lds}
</head>
<body class="{body_class}" data-inquiry-email="{e(INQUIRY_EMAIL)}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
<a class="wordmark" href="/">Anistar</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="primary-nav">Menu</button>
<nav id="primary-nav" class="primary" aria-label="Primary">{nav_html(current)}</nav>
</header>
"""


def foot():
    divs = "".join(f'<a href="/talent/{slug(d)}/">{e(d)}</a>' for d, _, _ in T)
    return f"""<footer class="foot">
<a class="wordmark" href="/">Anistar</a>
<p>Talent representation for anime, manga, comics, and games.</p>
<p class="foot-jp" lang="ja">{FOOTER_JP}</p>
<nav aria-label="Footer">{nav_html("")}</nav>
<nav class="foot-divs" aria-label="Fields">{divs}</nav>
<p class="colophon">© 2026 Anistar Agency</p>
</footer>
<script src="/app.js" defer></script>
</body></html>
"""


def shot(src, ratio, kicker, caption):
    img = f'<img src="{e(src)}" alt="">' if os.path.isfile(src.lstrip("/")) else ""
    kick = f'<span class="kicker" lang="ja">{e(kicker)}</span>' if kicker else ""
    text = f" {e(caption)}" if caption else ""
    cap = f"<figcaption>{kick}{text}</figcaption>" if (kicker or caption) else ""
    return (
        f'<figure class="shot"><div class="mat" style="aspect-ratio:{ratio}">'
        f'{img}<span class="filemark" aria-hidden="true">{e(src)}</span></div>{cap}</figure>'
    )


def crumbs(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": BASE + path}
            for i, (name, path) in enumerate(items, 1)
        ],
    }


def founders_html():
    bits = []
    for f in FOUNDERS:
        fig = shot(f["img"], f["ratio"], "創業者", "")
        bits.append(
            f'<article class="person">{fig}<h3>{e(f["name"])}</h3>'
            f'<p class="role">{e(f["role"])}</p><p>{e(f["bio"])}</p>'
            f'<p><a href="{e(f["link"])}">{e(f["link_label"])}</a></p></article>'
        )
    return "".join(bits)


def spread():
    bits = []
    for name, ratio, cls, blurb in FEATURED:
        meta = META[name]
        s = slug(name)
        fig = shot(f"/img/talent-{s}.jpg", ratio, meta["jp"], meta["cap"])
        bits.append(
            f'<article class="feature {cls}">{fig}<h3><a href="/talent/{s}/">{e(name)}</a></h3><p>{e(blurb)}</p></article>'
        )
    return "".join(bits)


def toc():
    bits = []
    for d, _, _ in T:
        meta = META[d]
        cls = "toc-item lead" if d in LEADS else "toc-item"
        bits.append(
            f'<a class="{cls}" href="/talent/{slug(d)}/"><span class="toc-name">{e(d)}</span>'
            f'<span class="toc-jp" lang="ja">{e(meta["jp"])}</span>'
            f'<span class="toc-lede">{e(meta["lede"])}</span></a>'
        )
    return "".join(bits)


def field_section(i, d, cs, with_photo):
    meta = META[d]
    s = slug(d)
    head_blob = " ".join([d, meta["jp"], meta["lede"]]).lower()
    items = []
    for n, ds, r in cs:
        blob = " ".join([n, ds, r, d]).lower()
        items.append(
            f'<li data-search="{e(blob)}"><a href="/talent/{s}/#{slug(n)}">{e(n)}</a></li>'
        )
    photo = shot(f"/img/talent-{s}.jpg", "3 / 4", meta["jp"], meta["cap"]) if with_photo else ""
    cls = "field with-photo" if with_photo else "field"
    return (
        f'<section class="{cls}" id="{s}" data-search="{e(head_blob)}">'
        f'<div class="field-copy"><h2><a href="/talent/{s}/">{e(d)}</a></h2>'
        f'<p class="jp" lang="ja">{e(meta["jp"])}</p><p class="lede">{e(meta["lede"])}</p></div>'
        f"{photo}<ul class=\"names\">{''.join(items)}</ul></section>"
    )


PROJECTS = [
    "Convention or live event",
    "Brand campaign or sponsorship",
    "Publishing or media launch",
    "Commission or production work",
    "Licensing or IP project",
    "Other",
]
BUDGETS = ["Under $5k", "$5k to $25k", "$25k to $100k", "$100k+"]


def specialty_select(required):
    groups = []
    for d, _, cs in T:
        opts = "".join(f'<option>{e(n)}</option>' for n, _, _ in cs)
        groups.append(f'<optgroup label="{e(d)}">{opts}</optgroup>')
    req = " required" if required else ""
    label = "Choose a field" if required else "If you know it"
    return f'<select name="specialty" data-label="Field"{req}><option value="">{label}</option>{"".join(groups)}</select>'


def division_select():
    opts = "".join(f'<option>{e(d)}</option>' for d, _, _ in T)
    return f'<select name="division" data-label="Field"><option value="">Choose a field</option>{opts}</select>'


def result_block():
    return (
        '<div class="result" data-result hidden>'
        '<p data-result-msg tabindex="-1"></p>'
        '<textarea readonly rows="8" data-result-text aria-label="Your note"></textarea>'
        '<button class="btn" type="button" data-copy>Copy this note</button>'
        "</div>"
    )


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Anistar Agency", "url": BASE + "/"}
    home = open("template.html", encoding="utf-8").read()
    rep = {
        "HEAD": head(
            "Anistar Agency",
            "Anistar is a talent agency for anime, cosplay, and creator talent, and for manga, comics, and games.",
            "/",
            extra_ld=(site_ld,),
            body_class="home",
        ),
        "FOOT": foot(),
        "COVER": shot("/img/cover.jpg", "3 / 4", "表紙", "A convention, a booth, or a premiere."),
        "SPREAD": spread(),
        "TOC": toc(),
        "FOUNDERS": founders_html(),
    }
    for k, v in rep.items():
        home = home.replace("{{" + k + "}}", v)
    assert "{{" not in home, re.findall(r"\{\{\w+\}\}", home)
    write("index.html", home)

    roster_ld = crumbs([("Anistar Agency", "/"), ("Roster", "/talent/")])
    fields = "".join(
        field_section(i, d, cs, i in ROSTER_PHOTOS) for i, (d, _, cs) in enumerate(T)
    )
    roster = head(
        "Roster | Anistar Agency",
        "Fields Anistar represents, from illustrators and cosplayers to voice actors, streamers, esports teams, and game studios.",
        "/talent/",
        current="roster",
        extra_ld=(roster_ld,),
        body_class="roster",
    )
    roster += f"""<main id="main" class="page">
<h1>Roster</h1>
<p class="page-kana" lang="ja">ロスター</p>
<p class="dek">The fields Anistar represents. A person is named here only after they have agreed to be listed.</p>
<form class="finder" id="finder" role="search" action="/talent/" method="get">
<label for="q">Search the roster</label>
<input id="q" name="q" type="search" autocomplete="off">
<button class="linkish" id="clear" type="button" hidden>Clear</button>
</form>
<p id="count" role="status" aria-live="polite"></p>
<div class="roster">{fields}</div>
<p id="none" class="none-msg" hidden>Nothing in the roster matches that search.</p>
</main>"""
    roster += foot()
    write("talent/index.html", roster)

    nd = len(T)
    for i, (d, _, cs) in enumerate(T):
        s = slug(d)
        meta = META[d]
        prev_d = T[i - 1][0]
        next_d = T[(i + 1) % nd][0]
        desc = meta["lede"]
        bc = crumbs([("Anistar Agency", "/"), ("Roster", "/talent/"), (d, f"/talent/{s}/")])
        cats = []
        for n, ds, r in cs:
            cats.append(
                f'<li id="{slug(n)}"><h2>{e(n)}</h2><p>{e(ds)}</p>'
                f'<p class="roles"><span class="sr">Roles in this field. </span>{e(r)}</p></li>'
            )
        side = "side-left" if i % 2 else ""
        page = head(
            f"{d} | Anistar Agency",
            desc,
            f"/talent/{s}/",
            current="roster",
            extra_ld=(bc,),
            body_class="division",
        )
        page += f"""<main id="main" class="page {side}">
<p class="where"><a href="/talent/">Roster</a></p>
<div class="div-top">
<div class="div-copy">
<h1>{e(d)}</h1>
<p class="page-kana" lang="ja">{e(meta["jp"])}</p>
<p class="dek">{e(meta["lede"])}</p>
<p class="div-links"><a href="/book/?division={urllib.parse.quote(d)}">Book from this field</a><a href="/apply/">Apply with work in this field</a></p>
</div>
{shot(f"/img/talent-{s}.jpg", "4 / 5", meta["jp"], meta["cap"])}
</div>
<div class="cats-wrap"><ol class="cats">{''.join(cats)}</ol></div>
<nav class="pager" aria-label="Other fields">
<a href="/talent/{slug(prev_d)}/"><span>Previous</span>{e(prev_d)}</a>
<a href="/talent/{slug(next_d)}/"><span>Next</span>{e(next_d)}</a>
</nav>
</main>"""
        page += foot()
        write(f"talent/{s}/index.html", page)

    book_ld = crumbs([("Anistar Agency", "/"), ("Book talent", "/book/")])
    project_opts = "".join(f"<option>{e(p)}</option>" for p in PROJECTS)
    budget_opts = "".join(f"<option>{e(b)}</option>" for b in BUDGETS)
    book = head(
        "Book talent | Anistar Agency",
        "Tell Anistar who you need to hire, and for what. Conventions, publishers, brands, and productions.",
        "/book/",
        current="book",
        extra_ld=(book_ld,),
        body_class="formpage",
    )
    book += f"""<main id="main" class="page">
<div class="sheet">
<div>
<h1>Book talent</h1>
<p class="dek">Tell us the job. A convention guest, a campaign, a recording, a commission. Name the field if you know it.</p>
<p class="quiet">We do not store this note on a server. If mail is not connected, the only copy is the one you take with you.</p>
</div>
<form class="form" id="inquiry-form" novalidate>
<div class="pair">
<label class="line"><span>Your name <span class="req">Required</span></span><input name="name" data-label="your name" required autocomplete="name"></label>
<label class="line"><span>Email <span class="req">Required</span></span><input name="email" data-label="your email" type="email" required autocomplete="email"></label>
</div>
<label class="line"><span>Company or organization</span><input name="org" autocomplete="organization"></label>
<div class="pair">
<label class="line"><span>Project type <span class="req">Required</span></span><select name="type" data-label="the project type" required><option value="">Choose one</option>{project_opts}</select></label>
<label class="line"><span>Timing, if you know it</span><input name="timing" autocomplete="off"></label>
</div>
<div class="pair">
<label class="line"><span>Field</span>{division_select()}</label>
<label class="line"><span>Budget range</span><select name="budget"><option value="">Prefer not to say</option>{budget_opts}</select></label>
</div>
<label class="line"><span>Closest specialty</span>{specialty_select(False)}</label>
<label class="line"><span>The job <span class="req">Required</span></span><textarea name="details" data-label="the job" rows="5" required></textarea></label>
<button class="btn" type="submit">Write the note</button>
<p class="form-error" role="alert" hidden></p>
{result_block()}
</form>
</div>
</main>"""
    book += foot()
    write("book/index.html", book)

    apply_ld = crumbs([("Anistar Agency", "/"), ("Apply", "/apply/")])
    apply = head(
        "Apply for representation | Anistar Agency",
        "Apply to be represented by Anistar. Send the work: a portfolio, a channel, credits, or a team page.",
        "/apply/",
        current="apply",
        extra_ld=(apply_ld,),
        body_class="formpage",
    )
    apply += f"""<main id="main" class="page">
<div class="sheet">
<div>
<h1>Apply for representation</h1>
<p class="dek">Send the work. A portfolio, a channel, credits, or a team page. One field is enough. A team applies as one entry.</p>
<p class="quiet">We do not store this note on a server. If mail is not connected, the only copy is the one you take with you.</p>
</div>
<form class="form" id="apply-form" novalidate>
<div class="pair">
<label class="line"><span>Name or team <span class="req">Required</span></span><input name="name" data-label="your name" required autocomplete="name"></label>
<label class="line"><span>Email <span class="req">Required</span></span><input name="email" data-label="your email" type="email" required autocomplete="email"></label>
</div>
<label class="line"><span>Field <span class="req">Required</span></span>{specialty_select(True)}</label>
<label class="line"><span>Portfolio and links <span class="req">Required</span></span><textarea name="links" data-label="your links" rows="4" required></textarea></label>
<label class="line"><span>About the work</span><textarea name="about" rows="4"></textarea></label>
<button class="btn" type="submit">Write the note</button>
<p class="form-error" role="alert" hidden></p>
{result_block()}
</form>
</div>
</main>"""
    apply += foot()
    write("apply/index.html", apply)

    missing_page = head(
        "Page not found | Anistar Agency",
        "This page is not on the Anistar Agency site.",
        "/404",
        body_class="missing",
    )
    missing_page += """<main id="main" class="miss">
<h1>This page is not on the site</h1>
<p>The address does not match a roster page, a booking note, or an application.</p>
<p><a href="/">Return to Anistar</a></p>
</main>"""
    missing_page += foot()
    write("404.html", missing_page)

    urls = [BASE + "/", BASE + "/talent/", BASE + "/book/", BASE + "/apply/"]
    urls += [f"{BASE}/talent/{slug(d)}/" for d, _, _ in T]
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc></url>" for u in urls)
        + "</urlset>\n",
    )
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

    with open("taxonomy.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Division", "Category", "Description", "Example roles", "Roster status"])
        for d, _, cs in T:
            for n, ds, r in cs:
                w.writerow([d, n, ds, r, "Not published"])
    md = "# Anistar Agency Talent Taxonomy\n\nAnime, manga, comics, webtoons, and gaming. No individual talent is listed.\n"
    for d, _, cs in T:
        md += f"\n## {d}\n\n| Category | Description | Example roles |\n|---|---|---|\n"
        md += "".join(f"| {n} | {ds} | {r} |\n" for n, ds, r in cs)
    write("TAXONOMY.md", md)

    files = ["index.html", "404.html", "talent/index.html", "book/index.html", "apply/index.html"]
    files += [f"talent/{slug(d)}/index.html" for d, _, _ in T]
    banned = [
        "EST. 2026",
        "PLACEHOLDER",
        "→",
        "↗",
        "←",
        "↑",
        "·",
        "—",
        "–",
        "elevate",
        "unlock",
        "seamless",
        "crafted",
        "with care",
        "built for",
        "Space Grotesk",
        "DM Sans",
        "Two clear paths",
        "system-ui",
        "Instrument Serif",
    ]
    hits = []
    for path in files:
        text = open(path, encoding="utf-8").read()
        for b in banned:
            if b in text:
                hits.append((path, b))
        if any(ord(ch) > 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF for ch in text):
            hits.append((path, "emoji"))
    if hits:
        raise SystemExit("banned copy found: " + repr(hits[:20]))
    print("pages", len(files))
    print("images")
    for src in ["/img/cover.jpg", "/img/henry-finn.jpg", "/img/ko-mori.jpg"] + [
        f"/img/talent-{slug(d)}.jpg" for d, _, _ in T
    ]:
        print(src)


if __name__ == "__main__":
    main()
