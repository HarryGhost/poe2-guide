/* R9: manual reading assistant, no game automation and no artificial progress locks. */
(()=>{'use strict';
 const root=document.getElementById('g-root');if(!root)return;
 const dataEl=document.getElementById('guided-craft-data');
 let D;try{D=JSON.parse(dataEl.textContent);}catch{root.innerHTML='<p class="notice danger">操作数据未载入。请打开 <a href="craft-steps-all.html">完整静态操作页</a>，不要使用缺失的步骤。</p>';return;}
 const $=id=>document.getElementById(id),E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const routes=new Map(D.routes.map(r=>[r.id,r]));
 let phase='early',route=D.default,step=routes.get(route).steps[0].id;
 const storageKey='poe2-r9-craft-reading';let storageOK=true;
 function save(){try{localStorage.setItem(storageKey,JSON.stringify({route,step,phase}));}catch{storageOK=false;}}
 function ext(url,text){return '<a href="'+E(url)+'" target="_blank" rel="noopener noreferrer">'+E(text)+' ↗</a>';}
 function material(mid){const m=D.materials[mid];return m?'<button type="button" class="g-material" data-g-material="'+E(mid)+'">'+E(m.zh)+' <span aria-hidden="true">?</span></button>':'';}
 function staticStep(r,s,i){return '<section class="g-static-step"><h3>'+E((i+1)+'. '+s.title)+'</h3>'+(s.kind==='boundary'?'<p class="g-boundary">只读说明 · 前提未验证，不当作执行指令</p>':'')+'<p><b>操作前：</b>'+E(s.before)+'</p><ol>'+s.action.map(a=>'<li>'+E(a)+'</li>').join('')+'</ol><p><b>点完看什么：</b>'+E(s.expect)+'</p><p><b>结果符合：</b>'+E(s.good)+'</p><p><b>不符合就停：</b>'+E(s.bad)+'</p>'+(s.materials.length?'<p><b>材料：</b>'+s.materials.map(m=>E(D.materials[m].zh)).join('；')+'</p>':'')+(s.note?'<p class="small muted">'+E(s.note)+'</p>':'')+'<p class="small">'+s.refs.map((u,n)=>ext(u,'依据'+(n+1))).join(' · ')+'</p></section>';}
 function stateRows(rows,label){if(!rows.length)return '';return '<div class="g-state"><h4>'+E(label)+'</h4><dl>'+rows.map(([k,v])=>'<dt>'+E(k)+'</dt><dd>'+E(v)+'</dd>').join('')+'</dl><p>这是条件示意，不是扫描你的装备，也不代表随机结果保证如此。</p></div>';}
 function fillSelect(){
  $('g-phase').value=phase;
  const list=D.routes.filter(r=>phase==='all'||r.phases.includes(phase));
  const a=list.filter(r=>r.id.startsWith('early-')),b=list.filter(r=>!r.id.startsWith('early-'));
  $('g-route').innerHTML=(a.length?'<optgroup label="Early基本加工 · 不要求高配材料">'+a.map(r=>'<option value="'+E(r.id)+'">'+E(r.title)+'</option>').join('')+'</optgroup>':'')+(b.length?'<optgroup label="作者进阶工艺 · 先核对起点">'+b.map(r=>'<option value="'+E(r.id)+'">'+E(r.title)+'</option>').join('')+'</optgroup>':'');
  $('g-route').value=route;
  const r=routes.get(route),entries=r.entries.slice();
  if(!entries.some(e=>e.step===step))entries.push({label:'正在读：'+r.steps.find(s=>s.id===step).title,step});
  $('g-entry').innerHTML=entries.map(e=>'<option value="'+E(e.step)+'">'+E(e.label)+'</option>').join('');$('g-entry').value=step;
 }
 function render(){
  const r=routes.get(route),s=r.steps.find(x=>x.id===step),i=r.steps.indexOf(s);fillSelect();
  $('g-route-intro').innerHTML='<p><b>'+E(r.title)+'：</b>'+E(r.goal)+'</p><p class="small"><b>起点：</b>'+E(r.start)+'</p>';
  $('g-step-count').textContent='第 '+(i+1)+' / '+r.steps.length+' 步';
  $('g-step-nav').innerHTML=r.steps.map((x,n)=>'<button type="button" data-g-step="'+E(x.id)+'" '+(x.id===step?'aria-current="step"':'')+' title="'+E(x.title)+'"><span>'+E(n+1)+'</span>'+E(x.title)+'</button>').join('');
  const boundary=s.kind==='boundary',ending=s.kind==='finish';
  const actionLabel=boundary?'这里先阅读，不操作':'这一步怎么做';
  const moveLabel=(route==='amulet'&&step==='resist')?'后缀已处理好，查看最后前缀':boundary?'继续阅读后文（不是执行许可）':s.kind==='prepare'?'状态符合，查看下一步':ending?'从当前状态重新查看':'结果符合，查看下一步';
  const next=s.next||r.steps[0].id;
  const repeatChoice=(route==='amulet'&&step==='resist')?'<button type="button" data-g-step="quality">还要加一个后缀：先重新补品质</button>':'';
  const extraLink=r.alternative&&routes.has(r.alternative)?'<a class="g-reference-link" href="#'+E(r.alternative)+'">先看后期的 '+E(routes.get(r.alternative).title)+'，不在同一件上直接接做 →</a>':'';
  $('g-main').innerHTML='<section class="g-action" aria-labelledby="g-current-title"><div class="g-card-title"><h2 id="g-current-title">'+E(s.title)+'</h2><button type="button" id="g-copy-step">复制这一步</button></div><div class="g-action-body">'+(boundary?'<p class="g-boundary"><b>这一环尚不能写成无条件照做。</b> 内容仍完整开放，但不要先消耗材料。</p>':'')+'<div class="g-before"><b>操作前，先对上这个状态</b>'+E(s.before)+'</div><div class="g-do-label">'+E(actionLabel)+'</div><ol class="g-do">'+s.action.map(a=>'<li>'+E(a)+'</li>').join('')+'</ol><div class="g-expect"><b>点完应该看到什么</b>'+E(s.expect)+'</div>'+(s.note?'<p class="g-step-note">'+E(s.note)+'</p>':'')+((r.id==='early-bow'&&step==='regal')?'<p class="g-step-note">还没有点富豪、且准备好物理提高蓝弓？<a href="#bow-noncrit/ready">可先比较作者精华升黄路线</a>。它不是富豪后的下一步。</p>':'')+'</div><div class="g-navigation">'+(i?'<button type="button" data-g-step="'+E(r.steps[i-1].id)+'">← 上一步</button>':'')+'<a class="btn" href="'+E(r.reference)+'">完整原文 / 原说明</a></div><div class="g-sources">'+E(r.sourceLabel)+'<br>'+s.refs.map((u,n)=>ext(u,'本步依据'+(n+1))).join(' ')+'</div></section>'+
  '<aside class="g-results" aria-label="材料和结果判断"><div class="g-card-title"><h2>先备材料，再看结果</h2></div><div style="padding:0 12px"><div class="g-materials">'+(s.materials.length?s.materials.map(material).join(''):'<span class="small muted">这一步没有必须消耗的材料。</span>')+'</div>'+((s.id==='reveal')?'<p class="small">可选：'+material('echoes')+'。决定使用，要在显现前准备。</p>':'')+'</div><div class="g-result good"><b>'+(ending?'✓ 这轮的结束标准':'✓ 结果符合时')+'</b><p>'+E(s.good)+'</p><button type="button" data-g-step="'+E(next)+'">'+E(moveLabel)+'</button>'+repeatChoice+'</div><div class="g-result bad"><b>! 不是这个结果，先停</b><p>'+E(s.bad)+'</p><button id="g-stop" type="button" aria-expanded="false" aria-controls="g-stop-detail">我不确定 / 与预期不一样</button><div id="g-stop-detail" class="g-stop-detail" hidden>现在不要再点材料。把鼠标移到装备，确认名称颜色、前后缀和刚新增的属性；看不清就先放回仓库。上方可以改选当前真实状态，或打开下方具体实例。<br><a href="craft-examples.html">看“好结果 / 坏结果”实例 →</a></div></div>'+stateRows(s.stateBefore,'操作前的词缀示意')+stateRows(s.stateAfter,'符合条件时的预期示意')+'</aside>';
  $('g-full-content').innerHTML='<p class="small">'+E(r.start)+'</p><p class="small">'+E(r.avoid)+'</p>'+r.steps.map((x,n)=>staticStep(r,x,n)).join('')+extraLink;
  $('g-print-content').innerHTML='<article class="g-static-route"><h2>'+E(r.title)+'</h2><p>'+E(r.sourceLabel)+'</p><p>'+E(r.goal)+'</p>'+r.steps.map((x,n)=>staticStep(r,x,n)).join('')+'</article>';
  $('g-source-note').innerHTML=E(r.scope)+' '+E(storageOK?'阅读位置尝试保存在当前浏览器，不记录“游戏打造成功”。':'此环境不允许保存阅读位置；仍可用网址里的路线/步骤书签直接打开。');
  save();
 }
 function go(rid,sid,update=true){
  const r=routes.get(rid)||routes.get(D.default);route=r.id;step=r.steps.some(x=>x.id===sid)?sid:r.steps[0].id;
  if(phase!=='all'&&!r.phases.includes(phase))phase=r.phases[0];
  if(update){try{history.replaceState(null,'','#'+route+'/'+step);}catch{}}
  render();
 }
 function fromHash(){let str='';try{str=decodeURIComponent(location.hash.slice(1));}catch{go(D.default,null,false);return;}
  if(str.startsWith('stage-')){const p=str.slice(6);if(D.phases.some(x=>x.id===p)){phase=p;const r=D.routes.find(x=>p==='all'||x.phases.includes(p));go(r.id,null,false);return;}}
  if(str.startsWith('mat-')&&D.materials[str.slice(4)]){render();openMaterial(str.slice(4));return;}
  const [rid,sid]=str.split('/');go(routes.has(rid)?rid:D.default,sid,false);
 }
 function plainStep(r,s,i){return (i+1)+'. '+s.title+(s.kind==='boundary'?'【只读说明，不执行】':'')+'\n操作前：'+s.before+'\n'+s.action.map((a,n)=>(n+1)+') '+a).join('\n')+'\n点完看：'+s.expect+'\n结果符合：'+s.good+'\n不符合先停：'+s.bad+(s.materials.length?'\n材料：'+s.materials.map(m=>D.materials[m].zh).join('；'):'')+(s.note?'\n注意：'+s.note:'')+'\n依据：'+s.refs.join(' | ');}
 async function copyText(text){try{if(!navigator.clipboard)throw Error();await navigator.clipboard.writeText(text);const t=$('toast');t.textContent='已复制；这是阅读清单，不会执行游戏操作。';t.hidden=false;setTimeout(()=>t.hidden=true,2400);}catch{$('g-copy-text').value=text;const d=$('g-copy-dialog');if(d.showModal)d.showModal();else d.setAttribute('open','');$('g-copy-text').focus();$('g-copy-text').select();}}
 function openMaterial(mid){const m=D.materials[mid];if(!m)return;$('g-material-title').textContent=m.zh;$('g-material-body').innerHTML='<p class="small muted">'+E(m.en)+'</p><p><b>它做什么：</b>'+E(m.effect)+'</p><p><b>先检查：</b>'+E(m.check)+'</p><p>'+ext(m.url,'材料说明（国际服数据中文）')+'</p><p class="small muted">查看说明不会使用材料。不要只看图标，把普通、强效/高级与完美版本当成同一种物品。</p>';const d=$('g-material-dialog');if(d.showModal)d.showModal();else d.setAttribute('open','');}
 $('g-phase').addEventListener('change',e=>{phase=e.target.value;const list=D.routes.filter(r=>phase==='all'||r.phases.includes(phase));go(list.some(r=>r.id===route)?route:list[0].id,null);});
 $('g-route').addEventListener('change',e=>go(e.target.value,null));$('g-entry').addEventListener('change',e=>go(route,e.target.value));
 root.addEventListener('click',e=>{const next=e.target.closest('[data-g-step]');if(next){go(route,next.dataset.gStep);return;}const mat=e.target.closest('[data-g-material]');if(mat){openMaterial(mat.dataset.gMaterial);return;}if(e.target.closest('#g-stop')){const box=$('g-stop-detail'),b=$('g-stop');box.hidden=!box.hidden;b.setAttribute('aria-expanded',String(!box.hidden));return;}if(e.target.closest('#g-copy-step')){const r=routes.get(route),s=r.steps.find(x=>x.id===step);copyText('Fubgun · '+r.title+'\n'+r.sourceLabel+'\n'+plainStep(r,s,r.steps.indexOf(s)));}});
 $('g-copy-route').addEventListener('click',()=>{const r=routes.get(route);copyText('Fubgun · '+r.title+'\n'+r.sourceLabel+'\n起点：'+r.start+'\n\n'+r.steps.map((s,i)=>plainStep(r,s,i)).join('\n\n'));});
 $('g-print-route').addEventListener('click',()=>window.print());
 $('g-material-close').addEventListener('click',()=>$('g-material-dialog').close());$('g-copy-close').addEventListener('click',()=>$('g-copy-dialog').close());
 window.addEventListener('hashchange',fromHash);
 if(location.hash)fromHash();else {try{const saved=JSON.parse(localStorage.getItem(storageKey)||'null');if(saved&&routes.has(saved.route)){phase=D.phases.some(x=>x.id===saved.phase)?saved.phase:'early';go(saved.route,saved.step,false);}else render();}catch{storageOK=false;render();}}
 window.__GUIDED_CRAFT={get route(){return route},get step(){return step},get phase(){return phase},routes:D.routes.map(r=>({id:r.id,steps:r.steps.map(s=>s.id)})),go};
})();
