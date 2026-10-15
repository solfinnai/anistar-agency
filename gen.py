cats=[("anime-artists","Anime Artists","🎨","Key-visual, character-design and fan-art illustrators working in anime styles."),
("manga-comic-artists","Manga & Comic Artists","📚","Pencillers, inkers, colorists and letterers for manga, US comics and graphic novels."),
("webtoon-creators","Webtoon Creators","📱","Vertical-scroll storytellers on WEBTOON, Tapas, Tappytoon and beyond."),
("illustrators","Illustrators & Concept Artists","🖌️","Book covers, card art, game concepts, merch and editorial illustration."),
("animators","Animators & Motion Artists","🎞️","2D/3D animators, Live2D riggers and motion designers."),
("cosplayers","Cosplayers","🎭","Guest cosplayers, prop & costume makers, convention appearances."),
("streamers","Streamers","🎮","Twitch, YouTube and Kick streamers in anime, gaming and art."),
("vtubers","VTubers","✨","Virtual talent, model artists, riggers and VTuber groups."),
("content-creators","Content Creators & Influencers","📸","TikTok, Instagram, YouTube and X creators in otaku culture."),
("celebrities","Celebrities & Special Guests","🌟","Notable names for conventions, campaigns and premieres."),
("models","Models","👗","Fashion, alt, J-fashion and brand ambassador models."),
("actors","Actors","🎬","Live-action actors for adaptations, commercials and stage."),
("voice-actors","Voice Actors","🎙️","Dubbing (EN/JP), games, audio drama and ADR talent."),
("musicians","Musicians & Composers","🎵","Anisong artists, J-pop/rock acts, DJs and soundtrack composers."),
("writers","Writers & Translators","✍️","Scriptwriters, light-novel authors, localizers and translators."),
("hosts","Hosts, MCs & Panelists","🎤","Convention hosts, panel moderators and event MCs."),
("dancers","Dancers & Idol Performers","💃","Idol groups, K/J-pop cover dancers and stage performers."),
("photographers","Photographers & Videographers","📷","Cosplay photographers, con coverage and editors."),
("game-creators","Game Creators & Esports","🕹️","Indie devs, esports players and fighting-game talent."),
("educators","Educators & Critics","🧠","Anime critics, analysts, art teachers and podcasters.")]
cards="".join(f'''<a class="cat" href="#cat-{s}"><span class="em">{e}</span><h3>{n}</h3><p>{d}</p></a>''' for s,n,e,d in cats)
sections="".join(f'''<section class="catsec" id="cat-{s}"><h3>{e} {n}</h3><p>{d}</p><div class="roster">'''+"".join(f'''<div class="talent ph"><div class="av">?</div><b>Placeholder Talent {i}</b><small>{n} · Roster slot open</small><span class="tag">PLACEHOLDER</span></div>''' for i in (1,2,3))+"</div></section>" for s,n,e,d in cats)
opts="".join(f"<option>{n}</option>" for s,n,e,d in cats)
html=open("template.html").read().replace("{{CARDS}}",cards).replace("{{SECTIONS}}",sections).replace("{{OPTS}}",opts)
open("index.html","w").write(html)
