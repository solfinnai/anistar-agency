import csv,html,re
from taxonomy import T
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
e=html.escape
nd=len(T);nc=sum(len(c) for _,_,c in T)
chips='<button class="chip on" data-d="all">All</button>'+"".join(f'<button class="chip" data-d="{slug(d)}">{ic} {e(d)}</button>' for d,ic,_ in T)
secs=""
for d,ic,cs in T:
  cards="".join(f'<article class="cat" data-s="{e((n+" "+ds+" "+r+" "+d).lower())}"><h4>{e(n)}</h4><p>{e(ds)}</p><small>Roles: {e(r)}</small><span class="tag">ROSTER: PLACEHOLDER — OPEN SLOT</span></article>' for n,ds,r in cs)
  secs+=f'<section class="div" id="div-{slug(d)}" data-d="{slug(d)}"><h3>{ic} {e(d)} <span class="cnt">{len(cs)}</span></h3><div class="cats">{cards}</div></section>'
opts="".join(f'<optgroup label="{e(d)}">'+"".join(f"<option>{e(n)}</option>" for n,_,_ in cs)+"</optgroup>" for d,_,cs in T)
h=open("template.html").read()
for k,v in {"CHIPS":chips,"SECTIONS":secs,"OPTS":opts,"ND":str(nd),"NC":str(nc)}.items(): h=h.replace("{{"+k+"}}",v)
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
