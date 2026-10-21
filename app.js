const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const EMAIL=document.body.dataset.inquiryEmail||'';
// nav
const menuButton=$('.menu-toggle'),navigation=$('#primary-nav');
menuButton?.addEventListener('click',()=>{const o=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(o));menuButton.setAttribute('aria-label',o?'Close navigation':'Open navigation');navigation.classList.toggle('open',o)});
$$('#primary-nav a').forEach(a=>a.addEventListener('click',()=>{menuButton.setAttribute('aria-expanded','false');navigation.classList.remove('open')}));
// directory
const search=$('#q'),filter=$('#division-filter');
function updateDirectory(){const term=search.value.trim().toLowerCase();let n=0;
 $$('.division').forEach(d=>{const inD=filter.value==='all'||filter.value===d.dataset.division;let m=0;
  $$('.category',d).forEach(c=>{const ok=!term||c.dataset.search.includes(term);c.hidden=!ok;if(ok)m++});
  d.hidden=!inD||m===0;if(!d.hidden){n+=m;if(term||filter.value!=='all')d.open=true}});
 $('#result-count').textContent=`Showing ${n} ${n===1?'specialty':'specialties'}`;$('#none').hidden=n>0}
if(search){search.addEventListener('input',updateDirectory);filter.addEventListener('change',updateDirectory);
 $('#clear-filters').addEventListener('click',()=>{search.value='';filter.value='all';updateDirectory();search.focus()});
 const p=new URLSearchParams(location.search);if(p.get('q')){search.value=p.get('q');updateDirectory()}}
// brief (shortlist) stored locally
const KEY='anistar-brief';
const getB=()=>{try{return JSON.parse(localStorage.getItem(KEY))||[]}catch{return[]}};
const setB=b=>{try{localStorage.setItem(KEY,JSON.stringify(b))}catch{}render()};
function toggle(n){const b=getB();setB(b.includes(n)?b.filter(x=>x!==n):[...b,n])}
function render(){const b=getB();
 $$('.brief-add').forEach(x=>{const on=b.includes(x.dataset.brief);x.setAttribute('aria-pressed',String(on));x.textContent=on?'✓ In brief':'+ Add to brief'});
 $$('[data-brief-count]').forEach(x=>{x.hidden=!b.length;x.textContent=b.length});
 const bar=$('[data-brief-bar]');if(bar){bar.hidden=!b.length||!!$('#inquire');$('[data-brief-n]').textContent=b.length}
 const list=$('[data-brief-list]');if(list){list.innerHTML='';b.forEach(n=>{const li=document.createElement('li');li.textContent=n;const r=document.createElement('button');r.type='button';r.className='brief-remove';r.setAttribute('aria-label','Remove '+n);r.textContent='×';r.onclick=()=>toggle(n);li.append(r);list.append(li)});$('[data-brief-empty]').hidden=b.length>0}}
document.addEventListener('click',ev=>{const t=ev.target.closest('.brief-add');if(t)toggle(t.dataset.brief)});
$('[data-brief-picker]')?.addEventListener('change',ev=>{const v=ev.target.value;if(v&&!getB().includes(v))toggle(v);ev.target.value=''});
render();
// forms: validate, compose text, mailto if configured, else copy
function handle(form,title,build){form.addEventListener('submit',ev=>{ev.preventDefault();const err=$('.form-error',form);
 const bad=$$('[required]',form).filter(i=>!i.value.trim()||(i.type==='email'&&!/^\S+@\S+\.\S+$/.test(i.value)));
 $$('[aria-invalid]',form).forEach(i=>i.removeAttribute('aria-invalid'));bad.forEach(i=>i.setAttribute('aria-invalid','true'));
 if(bad.length){err.hidden=false;err.textContent='Please complete the highlighted fields.';bad[0].focus();return}err.hidden=true;
 const f=Object.fromEntries(new FormData(form));const text=build(f);const res=$('[data-result]',form);res.hidden=false;$('[data-result-text]',form).value=text;
 if(EMAIL){$('[data-result-msg]',form).textContent='Opening your email app with this summary. If nothing opens, copy it below.';location.href=`mailto:${EMAIL}?subject=${encodeURIComponent(title+': '+(f.org||f.name))}&body=${encodeURIComponent(text)}`}
 else $('[data-result-msg]',form).textContent='Thanks. Anistar\'s inbox is not open yet, so nothing has been sent. Copy this summary and keep it for when inquiries open.';
 res.scrollIntoView({behavior:'smooth',block:'nearest'})})}
const inq=$('#inquiry-form');if(inq)handle(inq,'Anistar brief',f=>`ANISTAR BRIEF\nName: ${f.name}\nEmail: ${f.email}\nOrganization: ${f.org||'-'}\nProject type: ${f.type}\nTiming: ${f.timing||'-'}\nBudget: ${f.budget||'Not shared'}\nSpecialties: ${getB().join('; ')||'Not specified'}\n\nDetails:\n${f.details||'-'}`);
const ap=$('#apply-form');if(ap)handle(ap,'Anistar application',f=>`ANISTAR ROSTER APPLICATION\nName: ${f.name}\nEmail: ${f.email}\nSpecialty: ${f.specialty}\n\nLinks:\n${f.links}\n\nAbout:\n${f.about||'-'}`);
$$('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const t=$('[data-result-text]',b.closest('form'));try{await navigator.clipboard.writeText(t.value);b.textContent='Copied'}catch{t.select();document.execCommand('copy');b.textContent='Copied'}}));
