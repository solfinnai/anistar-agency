# Anistar Agency — Developer Handoff

**Live:** https://anistar-agency.vercel.app · **Repo:** https://github.com/solfinnai/anistar-agency
**Linear:** https://linear.app/henryfinnai/project/anistar-agency-eab3220dfbd8 · **Drive:** https://drive.google.com/drive/folders/12e7HSdn3xPCGKxbiaIob5MqZ0sD_Y6E2
**Notion:** https://app.notion.com/p/3cefdcf928578106b86ad9daa0be973e · **Taxonomy:** TAXONOMY.md

## What it is
Talent agency positioned to own the anime, manga, comics/webtoons and gaming talent ecosystem. The site presents **16 divisions and 135 talent categories** (full list: `TAXONOMY.md` / `taxonomy.csv`, plus the Google Sheet in Drive): Creators & Artists; Animation & Production Craft; Voice & Performance; Music & Audio; Writing & Story; Localization & Translation; Cosplay & Fashion; Models & Brand Faces; Streamers, VTubers & Creators; Esports & Pro Gaming; Game Development Talent; Celebrities, Hosts & Ambassadors; Events & Conventions; Media, Critics & Educators; IP, Licensing & Business; Emerging & Tech.

## Architecture (static, Oct 20 2026 upgrade)
- Zero-dependency static site, no backend, no DB, no paid services. Pages: `/` (home), `/talent/<division>/` (16 generated division pages), `404.html`, plus `sitemap.xml`, `robots.txt`, `og.png` (made from `og-source.html` with headless Chrome).
- Home sections: hero with two calls to action (Book talent / Apply), audience paths, what we do, talent map (division cards + search + filter + expandable divisions), how it works, for partners + selected-work proof slots (placeholders), founders, brief/inquiry form, roster application, FAQ.
- **Brief (shortlist):** "+ Add to brief" on every specialty (home and division pages), stored in `localStorage` (`anistar-brief`), count shown in the header button and a floating bar. The inquiry form includes the brief.
- **Forms:** client-side validation, then compose a plain-text brief/application. If `INQUIRY_EMAIL` in `site_config.py` is set, it opens a `mailto:`; it is **blank on purpose** (no confirmed inbox), so the site shows the summary with a Copy button and says nothing was sent.
- **Founders:** data in `site_config.py` (Henry Finn, Ko Mori). Bios use only verified sources (henryfinn.com, unicornstudios.ai, ELEVEN ARTS public profiles). Initials avatars, no photos.
- **SEO:** per-page title/description/canonical, Open Graph + Twitter card, JSON-LD (Organization with founders, WebSite, FAQPage on home; BreadcrumbList on division pages), sitemap, robots.
- **Accessibility/perf:** skip link, labelled inputs, `aria-invalid`, `aria-live` result count, `aria-pressed` on brief buttons, focus-visible outlines, reduced-motion support, no horizontal scroll at 390px. `vercel.json` sets clean URLs, cache headers and basic security headers.
- `.vercelignore` is an **allowlist**: only site files deploy. Untracked research/roster files sitting in the working folder are never uploaded.
- **Single source of truth:** `taxonomy.py` (list of divisions → categories with description + example roles).
- `python3 gen.py` generates `index.html` (from `template.html`), the division pages, `404.html`, `sitemap.xml`, `robots.txt`, `TAXONOMY.md` and `taxonomy.csv`. Never hand-edit those outputs.
- `app.js` (vanilla JS): search, division filter, clear-filters empty state, `?q=` deep links, brief/shortlist, form handling, mobile menu.
- Hosting: Vercel (Hobby/free), project `anistar-agency` under henryfinnai's Vercel account, deployed via CLI (not yet Git-connected).

## Run / deploy
```bash
python3 gen.py                  # regenerate index.html
python3 -m http.server 8000     # local preview
vercel deploy --prod            # deploy (free tier)
```
Recommended: connect the GitHub repo in Vercel so pushes to `main` auto-deploy.

## What is placeholder
- **Public roster:** no real talent is shown. Categories describe planned areas of representation. Only add signed, consenting talent.
- **Roster slots** on division pages ("Open roster slot · PLACEHOLDER · NOT A REAL PROFILE").
- **Selected work** slots (case study, partner logo, testimonial) are labelled placeholders. Never fill them with unverified clients, quotes or stats.
- **Inquiry delivery:** no inbox is configured; forms only produce a copyable summary.
- Text logo with a geometric star, abstract hero art, Google Fonts (not self-hosted), no privacy/terms pages.

## Research
- Findings doc: [2026-10-20 Anistar Agency Site Research and Recommendations (v1)](https://docs.google.com/document/d/1zH18gzPX65edCjWAIfUnma4mQOl1q8q54kxnm1rkSK4/edit), Research Library master Sheet row RL-270.

## Prioritized upgrade roadmap
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
- Final domain? Business email? Legal entity & state licensing (CA Talent Agencies Act if booking employment)?
- Which existing Notion rosters (cosplay/creator) are signed vs research-only? (Treat as research only until confirmed.)
- Commission model and which divisions/categories to launch first (135 is the map, not the launch scope).

- Should adult-content creator rosters be kept separate from the public brand?
- Use Next.js or keep static until roster exists?
