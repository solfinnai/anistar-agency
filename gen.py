import csv,html,re
from taxonomy import T
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
e=html.escape
nd=len(T);nc=sum(len(c) for _,_,c in T)
filter_options="".join(f'<option value="{slug(d)}">{e(d)}</option>' for d,_,_ in T)
secs=""
for i,(d,ic,cs) in enumerate(T,1):
  cards="".join(f'<article class="category" data-search="{e((n+" "+ds+" "+r+" "+d).lower(),quote=True)}"><h3>{e(n)}</h3><p>{e(ds)}</p><small>EXAMPLE ROLES: {e(r)}</small></article>' for n,ds,r in cs)
  secs+=f'<details class="division" id="div-{slug(d)}" data-division="{slug(d)}"{" open" if i==1 else ""}><summary><span class="division-index">{i:02d}</span><span class="division-title">{e(d)}</span><span class="division-count">{len(cs)} SPECIALTIES</span><span class="division-plus" aria-hidden="true">+</span></summary><div class="category-grid">{cards}</div></details>'
h=open("template.html").read()
for k,v in {"FILTER_OPTIONS":filter_options,"SECTIONS":secs,"ND":str(nd),"NC":str(nc)}.items(): h=h.replace("{{"+k+"}}",v)
open("index.html","w").write(h)
with open("taxonomy.csv","w",newline="") as f:
  w=csv.writer(f);w.writerow(["Division","Category","Description","Example roles","Roster status"])
  for d,_,cs in T:
    for n,ds,r in cs: w.writerow([d,n,ds,r,"Placeholder / open"])
md=f"# Anistar Agency Talent Taxonomy\n\n{nd} divisions · {nc} categories · Anime, manga, comics/webtoons and gaming. No real people listed.\n"
for d,ic,cs in T:
  md+=f"\n## {ic} {d} ({len(cs)})\n\n| Category | Description | Example roles |\n|---|---|---|\n"+"".join(f"| {n} | {ds} | {r} |\n" for n,ds,r in cs)
open("TAXONOMY.md","w").write(md)
print(nd,nc)
