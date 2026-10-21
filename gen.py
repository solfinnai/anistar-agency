import csv,html,re,json,os
from taxonomy import T
from site_config import BASE,INQUIRY_EMAIL,FOUNDERS
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
e=lambda s:html.escape(s,quote=True)
nd=len(T);nc=sum(len(c) for _,_,c in T)
STAR='<svg class="brand-symbol" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 1.5 19.3 12.7 30.5 16l-11.2 3.3L16 30.5l-3.3-11.2L1.5 16l11.2-3.3L16 1.5Z" fill="currentColor"/></svg>'
ORG={"@context":"https://schema.org","@type":"Organization","name":"Anistar Agency","url":BASE+"/","logo":BASE+"/favicon.svg",
 "description":"Talent agency in development for artists, performers, creators and teams across anime, manga, comics and gaming.",
 "founder":[{"@type":"Person","name":f["name"],"jobTitle":f["role"],"sameAs":[f["link"]]} for f in FOUNDERS]}

def head(title,desc,path,extra_ld=()):
  url=BASE+path
  lds="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (ORG,)+tuple(extra_ld))
  return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1018">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Anistar Agency">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{BASE}/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
{lds}
</head>
<body data-inquiry-email="{e(INQUIRY_EMAIL)}">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="shell nav-inner">
<a class="brand" href="/" aria-label="Anistar Agency home">{STAR}<span>ANISTAR<span class="brand-dot">.</span></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Open navigation"><span></span><span></span></button>
<nav id="primary-nav" class="primary-nav" aria-label="Primary navigation"><a href="/#talent">Talent</a><a href="/#how">How it works</a><a href="/#partners">For partners</a><a href="/#team">Founders</a><a href="/#apply">Join the roster</a></nav>
<a class="nav-cta" href="/#inquire">Book talent <span class="brief-count" data-brief-count hidden></span> <span aria-hidden="true">↗</span></a>
</div></header>
'''

FOOT=f'''<footer class="site-footer"><div class="shell footer-top"><a class="brand footer-brand" href="/" aria-label="Anistar Agency home">{STAR}<span>ANISTAR<span class="brand-dot">.</span></span></a><p>Talent across anime, manga, comics and gaming.</p><a href="#main">BACK TO TOP ↑</a></div>
<div class="shell footer-links"><nav aria-label="Divisions">{"".join(f'<a href="/talent/{slug(d)}/">{e(d)}</a>' for d,_,_ in T)}</nav></div>
<div class="shell footer-bottom"><span>© 2026 ANISTAR AGENCY</span><span>AN INDEPENDENT AGENCY IN DEVELOPMENT · NO TALENT, CLIENTS OR PARTNERS ARE LISTED YET</span></div></footer>
<div class="brief-bar" data-brief-bar hidden role="region" aria-label="Your brief"><span><b data-brief-n>0</b> specialties in your brief</span><a class="button button-light" href="/#inquire">Send brief ↗</a></div>
<script src="/app.js" defer></script>
</body></html>
'''

def cat_card(n,ds,r,d):
  return (f'<article class="category" data-search="{e((n+" "+ds+" "+r+" "+d).lower())}"><h3>{e(n)}</h3><p>{e(ds)}</p>'
          f'<small>EXAMPLE ROLES: {e(r)}</small><button type="button" class="brief-add" data-brief="{e(n)}" aria-pressed="false">+ Add to brief</button></article>')

# ---------- home ----------
filter_options="".join(f'<option value="{slug(d)}">{e(d)}</option>' for d,_,_ in T)
secs=""
for i,(d,ic,cs) in enumerate(T,1):
  cards="".join(cat_card(n,ds,r,d) for n,ds,r in cs)
  secs+=(f'<details class="division" id="div-{slug(d)}" data-division="{slug(d)}"{" open" if i==1 else ""}><summary><span class="division-index">{i:02d}</span>'
         f'<span class="division-title">{e(d)}</span><span class="division-count">{len(cs)} SPECIALTIES</span><span class="division-plus" aria-hidden="true">+</span></summary>'
         f'<div class="category-grid">{cards}</div><p class="division-more"><a class="inline-link dark" href="/talent/{slug(d)}/">Open the {e(d)} division page <span aria-hidden="true">↗</span></a></p></details>')
opts="".join(f'<optgroup label="{e(d)}">'+"".join(f'<option>{e(n)}</option>' for n,_,_ in cs)+'</optgroup>' for d,_,cs in T)
founders="".join(f'''<article class="founder"><div class="avatar" aria-hidden="true">{f["initials"]}</div><div><h3>{e(f["name"])}</h3><p class="founder-role">{e(f["role"]).upper()}</p><p>{e(f["bio"])}</p><a class="inline-link dark" href="{f["link"]}" rel="noopener" target="_blank">{e(f["link_label"])} <span aria-hidden="true">↗</span></a></div></article>''' for f in FOUNDERS)
FAQ=[("Is the roster live?","Not yet. Anistar is mapping the fields it will represent before it publishes anyone. Every roster slot on this site is a placeholder, and people or teams will appear only after they have agreed to be listed."),
("What kinds of talent does Anistar represent?",f"Anistar's scope covers {nd} divisions and {nc} specialties across anime, manga, comics, webtoons and gaming, from illustrators and voice actors to VTubers, esports teams and indie game studios."),
("Do esports teams and game studios count as talent?","Yes. Esports teams and organizations and independent game studios are represented as talent on the roster, not treated as clients."),
("How do I book talent or send a brief?","Add the specialties you need to a brief, then complete the short inquiry form. You will get a clean summary of your request to send or copy."),
("How do I apply for representation?","Use the roster application below. Share your field, your strongest work and the links that show it. Applications open fully once the intake process is staffed.")]
faq_html="".join(f'<details class="faq-item"><summary>{e(q)}<span aria-hidden="true">+</span></summary><p>{e(a)}</p></details>' for q,a in FAQ)
faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
site_ld={"@context":"https://schema.org","@type":"WebSite","name":"Anistar Agency","url":BASE+"/"}
h=open("template.html").read()
rep={"HEAD":head("Anistar Agency | Talent for anime, manga, comics & gaming",f"Anistar is building a talent agency for the artists, performers, creators and teams behind anime, manga, comics and gaming: {nd} divisions and {nc} specialties.","/",(site_ld,faq_ld)),
 "FOOT":FOOT,"FILTER_OPTIONS":filter_options,"SECTIONS":secs,"OPTS":opts,"FOUNDERS":founders,"FAQ":faq_html,"ND":str(nd),"NC":str(nc),
 "DIVCARDS":"".join(f'<a class="div-card" href="/talent/{slug(d)}/"><span class="division-index">{i:02d}</span><h3>{e(d)}</h3><p>{len(cs)} specialties</p><span aria-hidden="true">↗</span></a>' for i,(d,_,cs) in enumerate(T,1))}
for k,v in rep.items(): h=h.replace("{{"+k+"}}",v)
assert "{{" not in h, re.findall(r"\{\{\w+\}\}",h)
open("index.html","w").write(h)

# ---------- division pages ----------
for i,(d,ic,cs) in enumerate(T):
  s=slug(d);prev=T[i-1][0];nxt=T[(i+1)%nd][0]
  desc=f"{d} at Anistar Agency: {len(cs)} specialties including "+", ".join(n for n,_,_ in cs[:4])+". Roster in development."
  bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Anistar Agency","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Talent","item":BASE+"/#talent"},{"@type":"ListItem","position":3,"name":d,"item":f"{BASE}/talent/{s}/"}]}
  slots="".join(f'<div class="slot"><div class="avatar ghost" aria-hidden="true">?</div><b>Open roster slot</b><span class="tag">PLACEHOLDER · NOT A REAL PROFILE</span></div>' for _ in range(3))
  page=head(f"{d} talent | Anistar Agency",desc,f"/talent/{s}/",(bc,))+f'''<main id="main">
