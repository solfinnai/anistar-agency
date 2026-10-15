# Anistar Agency — Developer Handoff

**Live:** https://anistar-agency.vercel.app · **Repo:** https://github.com/solfinnai/anistar-agency
**Linear:** https://linear.app/henryfinnai/project/anistar-agency-eab3220dfbd8 · **Drive:** https://drive.google.com/drive/folders/12e7HSdn3xPCGKxbiaIob5MqZ0sD_Y6E2
**Notion:** https://app.notion.com/p/3cefdcf928578106b86ad9daa0be973e · **Taxonomy:** TAXONOMY.md

## What it is
Talent agency positioned to own the anime, manga, comics/webtoons and gaming talent ecosystem. The site presents **16 divisions and 135 talent categories** (full list: `TAXONOMY.md` / `taxonomy.csv`, plus the Google Sheet in Drive): Creators & Artists; Animation & Production Craft; Voice & Performance; Music & Audio; Writing & Story; Localization & Translation; Cosplay & Fashion; Models & Brand Faces; Streamers, VTubers & Creators; Esports & Pro Gaming; Game Development Talent; Celebrities, Hosts & Ambassadors; Events & Conventions; Media, Critics & Educators; IP, Licensing & Business; Emerging & Tech.

## Architecture (MVP)
- Zero-dependency static site: `index.html` + `styles.css`. No build step, no backend, no DB.
- **Single source of truth:** `taxonomy.py` (list of divisions → categories with description + example roles).
- `python3 gen.py` generates `index.html` (from `template.html`), `TAXONOMY.md` and `taxonomy.csv`. Never hand-edit those outputs.
- `app.js` adds client-side search plus division filter chips (vanilla JS, no deps). The apply-form dropdown is grouped by division.
- Hosting: Vercel (Hobby/free), project `anistar-agency` under henryfinnai's Vercel account, deployed via CLI (not yet Git-connected).

## Run / deploy
```bash
python3 gen.py                  # regenerate index.html
python3 -m http.server 8000     # local preview
vercel deploy --prod            # deploy (free tier)
```
Recommended: connect the GitHub repo in Vercel so pushes to `main` auto-deploy.

## What is placeholder
- **Every category card's roster** (labelled "ROSTER: PLACEHOLDER — OPEN SLOT") — no real talent is shown. Only add signed, consenting talent.
- Contact email `hello@anistar.agency` (domain not owned/registered).
- Apply form uses `mailto:` (no backend).
- Text logo ANI★STAR, emoji icons, no imagery, no privacy/terms pages.

## Prioritized upgrade roadmap
1. **Migrate to Next.js (App Router) + Tailwind**, keep static export; routes `/talent/[division]/[category]` and `/talent/[slug]` profiles generated from the taxonomy (move `taxonomy.py` to JSON/TS).
2. **Talent DB** — start in Notion (existing Anistar rosters) or Google Sheets; pull at build time (ISR). Fields: name, handle, division + categories (multi-select from taxonomy), bio, links, regions, languages, rates tier, availability, consent/rights status, publish flag.
3. **CMS** for pages/news (Notion-as-CMS, Sanity free tier, or MDX in repo).
4. **Inquiry/booking flow** — brand inquiry form (event type, budget, date, talent) + talent application; free options: Formspree/Web3Forms free tier or Vercel serverless → Sheet/Notion + notify. Add spam protection (Turnstile).
5. **Talent portal auth** — Clerk/Auth.js free tier; talent edits own profile, uploads media kit.
6. **SEO** — metadata per page, OG images, sitemap.xml, robots.txt, JSON-LD (Organization, Person).
7. **i18n JP/EN** — next-intl, `/ja` routes, localized category names.
8. **Analytics** — Vercel Web Analytics (free) or Plausible; track inquiry conversions.
9. Brand pass (logo, art direction), accessibility audit, legal pages.

## Decisions
- **Oct 15, 2026 (Henry):** esports teams/orgs and game studios are represented as **talent on the roster**, not clients. Roster categories: *Esports Teams & Orgs* (Esports & Pro Gaming) and *Indie Game Developers & Studios* (Game Development Talent). For Brands targets publishers, media companies, conventions and consumer brands.

## Open questions
- Final domain? Business email? Legal entity & state licensing (CA Talent Agencies Act if booking employment)?
- Which existing Notion rosters (cosplay/creator) are signed vs research-only? (Treat as research only until confirmed.)
- Commission model and which divisions/categories to launch first (135 is the map, not the launch scope).

- Should adult-content creator rosters be kept separate from the public brand?
- Use Next.js or keep static until roster exists?
