# Anistar Agency

Static site for a talent agency in development across anime, manga, comics and gaming. The directory covers 16 divisions and 135 specialties. It does not list individual talent yet.

Run `python3 gen.py` after changing `template.html` or `taxonomy.py`. Preview locally with `python3 -m http.server 8000`.

Live site: https://anistar-agency.vercel.app. See [HANDOFF.md](HANDOFF.md) for project context.

## October 20 editorial redesign

The homepage and division pages use an editorial layout with system fonts, a photographic introduction, a compact division index, and expandable specialty search and contact tools. Photo sources and credits are recorded in ASSETS.md. Downloaded photographs live in assets/ and are included by the deployment allowlist.

The existing inquiry and application tools generate local summaries. No monitored delivery inbox is configured. The interface states this before visitors open either form.

Source branch: codex/unsplash-editorial-redesign. Browser review images are in review/. Regenerate the public HTML with python3 gen.py after source changes.
