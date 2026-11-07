import csv, html, json, os, re, urllib.parse
from pathlib import Path
from taxonomy import T
from site_config import BASE, FOUNDERS, LICENSE_NUMBER, LICENSE_STATUS, STATUS

if LICENSE_STATUS != "forming" or LICENSE_NUMBER:
    raise SystemExit("LICENSE_STATUS must stay forming with an empty license number")

slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = lambda s: html.escape(s, quote=True)

FOOTER_JP = "アニメ、マンガ、コミック、ゲームのタレント事務所（準備中）"
COVER_JP = "アニメ、コスプレ、クリエイターの事務所（準備中）"
HOME_DESC = (
    "Anistar is a new agency under construction, accepting founding-roster applications "
    "from anime, cosplay, manga, comics, and games talent. Representation and booking are not yet available."
)

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
        "lede": "Pro players, fighting-game competitors, casters, coaches, and whole teams. Teams and organizations are talent categories.",
        "cap": "Players, casters, and whole teams.",
    },
    "Game Development Talent": {
        "jp": "ゲーム開発",
        "lede": "Designers, programmers, artists, producers, and indie studios. A studio is a talent category, the same as a solo developer.",
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
LEAD_LAYOUT = {
    "Creators & Artists": "lead wide",
    "Voice & Performance": "lead narrow",
    "Cosplay & Fashion": "lead flip",
}

names = [d for d, _, _ in T]
missing = [n for n in names if n not in META]
assert not missing, missing
assert len(T) == 16
assert sum(len(cs) for _, _, cs in T) == 135

# Free Unsplash License photographs shipped with the repo. Public pages do not display them.
PHOTO_CREDITS = [
    ("cover.jpg", "Cover", "Denys Nevozhai", "https://unsplash.com/@dnevozhai", "https://unsplash.com/photos/alleyway-with-red-lanterns-in-tokyo-D68ADLeMh5Q"),
    ("talent-creators-artists.jpg", "Creators & Artists", "Kelly Sikkema", "https://unsplash.com/@kellysikkema", "https://unsplash.com/photos/person-drawing-on-tablet-at-workspace-Dx1b5ucschA"),
    ("talent-animation-production-craft.jpg", "Animation & Production Craft", "Denise Jans", "https://unsplash.com/@dmjdenise", "https://unsplash.com/photos/photography-of-camera-reel-film-9lTUAlNB87M"),
    ("talent-voice-performance.jpg", "Voice & Performance", "Leo Wieling", "https://unsplash.com/@leowieling", "https://unsplash.com/photos/grayscale-photo-of-condenser-microphone-beside-pop-filter-bG8U3kaZltE"),
    ("talent-music-audio.jpg", "Music & Audio", "Caught In Joy", "https://unsplash.com/@caught_in_joy", "https://unsplash.com/photos/recording-studio-with-guitars-and-console-ptVBlniJi50"),
    ("talent-writing-story.jpg", "Writing & Story", "Aaron Burden", "https://unsplash.com/@aaronburden", "https://unsplash.com/photos/fountain-pen-on-black-lined-paper-y02jEX_B0O0"),
    ("talent-localization-translation.jpg", "Localization & Translation", "Romain Tordo", "https://unsplash.com/@romaintordo", "https://unsplash.com/photos/brown-wooden-shelf-with-books-1cJH4NJ4GpA"),
    ("talent-cosplay-fashion.jpg", "Cosplay & Fashion", "Phil Hearing", "https://unsplash.com/@philhearing", "https://unsplash.com/photos/hands-operating-a-sewing-machine-on-fabric-9m6eykr9_vU"),
    ("talent-models-brand-faces.jpg", "Models & Brand Faces", "Alyssa Strohmann", "https://unsplash.com/@anotherlovely", "https://unsplash.com/photos/hanged-top-on-brown-and-white-clothes-horse-TS--uNw-JqE"),
    ("talent-streamers-vtubers-creators.jpg", "Streamers, VTubers & Creators", "Klim Musalimov", "https://unsplash.com/@klim11", "https://unsplash.com/photos/microphone-on-boom-arm-for-podcasting-fxHq67K11-E"),
    ("talent-esports-pro-gaming.jpg", "Esports & Pro Gaming", "CHUTTERSNAP", "https://unsplash.com/@chuttersnap", "https://unsplash.com/photos/crowd-of-people-in-stadium-seating-gDDas5_ALRw"),
    ("talent-game-development-talent.jpg", "Game Development Talent", "JL Cabrera", "https://unsplash.com/@thekidph", "https://unsplash.com/photos/a-computer-keyboard-sitting-on-top-of-a-wooden-table-4GzqVNX0TCQ"),
    ("talent-celebrities-hosts-ambassadors.jpg", "Celebrities, Hosts & Ambassadors", "Riccardo Vosti", "https://unsplash.com/@riccardovosti", "https://unsplash.com/photos/a-stage-that-has-some-lights-on-it-00C4DqSeoKM"),
    ("talent-events-conventions.jpg", "Events & Conventions", "Nico Knaack", "https://unsplash.com/@xoxnk", "https://unsplash.com/photos/people-gathered-in-a-large-modern-atrium-with-escalators-6l47hN4-HhI"),
    ("talent-media-critics-educators.jpg", "Media, Critics & Educators", "Tyler Callahan", "https://unsplash.com/@tylercallahan", "https://unsplash.com/photos/photography-of-theater-chairs-e_RpjNyMgEM"),
    ("talent-ip-licensing-business.jpg", "IP, Licensing & Business", "Amaan Ali", "https://unsplash.com/@amaan01_", "https://unsplash.com/photos/person-holding-black-pen-writing-on-white-paper-e1GuDltUTlE"),
    ("talent-emerging-tech.jpg", "Emerging Tech", "Shahrooz Shekaraubi", "https://unsplash.com/@shahroozshekaraubi", "https://unsplash.com/photos/a-pair-of-vr-headset-sitting-on-top-of-a-table-BCLUHs9kDC0"),
]

# Photographs shown on the public pages. Contextual illustrations only.
ILLUSTRATIONS = [
    {
        "slot": "hero",
        "file": "talent/violet-evergarden.jpg",
        "webp": "talent/violet-evergarden.webp",
        "width": 1050,
        "height": 1400,
        "alt": "An adult cosplayer dressed as Violet Evergarden at the 14th Zhuhai Animation Show.",
        "caption": "Cosplay of Violet Evergarden, from the anime Violet Evergarden, at the 14th Zhuhai Animation Show. Not Anistar talent.",
        "where": "Homepage hero",
        "creator": "Yumeto",
        "creator_url": "https://commons.wikimedia.org/wiki/File:20251004_Cosplay_of_Violet_Evergarden_at_the_14th_Zhuhai_Animation_Show.jpg",
        "photo_page": "https://commons.wikimedia.org/wiki/File:20251004_Cosplay_of_Violet_Evergarden_at_the_14th_Zhuhai_Animation_Show.jpg",
        "source_page": "https://commons.wikimedia.org/wiki/File:20251004_Cosplay_of_Violet_Evergarden_at_the_14th_Zhuhai_Animation_Show.jpg",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "changes": "Resized and compressed for the page. This copy is offered under CC BY-SA 4.0.",
    },
    {
        "slot": "scene",
        "file": "talent/drawing-tablet.jpg",
        "webp": "talent/drawing-tablet.webp",
        "width": 1400,
        "height": 788,
        "alt": "A hand penciling comic panels on a display tablet.",
        "caption": "An illustrator penciling a comic page. Not Anistar talent.",
        "where": "Homepage, creators",
        "creator": "David Revoy",
        "creator_url": "https://www.davidrevoy.com/article334/making-of-episode-23",
        "photo_page": "https://www.davidrevoy.com/article334/making-of-episode-23",
        "source_page": "https://commons.wikimedia.org/wiki/File:Penciling_on_Wacom_Cintiq_13HD_by_David_Revoy.jpg",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "changes": "Resized and compressed for the page.",
    },
    {
        "slot": "scene",
        "file": "talent/evo-players.jpg",
        "webp": "talent/evo-players.webp",
        "width": 1800,
        "height": 591,
        "alt": "Competitive Super Smash Bros. Melee players standing together at Evo 2014.",
        "caption": "Players at Evo 2014. Not Anistar talent.",
        "where": "Homepage, esports",
        "creator": "vsmak350",
        "creator_url": "https://www.flickr.com/photos/vsmak/",
        "photo_page": "https://www.flickr.com/photos/vsmak/14661438753/",
        "source_page": "https://commons.wikimedia.org/wiki/File:Melee_It_On_Me_-_Super_Smash_Bros._Melee_players_at_Evo_2014.jpg",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "changes": "Resized and compressed for the page. This copy is offered under CC BY-SA 2.0.",
    },
]

ORG = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Anistar Agency",
    "url": BASE + "/",
    "logo": BASE + "/img/logo/anistar-lockup.png",
    "description": HOME_DESC,
    "founder": [
        {
            "@type": "Person",
            "name": f["name"],
            "jobTitle": f["role"],
            "sameAs": [href for href, _label in f["links"]],
        }
        for f in FOUNDERS
    ],
}


