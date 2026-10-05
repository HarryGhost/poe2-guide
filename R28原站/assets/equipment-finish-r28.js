/* R28: local manual planning only. Never writes to build/Atlas files. */
(()=>{'use strict';
function init(){
const root=document.getElementById('r28-finish');if(!root)return;
const D=JSON.parse(document.getElementById('r28-data').textContent),$=id=>document.getElementById(id),KEY='fubgun-r28-equipment-finish',allowedStatus=['todo','ready','done','na'];
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slots=Object.fromEntries(D.slots.map(s=>[s.id,s])),aug=Object.fromEntries(D.augments.map(a=>[a.id,a]));
const canon=x=>slots[D.aliases[x]||x]?(D.aliases[x]||x):'bow',base=x=>x==='weapon2'?'bow':x==='quiver2'?'quiver':x;
let records={},storageOK=true,stage='e01',slot='bow';
try{const v=JSON.parse(localStorage.getItem(KEY)||'{}');if(v&&typeof v==='object'&&!Array.isArray(v))records=v;}catch(e){storageOK=false;}
function isStage(s){return D.stages.some(t=>t.id===s);}
function parse(){let q=new URLSearchParams(location.search),hash=location.hash.replace(/^#/,'').split('/');stage=isStage(q.get('stage'))?q.get('stage'):isStage(hash[0])?hash[0]:'e01';slot=canon(q.get('slot')||hash[1]||'bow');}
parse();
function get(s=stage,k=slot){const v=records[s]?.[k];return v&&typeof v==='object'&&!Array.isArray(v)?v:{};}
function patch(o){if(D.plans[stage][slot].readonly)return;records[stage]??={};records[stage][slot]={...get(),...o};try{localStorage.setItem(KEY,JSON.stringify(records));storageOK=true;}catch(e){storageOK=false;}$('r28-saved').textContent=storageOK?'准备记录已保存 · 不是游戏状态':'浏览器不允许保存 · 可导出本次记录';}
function refs(keys){return [...new Set(keys)].map(k=>`<a href="${esc(D.sources[k].url)}" target="_blank" rel="noopener noreferrer">${esc(D.sources[k].title)}</a>`).join(' · ');}
function linkBack(){const k=slot.startsWith('charm')?'charms':slot.endsWith('_flask')?'flasks':slot==='quiver2'?'weapon2':slot;return stage.startsWith('e')?`equipment.html#${stage}/${k}`:`${stage}.html#gear`;}
function htmlPlan(p){return `<div class="r28-plan-text"><div class="r28-source">${esc(p.source)}</div><h2>${esc(p.name)} · ${esc(p.pick)}</h2><p>${esc(p.why)}</p><dl class="r28-facts"><div><dt>品质 / 加工</dt><dd>${esc(p.quality)}</dd></div><div><dt>孔位 / 去哪里放</dt><dd>${esc(p.socket)}</dd></div></dl><h3>照着做</h3><ol class="r28-steps">${p.steps.map(x=>`<li>${esc(x)}</li>`).join('')}</ol>${p.alternatives.length?`<details><summary>没有指定材料 / 需要解决别的缺口</summary><div class="detail"><ul>${p.alternatives.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></details>`:''}${p.special?`<p class="r28-note">${esc(p.special)}</p>`:''}<details><summary>操作后检查与不能混用</summary><div class="detail"><h4>操作后检查</h4><ul>${p.checks.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><h4>不这样做</h4><ul>${p.avoid.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></details><p class="r28-ref">${refs(p.sourceKeys)}</p><a class="r28-back" href="${linkBack()}">← 回对应装备 / 人物阶段</a></div>`;}
function effects(id,k){const a=aug[id];return a?.effects[base(k)]||'';}
function eligible(k){return D.augments.filter(a=>a.effects[base(k)]);}
function choices(p){
 const r=get();if(p.readonly){$('r28-selection').innerHTML='<p class="r28-warn">06仅供查看规则，不提供准备/完成按钮。原件冲突未解决。</p>';return;}
 let out='';if(['weapon2','quiver2'].includes(slot))out+=`<label class="r28-share"><input id="r28-shared" type="checkbox" ${r.shared!==false?'checked':''}>与主手共享同一件 / 尚未配置独立装备（不重复计算材料）</label>`;
 const share=['weapon2','quiver2'].includes(slot)&&r.shared!==false;
 if(share){out+='<p>共享时使用主手那件的品质和孔内物品；这里不另列购买清单。取消上方勾选才规划独立副手。</p>';}
 else if(p.cap){
  const chosen=Array.isArray(r.augments)?r.augments:[];out+='<p class="small">按普通孔上限规划，空白不会自动补满。现有合适增幅物可选“保留现有”，先检查是否 Socket-bound。材料需求等级以游戏物品说明为准。</p>';
  for(let i=0;i<p.cap;i++){
   const sel=chosen[i]||'';let opts='<option value="">先留空 / 未决定</option><option value="__keep"'+(sel==='__keep'?' selected':'')+'>保留现有物品（不计新材料）</option>';
   for(const group of [...new Set(eligible(slot).map(a=>a.kind))])opts+=`<optgroup label="${esc(group)}">`+eligible(slot).filter(a=>a.kind===group).map(a=>`<option value="${a.id}" ${sel===a.id?'selected':''}>${esc(a.name)}${a.limit?' · 限1':''}</option>`).join('')+'</optgroup>';
   const a=aug[sel];out+=`<div class="r28-socket-row"><label for="r28-socket-${i}">第 ${i+1} 孔</label><select id="r28-socket-${i}" data-r28-socket="${i}">${opts}</select><div class="r28-effect">${a?`<b>${esc(effects(sel,slot))}</b><span>${esc(a.notesBySlot?.[base(slot)]||a.note)}</span><small>${a.level?'需要人物'+a.level+'级':'需求等级以物品为准'}${a.ancient?' · 古老增幅物类别限制':''} · <a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">核对物品</a></small>`:sel==='__keep'?'保持原孔，不产生新材料数量。':'尚未安排，不意味着必须购买最高阶材料。'}</div></div>`;
  }
  out+=`<label class="r28-quality-note" for="r28-holes">本件当前已有孔（只用于估算缺孔数）<select id="r28-holes">${Array.from({length:p.cap+1},(_,i)=>`<option value="${i}" ${Number(r.holes||0)===i?'selected':''}>${i}</option>`).join('')}</select></label><p class="small">巧匠石只算计划使用到的孔位与已有孔之差，不要求所有空孔都打满。特殊自带孔/不可修改装备不适用此估算。</p>`;
 }else if(p.catalyst){
  const jewel=slot==='jewels',type=r.catalyst||'';out+=`<label for="r28-catalyst">${jewel?'天赋珠宝用精炼催化剂':'本件首饰用普通催化剂'}</label><select id="r28-catalyst"><option value="">先不加工 / 未决定</option>${D.catalysts.map(c=>`<option value="${c.id}" ${type===c.id?'selected':''}>${esc(jewel?c.refined:c.zh)} · ${esc(c.tag)}</option>`).join('')}</select>`;
  const c=D.catalysts.find(c=>c.id===type);if(c)out+=`<p class="r28-note">${esc(c.note)} 更换种类会取代原品质类型。<a href="${esc(jewel?c.refinedUrl:c.url)}" target="_blank" rel="noopener noreferrer">核对材料</a></p>`;
  if(jewel)out+='<p class="small">这项只记录一种待处理珠宝；多颗珠宝不同催化剂请逐颗记在备注中。没有精炼材料也不必停刷等齐。</p>';
  if(p.anoint)out+=`<label class="r28-share"><input id="r28-anoint" type="checkbox" ${r.anoint?'checked':''}>计划可选“锯齿锋缘”涂膏（确认预览再用料）</label>`;
 }else out+='<p>此栏位不使用普通符文孔。按上方操作处理；不为了填满表格而购买不适用材料。</p>';
 $('r28-selection').innerHTML=out;
}
function warningList(){
 let seen={},anc=[],messages=[];
 for(const s of D.slots){const r=get(stage,s.id);if(r.status==='na'||(['weapon2','quiver2'].includes(s.id)&&r.shared!==false))continue;for(const id of (Array.isArray(r.augments)?r.augments:[]).slice(0,s.cap)){if(!aug[id]||!effects(id,s.id))continue;(seen[id]??=[]).push(s.name);if(aug[id].ancient)anc.push(s.name+'：'+aug[id].name);}}
 for(const [id,where] of Object.entries(seen))if(aug[id].limit&&where.length>aug[id].limit)messages.push(aug[id].name+'在多个位置出现（'+where.join('、')+'）。请核对全身“限1”及武器组；不能直接照此重复镶嵌。');
 if(anc.length>1)messages.push('已安排多个深渊之眼：请核对古老增幅物类别上限，不因物品名称不同就同时装入。');
 $('r28-warnings').innerHTML=messages.length?'<div class="r28-warn"><b>当前准备单需复核</b><ul>'+messages.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></div>':'<p class="small muted">未发现本表能识别的重复限量项；这不等于客户端已验收。</p>';
 return messages;
}
function summary(){
 const materials={},statusText={todo:'待处理',ready:'材料已备',done:'已手动复核',na:'暂不适用'};let orbs=0;
 const rows=D.slots.map(s=>{const p=D.plans[stage][s.id],r=get(stage,s.id),chosen=Array.isArray(r.augments)?r.augments.slice(0,p.cap):[];let names=[];const skip=p.readonly||r.status==='na'||(['weapon2','quiver2'].includes(s.id)&&r.shared!==false);
  if(!skip){chosen.forEach((id,i)=>{if(aug[id]&&effects(id,s.id)){materials[aug[id].name]=(materials[aug[id].name]||0)+1;names.push(aug[id].name);}else if(id==='__keep')names.push('保留现有');});const last=chosen.reduce((n,x,i)=>(aug[x]&&effects(x,s.id))||x==='__keep'?i+1:n,0);orbs+=Math.max(0,last-Math.min(p.cap,Math.max(0,Number(r.holes)||0)));if(r.catalyst&&p.catalyst){const c=D.catalysts.find(c=>c.id===r.catalyst);if(c)names.push(s.id==='jewels'?c.refined:c.zh);}if(r.anoint&&p.anoint)names.push('锯齿锋缘涂膏');}
  return `<tr><th><button type="button" data-r28-slot="${s.id}">${esc(s.name)}</button></th><td>${p.readonly?'只读':statusText[r.status]||'待处理'}</td><td>${skip?(['weapon2','quiver2'].includes(s.id)?'共享/未独立配置，不重复投入':'按实际适用性处理'):esc(names.join('；')||'未安排新材料')}</td></tr>`;});
 $('r28-summary').innerHTML=`<p>材料数量只统计本阶段手动选入的新增幅物，不含背包已有材料；标为“已处理”的项目仍保留在计划总数中。品质通货数量因物品当前状态而异，不给固定包办数。</p><div class="r28-material-list">${Object.entries(materials).map(([k,v])=>`<span>${esc(k)} ×${v}</span>`).join('')||'<span>尚未安排新增幅物</span>'}<span>普通缺孔估算：巧匠石 ${orbs}（特殊物品另核）</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>部位</th><th>手动进度</th><th>本件安排</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}
function syncURL(){try{if(['http:','https:','file:'].includes(location.protocol)){const u=new URL(location.href);u.searchParams.set('stage',stage);u.searchParams.set('slot',slot);u.hash='work';history.replaceState(null,'',u);}}catch(e){} }
function render(){const p=D.plans[stage][slot],r=get();$('r28-stage').value=stage;$('r28-plan').innerHTML=htmlPlan(p);const actions=$('r28-actions');actions.innerHTML='';let node=$('r28-plan').querySelector('h3');while(node){const next=node.nextSibling;actions.appendChild(node);node=next;}choices(p);$('r28-status').value=allowedStatus.includes(r.status)?r.status:'todo';$('r28-note').value=typeof r.note==='string'?r.note:'';$('r28-status').disabled=p.readonly;$('r28-note').disabled=p.readonly;root.querySelectorAll('.r28-slots [data-r28-slot]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.r28Slot===slot)));warningList();summary();root.dataset.stage=stage;root.dataset.slot=slot;syncURL();window.dispatchEvent(new Event('r28-context'));}
root.addEventListener('click',e=>{const b=e.target.closest('[data-r28-slot]');if(b){slot=canon(b.dataset.r28Slot);render();if(b.closest('#r28-summary'))$('work').scrollIntoView({block:'start',behavior:'smooth'});}});
root.addEventListener('change',e=>{const t=e.target;if(t.id==='r28-stage'){stage=isStage(t.value)?t.value:'e01';render();return;}if(D.plans[stage][slot].readonly)return;
 if(t.matches('[data-r28-socket]')){const a=Array.isArray(get().augments)?get().augments.slice():[];a[Number(t.dataset.r28Socket)]=t.value==='__keep'||effects(t.value,slot)?t.value:'';patch({augments:a});choices(D.plans[stage][slot]);}
 else if(t.id==='r28-catalyst'){patch({catalyst:t.value});choices(D.plans[stage][slot]);}
 else if(t.id==='r28-shared'){patch({shared:t.checked});choices(D.plans[stage][slot]);}
 else if(t.id==='r28-holes')patch({holes:Math.max(0,Math.min(slots[slot].cap,Number(t.value)||0))});
 else if(t.id==='r28-status')patch({status:allowedStatus.includes(t.value)?t.value:'todo'});
 else if(t.id==='r28-anoint')patch({anoint:t.checked});warningList();summary();});
$('r28-note').addEventListener('input',e=>patch({note:e.target.value.slice(0,1200)}));
$('r28-export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({type:'manual-preparation-not-game-data',version:'R28',exportedAt:new Date().toISOString(),records},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='Fubgun_手动装备准备记录_R28.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
window.addEventListener('hashchange',()=>{parse();render();});
window.__FINISH_R28={state:()=>({stage,slot,records:JSON.parse(JSON.stringify(records))}),select:(s,k)=>{if(!isStage(s))throw Error('unknown stage');stage=s;slot=canon(k);render();},warnings:warningList,data:D};
render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
/* Keep the existing four-page workflow on the same character stage and item. */
(()=>{'use strict';function boot(){const nav=document.querySelector('.r28-process');if(!nav)return;
function sync(){const p=document.body.dataset.page;let stage='e01',slot='bow';
 if(p==='equipment'){const s=window.__EQUIPMENT_R14?.state();stage=s?.phase||stage;slot=s?.selected||slot;}
 else if(p==='craft'){const s=window.__CRAFT_R13?.state();stage=s?.phase||stage;slot=window.__EQUIPMENT_BRIDGE?.uid||s?.slot||slot;}
 else if(p==='runes'){const s=window.__FINISH_R28?.state();stage=s?.stage||stage;slot=s?.slot||slot;}
 else if(p==='finish-check')stage=document.getElementById('finish-check-stage')?.value||stage;
 const eqslot=slot.startsWith('charm')?'charms':slot.endsWith('_flask')?'flasks':slot==='quiver2'?'weapon2':slot;
 const craftslot=['ring1','ring2'].includes(slot)?'rings':eqslot==='weapon2'?'bow':eqslot;
 const urls=[stage.startsWith('e')?`equipment.html#${stage}/${eqslot}`:`${stage}.html#gear`,['e01','e02','e03','e04','e05'].includes(stage)?`craft.html?target=${encodeURIComponent(eqslot)}#${stage}/${craftslot}`:`${stage}.html#gear`,`runes.html?stage=${stage}&slot=${encodeURIComponent(slot)}#work`,`finish-check.html?stage=${stage}`];
 nav.querySelectorAll('a').forEach((a,i)=>a.href=urls[i]);
 const back=document.querySelector('.r28-heading>a');if(back&&p==='runes')back.href=urls[0];
 window.__R28_FLOW_STATE={stage,slot,urls};}
 nav.addEventListener('pointerdown',sync);nav.addEventListener('click',sync,true);
 window.addEventListener('r28-context',sync);window.addEventListener('craft-context-change',()=>setTimeout(sync,0));window.addEventListener('hashchange',()=>setTimeout(sync,0));
 document.addEventListener('change',()=>setTimeout(sync,0));document.addEventListener('click',()=>setTimeout(sync,0));sync();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();})();
