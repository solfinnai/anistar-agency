# Anistar Agency — Developer Handoff

**Live:** https://anistar-agency.vercel.app · **Repo:** https://github.com/solfinnai/anistar-agency
**Linear:** https://linear.app/henryfinnai/project/anistar-agency-eab3220dfbd8 · **Drive:** https://drive.google.com/drive/folders/12e7HSdn3xPCGKxbiaIob5MqZ0sD_Y6E2
**Notion:** https://app.notion.com/p/3cefdcf928578106b86ad9daa0be973e · **Taxonomy:** TAXONOMY.md

## What it is
Talent agency positioned to own the anime, manga, comics/webtoons and gaming talent ecosystem. The site presents **16 divisions and 135 talent categories** (full list: `TAXONOMY.md` / `taxonomy.csv`, plus the Google Sheet in Drive): Creators & Artists; Animation & Production Craft; Voice & Performance; Music & Audio; Writing & Story; Localization & Translation; Cosplay & Fashion; Models & Brand Faces; Streamers, VTubers & Creators; Esports & Pro Gaming; Game Development Talent; Celebrities, Hosts & Ambassadors; Events & Conventions; Media, Critics & Educators; IP, Licensing & Business; Emerging & Tech.

## Architecture (static)
- Zero-dependency static site, no backend, no DB, no paid services, no analytics. Pages: `/` (home), `/talent/` and `/talent/<division>/` (16 generated division pages), `/apply/` (talent interest), `/book/` (client planning note only), `/credits/`, `404.html`, plus `sitemap.xml`, `robots.txt`, `og.png`.
- Public status, from `site_config.py`: "Anistar is in development. Talent representation and booking services are not yet available." `LICENSE_STATUS` stays `forming`. Do not claim a jurisdiction, an application, a license number, or that the site can procure work.
- Home: status, two visible paths (Explore talent categories, Talent interest) plus a planning-only client link, founders, and the category map. No FAQ, no roster of people, no booking CTA.
- **Planning note:** "Add" on every category, stored in `localStorage` (`anistar-brief`) as category names only. The count sits on the Planning note link. The client page copies those names into a summary. Form fields are not stored.
- **Forms:** both pages prepare a copy on the device. They do not submit, open mail, or show a completed signup. `INQUIRY_EMAIL` stays blank and is not read. No `hello@anistar.agency`. Talent interest asks for a public name, division, category, one public URL, and an 18+ confirmation. The client note asks for an organization and a project, not a personal inbox.
- **Founders:** Henry Finn, co-founder, https://henryfinn.com. Ko Mori, co-founder, leads ELEVEN ARTS. Official links: https://www.elevenarts.net/ and https://www.instagram.com/eleven_arts/. Those links are not an endorsement, and the site does not recruit through that account or use its logo.
- **SEO:** per-page title/description/canonical, Open Graph + Twitter card, JSON-LD (Organization with founders, WebSite, BreadcrumbList on inner pages), sitemap, robots. No FAQ schema.
- **Accessibility:** skip link, visible navigation at 390px, labelled inputs, `aria-invalid`, `aria-live`, `aria-pressed` on category and filter controls, red focus rings, no horizontal scroll at 390px. `vercel.json` sets clean URLs, cache headers and basic security headers.
- `.vercelignore` is an **allowlist**: only site files deploy. Untracked research/roster files sitting in the working folder are never uploaded.
- **Single source of truth:** `taxonomy.py` (list of divisions → categories with description + example roles).
- `python3 gen.py` generates `index.html` (from `template.html`), the division pages, `404.html`, `sitemap.xml`, `robots.txt`, `TAXONOMY.md` and `taxonomy.csv`. Never hand-edit those outputs.
- `app.js` (vanilla JS): search, division filter, `?q=` and `?division=` deep links, local category shortlist, copy-only forms. Navigation stays visible. There is no hamburger and no network send.
- Hosting: Vercel project `anistar-agency`, production alias `anistar-agency.vercel.app`. As of 2026-11-06 the latest production deployment was created by the Vercel CLI (`source: cli`), with git metadata attached by that upload. Project details did not show a Git integration that auto-deploys this repository. Do not change that link, and do not deploy, without review.