def jp_text():
    blobs = [FOOTER_JP, COVER_JP]
    blobs += [m["jp"] for m in META.values()]
    seen = []
    for blob in blobs:
        for ch in blob:
            if ord(ch) > 127 and ch not in seen:
                seen.append(ch)
    return "".join(seen)


def font_links():
    latin = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap"
    jp = "https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@500;600&display=swap&text=" + urllib.parse.quote(jp_text())
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="{latin}" rel="stylesheet">'
        f'<link href="{jp}" rel="stylesheet">'
    )


NAV = [
    ("/talent/", "Talent categories", "categories"),
    ("/apply/", "Talent application", "interest"),
    ("/book/", "Planning note", "planning"),
]


def logo_html(class_name):
    return (
        f'<a class="{class_name}" href="/"><picture>'
        '<source srcset="/img/logo/anistar-lockup.webp" type="image/webp">'
        '<img src="/img/logo/anistar-lockup.png" alt="Anistar" width="1275" height="859">'
        "</picture></a>"
    )


def nav_html(current):
    parts = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == current else ""
        count = ""
        if key == "planning":
            count = ' <span class="count" data-brief-count hidden></span>'
        parts.append(f'<a href="{href}"{cur}>{label}{count}</a>')
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
<meta name="theme-color" content="#FBF4E8">
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
<link rel="icon" href="/img/logo/anistar-symbol-192.png" type="image/png">
{font_links()}
<link rel="stylesheet" href="/styles.css">
{lds}
</head>
<body class="{body_class}" data-license-status="{e(LICENSE_STATUS)}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
{logo_html("brand")}
<nav id="primary-nav" class="primary" aria-label="Primary">{nav_html(current)}</nav>
</header>
"""


def foot():
    divs = "".join(f'<a href="/talent/{slug(d)}/">{e(d)}</a>' for d, _, _ in T)
    return f"""<footer class="foot">
