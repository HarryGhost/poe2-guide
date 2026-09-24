'use strict';
(() => {
const DATA=JSON.parse(document.getElementById('guide-data').textContent);
const $=(s,r=document)=>r.querySelector(s); const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='poe2-guide-reviewed-v1';
let persisted={};try{persisted=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(_e){}
if(typeof persisted!=='object'||Array.isArray(persisted))persisted={};
const stageData=[
 {id:'story',label:'剧情前段',short:'冰射前 · 约1–30',title:'先把剧情推进和基础装备做好',intro:'这时不急着照抄04号。先用能解锁、能持续释放的弓技能，给换冰射准备资源。',tasks:[['使用已解锁的闪电箭矢；拿到引雷针后加入','这来自作者练级方向，不是04号完整技能表。辅助随宝石与属性条件补，不要求1级全齐。'],['比较弓的真实伤害，补鞋子移速与基本防御','不用等待暗金；对新手而言，能活着输出比按外观选装重要。'],['为换冰射保留未切割宝石，先确认各技能需求','到对应条件再换；没有完整24级动态配置，不编造精确换技能清单。']],ssf:'先用掉落的有效弓，便宜过渡；不要为了16级展示配置消耗全部材料。',trade:'只买明显改善推进的小成本装备，不提前购齐最高配暗金。',links:[['查看剧情里程碑','#route'],['看装备优先级','#build']]},
 {id:'ice',label:'刚换冰射',short:'约31–40',title:'先让冰射与狙击的基础链路跑起来',intro:'拿到冰射只是开始，不是已经达成暴击混合防御。龙卷射击原件从41级开始显示，这个阶段先不强求。',tasks:[['冰霜射击用于清图与冻结，练习狙击完美释放','先用已能取得的辅助，确保仍能造成冻结。没有对应孔位或属性，就逐步补。'],['确认印记、弹幕已取得且能负担消耗','按实际解锁与属性配置；没有狂怒球不等于弹幕没有基础重复。'],['保持生命、闪避、抗性和魔力供给','不为了模仿终点面板提前撤掉过渡防御；单体战缺蓝先修恢复。']],ssf:'先留能用的伤害弓和黄箭袋，不等卡迪罗。',trade:'优先买当前能装备、实伤更好的过渡弓，而不只是投射物+等级。',links:[['查看技能与减配','#skills'],['练习输出循环','#combat']]},
 {id:'late',label:'剧情后段',short:'约41级起',title:'把辅助机制补齐，但不要急着转型',intro:'获得足够等级与宝石后再加入龙卷等工具，逐步核对常驻与元技能；满足条件的项才做。',tasks:[['取得龙卷射击后加入；理解箭路与复制','原件41–100是显示区间。不是只有放下持续伤害就自动触发所有致盲条件。'],['整理主动、常驻和元技能各自的位置','幻影射手和升华蜃影神射不同；三个冰射位置需要分别核对，没解锁的先不装。'],['检查新阶段的抗性、属性与实际精魂保留','用游戏面板，不沿用旧章节扣抗数字或固定145精魂的说法。']],ssf:'遇到防御好的掉落先留；缺精魂可以少开一个非必要常驻。',trade:'按资源缺口补首饰/防具，不为后期涂膏拆掉基础防御。',links:[['计算当前精魂','#spirit'],['看武器组设置','#weapon-sets']]},
 {id:'maps',label:'异界推进',short:'低阶 → T15目标',title:'先稳定刷图，再攒一套转型装备',intro:'非暴击输出与生命/闪避防御可以继续过渡。暴击和混合防御是两组装备条件，不强迫每个分支都洗一次。',tasks:[['用当前配置稳定完成地图与地图首领','打不动或经常死时先看排障；等级到达不等于地图难度已验收。'],['同时准备暴击弓/箭袋与护盾头/闪避衣服','作者转混合防御建议约450物品护盾的头，不是角色总护盾；装备够了再集中调整。'],['在无小怪补给时测试完整输出与魔力恢复','虹吸印记II按物理攻击击中伤害偷取；不能按总冰伤或击杀回蓝估算单体续航。']],ssf:'攒齐替换装备再调整，当前主武器永远留备份；贵暗金不是前置条件。',trade:'先把转型两组装备配齐，比较成品与自制成本；不使用旧价格估算。',links:[['准备装备阶梯','#build'],['查天赋范围','#tree']]},
 {id:'crit',label:'04号定型',short:'条件齐备后',title:'锁定04，先修真实短板',intro:'继续保留冰射＋狙击，不追05/06的最高配变动。终局能力逐个首领实测，不能靠“毕业”标题代替。',tasks:[['逐项核对04号10组技能、武器Ⅰ/Ⅱ与升华','不混入Early冰尖箭矢或Uber魔力残片。元技能内槽需手工检查。'],['对照原件升级弓、防御、资源与有效词条','先补整体缺口，不以猎首、卡迪罗、传奇辅助作为必须集齐的毕业标签。'],['记录当前首领、难度和失败原因','命中、冻结、狙击释放、供蓝、生存分开检查；不能证明全部最高难度必过。']],ssf:'用实际得到的装备逐步替换；特定珠宝种子与国服掉落池未知的不列为必得。',trade:'补能解决当前失败原因的装备；不用为了作者Live最新实装改掉整套玩法。',links:[['打开04技能','#skills'],['终局实战验收','#combat']]}
];
const state={stage:stageData.some(s=>s.id===persisted.stage)?persisted.stage:'story',mode:persisted.mode==='trade'?'trade':'ssf',theme:persisted.theme==='light'?'light':'dark',checks:(persisted.checks&&typeof persisted.checks==='object')?persisted.checks:{},skillBranch:4,gearBranch:4,treeBranch:4};
function save(){try{localStorage.setItem(KEY,JSON.stringify({stage:state.stage,mode:state.mode,theme:state.theme,checks:state.checks}))}catch(_e){}}
function notify(text){const t=$('#toast');t.textContent=text;t.hidden=false;clearTimeout(notify.timer);notify.timer=setTimeout(()=>t.hidden=true,3400)}
function setTheme(theme){state.theme=theme;document.documentElement.dataset.theme=theme;$('#theme-toggle').textContent=theme==='dark'?'浅色':'深色';$('#theme-toggle').setAttribute('aria-label',theme==='dark'?'切换为浅色主题':'切换为深色主题');save()}
function syncModes(){ $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode))); $$('.mode-text').forEach(n=>{n.textContent=n.dataset[state.mode]||''});$('#header-mode').textContent=state.mode==='ssf'?'独狼':'可交易'; }
function renderStage(){
 $('#stage-options').innerHTML=stageData.map(s=>`<button class="choice" type="button" data-stage="${s.id}" aria-pressed="${s.id===state.stage}"><b>${esc(s.label)}</b><span>${esc(s.short)}</span></button>`).join('');
 const s=stageData.find(x=>x.id===state.stage);
 $('#stage-skill-note').textContent=state.stage==='crit'?'你选择了04号定型阶段：先核对下面这10组，再查装备与资源。':'你当前选择的是“'+s.label+'”。下面04号是后续定型参考，并非当前等级应一次全部装好。请先按首页三项任务和已满足的技能条件推进。';
 $('#now-title').textContent=s.title;$('#now-intro').textContent=s.intro;
 $('#task-list').innerHTML=s.tasks.map((t,i)=>{const id=`stage-${s.id}-${i}`;return `<label class="task"><input type="checkbox" data-check="${id}" ${state.checks[id]?'checked':''}><span>${esc(t[0])}<span class="task-detail">${esc(t[1])}</span></span></label>`}).join('');
 $('#now-links').innerHTML=s.links.map(([label,href],i)=>`<a class="btn ${i===0?'primary':''}" href="${href}">${esc(label)} →</a>`).join('')+`<p class="small muted" style="flex-basis:100%;margin:7px 0 0">${esc(state.mode==='ssf'?s.ssf:s.trade)}</p>`;
 const n=s.tasks.filter((_t,i)=>state.checks[`stage-${s.id}-${i}`]).length;$('#task-count').textContent=`已勾选 ${n} / 3`;
 $$('.stage-card').forEach(c=>c.classList.toggle('current',c.dataset.stageId===state.stage));
}
const routes=[
 ['story','剧情前段 · 冰射前','先用已解锁的闪电箭矢与引雷针推进','先提高能用的弓伤、移动与基本防御；辅助随条件补齐，不把高级连接全塞给1级角色。','不提供缺失的逐级节点连线；先保持当前合法路线。','目标：正常完成当前剧情战斗，保留换冰射资源。'],
 ['ice','约31级起 · 刚使用冰射','冰射清图，逐步建立冻结与狙击爆发','加入已经取得且能使用的冰冻印记、弹幕；不在31级就要求龙卷射击。','目前还不是Crit全套。缺孔按职责减配；不要使用禁止异常的辅助破坏冻结。','目标：会冻、会完美释放、循环能付得起魔力。'],
 ['late','约41级起 · 剧情后段','工具、常驻与元技能逐步补齐','取得龙卷后加入；按升华解锁蜃影神射；检查每套冰射宝石的内嵌位置。','按面板预算精魂；辅助、品质、保留变化不靠统一数字猜。','目标：完成剧情并为异界准备装备，不承诺达到某级就自动过关。'],
 ['maps','进异界早期 → T15目标','先稳定，再准备转型','黄弓、黄箭袋与防御先升级；暴击弓/箭袋和高ES头/高闪避衣服成套准备。','输出转暴击与防御转混合分别验收；可以少走中间分支，但不承诺一次也不洗。','目标：可靠完成地图和地图首领；T15是验证目标，不是等级保证。'],
 ['crit','条件齐备后 · 04号定型','保留冰射＋狙击，继续升级装备','按04号的技能、天赋范围、武器组核对，重点解决单体供蓝与受击后恢复。','原件存在重复与跨组记录；未在国服验证实际计点，不伪造“95级点完”。','目标：逐个验证具体终局首领和难度；全黄装全最高难度尚未证实。']
];
$('#route-cards').innerHTML=routes.map(([id,phase,title,gear,talent,target])=>`<article class="panel stage-card" data-stage-id="${id}"><div class="stage-level">${phase}</div><h3>${title}</h3><div class="grid-2"><div><div class="label-mini">现在做什么</div><p>${gear}</p></div><div><div class="label-mini">天赋 / 技能边界</div><p>${talent}</p></div></div><p class="small muted">${target}</p><button class="btn smallbtn subtle" type="button" data-stage-go="${id}">把这里设为当前阶段</button></article>`).join('');
const gearLadder=[
 ['弓','伤害底座优先','必需的是合格弓，不是指定暗金或“+等级”标签。','本地附加物理＋物理伤害提高；有价值的冰点伤、可用攻速。','转暴击时补合适基础与本地暴击；整体伤害够好后再兼顾投射物等级。','留掉落中最好的弓，用备用底材试做；没做好暴击弓就继续过渡。','比较完整伤害区间、攻速与基础暴击；不要只按+2/+3搜索购买。'],
 ['箭袋','黄装可长期推进','04原版使用卡迪罗；黄箭袋是功能替代，不是等效复制。','攻击物理/冰点伤、有效弓伤害；按实际缺口选择。','转暴击后补暴击、暴伤和合适速度；不把飞羽流矢收益算进没有该点的04。','不用等卡迪罗；有数条有效输出词条的黄箭袋先用。','暴击黄箭袋或卡迪罗都应比较实际收益；不能因原版用了就认定必须。'],
 ['衣服','高物品闪避','黄装；防御与资源缺口先解决，不只看一个百分比词条。','高最终物品闪避，兼顾生命、抗性。','进一步完善闪避与偏转等防御；需要精魂时再与整体属性一起取舍。','先穿能补齐防御的黄装，不为追一条特殊词条把基础抗性换空。','看品质等处理后的最终物品闪避，别只比较“提高140%”。'],
 ['头盔','转混合防御的关键','黄装；先过渡，之后配合诡计面纱与护盾恢复。','前期生命/抗性与合适防御，别过早丢掉生命保障。','高物品能量护盾。作者转型建议约450物品ES的头；不是统一硬通关线。','头盔未到位先不强转防御；角色总护盾450不等于头盔ES450。','和高闪避衣服、恢复条件一起准备，避免只换一个头就宣称防御成型。'],
 ['戒指 ×2','抗性与供需补位','黄装；与其他部位共同承担未在展示词条中列全的抗性。','生命、元素/混沌抗性、所需属性。','逐步兼顾攻击物理/冰点伤；一枚偏补缺口、一枚偏输出也可。','掉落能补缺口就用；击杀回蓝用于刷图，不能当无小怪首领永续。','不跟着05号把所有生命换成闪电点伤；先服务当前04配置。'],
 ['鞋子','移动能力先到位','04本来是黄鞋；不是必须阿兹里的金履。','可用移速、生命、抗性与合适防御。','再追更高移速、闪避/护盾、偏转；35%只是原件展示数值。','黄鞋可持续使用。不要为了指定暗金长时间穿没有基本移速的鞋。','先买适合整体缺口的鞋，不以展示35%当早期入场门槛。'],
 ['腰带','可靠防御，不等猎首','04本来是黄腰带；猎首不属于固定主方案的必需品。','生命、力量、抗性。','进一步补整体属性、防御与实际药剂/咒符需求。','默认黄腰带到后期；不要围绕猎首掉落安排独狼时间表。','先补生存与需求；无稀有怪可杀的首领战不能默认猎首增益。'],
 ['手套','点伤和暴伤逐步提高','04原件没有+2投射物技能等级。','生命、攻击物理/冰点伤、抗性。','按暴击体系补暴伤、适用攻速及剩余防御。','不要为了复制Live的+2和特殊投射物词条停下；未核实生成机制不写配方。','不把另一名国服角色或Live手套当04启动条件。'],
 ['项链','先满足资源，再追等级','黄装；投射物+3、精魂47是原件展示，不是初期硬门槛。','所需属性、抗性、实际需要的精魂。','兼顾投射物技能等级与其他有效词条；后续再考虑锯齿锋缘涂膏。','等级与精魂不兼得时按缺口取舍，允许少开非必要常驻。','检查最终常驻预算和属性要求，购买前不只看+技能等级。'],
 ['药剂 / 咒符','单体续航和异常应对','不是黄装打造栏；先用对应普通/魔法物品实现功能。','可靠生命药剂、魔力药剂；应对冻结、减速、点燃等对应问题。','有条件再换原版功能性暗金，理解替代后失去的额外效果。','暗金掉落池未确认的不等；普通/魔法功能替代先能工作。','按实际问题补，不因“暗金”就认定比现有药剂回复强或永久猛攻。'],
 ['珠宝','实装缺失，别补脑','原件没有珠宝词条、种子或确切搭配，不设指定必需种子。','已拥有的有效攻击/弓属性、速度，或实际资源短板。','暴击成型后再比较暴击/暴伤；特殊珠宝按真实词条与范围收益核对。','先普通珠宝，不为空想的特殊珠宝效果绕路；同名不等于同词条。','买前确认词条、影响半径及插槽，不能只买同名泉井之心或抗衡黑暗。']
];
$('#gear-ladder').innerHTML=gearLadder.map((g,i)=>`<article class="gear-card"><div class="gear-top"><span class="gear-index">${String(i+1).padStart(2,'0')}</span><div><div class="label-mini">${g[1]}</div><h3>${g[0]}</h3></div></div><p class="muted">${g[2]}</p><div class="gear-cols"><div><div class="label-mini">先拿 · 可替代词条</div><p>${g[3]}</p></div><div><div class="label-mini">再换 · 长期目标</div><p>${g[4]}</p></div></div><div class="mode-advice mode-text" data-ssf="${esc(g[5])}" data-trade="${esc(g[6])}"></div></article>`).join('');
const tips={
 SkillGemIceShot:['手动攻击 · 清图与冻结','不能用元素军械III或元素集中破坏它承担的冻结职责。'],
 SkillGemSnipe:['手动攻击 · 冻结后爆发','盲点要求敌人已致盲；命定绝杀I不是必定暴击。缺少这些条件不计满加成。'],
 SkillGemTornadoShot:['工具攻击 · 箭矢复制 / 致盲配置','原件显示区间从41级开始。复制有惩罚且不能递归；持续伤害本身不是击中。'],
 SkillGemFreezingMark:['手动工具 · 印记与增益','虹吸印记II按物理攻击击中伤害偷取。永恒印记只保护第一次激活；充能印记不产狂怒球。'],
 SkillGemBarrage:['手动工具 · 强化下一次攻击','无狂怒球也有基础重复。04顺序是冷却回复II → 永续充能 → 快速施法II；永续充能不是产球。'],
 SkillGemHeraldOfIce:['常驻 · 清图','此处元素集中不等于主冰射也能照搬。精魂保留用装好辅助后的面板核对。'],
 SkillGemGhostDance:['常驻 · 护盾恢复','需要与当前混合防御配合；不是旧版“受击立即按5%闪避回盾”。'],
 SkillGemWindDancer:['常驻 · 防御 / 反击','受击前后的状态不同，不以满层城内闪避当永久防御。'],
 SkillGemMirageArcher:['元技能 · 幻影输出','第一个内槽是冰霜射击主动宝石，不是辅助。检查激活、触发条件和实际保留。'],
 SkillGemAscendancyMirageDeadeye:['升华元技能 · 镶嵌冰射','先取得对应升华。其内嵌冰射与幻影射手、你手动冰射分开配。'],
 SkillGemIceTippedArrows:['参考分支工具 · 04不使用','只在原件实际列出的参考分支显示，不自动加进固定04。'],
 SkillGemCombatFrenzy:['参考分支常驻 · 04不使用','不要把它的保留和产球当作04已存在的能力。'],
 SkillGemManaRemnants:['最高配参考 · 04不使用','涉及另一套资源与辅助配置，不与04技能表合并。'],
 SkillGemWolfPounce:['Live参考 · 已隔离','Live升华字段冲突；不能当04锐眼必需的变形工具。']
};
function gem(id){return DATA.gems[id]||{id,zh:id.split('/').pop(),en:id.split('/').pop(),url:'',note:''}}
function branch(n){return DATA.branches.find(b=>b.number===Number(n))||DATA.branches[3]}
function branchNote(b){if(b.number===4)return '当前主线：04号。10组技能来自原始快照；实际等级、品质、逐技能武器绑定和最终消耗未导出。';if(b.number===6)return '隔离参考：Live文件头为Ranger1，升华节点全为Ranger3。只读，不作为锐眼升级方案直接导入。';if(b.number===5)return '最高配对照：这份已没有狙击，不是固定04号只换装备的版本。';return '过渡参考：不是要求按编号依次转型。该分支的宝石和装备不得与04号混抄。'}
function renderSkills(){const b=branch(state.skillBranch),q=$('#skill-filter').value.trim().toLowerCase();const skills=b.raw.skills.filter(s=>[s.id,gem(s.id).zh,gem(s.id).en,...(s.support_skills||[]).flatMap(x=>[x.id,gem(x.id).zh,gem(x.id).en])].join(' ').toLowerCase().includes(q));$('#skill-branch-note').textContent=branchNote(b)+` 当前显示${skills.length}/${b.raw.skills.length}组。`;
 $('#skill-cards').innerHTML=skills.map(s=>{const g=gem(s.id),t=tips[s.id.split('/').pop()]||['来源技能','以原始配置为准。'];return `<article class="skill-card" id="skill-${esc(s.id.split('/').pop())}"><div class="skill-header"><div><div class="skill-role">${t[0]}</div><h3>${g.zh}</h3><span class="skill-en">${g.en}</span></div><button type="button" class="copy-btn" data-copy-skill="${esc(s.id)}">复制连接</button></div><p class="skill-notes">${t[1]}</p><ol class="gem-chain">${(s.support_skills||[]).map(x=>{const m=gem(x.id),active=x.id.split('/').pop().startsWith('SkillGem');return `<li class="${active?'active-gem':''}"><a href="${esc(m.url||'#glossary')}" ${m.url?'target="_blank" rel="noopener noreferrer"':''}>${active?'〔主动〕':''}${esc(m.zh)}</a></li>`}).join('')}</ol><div class="skill-meta">角色显示区间：${s.level_interval?s.level_interval.join('–'):'未标'} · 非宝石等级 ${g.url?`<a href="${esc(g.url)}" target="_blank" rel="noopener noreferrer">机制来源 ↗</a>`:''}</div></article>`}).join('')||'<div class="empty">这个分支没有匹配的技能或辅助。清空搜索，或换参考分支查看。</div>';
}
const slots={Weapon1:'主武器',Weapon2:'第二套武器',Offhand1:'箭袋 / 副手Ⅰ',Offhand2:'副手Ⅱ',Helm1:'头盔',BodyArmour1:'衣服',Gloves1:'手套',Boots1:'鞋子',Amulet1:'项链',Belt1:'腰带',Ring1:'戒指Ⅰ',Ring2:'戒指Ⅱ',Flask1:'药剂栏',Charm1:'咒符栏'};
function renderGear(){const b=branch(state.gearBranch);$('#gear-branch-note').textContent=branchNote(b)+` 共${b.equipment.length}条装备记录；不是完整实装所有词条。`;
 $('#gear-records').innerHTML=b.equipment.map(e=>{const r=e.raw;return `<article class="equip-record"><span class="badge">${slots[r.inventory_id]||esc(r.inventory_id)} · ${r.slot_x??0},${r.slot_y??0}</span> <span class="badge ${r.unique_name?'warning':''}">${r.unique_name?'暗金，仅导出名称':r.inventory_id==='Flask1'||r.inventory_id==='Charm1'?'普通/魔法，原件未指定':'稀有装备目标'}</span><h4>${esc(e.zh)}</h4><div class="small muted">${esc(e.en)}</div><p class="record-text">${esc(e.translation)}</p><div class="small muted">角色显示区间：${r.level_interval?r.level_interval.join('–'):'未标'}${e.url?` · <a href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">名称/机制来源 ↗</a>`:''}</div></article>`}).join('');
}
function renderTree(){const b=branch(state.treeBranch),q=$('#node-filter').value.trim().toLowerCase(),scope=$('#node-scope').value;$('#tree-stats').innerHTML=['公共','武器组1','武器组2','升华'].map(s=>`<div class="stat"><small>${s} · 导出记录</small><strong>${b.counts[s]?.rows||0}</strong><small>${b.counts[s]?.distinct||0}个不同ID · 非实际点数</small></div>`).join('');
 const dup=Object.values(b.counts).flatMap(v=>Object.keys(v.duplicates)),cross=Object.entries(b.overlaps).filter(([_k,v])=>v.length).map(([k,v])=>`${k}：${v.join('、')}`).join('；');
 $('#tree-notice').innerHTML=b.ascendancyConflict.length?`<div class="notice danger"><strong>本分支升华字段冲突，不能直接照抄。</strong>文件头${esc(b.raw.ascendancy)}，但${b.ascendancyConflict.length}条升华属于其他前缀；不据此断言作者实际转职，也不擅自修复。</div>`:`<div class="notice ${dup.length||cross?'warn':''}">原件共${b.nodes.length}条记录。${dup.length?`同范围重复ID ${dup.length}种。`:''}${cross?esc(cross)+'。':''}记录不自动转成等级或洗点费用。</div>`;
 const rows=b.nodes.filter(n=>(scope==='all'||n.scope===scope)&&[n.zh,n.id,n.en||'',n.status].join(' ').toLowerCase().includes(q));
 $('#node-count').textContent=`显示 ${rows.length} / ${b.nodes.length} 条。名字带来源链接的是简体资料对照；其余沿用DSH词典，未完成国服客户端核验。`;
 $('#node-table').innerHTML=rows.map(n=>`<tr><td>${n.row}</td><td>${n.scope}</td><td>${esc(n.zh)}</td><td><code>${esc(n.id)}</code></td><td>${n.url?`<a href="${esc(n.url)}" target="_blank" rel="noopener noreferrer">简体资料有来源 ↗</a>`:'DSH词典待复核'}</td></tr>`).join('')||'<tr><td colspan="5">没有匹配节点。请清空筛选或检查分支。</td></tr>';
}
const troubleshoot=[
 ['冰射冻不住怪，先看什么？','先确认主冰射没有装元素军械III或元素集中；再看命中、武器冰伤底座、冻结辅助与目标阈值。不要只给狙击堆伤害而不修负责冻结的冰射。普通怪与首领不是同一冻结测试。'],
 ['狙击伤害忽高忽低，是不是少了暗金？','先看是否在冻结窗口内完美释放、是否直接命中、是否被别的攻击吃掉弹幕、目标是否真正致盲，以及当前武器组。不要把一次最大爆发当每次期望值。'],
 ['刷图有蓝，首领总是空蓝','把击杀回蓝从单体恢复里拿掉，检查魔力药剂、实际恢复、技能消耗和印记持续；虹吸印记II不是按总元素伤害偷取。提高技能等级会连带资源压力，不能只看伤害。'],
 ['有很多护盾却还是容易死','检查生命、当前抗性、受击后的闪避、偏转、护盾恢复是否工作，以及地面持续伤害。幽灵舞步需要条件；不能用城里满层状态证明整个战斗都一样。'],
 ['切一下武器，技能或增益不见了','检查该组的武器/属性需求、技能绑定与常驻激活；印记和自身增益各有持续与消耗规则，不是切组一定永久保留。优先复现原因，不用空副手当万能修复。'],
 ['换弓后投射物等级更高，反而感觉变弱','比较整把弓的物理/元素伤害、攻速、本地暴击、命中与技能总消耗。等级提高不等于武器底座更好；也检查换装后属性或抗性是否失衡。']
];
const traps=[
 ['技能等级 ≠ 武器伤害底座','冰射和狙击是武器攻击。物理点伤、本地物理提高、冰点伤和适用伤害加成都要一起看；投射物+等级不能替代低伤害武器。','S5'],
 ['命中率 ≠ 暴击率 ≠ 暴击伤害','没有命中就没有这次攻击伤害；先有合适的武器基础暴击，再谈暴击投资。完美释放与必定暴击不是同一件事。','S6'],
 ['元素军械II ≠ 元素军械III','III禁止被辅助技能造成元素异常。负责冻结的主冰射不能无脑升级过去；寒冰之捷上的元素集中也不能照搬给主冰射。','S19'],
 ['技能名“充能” ≠ 生成狂怒球','充能印记产生感电地面，永续充能影响消耗；没有球时弹幕仍有基础重复，但不能计算额外球重复。','S7'],
 ['能打T16 ≠ 全部终局毕业','地图阶级、地图首领与不同终局首领/难度需要分别验收。04静态导出没有给出全部最高难度国服全黄装通关证明。',''],
 ['有一条护盾 ≠ 混合防御已成型','高物品护盾头、诡计面纱、衣服闪避、恢复与生命抗性一起看。04没有猛兽之肤，不能照搬另一树的额外闪避收益。','S26'],
 ['旧版受击瞬回 ≠ 当前幽灵舞步','当前数据为近期失去幽魂缠身后按闪避的一部分每秒恢复能量护盾。不要抄旧版“受击立刻按5%闪避回盾”的算式。','S14'],
 ['普通穿透 ≠ 抗性反转','普通穿透默认有0抗下限，特殊规则另论；拉其塔之流按反转处理，不能把减抗、穿透和反转各自最大收益无条件相加。固定04并未装该传奇辅助。','S28'],
 ['原始行号 ≠ 加点顺序','旧站93点、不同页面123点等不能与这六份记录混成一个等级结论。现在全部按公共、Ⅰ、Ⅱ、升华保留原始行号；没有合法分级路径就不造图。','S3'],
 ['导出提示 ≠ 装备真实物品','原件装备表只填了部分目标词条。没有列抗性并不是可以不要抗性；区间78–100不是这把弓实际物品等级78。','S3'],
 ['Live Gear冲突 ≠ 可以擅自替作者转职','文件头Ranger1与Ranger3升华节点冲突，应隔离核实。不能因为这个字段就断言作者实际换职业，更不能只改文件头宣称修好。','S27']
];
const faqs=[
 ['我第一次玩，先导入04号吗？','先在首页选你当前阶段。04是定型参考，不是1级启动树；装备与技能条件不齐不要整树洗点。原件没有合法逐级点序，导入只帮助核对而非自动完成构筑。'],
 ['我是不是必须从01一直换到06？','不是。01–03是作者不同过渡快照；04保留狙击；05/06已没有狙击。新手围绕一条目标准备，不必每到一个编号就洗一次。06另有升华字段冲突。'],
 ['我刚31级，为什么找不到龙卷射击？','原文件给龙卷的显示区间从41级开始，当前条目也是更高阶技能。31级是冰射阶段开始，不是整个最终技能表同时解锁。仍须满足宝石、属性及实际客户端条件。'],
 ['“六连”是装备上六个孔吗？','本攻略说的是主技能达到五个辅助位，即主技能加五个辅助连接。用对应技能宝石孔位系统核对，不按PoE1装备六连方式购买衣服。'],
 ['暗金没掉，还能继续刷吗？','这条基本技能链不以猎首、卡迪罗、金履全部集齐为前提。按装备页的黄装和普通/魔法功能替代继续推进；不承诺损失特殊效果后仍与原版等强。'],
 ['元素军械、冻结、快速攻击，为什么与英文ID不一样？','内部ID会沿用旧名字。PrimalArmamentTwo对应元素军械II、Glaciation对应冻结、MartialTempoTwo对应快速攻击II。按中文＋英文现名＋ID查询，不另造宝石名。'],
 ['精魂一定要145、147还是150？','都不能当整套统一硬门槛。150只是四个基础保留参考值之和，最终受实际连接与词条影响。把装好辅助后的游戏面板值填入精魂工具，未使用的项目取消勾选。'],
 ['技能等级和品质有精确毕业值吗？','原件没有完整实际等级和品质，只有显示区间。网站提供作者品质升级顺序，不编出全部宝石必须20/20等门槛。技能升到属性和魔力真正负担得起的程度，再验收效果。'],
 ['怎么知道这次改的是网站而不只是报告？','打开当前页面即可看到新的阶段选择、技能分支筛选、精魂计算、全站搜索和正确下载。整个“网站”目录是可离线/可静态部署的成品；审阅说明与自动测试结果另放在包内。'],
 ['我在另一台电脑看，勾选怎么没了？','进度仅保存在当前浏览器的本地存储，不登录、不联网同步。换浏览器、清理数据或本地存储被禁用时，勾选可能不保留，但正文和下载仍可用。'],
 ['网页能保证我不再改树、所有首领都过吗？','不能。完整中文坐标连线、实际计点与国服同配置全部最高难度测试尚未取得。这里不再把原始记录收录齐全等同于“全验证毕业”。']
];
function detailsList(list,source=false){return list.map(([q,a,s])=>`<details><summary>${q}</summary><div class="detail-body"><p>${a}${source&&s?` <a class="source-link" href="#src-${s}">[${s}]</a>`:''}</p></div></details>`).join('')}
$('#troubleshoot-list').innerHTML=detailsList(troubleshoot);$('#trap-cards').innerHTML=detailsList(traps,true);$('#faq-cards').innerHTML=detailsList(faqs);
const changes=[
 ['阅读路径','首页改成阶段选择与三项行动；独狼/交易建议并列切换。专业数据仍保留，但不挤在新手第一屏。'],
 ['技能版本','按六份原件逐条生成，04默认10组；不再把Early冰尖箭矢、04狙击、Uber魔力残片合成一个终点。'],
 ['时序与资源','修正31级就全技能齐的说法；补充辅助孔/品质顺序、精魂面板计算和元技能内嵌主动宝石的区分。'],
 ['机制','补清虹吸印记II物理击中偷取、弹幕无球基础重复、印记消耗/时限、龙卷复制和新版幽灵舞步。'],
 ['天赋与风险','去掉93点旧说明；按原件统计、标武器组和重复；06冲突隔离，不把冲突直接说成作者转职。'],
 ['装备与打造','纠正基础防御排除护盾、药剂咒符黄装化、暗金必需与确定性工艺说法；修正精华层级、蜕变石/点金及高级崇高石。'],
 ['代码','修复首页被历史页劫持、深锚点不能打开折叠、失效下载路径；增加全站搜索、移动导航、键盘焦点和本地存储容错。'],
 ['可追溯性','原件不改ID和顺序；保留原站备份、数据校验和来源。网页测试与国服实际游戏验证分开，不混为一个“完整通过”。']
];
$('#change-list').innerHTML=changes.map(([a,b])=>`<div class="source-row"><strong>${a}</strong><p>${b}</p></div>`).join('');
$('#source-list').innerHTML=DATA.sources.map(s=>`<div class="source-row" id="src-${s.id}"><span class="badge">${s.id}</span><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a><p>${esc(s.note)}</p></div>`).join('');
function downloadCard(b){const desc=b.number===4?'当前定型参考；原始字节保留。装备未到位时先看阶段路线。':b.number===6?'只读文本隔离：升华字段冲突，不要改回.build就直接导入。':b.number===5?'最高配对照，已移除狙击；不是04无缝升级。':'过渡参考；不要求按编号依次洗点。';return `<article class="download-card"><div><strong>${esc(b.label)}</strong><p>${desc}</p><p><a href="天赋节点清单/${String(b.number).padStart(2,'0')}_节点_含武器组.md" download>完整节点中文清单（含范围与状态）</a></p><details><summary style="font-size:12px;padding:8px 10px;min-height:36px">原件SHA-256</summary><div class="detail-body"><code>${b.sha256}</code></div></details></div><a class="btn ${b.number===4?'primary':''}" href="${esc(b.download)}" download>${b.number===6?'下载隔离文本':'下载 .build'}</a></article>`}
$('#download-main').innerHTML=downloadCard(DATA.branches[3]);$('#download-others').innerHTML=DATA.branches.filter(b=>b.number!==4).map(downloadCard).join('');
['skill-branch','gear-branch','tree-branch'].forEach(id=>{const el=$('#'+id);el.innerHTML=DATA.branches.map(b=>`<option value="${b.number}" ${b.number===4?'selected':''}>${esc(b.label)}</option>`).join('')});
const glossaryEntries=[...(DATA.extraTerms||[]),...Object.values(DATA.gems).map(g=>({...g,type:'gem',status:'简体数据对照，未客户端全量核验'})),...Object.values(DATA.gearNames).map(g=>({...g,type:'gear',id:'',status:'简体数据对照，未客户端全量核验',note:'底材或暗金名称；不要只凭名称推测掉落来源。'})),...Object.values(DATA.nodeNames).map(g=>({...g,type:'node'}))];
function renderGlossary(){const type=$('#glossary-type').value,q=$('#glossary-filter').value.trim().toLowerCase();const found=glossaryEntries.filter(g=>(type==='all'||g.type===type)&&[g.id,g.zh,g.en||'',g.note||''].join(' ').toLowerCase().includes(q));$('#glossary-count').textContent=`共 ${found.length} 项。来源链接代表条目依据，不代表已执行国服游戏验证。`;
 $('#glossary-cards').innerHTML=found.map(g=>`<article class="gloss-card"><span class="badge ${g.type==='node'&&!g.url?'warning':''}">${g.type==='gem'?'技能 / 辅助':g.type==='gear'?'装备名称':g.type==='extra'?'练级补充':'天赋映射'} · ${esc(g.status)}</span><h4 style="margin-top:10px">${esc(g.zh)}</h4><div class="small muted">${esc(g.en||'')}</div>${g.id?`<code class="mini-code">${esc(g.id)}</code>`:''}<p>${esc(g.note||'具体词条与数值请核对当前版本技能面板。')}</p>${g.url?`<a class="small" href="${esc(g.url)}" target="_blank" rel="noopener noreferrer">查看条目来源 ↗</a>`:''}</article>`).join('')||'<div class="empty">没有找到。请试中文、英文现名或内部ID的一部分。</div>';
}
const reserves=[['herald','寒冰之捷',30],['ghost','幽灵舞步',30],['wind','风舞者',30],['mirage','幻影射手',60]];
$('#reserve-rows').innerHTML=reserves.map(([id,label,n])=>`<div class="reserve-row"><input type="checkbox" id="reserve-on-${id}" checked aria-label="计算${label}的保留"><label for="reserve-value-${id}">${label}</label><input id="reserve-value-${id}" type="number" min="0" max="9999" step="1" value="${n}" aria-label="${label}最终精魂保留"></div>`).join('');
function calcSpirit(){const active=reserves.filter(([id])=>$('#reserve-on-'+id).checked);const fields=[...active.map(([id])=>$('#reserve-value-'+id)),$('#spirit-other'),$('#spirit-available')];const out=$('#spirit-result');if(fields.some(f=>f.value.trim()===''||!f.checkValidity())){out.textContent='请输入0至9999的整数面板数值；空值或负数不能用于预算。';return}const total=active.reduce((n,[id])=>n+Number($('#reserve-value-'+id).value),0)+Number($('#spirit-other').value);const avail=Number($('#spirit-available').value);out.innerHTML=`录入的最终保留合计 <strong>${total}</strong>，精魂总量 <strong>${avail}</strong>。<br><span class="small">${avail>=total?'按录入数字，剩余 '+(avail-total)+'。这仅是算术预算，不证明游戏中全部技能已成功激活。':'按录入数字，还缺 '+(total-avail)+'。先调整非必要常驻或装备资源，勿误删核心防御。'}</span>`;}
let activeSection='start';
const sectionOrder=['start','route','skills','build','tree','combat','craft','solo','trap','faq','glossary','dl','sources'];
const navTitles={start:'从这里开始',route:'阶段路线',skills:'技能怎么配',build:'装备先换什么',tree:'天赋与武器组',combat:'实战与排障',craft:'打造与涂膏',solo:'独狼与交易',trap:'机制与防坑',faq:'新手问答',glossary:'中英术语查询',dl:'构筑文件下载',sources:'来源与修正'};
for(let i=0;i<sectionOrder.length;i++){const s=$('#'+sectionOrder[i]);s.insertAdjacentHTML('beforeend',`<nav class="pager" aria-label="章节翻页">${i?`<a href="#${sectionOrder[i-1]}">← ${navTitles[sectionOrder[i-1]]}</a>`:'<span></span>'}${i<sectionOrder.length-1?`<a href="#${sectionOrder[i+1]}">${navTitles[sectionOrder[i+1]]} →</a>`:'<a href="#start">回到开始 ↑</a>'}</nav>`)}
const mobileQuery=window.matchMedia('(max-width:820px)');
function syncLocks(){const searchOpen=!$('#search-mask').hidden;const menuOpen=mobileQuery.matches&&$('#sidebar').classList.contains('open');$('#page-container').inert=searchOpen||menuOpen;$('#sidebar').inert=searchOpen||(mobileQuery.matches&&!menuOpen);$('#sidebar').setAttribute('aria-hidden',String(mobileQuery.matches&&!menuOpen));document.body.style.overflow=searchOpen||menuOpen?'hidden':''}
function closeMenu(focus=false){$('#sidebar').classList.remove('open');$('#nav-mask').classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false');syncLocks();if(focus)$('#menu-toggle').focus()}
mobileQuery.addEventListener('change',()=>closeMenu());
function route(focus=false){let hash;try{hash=decodeURIComponent(location.hash.slice(1))}catch(_e){hash='start'}const target=document.getElementById(hash||'start');const s=target?.closest('section')||$('#start');activeSection=s.id;$$('main>section').forEach(x=>x.hidden=x!==s);$$('.nav-link').forEach(a=>a.setAttribute('aria-current',a.hash==='#'+s.id?'page':'false'));$('#current-section').textContent=navTitles[s.id]||'指南';document.title=`${navTitles[s.id]} · 锐眼冰射＋狙击 0.5.5`;
 closeMenu();if(target&&target!==s){let p=target.parentElement;while(p&&p!==s){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement}if(target.tagName==='DETAILS')target.open=true;requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'auto'}));}else{window.scrollTo({top:0,behavior:'auto'});if(focus)s.querySelector('h1')?.focus({preventScroll:true})}
}
async function copySkill(id){const s=branch(state.skillBranch).raw.skills.find(s=>s.id===id);if(!s)return;const text=`${branch(state.skillBranch).label}\n${gem(s.id).zh}（${gem(s.id).en}）\n${s.support_skills.map((x,i)=>`${i+1}. ${x.id.split('/').pop().startsWith('SkillGem')?'〔主动〕':''}${gem(x.id).zh} / ${gem(x.id).en}`).join('\n')}\n来源：用户上传原始.build；顺序保留，非技能解锁顺序。`;try{await navigator.clipboard.writeText(text);notify('已复制当前分支的完整连接')}catch(_e){const ta=document.createElement('textarea');ta.value=text;ta.setAttribute('aria-label','可复制的技能连接');ta.style.position='fixed';ta.style.top='0';ta.style.left='0';ta.style.width='1px';ta.style.opacity='0';document.body.append(ta);ta.select();try{if(document.execCommand('copy'))notify('已复制当前分支的完整连接');else notify('浏览器禁止自动复制，请在卡片中选择连接文字复制')}catch(_err){notify('浏览器禁止自动复制，请手动选择卡片文字')}ta.remove()}}
let searchDocs=[];
function buildSearchIndex(){searchDocs=[];for(const id of sectionOrder){const section=$('#'+id);const clone=section.cloneNode(true);$$('script,.controls,.pager,#node-table,#glossary-cards,#skill-cards,#gear-records',clone).forEach(n=>n.remove());searchDocs.push({title:navTitles[id],text:clone.textContent.replace(/\s+/g,' ').slice(0,16000),href:'#'+id,type:'guide'});$$('details',section).forEach((d,i)=>{if(!d.id)d.id='detail-'+id+'-'+i;searchDocs.push({title:d.querySelector('summary')?.textContent||navTitles[id],text:d.textContent.replace(/\s+/g,' '),href:'#'+d.id,type:'guide'})});}glossaryEntries.forEach(g=>searchDocs.push({title:g.zh+(g.en?' · '+g.en:''),text:[g.zh,g.en||'',g.id||'',g.note||''].join(' '),href:'#glossary',type:g.type,query:g.id||g.en||g.zh}));}
let returnFocus=null;
function openSearch(){returnFocus=document.activeElement;const mask=$('#search-mask');mask.hidden=false;syncLocks();$('#global-search').value='';renderSearch();$('#global-search').focus()}
function closeSearch(){if($('#search-mask').hidden)return;$('#search-mask').hidden=true;syncLocks();returnFocus?.focus()}
function renderSearch(){const q=$('#global-search').value.trim().toLowerCase();const result=$('#search-results');if(!q){result.innerHTML='<p class="small muted">试试：31级、没蓝、虹吸、武器组、精魂、Primal、诡计面纱。<br>键盘 Esc 关闭；搜索只在本地运行。</p>';return}const terms=q.split(/\s+/);const found=searchDocs.filter(d=>terms.every(t=>(d.title+' '+d.text).toLowerCase().includes(t))).sort((a,b)=>{const rank=d=>(d.type!=='guide'&&(d.query||'').toLowerCase().includes(q)?100:0)+(d.title.toLowerCase()===q?80:0)+(d.title.toLowerCase().includes(q)?30:0);return rank(b)-rank(a)}).slice(0,30);result.innerHTML=found.map((d,i)=>{const pos=d.text.toLowerCase().indexOf(terms[0]);const snippet=d.text.slice(Math.max(0,pos-28),Math.max(0,pos-28)+135);return `<a class="search-result" href="${esc(d.href)}" data-search-result="${i}" data-search-type="${d.type}" data-search-query="${esc(d.query||'')}"><strong>${esc(d.title)}</strong><small>${esc(snippet)}${snippet.length>=135?'…':''}</small></a>`}).join('')||'<p class="empty">没有匹配结果。请减少关键词，或试中英文名字/ID。</p>';}
document.addEventListener('click',ev=>{const t=ev.target.closest('button,a');if(!t)return;if(t.dataset.stage){state.stage=t.dataset.stage;save();renderStage()}if(t.dataset.stageGo){state.stage=t.dataset.stageGo;save();renderStage();location.hash='start'}if(t.dataset.mode){state.mode=t.dataset.mode;save();syncModes();renderStage()}if(t.dataset.copySkill)copySkill(t.dataset.copySkill);if(t.hasAttribute('data-search-result')){if(t.dataset.searchType!=='guide'){$('#glossary-type').value=t.dataset.searchType;$('#glossary-filter').value=t.dataset.searchQuery;renderGlossary()}closeSearch();if(t.hash===location.hash)route(true)}if(t.tagName==='A'&&t.hash&&t.getAttribute('href')?.startsWith('#')&&t.hash===location.hash)route(true);});
document.addEventListener('change',ev=>{const t=ev.target;if(t.matches('[data-check]')){state.checks[t.dataset.check]=t.checked;save();if(t.dataset.check.startsWith('stage-')){const s=stageData.find(x=>x.id===state.stage);$('#task-count').textContent=`已勾选 ${s.tasks.filter((_t,i)=>state.checks[`stage-${s.id}-${i}`]).length} / 3`;}}});
$$('[data-check]').forEach(c=>c.checked=!!state.checks[c.dataset.check]);
$('#skill-branch').addEventListener('change',e=>{state.skillBranch=Number(e.target.value);renderSkills()});$('#skill-filter').addEventListener('input',renderSkills);
$('#gear-branch').addEventListener('change',e=>{state.gearBranch=Number(e.target.value);renderGear()});
$('#tree-branch').addEventListener('change',e=>{state.treeBranch=Number(e.target.value);renderTree()});$('#node-scope').addEventListener('change',renderTree);$('#node-filter').addEventListener('input',renderTree);
$('#glossary-type').addEventListener('change',renderGlossary);$('#glossary-filter').addEventListener('input',renderGlossary);
$('#spirit').addEventListener('input',calcSpirit);$('#spirit').addEventListener('change',calcSpirit);
$('#theme-toggle').addEventListener('click',()=>setTheme(state.theme==='dark'?'light':'dark'));
$('#menu-toggle').addEventListener('click',()=>{const open=!$('#sidebar').classList.contains('open');$('#sidebar').classList.toggle('open',open);$('#nav-mask').classList.toggle('open',open);$('#menu-toggle').setAttribute('aria-expanded',String(open));syncLocks();if(open)$('#sidebar .nav-link').focus()});$('#nav-mask').addEventListener('click',()=>closeMenu(true));$('#menu-close').addEventListener('click',()=>closeMenu(true));
$('#search-open').addEventListener('click',openSearch);$('#search-close').addEventListener('click',closeSearch);$('#global-search').addEventListener('input',renderSearch);$('#search-mask').addEventListener('click',e=>{if(e.target===$('#search-mask'))closeSearch()});
$('#reset-progress').addEventListener('click',()=>{if(confirm('清除当前浏览器的阶段勾选与实战清单？主题和获取方式会保留。')){state.checks={};save();renderStage();$$('[data-check]').forEach(x=>x.checked=false);notify('已清除当前浏览器的勾选记录')}});
document.addEventListener('keydown',e=>{const editing=/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||'');if((e.key==='/'&&!editing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();openSearch()}if(e.key==='Escape'){const wasMenu=$('#sidebar').classList.contains('open');closeSearch();closeMenu(wasMenu)}if(e.key==='Tab'&&(!$('#search-mask').hidden||(mobileQuery.matches&&$('#sidebar').classList.contains('open')))){const trapRoot=!$('#search-mask').hidden?$('#search-mask'):$('#sidebar');const focusables=$$('a,button,input', trapRoot).filter(n=>n.getClientRects().length);const first=focusables[0],last=focusables.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}});
window.addEventListener('hashchange',()=>route(true));
setTheme(state.theme);syncModes();renderStage();renderSkills();renderGear();renderTree();renderGlossary();calcSpirit();buildSearchIndex();document.body.classList.add('js-ready');route(false);
window.__guideQA={counts:{branches:DATA.branches.length,gems:Object.keys(DATA.gems).length,equipmentNames:Object.keys(DATA.gearNames).length,nodeNames:Object.keys(DATA.nodeNames).length,skillRecords:DATA.branches.reduce((a,b)=>a+b.raw.skills.length,0),passiveRecords:DATA.branches.reduce((a,b)=>a+b.nodes.length,0)},edition:DATA.edition};
})();
