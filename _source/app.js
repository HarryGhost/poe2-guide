'use strict';
(()=>{
const DATA=JSON.parse(document.getElementById('guide-data').textContent);
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='poe2-six-branches-v2';let stored={};try{stored=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(_e){}
if(typeof stored!=='object'||Array.isArray(stored))stored={};
const validBranch=n=>Number.isInteger(Number(n))&&Number(n)>=1&&Number(n)<=6;
const state={current:validBranch(stored.current)?Number(stored.current):1,target:[4,5].includes(Number(stored.target))?Number(stored.target):0,mode:stored.mode==='trade'?'trade':'ssf',theme:stored.theme==='dark'?'dark':'light',checks:stored.checks&&typeof stored.checks==='object'&&!Array.isArray(stored.checks)?stored.checks:{},budgets:stored.budgets&&typeof stored.budgets==='object'&&!Array.isArray(stored.budgets)?stored.budgets:{},compareFrom:1,compareTo:2};
const ALIAS={route:'upgrade',build:'gear',trap:'pitfalls',dl:'downloads',download:'downloads',faq:'start',solo:'gear',combat:'combat',skills:'skills',tree:'tree',craft:'craft',glossary:'glossary',sources:'sources',start:'start',upgrade:'upgrade',gear:'gear',pitfalls:'pitfalls',downloads:'downloads'};
const titles={start:'阶段总览',upgrade:'进阶条件与差异',skills:'技能与精魂',gear:'装备与独狼替代',tree:'天赋与武器组',combat:'实战与排障',craft:'打造与涂膏',pitfalls:'机制防坑',glossary:'中英术语',downloads:'下载当前构筑',sources:'来源与检查'};
const pages=Object.keys(titles);let activePage='start';
function save(){try{localStorage.setItem(KEY,JSON.stringify({current:state.current,target:state.target,mode:state.mode,theme:state.theme,checks:state.checks,budgets:state.budgets}))}catch(_e){}}
function branch(n=state.current){return DATA.branches.find(b=>b.number===Number(n))||DATA.branches[0]}
function gem(id){return DATA.gems[id]||{zh:id.split('/').pop(),en:id.split('/').pop(),id,url:'',note:''}}
function shortid(id){return id.split('/').pop()}
function safeUrl(url){return /^https:\/\//.test(url||'')?url:''}
function external(url,label){return safeUrl(url)?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`:esc(label)}
function source(id){return `<a class="source-link" href="#src-${esc(id)}">[${esc(id)}]</a>`}
function notify(text){const t=$('#toast');t.textContent=text;t.hidden=false;clearTimeout(notify.timer);notify.timer=setTimeout(()=>t.hidden=true,4000)}
function opt(n){const b=branch(n);return `${String(b.number).padStart(2,'0')} · ${b.profile.title}`}
function options(selected,exclude=false){return DATA.branches.filter(b=>!exclude||b.number<6).map(b=>`<option value="${b.number}" ${b.number===Number(selected)?'selected':''}>${esc(opt(b.number))}${b.number===6?'【只读】':''}</option>`).join('')}
function currentBadge(){return `<span class="badge ok">当前查看 ${String(state.current).padStart(2,'0')}</span>`}
function checked(key){return state.checks[key]?'checked':''}
function task(key,text){return `<label class="task"><input type="checkbox" data-check="${esc(key)}" ${checked(key)}><span>${esc(text)}</span></label>`}
function pluralSlots(){return {'Weapon1':'主武器Ⅰ','Weapon2':'主武器Ⅱ','Offhand1':'箭袋 / 副手Ⅰ','Offhand2':'副手Ⅱ','Helm1':'头盔','BodyArmour1':'衣服','Gloves1':'手套','Boots1':'鞋子','Amulet1':'项链','Belt1':'腰带','Ring1':'戒指Ⅰ','Ring2':'戒指Ⅱ','Flask1':'药剂栏','Charm1':'咒符栏'}}
function slotName(e){const r=e.raw||e;return (pluralSlots()[r.inventory_id]||r.inventory_id)+(['Flask1','Charm1'].includes(r.inventory_id)?` ${Number(r.slot_x||0)+1}`:'')}
function scopeLabel(s){return s==='武器组1'?'武器Ⅰ':s==='武器组2'?'武器Ⅱ':s}
function interval(a){return !a?'未填写':Array.isArray(a)?a.join('–'):String(a)}
function setTheme(){document.documentElement.dataset.theme=state.theme;$('#theme-toggle').textContent=state.theme==='light'?'深色':'浅色';$('#theme-toggle').setAttribute('aria-label',state.theme==='light'?'切换深色主题':'切换浅色主题')}
function syncGlobal(){
 $('#current-bd').innerHTML=options(state.current);$('#target-bd').value=String(state.target);$('#mode').value=state.mode;
 $('#global-note').textContent=`当前查看：${opt(state.current)} · ${state.mode==='ssf'?'独狼':'可交易'}。技能、装备、天赋、操作与下载同步；长期目标不会替换当前配置。`;
 document.title=`${String(state.current).padStart(2,'0')} ${titles[activePage]} · 锐眼冰射进阶指南`;
}
function applyDefaultComparison(){state.compareFrom=state.current<=4?state.current:state.current===5?4:5;state.compareTo=state.current<=4?state.current+1:state.current===5?5:6}
function setCurrent(n,updateHash=true){if(!validBranch(n))return;state.current=Number(n);applyDefaultComparison();['#skill-filter','#node-filter'].forEach(s=>$(s).value='');$('#skill-kind').value='all';$('#node-scope').value='all';$('#node-status').value='all';save();renderAll();if(updateHash)writeHash();notify(`全站已切换为 ${opt(n)}${Number(n)===6?'（只读核对）':''}`)}
function writeHash(anchor=activePage){const q=new URLSearchParams({bd:String(state.current)});if(state.target)q.set('target',String(state.target));q.set('mode',state.mode);try{history.replaceState(null,'',`#${anchor}?${q}`)}catch(_e){}}
function renderHome(){
 $('#roadmap').innerHTML=DATA.branches.slice(0,5).map(b=>`<button class="road-item" type="button" data-view="${b.number}" aria-pressed="${b.number===state.current}"><span class="num">${String(b.number).padStart(2,'0')}</span><strong>${['初期','非暴击中期','混合防御','转暴击','高配进阶'][b.number-1]}</strong><span>${b.profile.short}</span></button>`).join('');
 const b=branch(),p=b.profile;
 $('#current-summary').innerHTML=`<div class="panel-head"><div><div class="eyebrow">CURRENT BUILD / 当前配置</div><h2>${esc(b.label)}</h2></div><span class="badge ${b.number===6?'danger':'ok'}">${esc(p.short)}</span></div><p>${esc(p.overview)}</p><p class="small muted"><b>适合阶段：</b>${esc(p.stage)}<br><b>实战目标：</b>${esc(p.goal)}</p><div class="notice ${b.number===6?'danger':''}">${esc(state.mode==='ssf'?p.ssf:p.trade)}</div><div class="actions"><a class="btn primary" href="#skills">查看这套技能 →</a><a class="btn" href="#gear">装备先换什么</a><a class="btn" href="#downloads">${b.number===6?'原件只读':'下载对应构筑'}</a></div>`;
 $('#task-list').innerHTML=p.tasks.map((t,i)=>task(`b${b.number}-start-${i}`,t)).join('');updateTaskCount();
 const t=state.target;
 $('#target-summary').innerHTML=t===0?'<p>还没选长期目标也没关系，先把当前配置做好。</p><p><b>保留狙击：</b>研究04；<b>高配冰射承担首领输出：</b>研究05。它们是玩法目标，不是自动通过全部终局的保证。</p>':t===4?'<p><b>你的目标：04，保留狙击。</b></p><p>按条件向04准备，达到后可以继续补装备；不是必须转05。当前查看不会因选目标而跳到04。</p>':'<p><b>你的目标：05，高配冰射。</b></p><p>先建立非暴击、混合防御与暴击条件，最后才评估去掉狙击；不是一开始照最高配配装。</p>';
 if(b.number===6)$('#target-summary').insertAdjacentHTML('beforeend','<p class="notice danger">06只读，不能作为目标自动升级。</p>');
 $('#branch-cards').innerHTML=DATA.branches.map(x=>`<article class="panel stage-card ${x.number===state.current?'active':''}"><div class="stage-number">${String(x.number).padStart(2,'0')} / ${esc(x.key)}</div><h3>${esc(x.profile.title)}</h3><div class="chips"><span class="badge ${x.number===6?'danger':''}">${esc(x.profile.short)}</span></div><p class="small">${esc(x.profile.overview)}</p><p class="small muted">${esc(x.profile.stage)}</p><div class="actions"><button class="btn smallbtn ${x.number===state.current?'primary':''}" data-view="${x.number}">${x.number===state.current?'当前正在查看':x.number===6?'查看只读快照':'查看完整配置'}</button><button class="btn smallbtn" data-compare-pair="${x.number===1?'1-2':(x.number-1)+'-'+x.number}">与${x.number===1?'02':'前一份'}对比</button></div></article>`).join('');
}
function updateTaskCount(){const n=branch().profile.tasks.filter((_x,i)=>state.checks[`b${state.current}-start-${i}`]).length;$('#task-count').textContent=`已勾选 ${n} / 3`}
const roleTips={
 SkillGemIceShot:['手动攻击 · 主要输出','01–04承担冻结与清图；05转为同时承担首领主要输出。元素军械III和元素集中不能无脑移到负责冻结的主冰射。'],
 SkillGemSnipe:['手动攻击 · 冻结后爆发','完美释放、直接命中与消耗冻结分别核对。只有连接了盲点的配置，才考虑已致盲目标的条件收益。'],
 SkillGemTornadoShot:['工具攻击 · 箭矢复制','放在箭路能利用的位置。复制有伤害惩罚，持续伤害不等于击中；不要默认致盲必定触发。'],
 SkillGemIceTippedArrows:['工具技能 · 当前原件包含','01–03保留，04以后移除。原件显示区间与实际技能需求不同，先按客户端确认可用。'],
 SkillGemFreezingMark:['印记工具 · 冻结增益','印记与自身增益不是同一个计时器。虹吸印记II按物理攻击击中伤害偷取，不按总冰伤计算。'],
 SkillGemBarrage:['工具技能 · 强化下一次攻击','无狂怒球也有基础重复，能量球增加额外重复；永续充能不是产球。重复攻击有伤害惩罚。'],
 SkillGemHeraldOfIce:['常驻 · 清图','原件连接按所属分支显示。这里的元素集中不能照搬给需要冻结的主冰射。'],
 SkillGemCombatFrenzy:['常驻 · 条件产球','01/02包含，03以后原件移除。不要在没有此技能的配置里继续计算它的球源。'],
 SkillGemGhostDance:['常驻 · 护盾恢复','与混合防御配套；不能套用旧版受击固定瞬回的计算。'],
 SkillGemWindDancer:['常驻 · 防御与反击','满层与受击后的状态不同。03原件没有这组，04才加入。'],
 SkillGemManaRemnants:['常驻 · 残片资源','05/06包含。辅助与残片生成/拾取需要实际生效，不等于固定永久恢复。'],
 SkillGemMirageArcher:['元技能 · 内嵌冰射','第一个冰霜射击是主动宝石，不是辅助。触发、属性和保留在游戏里单独核对。'],
 SkillGemAscendancyMirageDeadeye:['升华元技能 · 内嵌冰射','先获得对应升华。独立于幻影射手，不要漏配第二组内嵌冰射。'],
 SkillGemWolfPounce:['06只读 · 内嵌印记','原件在巨狼猛扑内嵌冰冻印记，并涉及第二武器。升华冲突未解，不能照抄。']
};
const metaIds=new Set(['SkillGemMirageArcher','SkillGemAscendancyMirageDeadeye','SkillGemWolfPounce']);
function role(s){return roleTips[shortid(s.id)]||['原件技能','按客户端面板核对。']}
function isReserveOrMeta(s){return branch().reserveSkills.includes(s.id)||metaIds.has(shortid(s.id))}
function chainHtml(s){if(!s)return '<p class="muted">此配置没有该技能。</p>';return `<ol class="chain">${s.support_skills.map((x,i)=>{const g=gem(x.id),active=shortid(x.id).startsWith('SkillGem');return `<li data-gem-id="${esc(x.id)}"><span class="chain-num">${i+1}</span><span>${active?'<span class="badge warn">内嵌主动</span> ':''}<b>${esc(g.zh)}</b><small>${esc(g.en)} · 显示区间 ${esc(interval(x.level_interval))}</small></span></li>`}).join('')}</ol>`}
function renderSkills(){const b=branch();$('#skills-title').textContent=`${String(b.number).padStart(2,'0')} · 技能与精魂`;$('#skills-intro').textContent=b.number===6?'完整保留原始10组记录，仅作核对；不提供可导入或可用性保证。':`${b.profile.short}。以下只展示${String(b.number).padStart(2,'0')}号的10组技能与所有内嵌连接，不混入其他分支。`;
 $('#skills-status').innerHTML=`<div class="notice ${b.number===6?'danger':''}">${esc(b.profile.note)}<br><span class="small">来源：上传的 ${esc(b.sourceFile)}。列表顺序保留；显示区间不等于技能等级或解锁保证。</span></div>`;
 const q=$('#skill-filter').value.trim().toLowerCase(),kind=$('#skill-kind').value;
 const list=b.raw.skills.filter(s=>{const all=[s,...s.support_skills].map(x=>x.id+' '+gem(x.id).zh+' '+gem(x.id).en).join(' ').toLowerCase();return (!q||q.split(/\s+/).every(t=>all.includes(t)))&&(kind==='all'||(kind==='reserve')===isReserveOrMeta(s))});
 $('#skill-count').textContent=`显示 ${list.length} / ${b.raw.skills.length} 组；原件共 ${b.raw.skills.reduce((a,s)=>a+s.support_skills.length,0)} 条内嵌技能/辅助记录。`;
 $('#skill-cards').innerHTML=list.map(s=>{const g=gem(s.id),r=role(s);return `<article class="skill-card" data-skill-id="${esc(s.id)}"><div class="skill-top"><div><h3>${esc(g.zh)}</h3><small class="muted">${esc(g.en)}</small></div><button class="btn smallbtn" type="button" data-copy="${esc(s.id)}">复制连接</button></div><div class="role">${esc(r[0])}</div>${chainHtml(s)}<p class="small muted" style="margin-top:12px">${esc(r[1])}</p><div class="skill-id">${esc(s.id)}</div><div class="source-note">原件角色显示区间：${esc(interval(s.level_interval))} · ${external(g.url,'名称与机制来源')}</div></article>`}).join('')||'<div class="empty">当前分支没有匹配。清除关键词，或在“中英术语”中查询其他分支。</div>';
 $('#skill-priorities').innerHTML=b.snipe?`<h3>孔位与品质先后 · 当前包含狙击</h3><div class="grid-2"><div><b>辅助孔升级</b><p>狙击 → 冰霜射击 → 寒冰之捷 → 冰冻印记。</p></div><div><b>品质升级</b><p>冰冻印记 → 寒冰之捷 → 狙击 → 冰霜射击。</p></div></div><p class="small muted">作者正文优先级 ${source('S1')}。缺孔通常从连接末端减少，但不能忽视技能职责：删冻结后冻不住，就要调整取舍；这是自己的过渡改动，不是原件等效配置。</p>`:`<h3>${b.number===6?'只读配置，不提供升级承诺':'当前05没有狙击，不再要求给狙击升孔'}</h3><p>先保证当前主冰射及资源链能工作；魔力残片与特殊辅助缺失时，不默认普通替换能得到同样输出和恢复。</p><p class="small muted">原作者通用优先级包含狙击，不能原封不动套到无狙击分支。本段是按所选配置整理的投入建议，不伪称作者为05/06单独给了新优先级。</p>`;
}
function budget(){let d=state.budgets[state.current];if(!d||typeof d!=='object'||Array.isArray(d))d=state.budgets[state.current]={total:'',other:'0',items:{}};if(!d.items||typeof d.items!=='object')d.items={};return d}
function renderSpirit(){const b=branch(),v=budget();$('#reserve-rows').innerHTML=b.reserveSkills.map(id=>{const k=shortid(id),x=v.items[k]||{on:true,value:''};return `<div class="reserve-row"><input type="checkbox" id="reserve-on-${k}" data-reserve-on="${k}" aria-label="启用${esc(gem(id).zh)}预算" ${x.on?'checked':''}><label for="reserve-value-${k}">${esc(gem(id).zh)}<small class="muted" style="display:block">${esc(gem(id).en)}</small></label><input id="reserve-value-${k}" data-reserve-value="${k}" type="number" min="0" max="99999" placeholder="实际保留" value="${esc(x.value)}"></div>`}).join('');$('#spirit-total').value=v.total??'';$('#spirit-other').value=v.other??'0';calcSpirit()}
function storeBudget(){const v=budget();v.total=$('#spirit-total').value;v.other=$('#spirit-other').value;$$('[data-reserve-value]').forEach(x=>{const k=x.dataset.reserveValue;v.items[k]={on:$(`#reserve-on-${k}`).checked,value:x.value}});save();calcSpirit()}
function calcSpirit(){const v=budget(),out=$('#spirit-result');const integer=x=>/^\d+$/.test(String(x))&&Number(x)<=99999;
 const items=branch().reserveSkills.map(id=>{const k=shortid(id);return {name:gem(id).zh,on:$(`#reserve-on-${k}`)?.checked,value:$(`#reserve-value-${k}`)?.value}}).filter(x=>x.on);
 const missing=items.filter(x=>!integer(x.value)).map(x=>x.name);if(!integer($('#spirit-total').value))missing.unshift('精魂总量');if(!integer($('#spirit-other').value))missing.push('其他保留');
 if(missing.length){out.textContent='尚不能计算：请填写0–99999的整数面板值。待填或无效项：'+missing.join('、')+'。';out.dataset.status='incomplete';return}
 const total=items.reduce((n,x)=>n+Number(x.value),0)+Number($('#spirit-other').value),available=Number($('#spirit-total').value),delta=available-total;
 out.innerHTML=`当前${String(state.current).padStart(2,'0')}号：录入保留合计 <b>${total}</b>，精魂总量 <b>${available}</b>。<br>${delta>=0?`按录入数字剩余 <b>${delta}</b>`:`按录入数字还缺 <b>${-delta}</b>`}。这只是算术核对，不代表游戏已经正确激活。`;out.dataset.status=delta>=0?'enough':'short';
}
const uniqueInfo={
 "Cadiro's Gambit":['特殊箭机制','原件使用，不是所有冰射配置的启动件。','黄箭袋：有效物理/冰点伤、弓伤害；暴击分支再补暴击/暴伤。失去特殊箭效果，不等强。'],
 "Lavianga's Spirits":['魔力药剂的持续效果','不能当成无限免费施法；实际恢复需负担技能消耗。','普通/魔法魔力药剂加可维持恢复；无小怪目标单独测，不用击杀回蓝充数。'],
 'Nascent Hope':['自身冻结时的咒符与护盾充能收益','额外护盾机制不随普通替代品保留。','普通/魔法融冰咒符解决冻结，另找实际护盾恢复方案。'],
 'The Fall of the Axe':['受减速触发及猛攻等收益','触发期间不等于永久常驻猛攻。','普通/魔法真银咒符应对减速；额外猛攻不等效。'],
 'Headhunter':['击杀稀有怪后获得增益','没有可击杀稀有怪的首领战不能默认享有偷取词缀。','生命、力量、抗性黄腰带。保留基础功能，不能复制清图增益。'],
 'Rite of Passage':['原件选用的特殊咒符','本包未核实全部国服效果与获取机制，不把它列为通关前提。','按实际异常风险使用普通/魔法功能咒符；非等效替代。'],
 "Hysseg's Claw":['06第二武器与变形链路相关','06有升华冲突，不把此武器加入01–05的必需清单。','不迁移06第二武器链路；继续原先能工作的配置。']
};
function gearAdvice(e){const id=e.raw.inventory_id,n=state.current,crit=n>=4,hybrid=n>=3,u=e.raw.unique_name;
 if(u){const a=uniqueInfo[u]||['原件暗金','机制尚未完整核实。','保留实际可工作的同部位功能。'];return {need:'原件使用；不是已证明的唯一解',target:a[0]+'。'+a[1],replace:a[2],ssf:'国服0.5.5确切掉落池未确认，不能安排成按时必得；用列出的替代方向继续推进。',trade:'按完整词条与整套缺口评估，不只按同名购买；特殊效果必须实际生效。'}}
 const map={
 Weapon1:{need:'必须有有效伤害弓；不绑定指定底材',target:crit?'武器伤害与本地暴击基础同时合格，再考虑投射物等级和暴伤。':'先看完整物理/元素伤害和攻速，不为了+等级放弃伤害底座。',replace:crit?'本地物理点伤、物理提高、冰点伤、本地暴击率；有余力再兼顾等级。':'本地物理点伤＋物理提高，兼顾冰点伤、可用攻速。',ssf:'掉落或备用底材打造；先有伤害升级再追高阶组合。',trade:'比较完整伤害、攻速、暴击与装备需求，不只搜+2/+3。'},
 Offhand1:{need:'黄箭袋可作为本阶段目标',target:crit?'支持暴击路线，不能只提升纸面暴伤。':'数条有效点伤、弓伤害、速度即可先用。',replace:crit?'物理/冰攻击点伤、弓伤害、暴击/暴伤；速度词条按实际天赋利用。':'物理/冰攻击点伤、弓伤害、攻击速度；投射物速度按实际天赋利用。',ssf:'先用多条有效词条的黄箭袋，不等待卡迪罗。',trade:'按现有弓与天赋比较综合收益。'},
 Helm1:{need:hybrid?'混合防御的重要装备，不绑定底材':'生命/闪避过渡装备',target:hybrid?'高物品护盾配合诡计面纱与恢复；作者约450物品ES建议不是角色总盾。':'优先生命、抗性和可用防御，不提前替换成不足以支撑的护盾头。',replace:hybrid?'本地护盾点数＋护盾提高、所需抗性/智慧；看最终物品护盾。':'生命、抗性、闪避；稀有度只在输出防御不缺时再考虑。',ssf:hybrid?'头与防具、恢复一起准备，未齐继续上一阶段。':'用实际掉落补基础缺口。',trade:'不要只看词条百分比；比较最终物品防御。'},
 BodyArmour1:{need:'承担主体防御，不绑定暗金',target:'高最终物品闪避，生命/抗性及其他实际防御缺口。',replace:'闪避点数＋闪避提高，按实际需要兼顾生命、抗性、偏转。',ssf:'先保有效基础防御，不为一条展示词缀重做全部装备。',trade:'按品质与处理后的最终物品闪避评估，不能只看“提高140%”。'},
 Gloves1:{need:'黄装可用，不要求Live的特殊词条',target:crit?'点伤与适用暴伤/攻速，保留生命与缺失抗性。':'点伤、攻速、生命与缺失抗性。',replace:'攻击物理/冰点伤、生命、抗性；额外输出按当前体系补。',ssf:'不等待+2投射物手套。词缀生成机制未核实，不给必成配方。',trade:'按当前分支购买，不能拿06展示替代每阶段的门槛。'},
 Boots1:{need:'移动与防御功能重要，黄装可用',target:hybrid?'合适闪避/护盾、移动速度及抗性/偏转等需要。':'移动速度、生命与抗性。',replace:'实际可用移速和防御；35%是原件展示，不是初期硬门槛。',ssf:'有可用移速就先用，不等指定暗金鞋。',trade:'先补跑图和生存，再追最高移动速度。'},
 Amulet1:{need:'资源缺口重要，不绑定暗金',target:'所需属性与精魂优先，再兼顾投射物技能等级；涂膏另行核对。',replace:'实际需要的精魂、属性/抗性；投射物等级有价值，但不要求原展示同时满值。',ssf:'等级与精魂不能兼得时先保证整体工作；可暂不开非必要常驻。',trade:'以装好辅助后的保留预算购买，不把+30/+47当所有配置通用数字。'},
 Belt1:{need:'黄腰带可承担长期基础防御',target:'生命、力量与抗性，其他按整套需求补。',replace:'生命、力量、元素/混沌抗性。',ssf:'默认用黄腰带推进，不围绕猎首掉落排时间。',trade:'不用为了原作者后期腰带跳过基础缺口。'},
 Ring1:{need:'黄戒指分担抗性、属性和点伤',target:'先补防御与资源缺口，再追原件点伤。',replace:'生命、元素/混沌抗性、所需属性；有效攻击点伤。',ssf:'一枚偏防御一枚偏输出也可。击杀回蓝不保证无小怪首领续航。',trade:'05展示闪电点伤不意味着可以忽略整套生命与抗性。'},
 Ring2:{need:'与另一枚戒指共同补缺口',target:'不要求两枚同时完美，先让整套正常工作。',replace:'生命、元素/混沌抗性、所需属性，再补攻击点伤。',ssf:'使用能解决当前缺口的掉落。',trade:'换戒指后重查属性、抗性与技能可用性。'},
 Flask1:{need:'必须有可靠回复；普通/魔法功能也可',target:'实际生命/魔力恢复、即时恢复或充能供给按需要选择。',replace:'同类型普通/魔法药剂与可维持充能、恢复词条；不是黄装打造。',ssf:'靠掉落与基础通货改善；不等功能暗金。',trade:'先比较恢复与使用条件，不把暗金直接视为更强。'},
 Charm1:{need:'按异常风险选功能，不必暗金',target:'应对冻结、减速、点燃等实际问题。',replace:'同功能普通/魔法咒符；优先功能，再追持续时间/充能词条。',ssf:'优先使用已得到且可触发的咒符。',trade:'核对实际咒符槽和触发风险，不能默认全部效果常驻。'}
 };return map[id]||{need:'原件记录',target:'完整机制尚需核对。',replace:'不提供未经核实的等效替代。',ssf:'保留当前有效配置。',trade:'购买前核实整套可用性。'};
}
function renderGear(){const b=branch();$('#gear-title').textContent=`${String(b.number).padStart(2,'0')} · 装备与获取路径`;
 $('#gear-advice').innerHTML=`<div class="notice ${b.number===6?'danger':''}">${esc(state.mode==='ssf'?b.profile.ssf:b.profile.trade)}<br><span class="small">作者要求火/冰/电抗性先到75%；上限和战斗减益改变时按当前面板核对。混抗逐步补，不硬写通关线。${source('S1')}</span></div>`;
 const crit=b.number>=4,hybrid=b.number>=3;
 $('#gear-ladder').innerHTML=`<ol><li><b>先补断链项：</b>移动、属性、抗性与生命/魔力回复；输出再高也不能靠失效技能工作。</li><li><b>弓＋箭袋：</b>${crit?'伤害与本地暴击同时合格；卡迪罗不是每套都必须有。':'先有效伤害，不提前用暴击天赋代替好武器。'}</li><li><b>头＋衣服＋恢复：</b>${hybrid?'按当前混合防御准备，头盔物品护盾、主体闪避与恢复一起看。':'保持生命/闪避；高护盾头是后续转型准备，不是现在必须替换。'}</li><li><b>首饰、手套、鞋、药剂与珠宝：</b>解决精魂/属性/供蓝，再增加有效伤害。符文与涂膏不抢在基础缺口之前。</li><li><b>特殊辅助与暗金：</b>${b.number>=5?'当前高配使用的特殊辅助必须单独核对；不能用普通替代仍宣称同样05。':'有价值再追，不等指定稀有掉落才开始刷图。'}</li></ol><p class="source-note">以上为按当前分支整理的投入顺序，不是打造成功率或最低通关数值线。</p>`;
 const uniques=b.equipment.filter(e=>e.raw.unique_name);
 $('#unique-list').innerHTML=`<div class="panel"><h3>当前原件使用 ${uniques.length} 件暗金</h3>${uniques.length?'<p class="small muted">“原件用了”不等于基本玩法唯一解。替代方案保功能，不承诺相同强度。</p><div class="table-wrap"><table class="wide-table"><thead><tr><th>部位 / 暗金</th><th>必需性与作用边界</th><th>可替代词条 / 方案</th><th>独狼获取可行性</th></tr></thead><tbody>'+uniques.map(e=>{const a=gearAdvice(e);return `<tr><td>${esc(slotName(e))}<br><b>${esc(e.zh)}</b><br><small>${esc(e.en)}</small></td><td>${esc(a.need)}<br>${esc(a.target)}</td><td>${esc(a.replace)}</td><td>${esc(a.ssf)}<br>${external(e.url,'物品资料')}</td></tr>`}).join('')+'</tbody></table></div>':'<p>01原始配置没有指定暗金。先做能工作的黄装和普通/魔法药剂，不把04/05暗金清单搬过来。</p>'}${b.specialSupports.length?`<div class="notice warn"><b>这份配置额外列出的高配辅助：</b>${b.specialSupports.map(id=>esc(gem(id).zh)).join('、')}。没有它们时，不假定普通辅助完全等效；需要重新检查技能与天赋收益。</div>`:''}</div>`;
 $('#gear-records').innerHTML=b.equipment.map((e,i)=>{const a=gearAdvice(e);return `<article class="gear-card" data-gear-index="${i}"><div class="gear-label">${esc(slotName(e))} · ${e.raw.unique_name?'原件暗金':'原件目标'}</div><h3>${esc(e.zh)}</h3><small class="muted">${esc(e.en)}</small><p class="gear-text" style="margin-top:13px">${esc(e.translation.split('\n').slice(1).join('\n')||(e.raw.unique_name?'原文件只填写暗金名称，没有实际roll或完整词条。':'原文件仅填写底材，没有导出词条。'))}</p><div class="note-grid"><div class="note-box"><b>必须性 / 当前目标</b>${esc(a.need)}<br>${esc(a.target)}</div><div class="note-box"><b>可替代词条</b>${esc(a.replace)}</div></div><p class="notice" style="font-size:12px">${state.mode==='ssf'?'独狼：':'可交易：'}${esc(state.mode==='ssf'?a.ssf:a.trade)}</p><details><summary>查看未改动的英文记录</summary><div class="detail-body"><pre>${esc(e.raw.additional_text||e.raw.unique_name||'未填写')}</pre></div></details><div class="source-note">角色显示区间 ${esc(interval(e.raw.level_interval))}；非物品等级或通关门槛。${external(e.url,'简体名称来源')}</div></article>`}).join('');
 $('#jewel-guide').innerHTML=`<h3>珠宝：有槽位，不等于有实装词条</h3><p>六份原件没有导出珠宝实装、种子与完整词条。先使用对当前${crit?'暴击':'非暴击'}配置有效的普通珠宝，兼顾实际恢复和防御缺口。</p><p>作者提到泉井之心、抗衡黑暗作为后续提升，但同名不等于同词条。没有目标珠宝时，不额外绕路去计算尚未拥有的加成。${source('S1')}</p>`;
}
function renderTree(){const b=branch();$('#tree-title').textContent=`${String(b.number).padStart(2,'0')} · 天赋与武器组`;
 $('#tree-warning').innerHTML=b.number===6?'<div class="notice danger"><b>升华冲突：</b>文件头Ranger1，10条升华节点为Ranger3系列。原样保留，只读。不能擅自改头部就当作修复。</div>':'<div class="notice warn">这里是完整节点清单，不是已经验证的逐级连线图。请用原始ID核对游戏显示；待核对中文只是提示，不能当作国服正式名。</div>';
 $('#tree-overview').innerHTML=Object.entries(b.counts).map(([s,v])=>`<div class="stat"><b>${v.rows}</b><span>${scopeLabel(s)}记录 / ${v.distinct}种ID</span></div>`).join('');
 $('#ascendancy-guide').innerHTML=b.number===6?'<h3>不能提供正常锐眼升华顺序</h3><p>06头部职业与节点系列不一致；此处不展示01–05的锐眼顺序，避免误导。</p><p class="small muted">请在下方“升华”范围查看实际冲突记录。</p>':`<h3>锐眼升华核对</h3><p><b>投射物近距离专精：零点射击 → 无限弹药 → 聚风 → 蜃影神射。</b></p><p class="small muted">选择ID为<code>AscendancyRanger1Notable2_2</code>，不是Far Shot；主动狙击与升华同中文名不是同一对象。作者正文顺序 ${source('S1')}。</p>`;
 $('#weapon-guide').innerHTML=`<h3>当前武器组安排</h3><p>${esc(b.profile.weapon)}</p><p class="small muted">按实际技能面板验证绑定、共享武器行为和属性；元技能内槽另行核对，不把未实测菜单当操作截图。</p>`;
 const q=$('#node-filter').value.trim().toLowerCase(),scope=$('#node-scope').value,status=$('#node-status').value;
 const rows=b.nodes.filter(n=>(scope==='all'||n.scope===scope)&&(status==='all'||(status==='sourced')===n.status.includes('有来源'))&&(!q||(n.zh+' '+n.id).toLowerCase().includes(q)));
 $('#node-count').textContent=`显示 ${rows.length} / ${b.nodes.length} 条记录；有简体来源的记录 ${b.namedCount} 条，待核对映射 ${b.nodes.length-b.namedCount} 条。不是实际花点数。`;
 $('#node-table').innerHTML=rows.map(n=>`<tr data-node-id="${esc(n.id)}"><td>${n.row}</td><td>${scopeLabel(n.scope)}</td><td>${esc(n.zh)}</td><td><code>${esc(n.id)}</code></td><td><span class="badge ${n.status.includes('有来源')?'ok':'warn'}">${esc(n.status)}</span>${n.url?'<br>'+external(n.url,'名称依据'):''}</td></tr>`).join('')||'<tr><td colspan="5">没有匹配节点。清除筛选后查看全部。</td></tr>';
 const dup=Object.entries(b.counts).flatMap(([s,x])=>Object.entries(x.duplicates).map(([id,n])=>`${scopeLabel(s)}：${id} ×${n}`));
 const overlaps=Object.entries(b.overlaps||{}).filter(([_s,ids])=>Array.isArray(ids)?ids.length:!!ids).map(([s,ids])=>`${scopeLabel(s)}：${Array.isArray(ids)?ids.join('、'):JSON.stringify(ids)}`);
 $('#tree-audit').innerHTML=`<details><summary>当前原件的重复与跨组记录</summary><div class="detail-body"><p><b>同组重复：</b>${esc(dup.join('；')||'未发现')}</p><p><b>公共与专精交叉：</b>${esc(overlaps.join('；')||'未发现')}</p><p class="small muted">保留原值，不自行删点。重复可能与导出或客户端解释有关，未据此判定整棵树非法，也未自动算出所需等级。</p></div></details>`;
}
function nodePill(id){const n=DATA.nodeNames[id]||{zh:'名称未确认',status:'未核对'};return `<span class="node-pill">${esc(n.zh)}<code>${esc(id)}</code><small>${esc(n.status)}</small></span>`}
function renderUpgrade(){const b=branch();$('#upgrade-gate').innerHTML=`<div class="panel"><div class="panel-head"><h2>${b.number<=4?`${String(b.number).padStart(2,'0')} → ${String(b.number+1).padStart(2,'0')}：先满足什么`:'当前没有必须进入的下一阶段'}</h2>${currentBadge()}</div><p>${esc(b.profile.nextNote)}</p><div class="task-list">${b.profile.gate.map((x,i)=>task(`b${b.number}-gate-${i}`,x)).join('')}</div><div class="notice warn"><b>条件不足：</b>${esc(b.profile.cannot)}</div>${state.target===4&&b.number===4?'<p class="notice">你选择的长期目标是保留狙击。已经在04时，不要求继续向05转型。</p>':''}<p class="source-note">勾选仅辅助准备，不会自动换BD。条件由原件差异与作者方向整理；没有伪造角色等级或洗点数。</p></div>`;
 $('#compare-from').innerHTML=options(state.compareFrom);$('#compare-to').innerHTML=options(state.compareTo);
 $('#compare-presets').innerHTML=['1-2','2-3','3-4','4-5','5-6'].map(pair=>`<button class="btn smallbtn" data-compare-pair="${pair}">${pair.replace('-',' → ')}${pair==='5-6'?'（只读对比）':''}</button>`).join('');renderDiff();
}
function renderDiff(){const a=branch(state.compareFrom),b=branch(state.compareTo),root=$('#diff-content');if(a.number===b.number){root.innerHTML='<div class="notice">两边是同一份文件。请选择不同分支；相同配置没有差异。</div>';return}
 const d=DATA.diffs[`${a.number}-${b.number}`],bad=a.number===6||b.number===6;
 let html=`<div class="diff-header"><h2 style="margin:0">${String(a.number).padStart(2,'0')} → ${String(b.number).padStart(2,'0')} 完整差异</h2><span class="badge ${bad?'danger':''}">${bad?'仅比较证据，不是升级建议':d.isProgression?'进阶方向对比':'反向差异 / 非推荐路线'}</span></div>`;
 html+=`<div class="notice ${bad?'danger':''}">${bad?'涉及06的对比不能作为锐眼转型步骤；升华字段冲突未解决。':'先把目标装备与资源准备好，再核对技能和天赋。比较数据来自上传的两份原件。'}<br><span class="small">${esc(a.label)} → ${esc(b.label)}</span></div>`;
 html+=`<div class="stat-row"><div class="stat"><b>${d.skills.length}</b><span>发生变化的技能组</span></div><div class="stat"><b>${d.equipment.length}</b><span>变化的装备记录</span></div><div class="stat"><b>${Object.values(d.nodes).reduce((n,v)=>n+v.removed.length,0)}</b><span>分组移出ID（非洗点数）</span></div><div class="stat"><b>${Object.values(d.nodes).reduce((n,v)=>n+v.added.length,0)}</b><span>分组移入ID（非花点数）</span></div></div>`;
 html+='<h3 class="section-heading">1 / 技能变化：新增、移除、辅助与顺序</h3>';
 html+=d.skills.map(s=>`<details ${s.kind!=='连接/显示区间调整'?'open':''}><summary>${esc(gem(s.id).zh)} · ${esc(s.kind)}${s.orderOnly?'（辅助集合相同，顺序变化）':''}</summary><div class="detail-body"><div class="diff-cols"><div><div class="label">${String(a.number).padStart(2,'0')} 原配置</div>${chainHtml(s.before)}${s.before?'<p class="small muted">显示区间 '+interval(s.before.level_interval)+'</p>':''}</div><div><div class="label">${String(b.number).padStart(2,'0')} 目标配置</div>${chainHtml(s.after)}${s.after?'<p class="small muted">显示区间 '+interval(s.after.level_interval)+'</p>':''}</div></div><p class="small" style="margin-top:12px"><span class="removed">移除：${esc(s.removed.map(id=>gem(id).zh).join('、')||'无')}</span><br><span class="added">新增：${esc(s.added.map(id=>gem(id).zh).join('、')||'无')}</span></p><code>${esc(s.id)}</code></div></details>`).join('')||'<p>技能组无变化。</p>';
 html+='<h3 class="section-heading">2 / 装备变化：对应同一栏位，不遗漏数值</h3>';
 html+=d.equipment.map(x=>`<details><summary>${esc(slotName(x.after||x.before))} · ${esc((x.before||{}).zh||'无')} → ${esc((x.after||{}).zh||'无')}</summary><div class="detail-body"><div class="diff-cols"><div><div class="label">${String(a.number).padStart(2,'0')} 原配置</div><pre>${esc(x.before?.translation||'未列此栏位')}</pre><p class="small muted">显示区间：${interval(x.before?.raw.level_interval)}</p></div><div><div class="label">${String(b.number).padStart(2,'0')} 目标配置</div><pre>${esc(x.after?.translation||'未列此栏位')}</pre><p class="small muted">显示区间：${interval(x.after?.raw.level_interval)}</p></div></div></div></details>`).join('')||'<p>装备记录无变化。</p>';
 html+='<h3 class="section-heading">3 / 天赋变化：分组集合对比</h3><p class="small muted">移组会同时出现一侧移出、一侧移入；重复行不自动修复。以下不是准确洗点费用，也不证明按列表顺序能合法连线。</p>';
 for(const [scope,v]of Object.entries(d.nodes)){html+=`<details><summary>${scopeLabel(scope)}：移出 ${v.removed.length} / 移入 ${v.added.length} / 相同 ${v.unchanged}</summary><div class="detail-body"><div class="diff-cols"><div><b class="removed">移出</b><div class="node-pills">${v.removed.map(nodePill).join('')||'<span class="small muted">无</span>'}</div></div><div><b class="added">移入</b><div class="node-pills">${v.added.map(nodePill).join('')||'<span class="small muted">无</span>'}</div></div></div></div></details>`}
 html+=`<div class="actions"><button class="btn ${b.number===6?'':'primary'}" data-view="${b.number}">仅切换网页查阅到 ${String(b.number).padStart(2,'0')}${b.number===6?'（只读）':''}</button><a class="btn" href="数据/全部分支逐项差异.json" download>下载完整差异数据</a></div>`;root.innerHTML=html;
}
const troubleshoot=[
 ['冰射冻不住','先看主冰射是否误用了禁止异常的辅助，再检查命中、武器伤害与冻结条件。普通怪能冻住，不意味着相同速度能冻住终局首领。','S5'],
 ['狙击伤害忽高忽低','01–04先查完美释放、直接命中、目标冻结与弹幕是否被其他攻击消耗。只有实际配置了盲点时再检查致盲；05/06没有狙击，不适用这项。','S6'],
 ['刷图不缺蓝，首领断蓝','把击杀回蓝从无小怪战斗预算中剔除，检查药剂、技能消耗、印记存在时间及物理击中偷取。不能按全部冰伤算虹吸印记II。','S10'],
 ['有护盾却经常死','先查生命、元素与混沌抗性、受击后的闪避/偏转及恢复；再查地面持续伤害和异常。不是只有护盾头就完成防御转型。','S26'],
 ['换武器组后技能不见了','检查该组武器、属性和技能绑定是否符合条件；不要先整树洗点，也不要以空副手作为万能修复。','S3'],
 ['高配辅助买了，伤害反而差','特殊辅助可能改变暴击或抗性结算；资源链也可能没工作。必须比较整套配置，不把单颗辅助在05的收益直接搬进04。','S29']
];
function detailList(list){return list.map(([q,a,s])=>`<details><summary>${esc(q)}</summary><div class="detail-body"><p>${esc(a)} ${s?source(s):''}</p></div></details>`).join('')}
function renderCombat(){const b=branch();$('#combat-title').textContent=`${String(b.number).padStart(2,'0')} · ${b.snipe?'冻结后的狙击爆发':b.number===5?'以冰射承担首领输出':'只读结构核对'}`;
 $('#combat-guide').innerHTML=`<div class="panel-head"><h2 style="margin:0">${esc(b.profile.short)}</h2>${currentBadge()}</div>${b.profile.combat.map(([title,text],i)=>`<div class="step"><span class="step-no">${i+1}</span><div><h4>${esc(title)}</h4><p>${esc(text)}</p></div></div>`).join('')}<p class="source-note">操作为根据原件与机制整理；05/06没有虚构作者实测循环。具体重复冰爆继承未证实，不计算“重复次数×最高单发”。${source('S1')}${source('S6')}${source('S7')}</p>`;
 const combatFrenzy=b.raw.skills.some(s=>shortid(s.id)==='SkillGemCombatFrenzy');
 $('#combat-notes').innerHTML=`<div class="grid-2"><div class="panel"><h3>${combatFrenzy?'当前有战斗狂怒':'当前没有战斗狂怒'}</h3><p>${combatFrenzy?'只在满足该技能触发条件后计算狂怒球收益。':'不能借用01/02的战斗狂怒产球；永续充能与充能印记都不能凭空产球。'}弹幕无球仍有基础额外重复2次；重复伤害有惩罚，不能直接乘满额伤害。${source('S7')}${source('S35')}</p></div><div class="panel"><h3>印记偷取，不等于全部冰伤回蓝</h3><p>虹吸印记II按物理攻击击中伤害偷取。已转换为元素的伤害不能仍当作物理。印记消耗、药剂实际恢复和技能费用必须一起验收。${source('S10')}</p></div></div>${b.number===6?'<div class="notice danger">06连独立印记的位置都发生改变，并有升华冲突。本页仅解释原件结构，不能当游戏操作教程。</div>':''}`;
 const checks=b.number===6?['保留原件，未擅自改职业或删除冲突节点。','没有把06放入游戏当作已审核锐眼构筑。']:['能命中并稳定处理当前目标的冻结/输出条件。',b.snipe?'能稳定完成弹幕＋完美释放狙击。':'不依赖狙击时，冰射仍能处理当前目标。','没有击杀补给时，能维持实际完整循环。','受击后的防御与恢复仍在工作，死亡原因可以追踪。'];
 $('#combat-checks').innerHTML=checks.map((x,i)=>task(`b${b.number}-combat-${i}`,x)).join('');$('#troubleshoot').innerHTML=detailList(troubleshoot);
}
const pitfalls=[
 ['技能等级不是伤害底座','冰射/狙击是武器攻击。本地物理点伤、物理提高、元素点伤、攻速与适用暴击都要一起看；+技能等级不能替代低伤害弓。','S5'],
 ['命中、暴击率、暴击伤害分开检查','攻击没命中就没有这次伤害。完美释放不是必定暴击，“命定绝杀”的提高值也不是最终100%暴击率。','S6'],
 ['元素军械II不能无脑换III','III会阻止被辅助技能造成元素异常；负责冻结的主冰射不能这样换。寒冰之捷的元素集中也不是主冰射的通用辅助。','S19'],
 ['印记与自身增益不是永久','印记有激活、消耗和持续时间。永恒印记只保护第一次激活，不等于永不消耗；充能印记不是狂怒球来源。','S11'],
 ['弹幕重复与狙击强化不能简单相乘','弹幕有重复伤害惩罚。狙击会消耗冻结；每次重复如何继承强化冰爆未完成同版本验证，不写虚假倍率。','S7'],
 ['混合防御不是堆一点护盾','头盔物品护盾、相应天赋、主体闪避、实际恢复、生命与抗性共同工作。幽灵舞步用当前规则，不抄旧瞬回公式。','S14'],
 ['抗性穿透与抗性反转不能混算','普通穿透默认有0抗下限，特殊机制另论。05使用拉其塔之流；减抗与穿透不能各自取最大收益再与反转无条件相加。','S29'],
 ['T15/T16不等于全部终局','地图阶级与具体终局首领难度应分开。作者网页的总体强度描述不能替每个静态分支和独狼替代方案作保证。',''],
 ['编号、原行号与角色等级不同','01–06是配置编号，天赋行号是导出记录顺序，31–100等是显示区间。三者都不能直接当成逐级分配路径。','S3'],
 ['05不是必须进入，06不是第五阶段的升级包','想保留狙击可以以04为目标；高配去狙击要另测单体。06头部与节点冲突，不应称为正常锐眼最高配。','S27']
];
function renderCraft(){$('#craft-current').innerHTML=`<div class="notice ${state.current===6?'danger':''}"><b>当前${String(state.current).padStart(2,'0')}号：</b>${state.current<=3?'优先非暴击伤害与防御升级；准备04时才同时准备暴击武器组合。':state.current<=5?'当前已是暴击方向，不应只照非暴击精华路线而忽略本地暴击基础。':'06只读；不根据未核实的特殊词条制造配方。'} ${esc(state.mode==='ssf'?'独狼优先备用底材与预算上限。':'交易时先比较买成品和自制的实际成本。')}</div>`}
const glossaryEntries=[...Object.values(DATA.gems).map(g=>({...g,type:'gem'})),...Object.entries(DATA.gearNames).map(([en,g])=>({...g,en:g.en||en,type:'gear'})),...Object.values(DATA.nodeNames).map(g=>({...g,type:'node'})),...(DATA.extraTerms||[]).map(g=>({...g,type:'extra'}))];
function renderGlossary(){const q=$('#glossary-filter').value.trim().toLowerCase(),kind=$('#glossary-kind').value;const list=glossaryEntries.filter(g=>(kind==='all'||g.type===kind)&&(!q||(g.zh+' '+(g.en||'')+' '+(g.id||'')).toLowerCase().includes(q)));$('#glossary-count').textContent=`显示 ${list.length} / ${glossaryEntries.length} 项，当前筛选不会改动源数据。`;$('#glossary-list').innerHTML=list.length?`<div class="table-wrap"><table class="wide-table"><thead><tr><th>中文映射</th><th>英文 / ID</th><th>状态与说明</th></tr></thead><tbody>${list.map(g=>`<tr><td><b>${esc(g.zh)}</b><br><span class="badge">${{gem:'技能/辅助',gear:'装备',node:'天赋',extra:'练级补充'}[g.type]}</span></td><td>${esc(g.en||'英文现名未收录')}<br><code>${esc(g.id||'')}</code></td><td>${esc(g.status||(g.url?'简体资料对照；未全量国服客户端核验':'来源待核对'))}<br><small class="muted">${esc(g.note||'')}</small>${g.url?'<br>'+external(g.url,'来源'):''}</td></tr>`).join('')}</tbody></table></div>`:'<p class="empty">没有匹配结果。试试英文名或内部ID。</p>'}
function renderDownloads(){const b=branch();$('#current-download').innerHTML=`<div class="panel ${b.number===6?'error-panel':''}"><div class="eyebrow">CURRENT / 与当前查阅一致</div><h2>${esc(b.label)}</h2><p>${b.number===6?'06仅保留只读文本，避免误导入。':'先用原件核对；中文提示版仅增加说明，国服导入未实测。'}</p><div class="actions"><a class="btn ${b.number===6?'':'primary'}" id="main-download" href="${esc(b.download)}" download>${b.number===6?'下载只读原件':'下载当前原始 .build'}</a><a class="btn" href="${esc(b.annotatedDownload)}" download>中文提示${b.number===6?'文本':' .build'}</a><a class="btn" href="六分支完整资料.html#b${b.number}" target="_blank">本分支完整静态资料</a></div></div>`;
 $('#download-list').innerHTML=DATA.branches.map(x=>`<div class="panel"><h3>${esc(x.label)}</h3><p class="small muted">${esc(x.profile.short)}${x.number===6?' · 不直接导入':''}</p><div class="actions"><a class="btn smallbtn" href="${esc(x.download)}" download>${x.number===6?'只读原件':'原始构筑'}</a><a class="btn smallbtn" href="${esc(x.annotatedDownload)}" download>中文提示</a><button class="btn smallbtn" data-view="${x.number}">切换查阅</button></div><details><summary>原件SHA-256</summary><div class="detail-body"><code>${esc(x.sha256)}</code></div></details></div>`).join('');
}
function renderSources(){const total=(k)=>DATA.branches.reduce((n,b)=>n+b.raw[k].length,0),support=DATA.branches.reduce((n,b)=>n+b.raw.skills.reduce((a,s)=>a+s.support_skills.length,0),0),named=DATA.branches.reduce((n,b)=>n+b.namedCount,0);
 $('#coverage').innerHTML=`<div class="stat-row"><div class="stat"><b>6</b><span>原始构筑快照</span></div><div class="stat"><b>${total('inventory_slots')}</b><span>装备记录</span></div><div class="stat"><b>${total('skills')} / ${support}</b><span>技能组 / 内嵌连接</span></div><div class="stat"><b>${total('passives')}</b><span>天赋记录，非花点</span></div></div><div class="panel"><h3>名称与数据的核对状态</h3><p>全部${Object.keys(DATA.gems).length}种技能/辅助、${Object.keys(DATA.gearNames).length}种装备名、${Object.keys(DATA.nodeNames).length}种天赋ID有对照记录。天赋中有简体来源的记录${named}条，其余${total('passives')-named}条沿用DSH映射并标注待核对；有中文文字不等于已核实国服正式名。</p><p class="small muted">结构完整性、中文名称证据、浏览器交互与游戏实测是不同检查层级。本包不把结构通过说成游戏已毕业。</p></div>`;
 $('#source-list').innerHTML=DATA.sources.map(s=>`<div class="panel" id="src-${esc(s.id)}"><h3><span class="badge">${esc(s.id)}</span> ${esc(s.title)}</h3><p class="small muted">${esc(s.note)}</p>${external(s.url,s.url)}</div>`).join('');
}
function renderAll(){syncGlobal();renderHome();renderSkills();renderSpirit();renderGear();renderTree();renderCombat();renderCraft();renderUpgrade();renderDownloads();}
function resetCheckUI(){$$('[data-check]').forEach(x=>x.checked=!!state.checks[x.dataset.check]);updateTaskCount()}
async function copySkill(id){const s=branch().raw.skills.find(s=>s.id===id);if(!s)return;const text=`${branch().label}\n${gem(s.id).zh} / ${gem(s.id).en}\n${s.support_skills.map((x,i)=>`${i+1}. ${shortid(x.id).startsWith('SkillGem')?'〔内嵌主动〕':''}${gem(x.id).zh} / ${gem(x.id).en}`).join('\n')}\n原件完整连接，显示区间不是等级顺序。`;
 try{if(!navigator.clipboard)throw new Error('unavailable');await navigator.clipboard.writeText(text);notify('已复制当前分支的连接')}catch(_e){$('#copy-text').value=text;$('#copy-dialog').showModal();$('#copy-text').focus();$('#copy-text').select()}}
// One branch state owns every guide section. Comparison has its own pair and never mutates it.
const mobile=matchMedia('(max-width:820px)');let returnFocus=null;
function syncLocks(){const searching=!$('#search-mask').hidden,menu=mobile.matches&&$('#sidebar').classList.contains('open');$('#main-wrap').inert=searching||menu;$('#sidebar').inert=searching||(mobile.matches&&!menu);$('#sidebar').setAttribute('aria-hidden',String(mobile.matches&&!menu));document.body.style.overflow=searching||menu?'hidden':''}
function closeMenu(focus=false){$('#sidebar').classList.remove('open');$('#nav-mask').classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false');syncLocks();if(focus)$('#menu-toggle').focus()}
function showPage(anchor='start',focus=false){const t=document.getElementById(anchor),s=t?.closest('section')||$('#start');activePage=s.id;$$('main>section').forEach(x=>x.hidden=x!==s);$$('.nav-link').forEach(a=>a.setAttribute('aria-current',a.hash==='#'+activePage?'page':'false'));$('#page-name').textContent=titles[activePage];syncGlobal();closeMenu();if(t&&t!==s){let p=t.parentElement;while(p&&p!==s){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement}if(t.tagName==='DETAILS')t.open=true;requestAnimationFrame(()=>t.scrollIntoView({block:'start'}))}else{window.scrollTo(0,0);if(focus)$('h1',s)?.focus({preventScroll:true})}}
function parseHash(focus=false){let raw;try{raw=decodeURIComponent(location.hash.slice(1))}catch(_e){raw='start'}let [anchor,query='']=raw.split('?');const _alias=ALIAS[anchor];if(_alias&&_alias!==anchor){anchor=_alias;try{history.replaceState(null,'','#'+anchor+(query?'?'+query:''))}catch(_e){}}const q=new URLSearchParams(query);let changed=false;if(q.has('bd')&&validBranch(q.get('bd'))&&Number(q.get('bd'))!==state.current){state.current=Number(q.get('bd'));applyDefaultComparison();changed=true;['#skill-filter','#node-filter'].forEach(id=>$(id).value='');$('#skill-kind').value='all';$('#node-scope').value='all';$('#node-status').value='all'}if(q.has('target')&&[0,4,5].includes(Number(q.get('target')))){state.target=Number(q.get('target'));changed=true}if(q.has('mode')&&['ssf','trade'].includes(q.get('mode'))){state.mode=q.get('mode');changed=true}if(changed){save();renderAll()}showPage(anchor||'start',focus)}
function openSearch(){returnFocus=document.activeElement;$('#search-mask').hidden=false;syncLocks();$('#global-search').value='';renderSearch();$('#global-search').focus()}
function closeSearch(){if($('#search-mask').hidden)return;$('#search-mask').hidden=true;syncLocks();returnFocus?.focus()}
function renderSearch(){const q=$('#global-search').value.trim().toLowerCase(),out=$('#search-results');if(!q){out.innerHTML='<p class="muted">搜索六分支、技能、装备、天赋或机制。试试：03、魔力残片、战斗狂怒、虹吸、精魂、Primal。</p>';return}
 const docs=[...DATA.branches.map(b=>({title:b.label,text:b.profile.overview+' '+b.key+' '+b.profile.short,type:'branch',number:b.number})),...glossaryEntries.map(g=>({title:g.zh+(g.en?' / '+g.en:''),text:(g.id||'')+' '+(g.note||''),type:'term',query:g.id||g.en||g.zh})),...pages.map(id=>{const clone=$('#'+id).cloneNode(true);$$('table,.skill-grid,.gear-grid,script',clone).forEach(n=>n.remove());return {title:titles[id],text:clone.textContent.replace(/\s+/g,' ').slice(0,14000),type:'page',anchor:id}})];
 const list=docs.filter(d=>q.split(/\s+/).every(t=>(d.title+' '+d.text).toLowerCase().includes(t))).sort((a,b)=>Number(b.title.toLowerCase().includes(q))-Number(a.title.toLowerCase().includes(q))).slice(0,40);
 out.innerHTML=list.map(d=>`<a class="search-result" href="#${d.type==='term'?'glossary':d.type==='branch'?'start':d.anchor}" data-search-kind="${d.type}" data-search-number="${d.number||''}" data-search-query="${esc(d.query||'')}"><b>${esc(d.title)}</b><small>${esc(d.text.slice(0,140))}</small></a>`).join('')||'<div class="empty">没有匹配；请减少关键词或使用英文/ID。</div>';
}
// Event delegation keeps refreshed cards interactive, without duplicated listeners.
document.addEventListener('click',e=>{const t=e.target.closest('button,a');if(!t)return;
 if(t.dataset.view){setCurrent(t.dataset.view);return}
 if(t.dataset.comparePair){const [a,b]=t.dataset.comparePair.split('-').map(Number);state.compareFrom=a;state.compareTo=b;renderUpgrade();location.hash=`upgrade?bd=${state.current}`;showPage('upgrade',true);return}
 if(t.dataset.copy){copySkill(t.dataset.copy);return}
 if(t.dataset.searchKind){e.preventDefault();const type=t.dataset.searchKind,query=t.dataset.searchQuery,number=t.dataset.searchNumber,anchor=t.getAttribute('href').slice(1);closeSearch();if(type==='branch')setCurrent(number);if(type==='term'){$('#glossary-filter').value=query;$('#glossary-kind').value='all';renderGlossary()}location.hash=`${anchor}?bd=${state.current}`;showPage(anchor,true);return}
 const href=t.getAttribute('href');if(t.tagName==='A'&&href?.startsWith('#')&&!href.includes('?')){e.preventDefault();const a=href.slice(1);location.hash=`${a}?bd=${state.current}`;showPage(a,true)}
});
document.addEventListener('change',e=>{const t=e.target;if(t.matches('[data-check]')){state.checks[t.dataset.check]=t.checked;save();resetCheckUI()}});
$('#current-bd').addEventListener('change',e=>setCurrent(e.target.value));$('#target-bd').addEventListener('change',e=>{state.target=Number(e.target.value);save();renderHome();renderUpgrade();writeHash();notify('长期目标已更新；当前查阅BD没有改变')});$('#mode').addEventListener('change',e=>{state.mode=e.target.value;save();syncGlobal();renderHome();renderGear();renderCraft();writeHash()});
$('#compare-from').addEventListener('change',e=>{state.compareFrom=Number(e.target.value);renderDiff()});$('#compare-to').addEventListener('change',e=>{state.compareTo=Number(e.target.value);renderDiff()});
$('#skill-filter').addEventListener('input',renderSkills);$('#skill-kind').addEventListener('change',renderSkills);$('#node-filter').addEventListener('input',renderTree);$('#node-scope').addEventListener('change',renderTree);$('#node-status').addEventListener('change',renderTree);$('#glossary-filter').addEventListener('input',renderGlossary);$('#glossary-kind').addEventListener('change',renderGlossary);$('#spirit').addEventListener('input',storeBudget);$('#spirit').addEventListener('change',storeBudget);
$('#theme-toggle').addEventListener('click',()=>{state.theme=state.theme==='light'?'dark':'light';setTheme();save()});$('#menu-toggle').addEventListener('click',()=>{const on=!$('#sidebar').classList.contains('open');$('#sidebar').classList.toggle('open',on);$('#nav-mask').classList.toggle('open',on);$('#menu-toggle').setAttribute('aria-expanded',String(on));syncLocks();if(on)$('#menu-close').focus()});$('#menu-close').addEventListener('click',()=>closeMenu(true));$('#nav-mask').addEventListener('click',()=>closeMenu(true));mobile.addEventListener('change',()=>closeMenu());$('#search-open').addEventListener('click',openSearch);$('#search-close').addEventListener('click',closeSearch);$('#global-search').addEventListener('input',renderSearch);$('#search-mask').addEventListener('click',e=>{if(e.target===$('#search-mask'))closeSearch()});$('#copy-close').addEventListener('click',()=>$('#copy-dialog').close());
$('#reset-checks').addEventListener('click',()=>{if(confirm('清除本浏览器全部分支的任务勾选？当前BD、长期目标和精魂录入保留。')){state.checks={};save();renderHome();renderUpgrade();renderCombat();notify('勾选记录已清除')}});
document.addEventListener('keydown',e=>{const editing=/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||'');if((e.key==='/'&&!editing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();openSearch()}if(e.key==='Escape'){const was=$('#sidebar').classList.contains('open');closeSearch();closeMenu(was)}if(e.key==='Tab'&&(!$('#search-mask').hidden||(mobile.matches&&$('#sidebar').classList.contains('open')))){const root=!$('#search-mask').hidden?$('#search-mask'):$('#sidebar');const f=$$('a,button,input,select',root).filter(n=>n.getClientRects().length&&!n.disabled);const first=f[0],last=f.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}});
window.addEventListener('hashchange',()=>parseHash(true));
for(let i=0;i<pages.length;i++)$('#'+pages[i]).insertAdjacentHTML('beforeend',`<nav class="pager" aria-label="章节翻页">${i?`<a href="#${pages[i-1]}">← ${titles[pages[i-1]]}</a>`:'<span></span>'}${i<pages.length-1?`<a href="#${pages[i+1]}">${titles[pages[i+1]]} →</a>`:'<a href="#start">返回阶段总览 ↑</a>'}</nav>`);
$('#pitfall-list').innerHTML=detailList(pitfalls);applyDefaultComparison();setTheme();renderAll();renderGlossary();renderSources();parseHash(false);document.body.classList.add('js-ready');
window.__guideQA={edition:DATA.edition,getState:()=>({current:state.current,target:state.target,mode:state.mode,compareFrom:state.compareFrom,compareTo:state.compareTo,page:activePage}),counts:{branches:DATA.branches.length,gems:Object.keys(DATA.gems).length,gearRecords:DATA.branches.reduce((n,b)=>n+b.equipment.length,0),skills:DATA.branches.reduce((n,b)=>n+b.raw.skills.length,0),nodes:DATA.branches.reduce((n,b)=>n+b.nodes.length,0)}};
})();
