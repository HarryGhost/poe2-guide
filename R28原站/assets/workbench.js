/* R19 continuation, preserving prior workflow. Local-only guide; no game automation, no guessed gear state. */
(()=>{'use strict';
const root=document.getElementById('craft-app');if(!root)return;
const D=JSON.parse(document.getElementById('workbench-data').textContent),S=D.simple;
const $=s=>root.querySelector(s),$$=s=>[...root.querySelectorAll(s)],esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const phases=D.phases.map(x=>x.id),items=D.items.map(x=>x.id),routes=new Map(D.routes.map(x=>[x.id,x]));
const KEY='fubgun-craft-r13';let saved={items:{},last:null};try{let v=JSON.parse(localStorage.getItem(KEY)||'null');if(v&&typeof v==='object')saved={items:v.items&&typeof v.items==='object'?v.items:{},last:v.last||null};}catch(_){}
let st={phase:'e01',slot:'bow',mode:'basic',route:'early-bow',step:'ready'},lastFocus=null,updating=false;
function save(){try{saved.last={phase:st.phase,slot:st.slot};localStorage.setItem(KEY,JSON.stringify(saved));}catch(_){}}
function rec(){if(!saved.items[st.slot]||typeof saved.items[st.slot]!=='object')saved.items[st.slot]={ilvl:'',state:'unknown'};return saved.items[st.slot];}
function item(){return D.items.find(x=>x.id===st.slot);}function route(){return routes.get(st.route);}function step(){return route().steps.find(x=>x.id===st.step)||route().steps[0];}
function advancedFor(){const ids=item().routes[st.phase].options.filter(x=>!x.startsWith('early-'));const def=item().routes[st.phase].default;return ids.includes(def)?def:ids[0];}
function url(u,label){return `<a href="${esc(u)}"${/^https:/.test(u)?' target="_blank" rel="noopener noreferrer"':''}>${esc(label)}</a>`;}
function material(id){let m=D.materials[id];return m?`<button class="c-mat" type="button" data-material="${esc(id)}">${esc(m.zh)} <span aria-hidden="true">ⓘ</span></button>`:'';}
function openDialog(title,body){lastFocus=document.activeElement;$('#c-dialog-title').textContent=title;$('#c-dialog-body').innerHTML=body;$('#c-dialog').showModal();$('#c-dialog-close').focus();}
$('#c-dialog-close').onclick=()=>$('#c-dialog').close();$('#c-dialog').addEventListener('close',()=>lastFocus?.focus?.());
function updateURL(){const hash=[st.phase,st.slot,st.route,st.step].join('/');try{history.replaceState(null,'','#'+hash);}catch(_){/* about:blank tests may disallow replaceState; no UI failure */}save();}
function validLevel(raw){if(raw==='')return {kind:'unknown',value:null};const v=Number(raw);return Number.isInteger(v)&&v>=1&&v<=100?{kind:'valid',value:v}:{kind:'invalid',value:null};}
const rareSlots=new Set(D.continuation?.normalRareSlots||[]);
function clearFinishCounts(){rec().prefixes='';rec().suffixes='';rec().reserve='';}
function finishingRender(){
 const c=step().finishCheck,box=$('#c-affix-check');box.hidden=!c;root.classList.toggle('is-finishing',!!c);
 $('#c-finish-entry').hidden=!rareSlots.has(st.slot)||st.mode!=='basic'||!!c;
 if(!c)return;
 $('#c-prefix-count').value=rec().prefixes??'';$('#c-suffix-count').value=rec().suffixes??'';
 $('#c-reserve-plan').value=rec().reserve??'';$('#c-reserve-label').hidden=!c.noReserved;
 updateAffixText();
}
function affixNumbers(){let a=$('#c-prefix-count').value,b=$('#c-suffix-count').value;return a===''||b===''?null:{p:Number(a),s:Number(b),total:Number(a)+Number(b)};}
function updateAffixText(){const c=step().finishCheck;if(!c)return;const a=affixNumbers();
 $('#c-affix-result').textContent=a?`已用 ${a.p}前＋${a.s}后＝${a.total}条；还能加 ${3-a.p}个前缀、${3-a.s}个后缀。`+(c.reservedPrefix?' 本路线保留最后前缀给渎灵，不普通乱填。':' 所加类别受剩余空位限制，不保证具体属性。'):'数全部随机词缀，而不是只数有用的：已有6条、其中4条好，仍然没有空位。';
}
function finishingGuard(){const c=step().finishCheck;if(!c)return null;const a=affixNumbers(),level=validLevel($('#c-ilvl').value),state=rec().state;
 const stop=(title,text)=>({cls:'stop',title,text,ok:false});
 if(state==='unrevealed')return stop('还有未显现词缀：先显现并核对','未显现词缀已经占位，不当成空位；先按对应显现步骤处理。');
 if(!['yellow','yellow-open','yellow4','yellow5','yellow6','yellow-bad','fractured'].includes(state))return stop('本步要求已完成前段工艺的黄装','蓝装不能用崇高补到5／6条；先按实际状态完成前段工艺。');
 if(!a)return stop('先数清前缀和后缀','只知道“4条都好”仍不够；确认分组后，本页会显示剩余空位。');
 if(!c.totals.includes(a.total))return stop(`当前${a.total}条，与本步不符`,`本步只接${c.totals.join('或')}条状态。实际5条请走单加；6条进入收尾；不要把下一步当作已经操作。`);
 if(c.prefixes!==undefined&&a.p!==c.prefixes)return stop('前缀状态与所选工艺不符',`这段原路线要求${c.prefixes}个前缀，请核对实际属性，不照模板硬做。`);
 if(c.suffixes!==undefined&&a.s!==c.suffixes)return stop('后缀状态与所选工艺不符',`本步要求${c.suffixes}个后缀；最后前缀／后缀不能混用。`);
 if(c.suffixLimit!==undefined&&a.s>c.suffixLimit)return stop('后缀已满，停止这轮定向添加','按原路线确认最后前缀空位，再读渎灵步骤。');
 if(6-a.total<c.adds)return stop('空位不足','本步添加条数超过实际空位，不使用双加预兆。');
 if(c.noReserved&&$('#c-reserve-plan').value!=='clear')return stop('先处理要预留的工艺空位','尚有精华／渎灵要做，或不确定时，不先用普通崇高填满；查看对应完整工艺。');
 const min=step().materials.includes('perfect-exalt')?50:step().materials.includes('greater-exalt')?35:0;
 if(min&&(level.kind!=='valid'||level.value<min))return stop(`本步材料要求物品等级至少${min}`,'这是通货最低词缀等级条件，不保证词缀阶级，也不能替代作者整条工艺的起点。');
 return null;
}
function stateOptions(){let arr=[['unknown','还没看清 / 尚未选装备'],['unidentified','未鉴定（先看清属性）'],['white','白装（普通）'],['blue1','蓝装，只有1条随机词缀'],['blue2','蓝装，已有2条随机词缀'],['yellow','黄装 / 已有成品，先比较']];if(rareSlots.has(st.slot))arr.push(['yellow4','黄装4条合用：继续补第5条'],['yellow5','黄装已有5条：继续补第6条'],['yellow6','黄装已经6条：不再加词缀'],['yellow-bad','刚补出不合用词缀：先看处理']);if(st.mode==='advanced')arr.push(['unrevealed','黄装，已有未显现渎灵词缀'],['fractured','已确认破溃固定＋3的项链'],['plainplus3','只有普通＋3，未破溃固定']);if(!['flasks','charms'].includes(st.slot))arr.push(['yellow-open',rareSlots.has(st.slot)?'黄装3条：准备增加第4条':'黄装，确认仍有本类装备的合法空位']);arr.push(['special','暗金 / 腐化 / 镜像 / 不明特殊状态']);return arr;}
function basicStep(state){const ids=route().steps.map(s=>s.id);const n={unknown:'ready',unidentified:'ready',white:ids.includes('white')?'white':'trans',blue1:ids.includes('augment')?'augment':'aug',blue2:ids.includes('regal')?'regal':'check',yellow:'check',yellow4:'finish-four',yellow5:'finish-five',yellow6:'check','yellow-bad':'bad-roll','yellow-open':ids.includes('exalt')?'exalt':'check',special:'ready'}[state]||'ready';return ids.includes(n)?n:route().steps[0].id;}
function initialStateForStep(r,id){if(r.startsWith('early-'))return {white:'white',trans:'white',augment:'blue1',aug:'blue1',regal:'blue2',exalt:'yellow-open','finish-four':'yellow4','finish-five':'yellow5','bad-roll':'yellow-bad',check:'yellow'}[id]||'unknown';return 'unknown';}
function parseHash(){let parts=[];try{parts=decodeURIComponent(location.hash.slice(1)).split('/');}catch(_){}let has=false;if(phases.includes(parts[0])&&items.includes(parts[1])){st.phase=parts[0];st.slot=parts[1];has=true;if(routes.has(parts[2])&&item().routes[st.phase].options.includes(parts[2])){st.route=parts[2];st.step=parts[3]||'ready';}else{st.route='early-'+st.slot;st.step='ready';}}else if(routes.has(parts[0])){st.route=parts[0];st.phase=st.route.startsWith('early-')?'e01':({'bow-noncrit':'e02','bow-crit':'e04','quiver-standard':'e02','helmet-stable':'e03','helmet-random':'e03','amulet':'e04','quiver-advanced':'e05','emerald':'e05'}[st.route]||'e01');st.slot=items.find(id=>D.items.find(x=>x.id===id).routes.e01.options.includes(st.route))||'bow';st.step=parts[1]||'ready';has=true;}
 if(!has&&saved.last&&phases.includes(saved.last.phase)&&items.includes(saved.last.slot)){st.phase=saved.last.phase;st.slot=saved.last.slot;st.route='early-'+st.slot;}
 st.mode=st.route.startsWith('early-')?'basic':'advanced';if(!routes.has(st.route))st.route='early-'+st.slot;if(!route().steps.some(s=>s.id===st.step))st.step=route().steps[0].id;
 if(st.mode==='basic'&&st.step!=='ready')rec().state=initialStateForStep(st.route,st.step);
 render(true);}
function switchRoute(id){if(!routes.has(id))return;const it=D.items.find(x=>x.routes[st.phase].options.includes(id));if(!it)return;st.slot=it.id;st.route=id;st.mode=id.startsWith('early-')?'basic':'advanced';st.step=route().steps[0].id;clearFinishCounts();render(true);}
function goStep(id){if(!route().steps.some(x=>x.id===id))return;st.step=id;clearFinishCounts();if(st.mode==='basic')rec().state=initialStateForStep(st.route,id);render(true);}
function requiredLevel(){const t=D.thresholds[st.route];return st.mode==='advanced'&&t?.min?(st.route==='amulet'&&rec().t1Resist?82:t.min):null;}
function investmentText(){const n=requiredLevel(),l=validLevel($('#c-ilvl').value);if(st.mode==='basic')return '投入建议：现在有短板才少量加工，不必等人物70／80级。四条已够用可以停，第5／6条是可选后续。';if(n===null)return '这条工艺没有已核实的统一物品等级起点；不补填80，先看原步骤和只读限制。';return '作者本条工艺起点：物品等级 '+n+'；不是人物等级。'+(l.kind==='valid'&&l.value>=n?'当前只通过等级这一项；':'')+'还要核对底材、起手词缀、材料、佩戴需求和预算，不因数字更高就必做。';}
function guard(){const level=validLevel($('#c-ilvl').value),state=rec().state||'unknown',r=route(),s=step();
 if(D.routeWarnings[r.id]||s.kind==='boundary')return {cls:'danger',title:'只读，不按这段花材料',text:D.routeWarnings[r.id]||'这一步的前提尚未核实，不能按自动下一步执行。',ok:false};
 if(state==='special')return {cls:'stop',title:'先不按普通加工',text:'暗金、腐化、镜像或不明特殊状态先单独核对；不拿昂贵材料试能不能点。',ok:false};
 if(level.kind==='invalid')return {cls:'stop',title:'物品等级输入不对',text:'填写1–100之间的整数；空白表示未知，不按0处理。',ok:false};
 const minimum=requiredLevel();if(minimum){if(level.kind==='unknown')return {cls:'stop',title:`先确认物品等级（作者起点 ${minimum}）`,text:'可以继续读完整工艺；不知道ilvl时，先不按高投入路线操作。',ok:false};if(level.value<minimum)return {cls:'stop',title:`物品等级 ${level.value} 低于本次目标的 ${minimum} 起点`,text:st.route==='amulet'&&rec().t1Resist?'你选择了追最高阶抗性，作者按82起步。80仍可看不追此目标的路线；不保证随机结果。':'这件仍可比较或普通加工；不要照此完整工艺投入预兆、精华和后续材料。',ok:false};}
 if(st.mode==='advanced'&&r.id==='amulet'&&state!=='fractured')return {cls:'stop',title:'必须先确认“＋3已破溃固定”',text:'普通＋3、只有金色文字或不知道是否固定，都不能进入剥离清理步骤。',ok:false};
 if(st.mode==='advanced'&&['essence','regal'].includes(s.id)&&!['blue1','blue2'].includes(state))return {cls:'stop',title:'这一步要求蓝装，不是现有黄装',text:'先按下面的前提核对颜色和词缀；已经升黄应查看后续状态，不能再接蓝装升黄精华。',ok:false};
 if(st.mode==='advanced'&&s.id==='essence'&&state==='blue1'&&r.id.startsWith('bow-'))return {cls:'stop',title:'作者此处先要求两条蓝装词缀',text:'先完成并核对增幅后的蓝弓；本步骤不是直接对任意一条蓝弓使用。',ok:false};
 if(state==='unknown')return {cls:'',title:'先选你手里这件的状态',text:'不会把你默认成已经有合格蓝装。“怎么认装备”就在右上方。',ok:false};
 if(state==='unidentified')return {cls:'',title:'先鉴定，再决定是否投入',text:'知识卷轴只让你看清词缀；鉴定后重新选择蓝装或黄装状态。',ok:false};
 const fg=finishingGuard();if(fg)return fg;
 if(!$('#c-ready').checked)return {cls:'',title:st.mode==='basic'?(level.value?`ilvl ${level.value}：可作为普通加工候选`:'物品等级未知：只先看普通加工'):'等级只是其中一项条件',text:'先读右侧前提并核对备用装备；随机结果、词缀组和材料限制不会由网页自动判断。',ok:false};
 return {cls:'good',title:'可按已确认状态阅读本步',text:st.mode==='basic'?'本步使用普通通货，不套75级完整工艺；是否能用仍以材料提示为准。':'仅按你勾选的前提继续；满足ilvl不保证词缀合法、投入划算或随机结果。',ok:true};}
function showStatus(){const g=guard();$('#c-investment').textContent=investmentText();const box=$('#c-status');box.className='c-status '+g.cls;box.innerHTML=`<b>${esc(g.title)}</b><span>${esc(g.text)}</span>`;const op=$('#c-op-guard');if(op){op.hidden=!['stop','danger'].includes(g.cls);op.textContent=op.hidden?'':'先不要点材料：'+g.title+'。下方只供查阅，不能代表这件已符合条件。';}$('#c-ilvl').setAttribute('aria-invalid',validLevel($('#c-ilvl').value).kind==='invalid'?'true':'false');return g;}
function targetHTML(){const t=S.targets[st.slot],r=route(),s=step(),it=item(),advanced=st.mode==='advanced';let want=[...t.want],number=t.number;
 if(st.slot==='helmet'&&['e03','e04','e05'].includes(st.phase))want=['头盔顶部最终护盾','智慧与整套需求满足','缺失抗性／恢复配套'];
 if(st.slot==='bow'&&(['e04','e05'].includes(st.phase)||r.id==='bow-crit'))want=['本地物理／冰霜伤害底座','本地基础暴击与攻速','投射物技能等级（再查耗蓝）'];
 if(advanced&&r.id==='bow-noncrit'&&s.id==='essence')number='本颗精华物理点伤范围：最小端16–24，最大端28–42。例如16–28是其中一种结果，不是固定成品。';
 if(advanced&&r.id==='bow-crit'&&s.id==='essence')number='强效寻觅的本地暴击词缀范围：＋3.11至＋3.8个百分点。不是全局“提高3.11%”；国服提示不符先停。';
 if(advanced&&r.id==='amulet')number='普通精魂前缀43–46／47–50为两档已核对范围，不保证掷出。整条项链仍需已破溃＋3和ilvl80（作者追最高档抗性82）。';
 if(s.finishCheck){
 const a=affixNumbers(),f=s.finishCheck;
 const suffixGoals={bow:['攻击速度／投射物技能等级','命中或当前BD需要的暴击属性'],quiver:['攻速／投射物技能等级','当前BD需要的暴击相关属性'],helmet:['当前缺少的抗性／智慧'],body:['当前缺少的抗性／属性'],gloves:['攻击速度／缺失抗性'],boots:['当前缺少的抗性／属性'],amulet:['本路线定向后缀，偏向缺少的元素抗性'],belt:['力量／缺失抗性'],rings:['缺少的抗性／属性']};
 const prefixGoals={bow:['物理／冰霜点伤、本地物理提高'],quiver:['攻击点伤／弓伤害'],helmet:['本路线要求的护盾前缀'],body:['闪避／生命'],gloves:['攻击点伤／生命'],boots:['移速／生命'],amulet:['按原路线显现最后前缀'],belt:['生命'],rings:['生命／攻击点伤']};
 const pg=a&&a.p<3?(prefixGoals[st.slot]||[]):[],sg=a&&a.s<3?(suffixGoals[st.slot]||[]):[];
 const scopeText=!a?'先确认上方两类数量，再看剩余位置。':a.p===3?'前缀已满：这次只能加后缀。':a.s===3?'后缀已满：这次只能加前缀。':'前后缀都有空位；普通崇高不能保证先加哪一类。';
 return `<p class="c-fin-target"><b>${esc(scopeText)}</b></p>${a?`<p class="c-micro">可关注的方向（不是保证结果）</p><ul class="c-target-list">${[...pg,...sg].map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}<p class="c-micro">仍受物品等级、已有词缀组和材料规则限制。已有6条、只有4条合用，不等于还有2个空位。</p><button type="button" class="c-text-button" data-open-reference>查看整件目标、底材和数值</button>`;
 }
 const usable=it.bases.filter(x=>(x.phases||[]).includes(st.phase));const names=usable.slice(0,2).map(x=>x.name).join('；')||it.bases[0]?.name||'看本页完整底材';
 return `<ul class="c-target-list">${want.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${advanced?`<p class="c-target-note">${esc(S.advanced_goals[r.id]||r.goal)}</p>`:''}<p class="c-goal-number">${esc(number)}</p><p class="c-bases-short"><b>底材怎么选</b>${esc(names)}。先确认实际佩戴需求；可用成品不必从白装重做。</p><p class="c-avoid">${esc(t.avoid)}</p><button type="button" class="c-text-button" data-open-reference>看完整底材与作者数值</button>`;}
function view(){const state=rec().state||'unknown',s=step();
 if(st.mode==='basic'&&state==='unidentified')return {title:'鉴定一次，看清以后再决定',before:'物品未鉴定；先别使用改变词缀的通货。',actions:['右键「知识卷轴」→ 左键这件物品一次。'],expect:'“未鉴定”消失，能够读到随机属性。',good:'看清后，在上方重新选择实际状态；不自动认为鉴定结果值得继续。',bad:'不是未鉴定物品或提示不匹配：停止，不换贵材料试。',materials:['wisdom'],refs:['https://poe2db.tw/cn/Scroll_of_Wisdom']};
 if(st.mode==='basic'&&(state==='unknown'||state==='special'))return {title:state==='special'?'先核对特殊状态，不点材料':'先认颜色和词缀，暂不花材料',before:'这页需要你确认物品状态，但不要求你先懂所有打造术语。',actions:['点上方“怎么认装备”，按图文顺序查看名称颜色、物品等级和词缀分组。','在上方选真实状态；白装、蓝装1条、蓝装2条、黄装各有不同处理。'],expect:'知道这件属于哪一种；仍看不清就选特殊状态，先停。',good:'状态明确后，右侧会自动显示相应的一步，不从第一步机械连做。',bad:'不按文字行数猜词缀；不用剥离、混沌或精华试验。',materials:[],refs:S.sources.map(x=>x[1]).slice(0,2)};
 return {title:s.title,before:s.before,actions:s.action,expect:s.expect,good:s.good,bad:s.bad,materials:s.materials,refs:s.refs||[],note:s.note||''};}
function actionRender(){finishingRender();const v=view(),s=step(),g=showStatus();$('#c-prereq').innerHTML='<b>操作前：</b>'+esc(v.before);$('#c-materials').innerHTML=v.materials.length?'<span class="c-micro">本步材料</span>'+v.materials.map(material).join(''):'<span class="c-micro">本步不消耗材料</span>';
 $('#c-action-title').textContent=v.title;$('#c-actions').innerHTML=v.actions.map(x=>`<li>${esc(x)}</li>`).join('');$('#c-expect').innerHTML='<b>应看到：</b>'+esc(v.expect);
 $('#c-result-good').innerHTML='<b>符合时：</b>'+esc(v.good);$('#c-result-stop').innerHTML='<b>不符合：</b>'+esc(v.bad);
 $('#c-step-badge').textContent=st.mode==='basic'?'普通加工 / 一次一颗':`${route().steps.findIndex(x=>x.id===st.step)+1} / ${route().steps.length}（查阅）`;
 const buttons=[];
 if(st.mode==='basic'&&['unknown','special'].includes(rec().state))buttons.push('<button type="button" class="primary" data-help-open>先学会认这件装备</button>');
 else if(st.mode==='basic'&&rec().state==='unidentified')buttons.push('<button type="button" class="primary" data-choose-state>已鉴定，重新选状态</button>');
 else{
  if(s.next)buttons.push(`<button type="button" class="primary" data-next="${esc(s.next)}">${esc(s.nextLabel||'查阅下一步 →')}</button>`);
  (s.choices||[]).forEach(c=>buttons.push(`<button type="button" data-next="${esc(c.id)}">${esc(c.label)}</button>`));
  buttons.push('<button type="button" data-compare>先比较旧装</button>');if(!(s.choices||[]).some(x=>x.id==='bad-roll'))buttons.push('<button type="button" data-stop>结果不合用 / 先停</button>');
 }
 if(st.mode==='basic'&&['blue2','yellow'].includes(rec().state)&&advancedFor())buttons.push('<button type="button" data-open-advanced>改看作者完整工艺</button>');
 $('#c-buttons').innerHTML=buttons.join('');
 $('#c-action-source').innerHTML=(st.mode==='basic'?'Fubgun目标＋本站操作解释；非作者每个部位的独立配方。 ':'Fubgun工艺＋操作解释；未做国服实测。 ')+v.refs.slice(0,2).map((u,i)=>url(u,'依据'+(i+1))).join(' · ');
 if(!g.ok&&g.cls==='danger')$('#c-step-badge').textContent='原步骤只读';
 $('#c-target-body').innerHTML=targetHTML();$('#c-result-panel').hidden=true;updateURL();}
function populateReferences(){const it=item(),t=D.thresholds[st.route];$('#c-bases').innerHTML=`<p><b>${esc(t?.text||'普通加工没有统一ilvl75要求。追求特定词缀时，另核对词缀生成等级与材料提示。')}</b></p>`+it.bases.map(b=>{let w=it.wear[b.en];return `<p><b>${esc(b.name)}</b> / ${esc(b.en)}<br>${esc(b.why)}${w?`<br>底材佩戴要求：人物${esc(w.level)}级；力量${esc(w.str)} / 敏捷${esc(w.dex)} / 智慧${esc(w.int)}。不是工艺ilvl。`:''}</p>`;}).join('');
 const rows=D.numeric.metrics[st.phase][st.slot];$('#c-numbers').innerHTML=rows.map(q=>`<div class="c-number-row"><b>${esc(q.label)}</b><span>${esc(q.value)}</span><small>〔${esc(q.kind)}〕${esc(q.meaning)}</small></div>`).join('')+`<p>${esc(D.numeric.physical.advice)}</p>`;
 $('#c-snapshot').innerHTML=(it.snapshots[st.phase]||[]).map(x=>`<pre>${esc(x.text)}</pre>`).join('');
 $('#c-timeline').innerHTML=(D.routeWarnings[st.route]?`<p class="c-readonly">${esc(D.routeWarnings[st.route])}</p>`:'')+route().steps.map((s,i)=>`<button type="button" class="c-timeline-step ${s.id===st.step?'active':''}" data-step="${esc(s.id)}">${i+1}. ${esc(s.title)}</button>`).join('')+'<p class="c-micro">点击只切换查阅；网页不会替你生成新词缀，也不会认定游戏里已完成前一步。</p>';
 $('#c-all-materials').innerHTML=[...new Set(route().steps.flatMap(x=>x.materials))].map(material).join(' ');$('#c-finishing').innerHTML=D.finish.map(([a,b])=>`<p><b>${esc(a)}</b>：${esc(b)}</p>`).join('');$('#c-citations').innerHTML='<p>'+S.sources.map(([a,b])=>url(b,a)).join(' · ')+'</p>';
 $('#c-bow-calc').hidden=st.slot!=='bow';$('#c-compare-example').innerHTML='<b>具体判断例：</b>'+esc(S.targets[st.slot].example);calcBow();calcRes();}
function render(reset){updating=true;const fin=document.getElementById('c-rune-link'),chk=document.getElementById('c-finish-check-link');if(fin)fin.href='runes.html?stage='+st.phase+'&slot='+st.slot+'#work';if(chk)chk.href='finish-check.html?stage='+st.phase;const r=rec();if(reset)$('#c-ready').checked=false;
 $('#c-phase').innerHTML=D.phases.map(p=>`<option value="${p.id}">${esc(S.stages[p.id])}</option>`).join('');$('#c-phase').value=st.phase;
 $('#c-slot').innerHTML=D.items.map(x=>`<option value="${x.id}">${esc(x.title)}</option>`).join('');$('#c-slot').value=st.slot;
 $('#c-advanced-bar').hidden=st.mode!=='advanced';$$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===st.mode)));
 const opts=item().routes[st.phase].options.filter(x=>!x.startsWith('early-'));$('#mode-advanced').disabled=!opts.length;$('#mode-advanced').title=opts.length?'':'作者未给本部位独立高级配方；目标和全部已有资料仍可查。';
 $('#c-route').innerHTML=opts.map(id=>`<option value="${id}">${esc(routes.get(id).title)}${D.routeWarnings[id]?'〔只读〕':''}</option>`).join('');$('#c-route').value=st.route;
 $('#c-step').innerHTML=route().steps.map((s,i)=>`<option value="${s.id}">${i+1}. ${esc(s.title)}</option>`).join('');$('#c-step').value=st.step; const hint=$('#c-advanced-hint');if(hint)hint.textContent=st.mode==='advanced'&&st.phase==='e01'?'现在浏览后续完整工艺，不是Early必须做到；可以随时切回普通加工。':'可直接查后面的步骤，不代表游戏已完成。';
 const so=stateOptions();if(!so.some(x=>x[0]===r.state))r.state='unknown';$('#c-item-state').innerHTML=so.map(([id,t])=>`<option value="${id}">${esc(t)}</option>`).join('');$('#c-item-state').value=r.state;
 $('#c-ilvl').value=typeof r.ilvl==='string'?r.ilvl:'';
 $('#c-resist-target').hidden=!(st.mode==='advanced'&&st.route==='amulet');$('#c-t1-resist').checked=!!r.t1Resist;
 if(st.mode==='basic')st.step=basicStep(r.state);actionRender();populateReferences();updating=false;
 window.__CRAFT_R19=window.__CRAFT_R13={state:()=>({...st,item:{...rec()},guard:guard()}),counts:{routes:D.routes.length,steps:D.routes.reduce((n,r)=>n+r.steps.length,0)},level:validLevel,requiredLevel};window.__CRAFT_R20=window.__CRAFT_R19;window.dispatchEvent(new CustomEvent('craft-context-change'));}
function calcBow(){const ids=['old-min','old-max','old-aps','new-min','new-max','new-aps'],vs=ids.map(k=>$('#c-'+k).value),out=$('#c-dps');if(vs.some(x=>x==='')){out.textContent='6个数字全部填写后比较；未知不按0。';return;}const a=vs.map(Number);if(a.some(x=>!Number.isFinite(x)||x<0)||a[2]<=0||a[5]<=0||a[1]<a[0]||a[4]<a[3]){out.textContent='请核对：伤害不能为负，最大值不小于最小值，每秒攻击次数大于0。';return;}let old=(a[0]+a[1])/2*a[2],now=(a[3]+a[4])/2*a[5];out.textContent=`武器物理部分：${old.toFixed(1)} → ${now.toFixed(1)}。`+(old>0?`变化 ${now>=old?'+':''}${((now/old-1)*100).toFixed(1)}%。`:'现用品为0，不计算百分比。')+'这不是冰射／狙击总DPS，也不单凭它判定值得继续投入。';}
function calcRes(){let v=$('#c-res-now').value,c=$('#c-res-cap').value,o=$('#c-res-result');if(v===''||c===''){o.textContent='填写实际面板后显示缺口。';return;}let n=Number(v),m=Number(c);if(!Number.isFinite(n)||!Number.isFinite(m)||m<0||m>100||n < -500||n>1000){o.textContent='请核对数字，上限为0–100。';return;}o.textContent=n<m?`这项还缺 ${+(m-n).toFixed(2)} 个百分点；从能补这一项的部位解决。`:`已达到填写的上限；其余抗性与地图减益另查。`;}
$('#c-phase').onchange=e=>{st.phase=e.target.value;if(st.mode==='advanced')st.route=advancedFor()||'early-'+st.slot;st.mode=st.route.startsWith('early-')?'basic':'advanced';st.step='ready';render(true);};
$('#c-slot').onchange=e=>{st.slot=e.target.value;st.route=st.mode==='advanced'?(advancedFor()||'early-'+st.slot):'early-'+st.slot;st.mode=st.route.startsWith('early-')?'basic':'advanced';st.step='ready';render(true);};
$('#c-route').onchange=e=>switchRoute(e.target.value);$('#c-step').onchange=e=>goStep(e.target.value);
$('#c-item-state').onchange=e=>{rec().state=e.target.value;clearFinishCounts();$('#c-ready').checked=false;if(st.mode==='basic')st.step=basicStep(e.target.value);actionRender();populateReferences();save();};
$('#c-ilvl').oninput=()=>{if(updating)return;rec().ilvl=$('#c-ilvl').value;$('#c-ready').checked=false;showStatus();save();};$('#c-ready').onchange=showStatus;
$('#c-t1-resist').onchange=e=>{rec().t1Resist=e.target.checked;$('#c-ready').checked=false;showStatus();save();};
['c-prefix-count','c-suffix-count','c-reserve-plan'].forEach(id=>$('#'+id).onchange=()=>{rec().prefixes=$('#c-prefix-count').value;rec().suffixes=$('#c-suffix-count').value;rec().reserve=$('#c-reserve-plan').value;$('#c-ready').checked=false;updateAffixText();showStatus();$('#c-target-body').innerHTML=targetHTML();save();});
function help(){const el=$('#c-recognition');el.hidden=!el.hidden;$('#c-help').setAttribute('aria-expanded',String(!el.hidden));}
$('#c-help').onclick=help;$('#c-help').setAttribute('aria-controls','c-recognition');$('#c-help').setAttribute('aria-expanded','false');
root.addEventListener('click',e=>{let b=e.target.closest('button');if(!b)return;
 if(b.dataset.finishJump&&rareSlots.has(st.slot)){st.mode='basic';st.route='early-'+st.slot;goStep(b.dataset.finishJump);return;}
 if(b.dataset.mode==='basic')switchRoute('early-'+st.slot);
 if(b.dataset.mode==='advanced'&&advancedFor())switchRoute(advancedFor());
 if(b.hasAttribute('data-open-advanced')&&advancedFor())switchRoute(advancedFor());
 if(b.dataset.next)goStep(b.dataset.next);
 if(b.dataset.step){goStep(b.dataset.step);$('.c-inspect').scrollIntoView({block:'start'});}
 if(b.hasAttribute('data-help-open')){if($('#c-recognition').hidden)help();$('#c-recognition').scrollIntoView({block:'nearest'});}
 if(b.hasAttribute('data-choose-state'))$('#c-item-state').focus();
 if(b.hasAttribute('data-open-reference')){$('#c-reference').open=true;$('#c-reference').scrollIntoView({block:'start'});}
 if(b.hasAttribute('data-compare')){$('#c-compare-details').open=true;$('#c-comparison').scrollIntoView({block:'nearest'});}
 if(b.hasAttribute('data-stop')&&route().steps.some(s=>s.id==='bad-roll')&&step().finishCheck){goStep('bad-roll');return;}
 if(b.hasAttribute('data-stop')){let x=$('#c-result-panel');x.hidden=false;x.innerHTML=`<h3>这一步先停，不追着救装备</h3><p>${esc(view().bad)}</p><p>${esc(S.targets[st.slot].example)}</p><p><a href="after-quests.html#routine">保留旧装备，回到刷图与下一轮目标 →</a></p>`;x.scrollIntoView({block:'nearest'});}
 if(b.dataset.material){const m=D.materials[b.dataset.material];if(m)openDialog(m.zh,`<p class="c-micro">${esc(m.en)}</p><h3>它做什么</h3><p>${esc(m.effect)}</p><h3>使用前确认</h3><p>${esc(m.check)}</p><p>${url(m.url,'查看来源（国际服数据简体展示）')}</p>`);}
});
$('#c-new-item').onclick=()=>{saved.items[st.slot]={ilvl:'',state:'unknown'};st.step='ready';['old-min','old-max','old-aps','new-min','new-max','new-aps','res-now'].forEach(x=>$('#c-'+x).value='');render(true);$('#c-ilvl').focus();};
$('#c-copy').onclick=async()=>{const v=view(),g=guard(),txt=[S.stages[st.phase]+' / '+item().title,'工艺：'+route().title,'作者本次起点：'+(requiredLevel()??'普通加工无统一75／80门槛')+(st.route==='amulet'&&rec().t1Resist?'（追最高阶抗性）':''),'物品等级：'+($('#c-ilvl').value||'未知'),'状态：'+$('#c-item-state').selectedOptions[0].textContent,...(step().finishCheck?['前后缀：'+($('#c-affix-result').textContent||'未知')]:[]),g.title+'。'+g.text,'操作前：'+v.before,'本次目标：'+S.targets[st.slot].want.join('；'),v.title,...v.actions,'应看到：'+v.expect,'符合：'+v.good,'不符合：'+v.bad,'不读取游戏，不保证结果。'].join('\n');try{if(!navigator.clipboard)throw Error('clipboard unavailable');await navigator.clipboard.writeText(txt);openDialog('已复制本步','<p>只复制这一步和它的前提，不把全部材料当成连续操作。</p>');}catch(_){openDialog('手动复制本步','<p>浏览器未允许自动复制，选中下面文字后按Ctrl+C。</p><textarea id="c-copy-text" aria-label="本步操作文字" readonly></textarea>');$('#c-copy-text').value=txt;$('#c-copy-text').select();}};
['old-min','old-max','old-aps','new-min','new-max','new-aps'].forEach(x=>$('#c-'+x).oninput=calcBow);$('#c-res-now').oninput=calcRes;$('#c-res-cap').oninput=calcRes;
let printOpen=[];window.addEventListener('beforeprint',()=>{printOpen=$$('.c-extra details').map(x=>[x,x.open]);$$('.c-extra details').forEach(x=>x.open=true);});window.addEventListener('afterprint',()=>printOpen.forEach(([x,b])=>x.open=b));window.addEventListener('hashchange',()=>{if(!updating)parseHash();});parseHash();
})();
