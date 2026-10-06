/* R21: offline rune guidance. Manual inputs, not a client scan. */
(()=>{'use strict';
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dataEl=document.getElementById('finish-data'),root=document.getElementById('finish-app');
if(root&&dataEl){const D=JSON.parse(dataEl.textContent),stageSel=document.getElementById('finish-stage');let stage='e01',slot='bow';
let chosen={},grade=2,state='unknown';const grades=['次级','普通','高级','完美'];
const stages=new Map(D.stages.map(s=>[s.id,s]));
const params=new URLSearchParams(location.search);if(stages.has(params.get('stage')))stage=params.get('stage');if(D.slots[params.get('slot')])slot=params.get('slot');
const current=()=>D.plans[stage][slot];
function setURL(){try{const u=new URL(location.href);u.searchParams.set('stage',stage);u.searchParams.set('slot',slot);history.replaceState(null,'',u);}catch(_){} }
function overview(){stageSel.value=stage;let rows=Object.entries(D.plans[stage]).map(([id,p])=>`<tr ${id===slot?'class="selected"':''}><th><button type="button" data-finish-slot="${id}" aria-pressed="${id===slot}">${esc(p.name)}</button></th><td>${esc(p.pick)}<small>${p.socket===null?'只读':p.socket?'普通最多'+p.socket+'孔':'普通不打符文孔'}</small></td></tr>`).join('');document.getElementById('finish-overview').innerHTML='<table class="finish-slot-table"><tbody>'+rows+'</tbody></table>';
 document.getElementById('finish-back').href='equipment.html#'+(stage.startsWith('e')?stage+'/': 'e01/')+(slot==='rings'?'ring1':slot);
 document.getElementById('finish-check-link').href='finish-check.html?stage='+stage;
}
function refs(p){return '<p class="finish-sources">'+p.src.map(k=>{let s=D.sources.find(x=>x.id===k);return `<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${k==='F'?'作者原文':'规则 '+k}</a>`;}).join(' · ')+'</p>';}
function render(){overview();const p=current(),el=document.getElementById('finish-plan');
 document.getElementById('finish-work-title').textContent=p.name+' · 收尾操作';document.getElementById('finish-origin').textContent=stage==='e06'?'只读':p.source.startsWith('Fubgun')?'作者明确推荐':'补充选择建议';
 if(stage==='e06'){el.innerHTML=`<p class="notice danger"><b>06只读：</b>${esc(p.goal)}</p><p>${esc(p.watch)}</p><a href="e06.html">查看06原件</a>`;return;}
 let text=`<p class="finish-primary">${esc(p.pick)}</p><p class="small">${esc(p.goal)}</p>`;if(slot==='helmet'&&['e03','e04','e05'].includes(stage))text+='<p class="finish-alert"><b>别把插上当作达标：</b>原件低词缀例＋20品质＋1颗高级钢铁，约396物品护盾，仍不到作者约450的建议。</p>';
 if(!p.socket){text+=`<p class="finish-alert"><b>这个部位不走普通符文开孔。</b> ${esc(p.watch)}</p><p>${esc(p.quality)}</p><ol class="finish-short">${p.alternatives.map(x=>'<li>'+esc(x)+'</li>').join('')}</ol><a class="btn" href="finish-check.html?stage=${stage}#${slot==='amulet'||slot==='rings'?'anoint':slot==='flasks'||slot==='charms'?'recovery':'gem-finishing'}">去做对应收尾 →</a>`+refs(p);el.innerHTML=text;return;}
 const defaultId=(slot==='bow'||slot==='body'&&stage.startsWith('e')||slot==='helmet'&&['e03','e04','e05'].includes(stage))?'iron':'';
 const pick=Object.hasOwn(chosen,slot)?chosen[slot]:defaultId;
 text+=`<div class="finish-inputs"><label>本次放哪种 <select id="finish-rune"><option value="">选择实际缺口／目标</option>${D.runes.map(r=>`<option value="${r.id}" ${r.id===pick?'selected':''}>${esc(r.zh)}</option>`).join('')}</select></label><label>等阶 <select id="finish-grade">${grades.map((v,i)=>`<option value="${i}" ${i===grade?'selected':''}>${v}</option>`).join('')}</select></label></div>`;
 text+='<div id="finish-effect" class="finish-effect"></div>';
 text+=`<label class="finish-state-label">手里这件的孔位状态 <select id="finish-state"><option value="unknown">还没确认／不会认</option><option value="empty">看见至少1个空增幅器孔</option><option value="none">没有孔，未腐化，支持普通开孔</option><option value="replace">孔已装普通增幅器，想覆盖</option><option value="bound">目标孔写着“插槽绑定”</option><option value="special">腐化／镜像／不明特殊状态</option></select></label><div id="finish-action"></div>`;
 text+=`<details class="finish-small-details"><summary>怎么认孔与原文中的“羁绊”？</summary><p>打开这件装备的物品说明，寻找增幅器插槽和已镶嵌效果；不要去技能面板数辅助槽。未确认就先不消耗材料。普通弓／衣服最多2孔，头／手／鞋各1孔，特殊额外孔另看物品。<b>羁绊是萨满专属额外属性，不是这套锐眼的增益；插槽绑定则是不可移除或替换的限制。</b></p></details>`;
 text+=`<div class="finish-quality"><b>品质怎么收尾</b><p>${esc(p.quality)}</p></div><details class="finish-small-details"><summary>没有首选时怎么换／为什么这样选</summary>${p.alternatives.map(x=>'<p>'+esc(x)+'</p>').join('')}<p>${esc(p.watch)}</p></details>`+refs(p);
 el.innerHTML=text;document.getElementById('finish-state').value=state;updateAction();
}
function updateAction(){const p=current(),r=D.runes.find(x=>x.id===document.getElementById('finish-rune')?.value),g=Number(document.getElementById('finish-grade')?.value??grade),part=slot==='bow'?'weapon':'armour',effect=document.getElementById('finish-effect'),action=document.getElementById('finish-action');if(!effect||!action)return;
 if(!r){effect.innerHTML='<span>未选符文：先按这件装备要解决的缺口选择，不自动替你假设缺冰抗。</span>';}
 else if(r[part][g]===null){effect.innerHTML='<b>此等阶未核实，先不操作。</b> 选已核对的等阶或查看实际物品说明。';}
 else{effect.innerHTML=`<b>${esc(grades[g]+r.zh)} → ${esc(part==='weapon'?r.labelW:r.labelA)} ${esc(r[part][g])}</b><small>每颗效果；${g===0?'次级需求以物品说明为准':'人物等级需求 '+[0,15,30,50][g]+'（不是装备物品等级）'}。${esc(r.note)}</small>`;}
 const kind=state;let block='';
 if(kind==='bound')block='<div class="notice danger"><b>不要覆盖、移除或萃取。</b> 插槽绑定会永久占孔。需要改变方案时，另选未绑定的装备／孔，不把昂贵增幅器放上去尝试。</div>';
 else if(kind==='special')block='<div class="notice warn"><b>先停。</b> 普通未腐化装备的操作不能直接套在这件上。先看客户端与具体材料的限制；不用萃取石测试，因为会摧毁装备。</div>';
 else if(!r||r[part][g]===null)block='<p class="finish-action"><b>本步：先选目标和已核实的符文等阶。</b> 下方完整规则随时可看，不会锁住其他阶段。</p>';
 else if(kind==='unknown')block='<p class="finish-action"><b>本步：先确认装备上有没有空的增幅器孔。</b><br>下面“怎么认孔”在同一页；看不清时不要先点材料。</p>';
 else if(kind==='none')block='<p class="finish-action"><b>本次只用：巧匠石 ×1。</b><br>右键「巧匠石」→ 左键这件装备一次 → 确认多出一个空增幅器孔。<br><small>若被拒绝，先核对部位、孔数与状态；不是改用高等工匠石。确认已出现空孔后，把上面的状态改为“看见空孔”。</small></p>';
 else if(kind==='empty')block=`<p class="finish-action"><b>本次只用：${esc(grades[g]+r.zh)} ×1。</b><br>右键符文 → 左键这件装备／目标空孔一次，按客户端镶嵌提示确认。<br><small>先检查装备／人物需求，效果要读${slot==='bow'?'战斗武器':'护甲（防具）'}这一行；不要同时按住连点。</small></p><p class="finish-result"><b>装完：</b>空孔变为已镶嵌，并出现对应效果。检查顶部防御／物理或人物属性／抗性变化；仍有缺口再决定下一孔。数量不是自动必须装满。</p>`;
 else block=`<div class="notice warn"><b>这是覆盖，不返还旧的普通增幅器。</b>先确认旧增幅器不带“插槽绑定”，失去旧抗性／属性不会让全身失效。</div><p class="finish-action">确认接受旧效果消失后：右键「${esc(grades[g]+r.zh)}」→ 左键目标装备／孔位，按客户端覆盖提示操作一次。<br><small>被拒绝时停止；不要用会毁装备的萃取石代替。</small></p>`;
 action.innerHTML=block;document.getElementById('finish-live').textContent=p.name+'，'+(r?r.zh:'未选符文')+'，'+state+'；本页没有读取或改动游戏。';
}
root.addEventListener('change',e=>{if(e.target.id==='finish-stage'){stage=e.target.value;state='unknown';render();setURL();}else if(e.target.id==='finish-rune'){chosen[slot]=e.target.value;updateAction();}else if(e.target.id==='finish-grade'){grade=Number(e.target.value);updateAction();}else if(e.target.id==='finish-state'){state=e.target.value;updateAction();}});
root.addEventListener('click',e=>{const b=e.target.closest('[data-finish-slot]');if(b){slot=b.dataset.finishSlot;state='unknown';render();setURL();if(innerWidth<850)document.getElementById('work').scrollIntoView({block:'start'});}});
render();window.__FINISH_R21={data:D,state:()=>({stage,slot,state,grade}),select:(s,k)=>{if(stages.has(s)&&D.slots[k]){stage=s;slot=k;state='unknown';render();setURL();}}};
}
const cs=document.getElementById('finish-check-stage'),cd=document.getElementById('finish-check-data');if(cs&&cd){const d=JSON.parse(cd.textContent);let init=new URLSearchParams(location.search).get('stage');if(!Object.hasOwn(d,init))init='e01';function show(s){cs.value=s;document.getElementById('finish-check-list').innerHTML=d[s];document.querySelectorAll('#finish-check-list input[data-check]').forEach(x=>{try{x.checked=localStorage.getItem('poe2-r21-finish-'+x.dataset.check)==='1';}catch(_){}});try{const u=new URL(location.href);u.searchParams.set('stage',s);history.replaceState(null,'',u);}catch(_){}}
cs.addEventListener('change',()=>show(cs.value));document.getElementById('finish-check-list').addEventListener('change',e=>{const x=e.target.closest('input[data-check]');if(x){try{localStorage.setItem('poe2-r21-finish-'+x.dataset.check,x.checked?'1':'0');}catch(_){}}});show(init);}
})();