<section class="div-hero"><div class="shell"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Anistar</a> / <a href="/#talent">Talent</a> / <span aria-current="page">{e(d)}</span></nav>
<p class="eyebrow"><span class="eyebrow-line"></span> DIVISION {i+1:02d} / {nd:02d}</p><h1 class="div-title">{e(d)}</h1>
<p class="hero-lede">{len(cs)} specialties Anistar plans to represent in this division. Add the ones you need to a brief, or apply if this is your field.</p>
<div class="hero-actions"><a class="button button-light" href="/#inquire">Book this division <span aria-hidden="true">↗</span></a><a class="text-link" href="/#apply">Apply for representation <span aria-hidden="true">↗</span></a></div></div></section>
<section class="section-pad directory"><div class="shell"><p class="section-label">SPECIALTIES</p><div class="category-grid wide">{"".join(cat_card(n,ds,r,d) for n,ds,r in cs)}</div>
<p class="section-label" style="margin-top:70px">ROSTER</p><div class="slots">{slots}</div>
<div class="directory-note"><span class="note-marker" aria-hidden="true">i</span><p>The roster is in development. These slots are placeholders, not people. Talent is published only after they agree to be listed.</p></div>
<nav class="pager" aria-label="Other divisions"><a href="/talent/{slug(prev)}/">← {e(prev)}</a><a href="/talent/{slug(nxt)}/">{e(nxt)} →</a></nav></div></section>
</main>'''+FOOT
  os.makedirs(f"talent/{s}",exist_ok=True);open(f"talent/{s}/index.html","w").write(page)

# ---------- 404, sitemap, robots ----------
open("404.html","w").write(head("Page not found | Anistar Agency","This page does not exist.","/404")+'<main id="main"><section class="div-hero"><div class="shell"><h1 class="div-title">Page not found.</h1><p class="hero-lede">The page you were looking for is not here.</p><a class="button button-light" href="/">Back to Anistar ↗</a></div></section></main>'+FOOT)
urls=[BASE+"/"]+[f"{BASE}/talent/{slug(d)}/" for d,_,_ in T]
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{u}</loc></url>" for u in urls)+"</urlset>\n")
open("robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

# ---------- data exports ----------
with open("taxonomy.csv","w",newline="") as f:
  w=csv.writer(f);w.writerow(["Division","Category","Description","Example roles","Roster status"])
  for d,_,cs in T:
    for n,ds,r in cs: w.writerow([d,n,ds,r,"Placeholder / open"])
md=f"# Anistar Agency Talent Taxonomy\n\n{nd} divisions · {nc} categories · Anime, manga, comics/webtoons and gaming. No real people listed.\n"
for d,ic,cs in T:
  md+=f"\n## {ic} {d} ({len(cs)})\n\n| Category | Description | Example roles |\n|---|---|---|\n"+"".join(f"| {n} | {ds} | {r} |\n" for n,ds,r in cs)
open("TAXONOMY.md","w").write(md)
print(nd,nc,len(urls))