<p class="status">{e(STATUS)}</p>
{logo_html("brand")}
<p class="foot-jp" lang="ja">{FOOTER_JP}</p>
<nav aria-label="Footer">{nav_html("")}</nav>
<nav class="foot-divs" aria-label="Divisions">{divs}</nav>
<p class="colophon">© 2026 Anistar Agency</p>
<p class="colophon"><a href="/credits/">Image file credits</a></p>
</footer>
<script src="/app.js" defer></script>
</body></html>
"""


def status_html():
    return f'<p class="status">{e(STATUS)}</p>'


def crumbs(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": BASE + path}
            for i, (name, path) in enumerate(items, 1)
        ],
    }


def add_button(name):
    return (
        f'<button type="button" class="brief-add" data-brief="{e(name)}" aria-pressed="false">Add</button>'
    )


def founders_html():
    bits = []
    for founder in FOUNDERS:
        links = "".join(
            f'<li><a href="{e(href)}">{e(label)}</a></li>' for href, label in founder["links"]
        )
        bits.append(
            f'<article class="person"><h3>{e(founder["name"])}</h3>'
            f'<p class="role">{e(founder["role"])}</p><p>{e(founder["bio"])}</p>'
            f'<ul class="url-list">{links}</ul></article>'
        )
    return "".join(bits)


def illustration_figure(item, cls):
    return (
        f'<figure class="{cls}">'
        f'<picture><source srcset="/img/{item["webp"]}" type="image/webp" width="{item["width"]}" height="{item["height"]}">'
        f'<img src="/img/{item["file"]}" alt="{e(item["alt"])}" width="{item["width"]}" height="{item["height"]}" style="aspect-ratio:{item["width"]}/{item["height"]}"></picture>'
        f'<figcaption>{e(item["caption"])} <a href="/credits/">Image credits</a></figcaption>'
        f"</figure>"
    )


def hero_photo():
    item = next(photo for photo in ILLUSTRATIONS if photo["slot"] == "hero")
    return illustration_figure(item, "hero-photo")


def scene_photos():
    figures = "".join(
        illustration_figure(photo, "scene") for photo in ILLUSTRATIONS if photo["slot"] == "scene"
    )
    return (
        '<section class="scenes" aria-label="Category illustrations">'
        '<p>Category illustrations. Not a roster, and not an endorsement.</p>'
        f"{figures}</section>"
    )


def hero_index():
    bits = []
    for division, _, _cs in T:
        meta = META[division]
        cls = ' class="lead"' if division in LEADS else ""
        bits.append(
            f'<li{cls}><a href="#{slug(division)}"><span class="side-name">{e(division)}</span>'
            f'<span class="side-jp" lang="ja">{e(meta["jp"])}</span></a></li>'
        )
    return f'<ol class="side-index">{"".join(bits)}</ol>'


def index_blocks():
    bits = []
    for division, _, categories in T:
        meta = META[division]
        layout = LEAD_LAYOUT.get(division, "")
        cls = f"index-block {layout}".strip()
        items = []
        for name, _desc, _roles in categories:
            items.append(
                f'<li><a href="/talent/{slug(division)}/#{slug(name)}">{e(name)}</a>{add_button(name)}</li>'
            )
        bits.append(
            f'<article class="{cls}" id="{slug(division)}">'
            f'<div class="index-copy"><h3><a href="/talent/{slug(division)}/">{e(division)}</a></h3>'
            f'<p class="jp" lang="ja">{e(meta["jp"])}</p>'
            f'<p class="count">{len(categories)} categories</p>'
            f'<p>{e(meta["lede"])}</p></div>'
            f'<ul class="cat-list">{"".join(items)}</ul></article>'
        )
    return "".join(bits)


def field_section(division, categories):
    meta = META[division]
    head_blob = " ".join([division, meta["jp"], meta["lede"]]).lower()
    items = []
    for name, desc, roles in categories:
        blob = " ".join([name, desc, roles, division]).lower()
        items.append(
            f'<li data-search="{e(blob)}"><a href="/talent/{slug(division)}/#{slug(name)}">{e(name)}</a>{add_button(name)}</li>'
        )
    return (
        f'<section class="field" id="{slug(division)}" data-division="{e(division)}" data-search="{e(head_blob)}">'
        f'<div class="field-copy"><h2><a href="/talent/{slug(division)}/">{e(division)}</a></h2>'
        f'<p class="jp" lang="ja">{e(meta["jp"])}</p><p class="lede">{e(meta["lede"])}</p></div>'
        f'<ul class="cat-list">{"".join(items)}</ul></section>'
    )


def filters():
    buttons = [
        '<button type="button" class="filter" data-division="all" aria-pressed="true">All divisions</button>'
    ]
    for division, _, _categories in T:
        buttons.append(
            f'<button type="button" class="filter" data-division="{e(division)}" aria-pressed="false">{e(division)}</button>'
        )
    return f'<div class="filters" role="group" aria-label="Filter by division">{"".join(buttons)}</div>'


PROJECTS = [
    "Convention or live event",
    "Publishing or media project",
    "Brand project",
    "Production or commission",
    "Licensing project",
    "Other",
]


def division_select(required):
    opts = "".join(
        f'<option value="{e(d)}" data-slug="{slug(d)}">{e(d)}</option>' for d, _, _ in T
    )
    req = " required" if required else ""
    label = "Choose a division" if required else "If you know it"
    return f'<select name="division" data-label="the division"{req}><option value="">{label}</option>{opts}</select>'


def specialty_select(required):
    groups = []
    for division, _, categories in T:
        opts = "".join(f'<option value="{e(name)}">{e(name)}</option>' for name, _, _ in categories)
        groups.append(f'<optgroup label="{e(division)}">{opts}</optgroup>')
    req = " required" if required else ""
    label = "Choose a category" if required else "If you know it"
    return (
        f'<select name="specialty" data-label="the category"{req}>'
        f'<option value="">{label}</option>{"".join(groups)}</select>'
    )


def specialty_picker():
    groups = []
    for division, _, categories in T:
        opts = "".join(f'<option value="{e(name)}">{e(name)}</option>' for name, _, _ in categories)
        groups.append(f'<optgroup label="{e(division)}">{opts}</optgroup>')
    return (
        '<label class="picker"><span>Add a category from the map</span>'
        f'<select data-brief-picker><option value="">Choose a category</option>{"".join(groups)}</select></label>'
    )


def result_block(copy_label="Copy this note", note_label="Note to copy"):
    return (
        '<div class="result" data-result hidden>'
        '<p data-result-msg tabindex="-1" aria-live="polite"></p>'
        f'<textarea readonly rows="8" data-result-text aria-label="{e(note_label)}"></textarea>'
        f'<button class="textbtn" type="button" data-copy>{e(copy_label)}</button>'
        "</div>"
    )


# title, official href, short source label, source href
FILMS = [
    (
        "Maquia: When the Promised Flower Blooms",
        "https://www.elevenarts.net/anime/films",
        "North American theatrical release",
        "https://www.animenewsnetwork.com/press-release/2018-04-12/eleven-arts-anime-studio-to-release-maquia-when-the-promised-flower-blooms/.130262",
    ),
    (
        "Penguin Highway",
        "https://www.elevenarts.net/titles/penguin-highway",
        "North American theatrical release",
        "https://www.scifijapan.com/godzilla-toho/penguin-highway-comes-to-north-american-theaters-starting-april-12",
    ),
    (
        "Ryoma! The Prince of Tennis",
        "https://www.elevenarts.net/anime/anime-news",
        "North American distribution",
        "https://www.elevenarts.net/anime/anime-news",
    ),
    (
        "Millennium Actress",
        "https://www.elevenarts.net/anime/films",
        "North American release",
        "https://www.elevenarts.net/anime/anime-news",
    ),
    (
        "A Silent Voice",
        "https://www.elevenarts.net/titles/a-silent-voice",
        "U.S. theatrical screenings",
        "https://www.theouterhaven.net/2017/09/u-s-screenings-silent-voice-revealed/",
    ),
]


def films_html():
    items = []
    for title, href, source_label, source_href in FILMS:
        items.append(
            "<li>"
            f'<a class="film-title" href="{e(href)}">{e(title)}</a>'
            f'<a href="{e(source_href)}">{e(source_label)}</a>'
            "</li>"
        )
    return f'<ul class="films">{"".join(items)}</ul>'


def credibility_html():
    return f"""<section class="credibility" id="credibility" aria-labelledby="credibility-title">
