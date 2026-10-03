'use strict';
(()=>{
 const el=document.getElementById('preparation-data');if(!el)return;
 const D=JSON.parse(el.textContent),$=s=>document.querySelector(s),all=s=>[...document.querySelectorAll(s)];
 const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let phase='e01',slot='bow',tab='bases';
 const slots=new Set(D.items.map(x=>x.id)),phases=new Set(D.phases.map(x=>x.id)),tabs=new Set(['bases','routine','supplies','basics']);
 function refs(keys){return '<span class="p-refs">'+[...new Set(keys)].map(k=>{const s=D.sources[k];return `<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">[${esc(k)}] ${esc(s.title)}</a>`}).join(' · ')+'</span>'}
 function matches(it,q){return JSON.stringify(it).toLowerCase().includes(q)}
 function hash(){return '#'+phase+'/'+slot+'/'+tab}
 function saveHash(){try{history.replaceState(null,'',hash())}catch(e){/* Sandboxed/about pages still render. */}}
 function current(){return D.items.find(x=>x.id===slot)||D.items[0]}
 function render(){
  $('#p-phase').value=phase;
  all('[data-prep-tab]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.prepTab===tab)));
  tabs.forEach(k=>$('#p-panel-'+k).hidden=k!==tab);
  const q=$('#p-search').value.trim().toLowerCase(),hits=D.items.filter(i=>!q||matches(i,q));
  $('#p-slot-tabs').innerHTML=hits.map(i=>`<button type="button" data-slot="${esc(i.id)}" aria-pressed="${i.id===slot}">${esc(i.title)}</button>`).join('');
  if(q&&!hits.some(i=>i.id===slot)&&hits.length)slot=hits[0].id;
  all('[data-slot]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.slot===slot)));
  const p=D.phases.find(x=>x.id===phase);
  $('#p-stage-summary').innerHTML=`<b>${esc(p.label)}</b><p>${esc(p.focus)}</p><small>${esc(p.next)} <a href="${phase}.html">查看本阶段完整配置</a> · <a href="e06.html">06冲突实装仍可只读查看</a></small>`;
  if(!hits.length){$('#p-slot-result').innerHTML='<div class="p-empty">没有匹配的部位。试试“弓、项链、护盾、半成品”，或清除搜索。其他章节和阶段没有被锁定。</div>';return}
  const it=current();
  const bases=[...it.bases].sort((a,b)=>Number(b.phases.includes(phase))-Number(a.phases.includes(phase))).map(b=>`<div class="p-base ${b.phases.includes(phase)?'':'future'}"><div class="p-base-head"><b>${esc(b.name)}</b><span class="p-status ${b.phases.includes(phase)?'now':''}">${b.phases.includes(phase)?'本阶段可比较':'非本阶段优先·对照查看'}</span></div><small class="p-en">${esc(b.en)} · ${esc(b.kind)}</small><p>${esc(b.why)}</p>${refs(b.refs)}</div>`).join('');
  const states=it.states.map((s,i)=>`<details class="p-state" ${i===1?'open':''}><summary>${esc(s.label)}</summary><div class="detail"><p><b>值得留：</b>${esc(s.keep)}</p><p><b>接下来：</b>${esc(s.action)}</p><p class="action-note"><b>先停：</b>${esc(s.stop)}</p><a class="btn" href="craft.html#${esc(s.routesByPhase?.[phase]||s.route)}">打开本阶段对应工艺 →</a><p class="small muted">进入后选择实际状态；链接不是自动批准消耗材料。高阶路线前提不符就回基础加工。</p></div></details>`).join('');
  $('#p-slot-result').innerHTML=`<div class="p-workspace"><div><section class="card"><div class="card-head skill"><h2>${esc(it.title)} · 刷图时留什么</h2></div><div class="card-body"><p class="p-summary">${esc(it.goal)}</p><div class="p-goal">${esc(it.goals[phase])}</div><div class="p-base-list">${bases}</div><p class="p-reminder">不是“名单外全部丢弃”。已鉴定的好词缀成品，可能比名字正确的白底更值得留。</p></div></section><details><summary>现在与后续的留装重点</summary><div class="detail"><p><b>Early：</b>${esc(it.early)}</p><p><b>后续：</b>${esc(it.later)}</p>${refs(it.refs)}</div></details><div class="p-actions"><button id="p-copy-item" type="button">复制本阶段留装清单</button><a href="prepare-all.html#${esc(it.id)}">本部位全部阶段展开</a></div></div><div><section class="card"><div class="card-head combat"><h2>回城后 · 按这件的状态接工艺</h2></div><div class="card-body">${states}</div></section><div class="notice"><b>本部位不要误判</b>${it.watch.map(s=>'<p>'+esc(s)+'</p>').join('')}</div></div></div>`;
  $('#p-copy-item').addEventListener('click',copyItem);
  saveHash();
 }
 function copyItem(){const it=current(),p=D.phases.find(x=>x.id===phase);const lines=[p.label+' / '+it.title,it.goals[phase],'【底材】',...it.bases.map(b=>b.name+' / '+b.en+'：'+b.why),'【留与做】',...it.states.map(s=>s.label+'\n留：'+s.keep+'\n做：'+s.action+'\n停：'+s.stop+'\n本阶段工艺：craft.html#'+(s.routesByPhase?.[phase]||s.route)),'【来源与边界】','作者/官方数据/编辑建议分开；不是自动扫描库存，也不是成功率承诺。'];$('#p-copy-text').value=lines.join('\n\n');$('#p-copy-dialog').showModal();$('#p-copy-text').select();}
 function parse(){try{const parts=decodeURIComponent(location.hash.slice(1)).split('/');if(phases.has(parts[0]))phase=parts[0];if(slots.has(parts[1]))slot=parts[1];if(tabs.has(parts[2]))tab=parts[2]}catch(e){}render()}
 $('#p-phase').addEventListener('change',e=>{phase=e.target.value;render()});
 $('#p-slot-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-slot]');if(!b)return;slot=b.dataset.slot;render()});
 all('[data-prep-tab]').forEach(b=>b.addEventListener('click',()=>{tab=b.dataset.prepTab;render()}));
 $('#p-search').addEventListener('input',()=>{tab='bases';render()});$('#p-clear-search').addEventListener('click',()=>{$('#p-search').value='';render()});
 $('#p-copy-close').addEventListener('click',()=>$('#p-copy-dialog').close());
 $('#p-reset-session').addEventListener('click',()=>{all('[data-check^="p-session-"]').forEach(c=>{c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))})});
 window.addEventListener('hashchange',parse);
 window.addEventListener('beforeprint',()=>all('#p-slot-result details').forEach(d=>{d.dataset.printWasOpen=String(d.open);d.open=true}));
 window.addEventListener('afterprint',()=>all('#p-slot-result details').forEach(d=>{if(d.dataset.printWasOpen)d.open=d.dataset.printWasOpen==='true'}));
 parse();
})();
