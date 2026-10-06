/* Progressive enhancement: all 8 recipes are present in HTML, never progress gated. */
(() => {
  'use strict';
  const root=document.getElementById('craft-recipes');
  if (!root) return;
  const all=root.dataset.expanded==='true';
  const panels=Array.from(root.querySelectorAll('[data-recipe]'));
  const links=Array.from(document.querySelectorAll('[data-craft-choice]'));
  let current=panels[0]?.id;
  function select(id,scroll=false){
    if(!panels.some(x=>x.id===id)) return;
    current=id;
    for(const p of panels) p.hidden=!all&&p.id!==id;
    for(const a of links){const active=a.dataset.craftChoice===id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');}
    if(scroll)document.getElementById(id).scrollIntoView({block:'start'});
  }
  function hash(){let id='';try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
    if(panels.some(x=>x.id===id)){select(id);return;}
    const el=document.getElementById(id);if(el&&el.matches('.craft-material')){const q=document.getElementById('craft-material-filter');if(q){q.value='';q.dispatchEvent(new Event('input'));}el.hidden=false;el.open=true;}
  }
  for(const a of links)a.addEventListener('click',()=>select(a.dataset.craftChoice));
  select(current);hash();window.addEventListener('hashchange',hash);
  const filter=document.getElementById('craft-material-filter');
  const mats=Array.from(document.querySelectorAll('.craft-material'));
  const count=document.getElementById('craft-material-count');
  function search(){const q=(filter?.value||'').trim().toLowerCase();let n=0;
    for(const m of mats){m.hidden=!!q&&!m.textContent.toLowerCase().includes(q);if(!m.hidden)n++;}
    if(count)count.textContent=`显示 ${n} / ${mats.length} 项；每一项都附英文和使用条件。`;
  }
  filter?.addEventListener('input',search);search();
  const expandedBefore=new Map();
  window.addEventListener('beforeprint',()=>{panels.forEach(p=>p.hidden=false);document.querySelectorAll('details').forEach(d=>{expandedBefore.set(d,d.open);d.open=true;});});
  window.addEventListener('afterprint',()=>{expandedBefore.forEach((v,d)=>d.open=v);expandedBefore.clear();select(current);});
  window.__CRAFT_TEST={recipes:panels.map(x=>x.id),get current(){return current;},all};
})();