<h2 id="credibility-title">From Japanese anime releases to a new home for talent</h2>
<div class="cred-grid">
<article class="ko" id="ko">
<h3>Ko Mori</h3>
<p class="role">Co-founder of Anistar. Founder and CEO of ELEVEN ARTS.</p>
<p>Ko Mori co-founded Anistar with Henry Finn. He leads ELEVEN ARTS, a Los Angeles distributor bringing Japanese anime to North American audiences. ELEVEN ARTS is a separate company.</p>
<p class="ko-links"><a href="https://www.elevenarts.net/">ELEVEN ARTS</a><a href="https://www.instagram.com/eleven_arts/">ELEVEN ARTS on Instagram</a></p>
<h3 class="film-heading">Selected ELEVEN ARTS releases</h3>
{films_html()}
</article>
<article class="henry" id="henry">
<h3><a href="https://henryfinn.com">Henry Finn</a></h3>
<p class="role">Co-founder of Anistar.</p>
<p>Henry Finn is a co-founder of Anistar. He started it with Ko Mori.</p>
</article>
</div>
</section>"""


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main():
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Anistar Agency", "url": BASE + "/"}
    home = Path("template.html").read_text(encoding="utf-8")
    rep = {
        "HEAD": head(
            "Anistar Agency",
            HOME_DESC,
            "/",
            extra_ld=(site_ld,),
            body_class="home",
        ),
        "STATUS": STATUS,
        "FOOT": foot(),
        "HERO_PHOTO": hero_photo(),
        "HERO_INDEX": hero_index(),
        "SCENE_PHOTOS": scene_photos(),
        "FOUNDERS": founders_html(),
        "CREDIBILITY": credibility_html(),
        "INDEX": index_blocks(),
    }
    for key, value in rep.items():
        home = home.replace("{{" + key + "}}", value)
    assert "{{" not in home, re.findall(r"\{\{\w+\}\}", home)
    write("index.html", home)

    roster_ld = crumbs([("Anistar Agency", "/"), ("Talent categories", "/talent/")])
    fields = "".join(field_section(division, categories) for division, _, categories in T)
    roster = head(
        "Talent categories | Anistar Agency",
        "Sixteen divisions and 135 categories. No individual talent is listed. Anistar is in development.",
        "/talent/",
        current="categories",
        extra_ld=(roster_ld,),
        body_class="roster",
    )
    roster += f"""<main id="main" class="page" tabindex="-1">
{status_html()}
<h1>Talent categories</h1>
<p class="page-kana" lang="ja">カテゴリ</p>
<p class="dek">Sixteen divisions and 135 categories. Esports teams and game studios are talent categories. A person is named here only after they have agreed to be listed. Nobody is listed yet.</p>
<form class="finder" id="finder" role="search" action="/talent/" method="get" onsubmit="event.preventDefault()">
<label for="q">Search categories</label>
<input id="q" name="q" type="search" autocomplete="off">
<button class="textbtn" id="clear" type="button" hidden>Clear</button>
</form>
{filters()}
<p id="count" role="status" aria-live="polite"></p>
<div class="roster">{fields}</div>
<p id="none" class="none-msg" hidden>No category matches that search.</p>
</main>"""
    roster += foot()
    write("talent/index.html", roster)

    total = len(T)
    for index, (division, _, categories) in enumerate(T):
        division_slug = slug(division)
        meta = META[division]
        prev_name = T[index - 1][0]
        next_name = T[(index + 1) % total][0]
        trail = crumbs([("Anistar Agency", "/"), ("Talent categories", "/talent/"), (division, f"/talent/{division_slug}/")])
        cats = []
        for name, desc, roles in categories:
            cats.append(
                f'<li id="{slug(name)}"><div class="cat-head"><h2>{e(name)}</h2>{add_button(name)}</div>'
                f'<div class="cat-body"><p>{e(desc)}</p>'
                f'<p class="roles"><span class="sr">Example roles. </span>{e(roles)}</p></div></li>'
            )
        quoted = urllib.parse.quote(division)
        page = head(
            f"{division} | Anistar Agency",
            meta["lede"] + " Anistar is in development.",
            f"/talent/{division_slug}/",
            current="categories",
            extra_ld=(trail,),
            body_class="division",
        )
        page += f"""<main id="main" class="page" tabindex="-1">
{status_html()}
<p class="where"><a href="/talent/">Talent categories</a></p>
<div class="div-top">
<div class="div-copy">
<h1>{e(division)}</h1>
<p class="page-kana" lang="ja">{e(meta["jp"])}</p>
<p class="dek">{e(meta["lede"])}</p>
<div class="div-links"><a class="btn" href="/apply/?division={quoted}">Talent application</a><a class="textlink" href="/book/?division={quoted}">Client planning note</a></div>
<p class="quiet">Open a talent application with this division filled in.</p>
</div>
<p class="div-note">Add a category to the planning note if a future project might need it. The list stays in this browser.</p>
</div>
<div class="cats-wrap"><ol class="cats">{''.join(cats)}</ol></div>
<nav class="pager" aria-label="Other divisions">
<a href="/talent/{slug(prev_name)}/"><span>Previous</span>{e(prev_name)}</a>
<a href="/talent/{slug(next_name)}/"><span>Next</span>{e(next_name)}</a>
</nav>
</main>"""
        page += foot()
        write(f"talent/{division_slug}/index.html", page)

    plan_ld = crumbs([("Anistar Agency", "/"), ("Client planning note", "/book/")])
    project_opts = "".join(f'<option value="{e(project)}">{e(project)}</option>' for project in PROJECTS)
    plan = head(
        "Client planning note | Anistar Agency",
        "Prepare a planning note for your own records. Anistar does not book talent from this page, and nothing is sent.",
        "/book/",
        current="planning",
        extra_ld=(plan_ld,),
        body_class="formpage",
    )
    plan += f"""<main id="main" class="page" tabindex="-1">
{status_html()}
<div class="sheet">
<div class="sheet-copy">
<h1>Client planning note</h1>
<p class="dek">Use this page to draft which categories a future project might need. Anistar cannot book talent from it.</p>
<p class="quiet">Nothing is sent. Nothing is stored on a server. Leave out personal contact details. This page cannot upload files.</p>
</div>
<div class="sheet-form">
<div class="shortlist">
<h2>Categories on this note</h2>
<p data-brief-empty>No categories yet. Add them from a division page, or choose one below. They stay in this browser only.</p>
<ul data-brief-list></ul>
{specialty_picker()}
</div>
<form class="form" id="inquiry-form" method="post" action="/book/" novalidate onsubmit="event.preventDefault()" autocomplete="off" data-nosend="true">
<label class="line"><span>Organization <span class="req">Required</span></span><input name="org" data-label="the organization" required autocomplete="organization"></label>
<div class="pair">
<label class="line"><span>Project type <span class="req">Required</span></span><select name="type" data-label="the project type" required><option value="">Choose one</option>{project_opts}</select></label>
<label class="line"><span>Timing, if you know it</span><input name="timing" autocomplete="off"></label>
</div>
<div class="pair">
<label class="line"><span>City, if you know it</span><input name="city" autocomplete="off"></label>
<label class="line"><span>Division</span>{division_select(False)}</label>
</div>
<label class="line"><span>Category</span>{specialty_select(False)}</label>
<label class="line"><span>What the project would need <span class="req">Required</span></span><textarea name="details" data-label="what the project would need" rows="5" required></textarea></label>
<button class="btn" type="button" data-prepare>Prepare a copy</button>
<p class="form-error" role="alert" hidden></p>
{result_block()}
</form>
</div>
</div>
</main>"""
    plan += foot()
    write("book/index.html", plan)

    apply_ld = crumbs([("Anistar Agency", "/"), ("Talent application", "/apply/")])
    apply = head(
        "Talent application | Anistar Agency",
        "Anistar is a new agency under construction, accepting founding-roster applications from adults in anime, cosplay, manga, comics, and games. Preparing an application here does not send it.",
        "/apply/",
        current="interest",
        extra_ld=(apply_ld,),
        body_class="apply",
    )
    apply += f"""<main id="main" class="page apply" tabindex="-1">
{status_html()}
<div class="apply-grid">
<div class="apply-intro">
<h1>Join Anistar's founding talent roster</h1>
<p class="dek">Prepare your expression of interest while our new agency takes shape.</p>
<p>Adults in anime, cosplay, manga, comics, and games are invited, including voice, music, esports, and the wider category map. A team or a studio can apply under one name. No following size is required.</p>
<h2>Our planned support, subject to licensing and representation agreements</h2>
<dl class="benefits">
<div><dt>Category positioning</dt><dd>A portfolio presented in the category that fits the work, from cosplay and manga to voice and games.</dd></div>
<div><dt>Creator collaborations</dt><dd>Introductions among creators who want to work together.</dd></div>
<div><dt>Interviews and content</dt><dd>Conversations and short features about the work you are making.</dd></div>
<div><dt>Cross-market partnerships</dt><dd>Future brand, convention, and representation opportunities across North America, South America, Japan, Europe, and the Middle East.</dd></div>
</dl>
</div>
<div class="apply-form">
<h2>Prepare your application</h2>
<p class="quiet">This preview lets you prepare and copy your application. Online submission is not available yet. Nothing is sent.</p>
<p data-from-division hidden></p>
<form class="form" id="apply-form" method="post" action="/apply/" novalidate onsubmit="event.preventDefault()" autocomplete="off" data-nosend="true">
<fieldset>
<legend>About you</legend>
<label class="line"><span>Name or stage name <span class="req">Required</span></span><input name="name" data-label="your name or stage name" required autocomplete="name"></label>
<label class="line"><span>Email <span class="req">Required</span></span><input name="email" data-label="your email" type="email" inputmode="email" required autocomplete="email"></label>
</fieldset>
<fieldset>
<legend>Your work</legend>
<label class="line"><span>Division <span class="req">Required</span></span>{division_select(True)}</label>
<label class="line"><span>Category <span class="req">Required</span></span>{specialty_select(True)}</label>
<label class="line"><span>Portfolio or profile URL <span class="req">Required</span></span><input name="url" data-label="a portfolio or profile URL" type="url" inputmode="url" placeholder="https://" required autocomplete="url"></label>
<label class="line"><span>Languages <span class="req">Required</span></span><input name="languages" data-label="the languages you work in" required autocomplete="off"></label>
</fieldset>
<fieldset>
<legend>What you want</legend>
<label class="line"><span>Interests and goals <span class="req">Required</span></span><textarea name="goals" data-label="your interests and goals" rows="4" required></textarea></label>
</fieldset>
<label class="check"><input name="adult" value="yes" type="checkbox" data-label="the confirmation that you are 18 or older" required><span>I am 18 or older. I understand this application is not sent and is not a representation agreement.</span></label>
<button class="btn" type="button" data-prepare>Prepare application</button>
<p class="form-error" role="alert" hidden></p>
{result_block("Copy application", "Application to copy")}
</form>
</div>
<div class="apply-ko">
{credibility_html()}
</div>
</div>
</main>"""
    apply += foot()
    write("apply/index.html", apply)

    missing_page = head(
        "Page not found | Anistar Agency",
        "This page is not on the Anistar site.",
        "/404",
        body_class="missing",
    )
    missing_page += f"""<main id="main" class="miss" tabindex="-1">
{status_html()}
<h1>This page is not on the site</h1>
<p>The address does not match a category, a talent application, or a client planning note.</p>
<p><a href="/">Return to Anistar</a></p>
</main>"""
    missing_page += foot()
    write("404.html", missing_page)

    credits_ld = crumbs([("Anistar Agency", "/"), ("Image file credits", "/credits/")])
    credits = head(
        "Image file credits | Anistar Agency",
        "Photographs shown on the Anistar site, with creator, license, and source page. They are category illustrations, not Anistar talent.",
        "/credits/",
        extra_ld=(credits_ld,),
    )
    shown = []
    for item in ILLUSTRATIONS:
        shown.append(
            "<li>"
            f'<p class="credit-where">{e(item["where"])}</p>'
            f'<p class="credit-file">/img/{e(item["file"])}</p>'
            f'<p>{e(item["creator"])}. <a href="{e(item["creator_url"])}">{e(item["creator_url"])}</a></p>'
            f'<p><a href="{e(item["source_page"])}">{e(item["source_page"])}</a></p>'
            f'<p><a href="{e(item["photo_page"])}">{e(item["photo_page"])}</a></p>'
            f'<p><a href="{e(item["license_url"])}">{e(item["license"])}</a></p>'
            f'<p>{e(item["changes"])}</p>'
            "</li>"
        )
    rows = []
    for file, where, name, profile, photo in PHOTO_CREDITS:
        rows.append(
            "<li>"
            f'<p class="credit-where">{e(where)}</p>'
            f'<p class="credit-file">/img/{e(file)}</p>'
            f'<p><a href="{e(profile)}">{e(profile)}</a></p>'
            f'<p><a href="{e(photo)}">{e(photo)}</a></p>'
            f"<p>{e(name)}</p>"
            "</li>"
        )
    credits += f"""<main id="main" class="page" tabindex="-1">
{status_html()}
<h1>Image file credits</h1>
<p class="dek">Three photographs are shown on the homepage as category illustrations. They are not pictures of Anistar talent or clients. Nobody pictured has a representation agreement with Anistar, and the photographs are not an endorsement by the people, the events, or the characters in the costumes.</p>
<p>No model release is held by Anistar. Wikimedia Commons did not flag a personality-rights restriction on these three files. Costumes and the game in the photographs belong to their own rightsholders. The files are used as photographs of a convention and a tournament, not as character art or game artwork.</p>
<h2>Shown on the site</h2>
<ol class="credits">
{"".join(shown)}
</ol>
<h2>Stored, not shown</h2>
<p class="dek">These other files are stored with the project under /img. They come from Unsplash, under the <a href="https://unsplash.com/license">Unsplash License</a>. They are photographs of places and tools. The public pages do not use them.</p>
<ol class="credits">
{"".join(rows)}
</ol>
</main>"""
    credits += foot()
    write("credits/index.html", credits)

    lines = [
        "# Photography credits",
        "",
        "Shown photographs are category illustrations. They are not Anistar talent, clients, or an endorsement.",
        "No model release is held by Anistar.",
        "",
        "| File | Where | Creator | License | Source page | Photo page |",
        "|---|---|---|---|---|---|",
    ]
    for item in ILLUSTRATIONS:
        lines.append(
            f'| {item["file"]} | {item["where"]} | {item["creator"]} | {item["license"]} {item["license_url"]} | {item["source_page"]} | {item["photo_page"]} |'
        )
    lines += [
        "",
        "Other files under img/ are from Unsplash and are not shown on the public pages: https://unsplash.com/license",
        "",
        "| File | Well | Photographer | Profile | Unsplash photo |",
        "|---|---|---|---|---|",
    ]
    for file, where, name, profile, photo in PHOTO_CREDITS:
        lines.append(f"| {file} | {where} | {name} | {profile} | {photo} |")
    lines.append("")
    write("img/CREDITS.md", "\n".join(lines))

    urls = [BASE + "/", BASE + "/talent/", BASE + "/book/", BASE + "/apply/", BASE + "/credits/"]
    urls += [f"{BASE}/talent/{slug(division)}/" for division, _, _ in T]
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc></url>" for u in urls)
        + "</urlset>\n",
    )
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

    with open("taxonomy.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Division", "Category", "Description", "Example roles", "Roster status"])
        for division, _, categories in T:
            for name, desc, roles in categories:
                writer.writerow([division, name, desc, roles, "Not published"])
    md = "# Anistar Agency Talent Taxonomy\n\nAnime, manga, comics, webtoons, and gaming. No individual talent is listed. Esports teams and game studios are talent categories.\n"
    for division, _, categories in T:
        md += f"\n## {division}\n\n| Category | Description | Example roles |\n|---|---|---|\n"
        md += "".join(f"| {name} | {desc} | {roles} |\n" for name, desc, roles in categories)
    write("TAXONOMY.md", md)

    files = ["index.html", "404.html", "talent/index.html", "book/index.html", "apply/index.html", "credits/index.html"]
    files += [f"talent/{slug(division)}/index.html" for division, _, _ in T]
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
        "Book talent",
        "hello@anistar.agency",
        "hire through us",
        "hire through the agency",
        "Apply for representation",
        "mailto:",
        "Labor Code",
        "privacy policy",
        "Terms of",
        "we will reply",
        "family=Inter",
        "family=Geist",
        "Bodoni",
        "gradient(",
    ]
    hits = []
    for path in files:
        text = Path(path).read_text(encoding="utf-8")
        for phrase in banned:
            if phrase in text:
                hits.append((path, phrase))
        if any(ord(ch) > 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF for ch in text):
            hits.append((path, "emoji"))
        if "filemark" in text or 'class="mat"' in text:
            hits.append((path, "image-box"))
    if hits:
        raise SystemExit("banned copy found: " + repr(hits[:30]))
    print("pages", len(files))


if __name__ == "__main__":
    main()