## Run / deploy
```bash
python3 gen.py                         # regenerate pages from taxonomy.py and template.html
python3 -m unittest tests.test_site   # routes, copy, shortlist, and no-send checks
python3 -m http.server 8000            # local preview
```
Production deploy and connecting this repo to Vercel are separate approvals. Do not run them from a copy pass.

## What is placeholder
- **Public roster:** no real talent is shown. Categories describe the map. Only add signed, consenting talent later, with approval.
- **Inquiry delivery:** no inbox is configured. Forms only prepare a copy and say nothing was sent. Do not add a privacy or terms stub and present it as a policy.
- The public mark is the supplied lockup in `img/logo/` (transparent PNG, plus a symbol crop taken from that file). Navy `#1B174D`, gold `#FCCE77`, and pink `#FA7590` are sampled from it. Google Fonts remain Newsreader, IBM Plex Sans, and Noto Serif JP. Unsplash files remain in `img/` for attribution and are not used as a roster.

## Research
- Findings doc: [2026-10-20 Anistar Agency Site Research and Recommendations (v1)](https://docs.google.com/document/d/1zH18gzPX65edCjWAIfUnma4mQOl1q8q54kxnm1rkSK4/edit), Research Library master Sheet row RL-270.

## Prioritized upgrade roadmap

Historical notes only. They do not authorize data collection, booking, analytics, or a framework migration.
0. **Turn on real inquiry delivery:** confirm a monitored inbox and set `INQUIRY_EMAIL`, or wire a free form endpoint / Vercel function to a Sheet with Turnstile spam protection. Add privacy policy before collecting data.
1. **Migrate to Next.js (App Router) + Tailwind**, keep static export; routes `/talent/[division]/[category]` and `/talent/[slug]` profiles generated from the taxonomy (move `taxonomy.py` to JSON/TS).
2. **Talent DB** — start in Notion (existing Anistar rosters) or Google Sheets; pull at build time (ISR). Fields: name, handle, division + categories (multi-select from taxonomy), bio, links, regions, languages, rates tier, availability, consent/rights status, publish flag.
3. **CMS** for pages/news (Notion-as-CMS, Sanity free tier, or MDX in repo).
4. **Inquiry/booking flow** — brand inquiry form (event type, budget, date, talent) + talent application; free options: Formspree/Web3Forms free tier or Vercel serverless → Sheet/Notion + notify. Add spam protection (Turnstile).
5. **Talent portal auth** — Clerk/Auth.js free tier; talent edits own profile, uploads media kit.
6. **SEO** — done at static level (meta, OG, sitemap, JSON-LD). Next: talent profile pages with Person schema, per-division OG images, real domain + Search Console.
7. **i18n JP/EN** — next-intl, `/ja` routes, localized category names.
8. **Analytics** — Vercel Web Analytics (free) or Plausible; track inquiry conversions.
9. Brand pass (logo, art direction, illustration), self-host fonts, full accessibility audit (axe), legal pages, case studies once real work exists.

## Decisions
- **Oct 20, 2026 (Henry):** Henry Finn and Ko Mori are Co-Founders and appear in the Founders section. Anistar is kept separate from Erocosplay TCG.
- **Oct 15, 2026 (Henry):** esports teams/orgs and game studios are represented as **talent on the roster**, not clients. Roster categories: *Esports Teams & Orgs* (Esports & Pro Gaming) and *Indie Game Developers & Studios* (Game Development Talent). For Brands targets publishers, media companies, conventions and consumer brands.

## Open questions
- Final domain? Business email? Which licensing track applies, if any? Do not state a jurisdiction or a filing until one is actually on record.
- Which existing Notion rosters (cosplay/creator) are signed vs research-only? (Treat as research only until confirmed.)
- Commission model and which divisions/categories to launch first (135 is the map, not the launch scope).

- Should adult-content creator rosters be kept separate from the public brand?
- Use Next.js or keep static until roster exists?
