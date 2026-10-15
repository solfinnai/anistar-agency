const q=document.getElementById('q'),chips=[...document.querySelectorAll('.chip')],divs=[...document.querySelectorAll('.div')];let cur='all';
function f(){const t=q.value.trim().toLowerCase();let any=0;divs.forEach(d=>{let n=0;d.querySelectorAll('.cat').forEach(c=>{const m=!t||c.dataset.s.includes(t);c.hidden=!m;n+=m});const show=(cur==='all'||d.dataset.d===cur)&&n>0;d.hidden=!show;any+=show});document.getElementById('none').hidden=!!any}
q.addEventListener('input',f);chips.forEach(c=>c.onclick=()=>{chips.forEach(x=>x.classList.remove('on'));c.classList.add('on');cur=c.dataset.d;f()});
