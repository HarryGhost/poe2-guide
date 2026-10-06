(()=>{'use strict';
const data=JSON.parse(document.getElementById('local-data').textContent);const $=(s)=>document.querySelector(s);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function setMenu(on){$('#sidebar').classList.toggle('open',on);$('#menu-button').setAttribute('aria-expanded',String(on));$('#backdrop').hidden=!on;}
$('#menu-button')?.addEventListener('click',()=>setMenu(!$('#sidebar').classList.contains('open')));$('#backdrop')?.addEventListener('click',()=>setMenu(false));
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.close).close()));
document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
document.querySelectorAll('[data-image]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();$('#image-content').src=a.dataset.image;$('#image-dialog').showModal();}));
function revealHash(){const id=decodeURIComponent(location.hash.slice(1));const el=document.getElementById(id);if(el){for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;}}
window.addEventListener('hashchange',revealHash);revealHash();
// The index is a strict whitelist of the player's snapshot and the one retained target.
const index=[];const add=(title,text,url,more='')=>index.push({title,text,url,more});
for(const it of data.items){add(it.player.name,it.label+' · '+it.status,'equipment.html#'+it.id,it.player.raw_tooltip+' '+it.target.name+' '+it.target.modifiers.join(' ')+' '+it.advice);if(it.guide)for(const b of it.guide.bases)add(b.name,it.label+' · 当前构筑底材与替代','equipment.html#'+it.id,b.why+' '+it.guide.compare);}
for(const s of data.skills)add(s.name,'当前技能与作者默认连接','setup.html#skills',s.gems.map(g=>g.name).join(' '));
for(const s of data.extra_skills)add(s.name,'我的现有技能 · 与目标衔接待核对','setup.html#skills',s.gems.join(' '));
for(const j of data.jewels)add(j.name,'人物珠宝 · 作者示例，不是本轮采购目标','setup.html#jewels',j.modifiers.join(' '));
add('击杀回蓝蓝玉','普通珠宝的用途、取得与替代','setup.html#jewels','缺蓝 回蓝 蓝玉 资源');
add('左戒指抗性净变化','映射后的冷抗、闪电抗、火抗和魔力一起比较','crafting.html#ring','卡兰德之触 冷抗 电抗 生命 成品');
add('机遇与两瓶药剂','先准备手动应急回复，旧瓶保留','crafting.html#flasks','生命药剂 魔力药剂 机遇 不能手动 扣生命');
add('护盾头与防御配套','智慧、精魂、幽灵舞步和胸甲抗性一起核对','crafting.html#helmet','能盾 能量护盾 450 智慧 先祖冠冕 风舞者');
add('当前天赋参考','仅暴击混合防御，参考树不是我的完整已点树','setup.html#tree','天赋 升华 加点 洗点 94 84');
add('个人异界树未取得','只保留当前刷图边界，不选择高投入收益刷法','reference.html#atlas','异界 地图 T16 刷图');
for(const e of data.ring_essences)add(e.name,'备用戒指的可选材料 · 未选不执行','crafting.html#ring-craft',e.effect+' '+e.limit);
for(const a of data.arrows)add(a.name,a.effect,'equipment.html#quiver','卡迪罗 箭袋');
for(const f of data.filters)add(f.name,'原文件字节不改，不自动切换游戏设置','reference.html', '过滤器 原版 颜色 声音');
function search(){const q=$('#search-input').value.trim().toLowerCase();const words=q.split(/\s+/).filter(Boolean);const rs=words.length?index.filter(r=>words.every(w=>(r.title+' '+r.text+' '+r.more).toLowerCase().includes(w))):index.filter(r=>['左戒指抗性净变化','机遇与两瓶药剂','护盾头与防御配套','当前天赋参考'].includes(r.title));const unique=rs.filter((r,i,a)=>a.findIndex(x=>x.title===r.title&&x.url===r.url)===i);$('#search-results').innerHTML=unique.length?unique.slice(0,30).map(r=>`<a href="${esc(r.url)}"><b>${esc(r.title)}</b><p>${esc(r.text)}</p></a>`).join(''):'<p class="empty">当前使用版没有这项内容。这里只搜索你的现装和保留的这套攻略。</p>';}
function openSearch(){setMenu(false);$('#search-dialog').showModal();search();$('#search-input').focus();}
$('#search-button').addEventListener('click',openSearch);$('#search-input').addEventListener('input',search);$('#search-results').addEventListener('click',e=>{if(e.target.closest('a'))$('#search-dialog').close();});document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();openSearch();}});
// Local reading states only. No game connection, writes, shopping or currency actions.
function workTab(){if(!$('.work-tabs'))return;const id=location.hash.replace('#','');let v=['ring','flasks','helmet'].includes(id)?id:'ring';$('.work-tabs').querySelectorAll('a').forEach(a=>{const active=a.dataset.work===v;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});document.querySelectorAll('.work-panel').forEach(p=>p.hidden=p.id!==v);}
window.addEventListener('hashchange',workTab);workTab();
const body=(title,intro,condition,result,next='',warn='')=>`<div class="result-label">阅读步骤 · 不执行游戏操作</div><h3>${esc(title)}</h3><p>${esc(intro)}</p>${condition?`<p><b>使用前：</b>${esc(condition)}</p>`:''}${result?`<p><b>结果先验收：</b>${esc(result)}</p>`:''}${warn?`<p class="caution">${esc(warn)}</p>`:''}${next}`;
const nextBtn=(state,label)=>`<button type="button" data-ring-next="${state}">${esc(label)}</button>`;
function renderRing(){const select=$('#ring-state');if(!select)return;const st=select.value;const blue=['magic1','magic2'].includes(st);$('#purpose-wrap').hidden=!blue;const purpose=$('#ring-purpose').value;const useEss=blue&&['life','cold','lightning'].includes(purpose);$('#essence-wrap').hidden=!useEss;let h='';
 if(st==='ready')h=body('先比较候选成品，不用材料','已知需要的是左戒的冷抗、闪电抗与生命，先核对映射后的净收益。','现用品留着；候选能穿，最终火抗和魔力没有意外下降。','有净提升才能考虑更换；没有合适成品也不必为了清单去花材料。');
 else if(st==='special')h=body('停止普通戒指加工模板','暗金、腐化、镜像、未弄清的特殊状态不走这里。','','保留现用品，确认物品类别与规则后再看对应方法。','','不要把卡兰德之触或其他暗金当作普通蓝装升黄。');
 else if(st==='white')h=body('确定留底材后，蜕变石一次','白装起步只是可选路线；已有合适蓝装或黄装，不必退回白装。','已鉴定、可用的备用普通戒指，且本轮预算允许。','变成蓝装后读新增词缀：有用才继续比较；没用先停。',`<div class="result-actions">${nextBtn('magic1','已确认一词蓝装：查看下一步')}${nextBtn('ready','先不做，回成品比较')}</div>`);
 else if(blue){
  if(!purpose)h=body('先确定这一颗材料要解决什么','一词蓝装的增幅是可选项；精华和富豪是升黄前的分支，不是先后连招。','不数说明文字行，先认清显性词缀组、前后缀和当前稀有度。','没有选择用途和材料，不默认推荐使用。');
  else if(purpose==='augment'&&st==='magic2')h=body('两词蓝装不再用增幅','此项只用于普通的一词蓝装。','','改选一次升黄分支，或直接使用现有候选。','','不能因为材料菜单里有增幅就继续点。');
  else if(purpose==='augment')h=body('可选增幅石一次','保住一条有用词缀、接受另一条随机结果时，才考虑增幅。','蓝装当前只有一条显性词缀，另一侧有合法空位。','结果合用就比较使用；不合用先停，不接随机删除。',`<div class="result-actions">${nextBtn('magic2','已确认两词蓝装：重新选择下一步')}${nextBtn('ready','停止追加')}</div>`);
  else if(purpose==='regal')h=body('富豪石一次，随机升黄','选择这条后，不再接普通升黄精华。','当前仍为蓝装，已有词缀值得保留；确认物品和材料适用。',`原有词缀保留并新增一条。${st==='magic1'?'一词蓝装进入两词黄装验收。':'两词蓝装进入三词黄装验收。'}`,`<div class="result-actions">${nextBtn(st==='magic1'?'rare2':'rare3','已确认升黄：先验收')}${nextBtn('ready','先不追加')}</div>`);
  else{const mat=data.ring_essences.find(x=>x.id===$('#ring-essence').value);if(!mat)h=body('材料未选，不执行','只选择手中实际有、并适用于备用戒指的精华。','生命和抗性词缀分组、前后缀空位、成品需求都要核对。','同一件不能为补多个缺口连续使用升黄精华。','','强效身躯不适用于戒指；本表不提供该非法选项。');else h=body(mat.name+' ×1',mat.effect+'。这是网页材料数据范围，不保证最高值。','当前仍是蓝装；无同组冲突，材料允许，对应侧有合法空位。'+mat.limit,'单次升黄后先看整件是否值得使用。只定向补这一个目标，不保证其他抗性和生命都同时到位。',`<div class="result-actions">${nextBtn(st==='magic1'?'rare2':'rare3','已确认升黄：进入验收')}${nextBtn('ready','这件够用，停止追加')}</div>`,'不能在升黄后再点另一颗普通升黄精华。');}
 }
 else if(st==='rare6')h=body('六词黄装：结束普通加词缀','六条只代表通常词缀容量已满，不代表六条都好。','确认真实词缀分组，不把品质、固有和镶嵌当额外显性词缀。','先比较映射后的整套净变化，决定是否换上；旧装备保留。',`<div class="result-actions">${nextBtn('ready','回到净变化比较')}</div>`,'不自动用混沌或剥离删坏词缀，也不寻找第七条。');
 else{const n=Number(st.replace('rare',''));h=body(`黄装${n}条：先验收，不是自动补满`,'已经能解决本轮缺口就可以停；只有额外投入确实值得才考虑再补一条。','确认目标侧有合法空位、没有需预留的专用工艺；无误开的双加或定向预兆；接受随机结果与预算。',`决定继续时，普通崇高石一次，预计新增第${n+1}条；不是提高已有词缀数值。读完结果再决定下一步。`,`<div class="result-actions">${nextBtn('ready','已经够用／停止追加')}${nextBtn('rare'+(n+1),'已确认新增一条：重新验收')}</div>`,'不合用先停，不因为已有投入就自动随机删改。');}
 $('#ring-result').innerHTML=h;$('#ring-result').querySelectorAll('[data-ring-next]').forEach(b=>b.addEventListener('click',()=>{select.value=b.dataset.ringNext;$('#ring-purpose').value='';updateEssences();renderRing();}));}
function updateEssences(){if(!$('#ring-purpose'))return;const purpose=$('#ring-purpose').value;const key={life:'生命',cold:'冰霜抗性',lightning:'闪电抗性'}[purpose];const list=key?data.ring_essences.filter(x=>x.effect.includes(key)):[];$('#ring-essence').innerHTML='<option value="">未选材料，不执行</option>'+list.map(x=>`<option value="${esc(x.id)}">${esc(x.name)} · ${esc(x.effect)}</option>`).join('');}
$('#ring-state')?.addEventListener('change',()=>{$('#ring-purpose').value='';updateEssences();renderRing();});$('#ring-purpose')?.addEventListener('change',()=>{updateEssences();renderRing();});$('#ring-essence')?.addEventListener('change',renderRing);renderRing();
function helm(){if(!$('#helmet-step'))return;const step=data.helmet_recipe.find(x=>x.id===$('#helmet-step').value)||data.helmet_recipe[0];$('#helmet-result').innerHTML=`<div class="result-label">备用护盾头 · 专用条件路线</div><h3>${esc(step.title)}</h3><p><b>操作前：</b>${esc(step.before)}</p>${step.action.map(x=>`<p>${esc(x)}</p>`).join('')}<p><b>预计结果：</b>${esc(step.expect)}</p><p><b>结果合适：</b>${esc(step.good)}</p><p class="caution"><b>不符合就停：</b>${esc(step.bad)}</p>${step.note?`<p class="small muted">${esc(step.note)}</p>`:''}<div class="result-actions">${step.next&&data.helmet_recipe.some(x=>x.id===step.next)?`<button data-helm-next="${esc(step.next)}">已确认结果：看下一步</button>`:''}<button data-helm-next="finish">停止追加：看换装验收</button></div>`;$('#helmet-result').querySelectorAll('[data-helm-next]').forEach(b=>b.addEventListener('click',()=>{$('#helmet-step').value=b.dataset.helmNext;helm();}));}
$('#helmet-step')?.addEventListener('change',helm);helm();
window.GhostlinessGuide={edition:'R46',retainedBuild:'Crit Hybrid',searchIndex:index,visibleBuildCount:1};
})();
