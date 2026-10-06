// R44 is a display-only localization layer. Capture data, evidence, IDs,
// original build files and every filter remain byte-for-byte unchanged.
const L44=window.FUBGUN_LOCALIZATION44;
const N44=L44.names;
const escRE44=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const lower44=Object.fromEntries(Object.entries(N44).map(([a,b])=>[a.toLowerCase(),b]));
const re44=new RegExp('(?<![A-Za-z0-9_])(?:'+Object.keys(N44).sort((a,b)=>b.length-a.length).map(escRE44).join('|')+')(?![A-Za-z0-9_])','gi');
function cn44(input){
 let s=String(input??''); if(L44.sentences[s])s=L44.sentences[s];s=s.replace('请按完整文件名选择，不要选带 GoldFix、Bases_Shards 或 Materials 的旧派生版。','请从本页下载原版，不要混用历史金币修正或补材料派生版。');
 s=s.replace(/[’‘]/g,"'");
 for(let i=0;i<2;i++)s=s.replace(re44,x=>lower44[x.toLowerCase()]||x);
 for(const [a,b] of Object.entries(L44.textAliases))s=s.split(a).join(b);
 return s.replace(/\bLv\.?\s*(\d+)/g,'$1级').replace(/\bIII\b/g,'Ⅲ').replace(/\bII\b/g,'Ⅱ').replace(/\bIV\b/g,'Ⅳ').replace(/\bI\b/g,'Ⅰ').replace(/物品等级(\d)/g,'物品等级 $1').replace(/\bilvl(\d+)/g,'物品等级 $1').replace(/\.构筑/g,'构筑文件').replace(/两组共用\s*\/\s*两组共用/g,'两组共用');
}
function r44IsOriginal(el){return !!el?.closest('[data-r44-original],pre,.r43-rawparagraph,.r43-node-ids,script,style');}
function r44Translate(root){
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const todo=[];let n;
 while(n=w.nextNode())if(n.parentElement&&!r44IsOriginal(n.parentElement)&&n.textContent.trim())todo.push(n);
 for(const t of todo)t.textContent=cn44(t.textContent);
 root.querySelectorAll?.('[title],[placeholder],[aria-label],img[alt]').forEach(e=>{if(r44IsOriginal(e))return;for(const k of ['title','placeholder','aria-label','alt'])if(e.hasAttribute(k))e.setAttribute(k,cn44(e.getAttribute(k)));});
}
function r44HTML(s,prep){const t=document.createElement('template');t.innerHTML=s;prep?.(t.content);r44Translate(t.content);return t.innerHTML;}
const _r44originals=r43Originals,_r44card=r43Card,_r44jewelcard=r43JewelCard,_r44prose=r43Prose,_r44tree=r43Tree,_r44tools=tools,_r44audit=r43Audit;
r43Originals=function(it){return _r44originals(it).replace('<pre>','<pre data-r44-original>');};
r43Prose=function(b,section){return _r44prose(b,section).replace('class="r43-proof"','class="r43-proof r44-source-prose"');};
r43Kind=function(m){if(m.tier_label){const x=m.tier_label.match(/^([PS])(\d+)$/);if(x)return (x[1]==='P'?'前缀':'后缀')+'·'+x[2]+'阶';}return m.kind==='implicit_styled'?'固有样式':m.text.startsWith('Allocates ')?'涂膏／授予':'面板';};
r43GemName=function(n){return cn44(C43.skillTranslations[n]||n).replace(/\s+([ⅠⅡⅢⅣ])/g,' $1');};
r43Panel=function(panel,css=''){return `<ul class="r43-mods ${css}">${panel.modifiers.map((m,i)=>`<li data-r43-mod="${i}"><span class="r43-mod-kind">${esc(r43Kind(m))}</span><span>${esc(cn44(L44.modifiers[m.text]||m.zh||m.text))}</span></li>`).join('')}</ul>`;};
r43Card=function(it,b,isolated=false){return r44HTML(_r44card(it,b,isolated),root=>{
 root.querySelector('header h2').textContent=cn44(it.name);
 root.querySelector('header .r43-zhname')?.remove();
 // The raw source ID remains within the evidence layer, never translated.
 const ev=root.querySelector('.r43-proof');if(ev){const p=document.createElement('p');p.dataset.r44Original='true';p.className='r44-original-name';p.textContent=it.name;ev.insertBefore(p,ev.children[1]);}
});};
r43JewelCard=function(j,b){return r44HTML(_r44jewelcard(j,b),root=>{
 root.querySelector('header h2').textContent=cn44(j.name);root.querySelector('.r43-zhname')?.remove();
 root.querySelector('.r43-binding b').textContent='珠宝孔绑定状态';
 const ev=root.querySelector('.r43-proof');if(ev){const p=document.createElement('p');p.dataset.r44Original='true';p.className='r44-original-name';p.textContent=j.name+' · '+j.node_id;ev.insertBefore(p,ev.children[1]);}
});};
r43BuildTabs=function(route='gear',extra={}){return `<nav class="r43-builds" aria-label="选择构筑阶段">${C43.builds.map(b=>routeLink(route,esc(cn44(b.name))+(b.stage==='e06'?'<small>只读</small>':''),'r43-build '+(state.stage===b.stage?'is-active':'')+(b.stage==='e06'?' separate':''),{stage:b.stage,...extra})).join('')}</nav>`;};
labelStage=function(p){return cn44(C43.builds.find(b=>b.stage===p.id)?.name||p.label);};
r43Choices=function(v){return `<div class="r43-panel"><h2>${esc(cn44(v.name))} · 作者保存的已选项</h2><p>${v.keystone_selections.length} 条已选记录。节点和选项直接用中文查看，原名与编号放在折叠证据里。</p><p>这是作者当前保存的选择，不是本站备料建议。全部候选、父节点完整效果和解锁条件仍按原采集的已知边界处理。</p></div><label class="r43-search">查节点或选项<input id="r43-node-query" type="search" placeholder="例如：森林、预兆、精华、阿曼娜姆"></label><div class="r43-atlas-rows">${v.keystone_selections.map(x=>{
 const parent=cn44(N44[x.node_name]||x.zhName||x.node_name),choice=cn44(L44.choices[x.author_selected.name]||x.zhChoice||x.author_selected.selection_description||x.author_selected.name);
 return `<article class="r43-node" data-r43-node="${esc((parent+' '+choice+' '+x.node_name+' '+x.author_selected.name+' '+x.groups.join(' ')).toLowerCase())}"><div><small>${esc(cn44(x.groups.join(' / ')||'源记录'))}</small><h3>${esc(parent)}</h3><details class="r43-proof r44-node-proof"><summary>原名与选择证据</summary><div data-r44-original><p>${esc(x.node_name)}</p><p>${esc(x.author_selected.name)}</p><p>${esc(x.author_selected.selection_description)}</p><code>${esc(x.node_id)}</code></div></details></div><div><span class="r43-label">作者已选</span><b>${esc(choice)}</b></div></article>`;
 }).join('')}</div><p class="r43-no-matches" hidden>没有匹配项。清空搜索可显示该方案所有已选节点。</p>${r43EvidenceLink('atlas.json','原始选项绑定记录')}`;};
// Preserve the actual original image. Chinese names sit in the priority list;
// do not draw fake translated coordinates or remove original-tree evidence.
r43Tree=function(b){return r44HTML(_r44tree(b),root=>{
 const f=root.querySelector('figure.r43-tree');if(f){const d=document.createElement('details');d.className='r43-proof r44-tree-proof';const s=document.createElement('summary');s.textContent='查看作者加点原图（原图不改写；可放大）';d.append(s);f.replaceWith(d);d.append(f);}
 root.querySelectorAll('.r43-node-ids').forEach(e=>e.dataset.r44Original='true');
});};
function namesPage44(){const checked=L44.sources.filter(x=>x.checked==='2026-10-05'&&x.category!=='网站构筑／刷法中文标签');return heading('资料 / 中文名称','中文名称与来源','装备、技能、材料、人物天赋和异界节点统一用中文阅读。')+
 `<div class="r43-panel"><p>${esc(L44.boundary)}</p><p>构筑阶段和七套刷法的中文标题是本网站的阅读标签，不冒称游戏物品名称。范围、数值、配方、武器组绑定与只读限制没有随翻译改动。</p></div><section class="r43-section"><h2>名称核对表</h2><p>本轮直接核对的专名在下面列出。原文和出处默认折叠，需要核查时再展开。</p><div class="r44-name-grid">${checked.map(x=>`<article class="r43-panel"><h3>${esc(x.zh)}</h3><small>${esc(x.category)}</small><details class="r43-proof"><summary>原名与来源</summary><div data-r44-original><p>${esc(x.en)}</p>${safeLink(x.source,'查看简体数据条目')}</div><p>${esc(x.status)}</p></details></article>`).join('')}</div></section><section class="r43-section"><h2>原始文件不翻译</h2><p>过滤器、原构筑、截图、原始采集记录和历史文件保持原字节。英文只用于原始证据与程序标识，不要求读者在正文辨认英文。</p><a class="btn" href="R44_中文名称与来源说明.md">查看名称说明</a></section>`+footer();}
tools=function(k,p){return k==='names'?namesPage44():_r44tools(k,p);};
footer=function(){return `<footer class="footer"><span>冰霜射击攻略 · R44 中文阅读版</span><div>${q42Link('tools/names','中文名称与来源')} · ${q42Link('tools/filters','四份未修改的原版过滤器')}</div></footer>`;};
const _search44=searchData;
let searchIndex44=null;
function makeSearch44(){let xs=[];for(const b of C43.builds){const title=cn44(b.name);xs.push({title,text:'当前构筑的全身装备',route:'gear',params:{stage:b.stage},query:b.name});
 for(const it of b.equipment)xs.push({title:cn44(it.name),text:title+' · 完整面板与镶嵌',route:'item/'+it.uid,params:{stage:b.stage,tab:'target'},query:it.name+' '+cn44(it.panel.modifiers.map(m=>L44.modifiers[m.text]||m.zh||m.text).join(' '))+' '+it.socketed_items.map(s=>s.name+' '+cn44(s.name)).join(' ')});
 for(const j of b.jewels)xs.push({title:cn44(j.name),text:title+' · 珠宝展示 '+j.display_order,route:'jewels',params:{stage:b.stage},query:j.name+' '+cn44(j.panel.modifiers.map(m=>L44.modifiers[m.text]||m.zh||m.text).join(' '))});
 for(const p of b.treePriorities)xs.push({title:cn44(p.name),text:title+' · 人物天赋优先列表',route:'character',params:{stage:b.stage,tab:'tree'},query:p.name});
 }
 for(const v of C43.atlas){for(const n of v.keystone_selections)xs.push({title:cn44(N44[n.node_name]||n.zhName||n.node_name),text:cn44(v.name)+' · '+cn44(L44.choices[n.author_selected.name]||n.zhChoice),route:'atlas/'+v.id,params:{tab:'choices'},query:n.node_name+' '+n.author_selected.name});for(const master of v.masters)for(const o of master.candidate_options)xs.push({title:cn44(o.name),text:cn44(master.name)+' · '+(o.author_selected?'作者已选':'未选候选'),route:'atlas/'+v.id,params:{tab:'masters'},query:o.name+' '+cn44((o.zhEffects||o.effects).join(' '))});}
 return xs;}
searchData=function(q){if(!searchIndex44)searchIndex44=makeSearch44();const w=String(q||'').toLowerCase().trim().split(/\s+/).filter(Boolean);let xs=w.length?searchIndex44.filter(x=>w.every(s=>(x.title+' '+x.text+' '+x.query).toLowerCase().includes(s))):searchIndex44.filter(x=>x.params.stage===state.stage).slice(0,6);xs.sort((a,b)=>(b.params.stage===state.stage)-(a.params.stage===state.stage));const legacy=_search44(q).map(x=>({...x,title:cn44(x.title),text:cn44(x.text)}));return [...xs,...legacy].filter((x,i,a)=>a.findIndex(y=>y.title===x.title&&y.text===x.text&&y.route===x.route)===i).slice(0,24);};

// Difference text remains exact evidence rather than a wall of English in the reading page.
r43Audit=function(){return r44HTML(_r44audit(),root=>{const sec=root.querySelector('section.r43-section');if(sec){const table=sec.querySelector('table');if(table){const host=table.closest('.table-wrap')||table;const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent='展开六件装备的新旧保存原文（仅作核对）';d.append(su);host.replaceWith(d);d.append(host);host.dataset.r44Original='true';}}});};
coverage=function(){return r43Audit();};
// Keep real filenames and checksums, but move them into a fold, never rename file bytes.
const _tools44withNames=tools;
tools=function(k,p){if(k==='capture-audit')return r43Audit();return _tools44withNames(k,p);};


function buildDownloads44(){return heading('原件下载','六份人物构筑原件','中文名称用于选择；下载的原文件保持不变。')+`<div class="panel">${D.branches.map((b,i)=>`<div class="source-row"><div><strong>${esc(cn44(C43.builds[i]?.name||b.label))}${i===5?' · 只读':''}</strong><details class="r43-proof"><summary>查看原文件名</summary><p data-r44-original>${esc(b.sourceFile)}</p></details></div>${b.downloadData?`<a class="btn" href="${b.downloadData}" download="${esc(b.download.split('/').pop())}">${b.ascendancyConflict?'下载只读原件':'下载原件'}</a>`:'<span class="tag gold">冲突原件保留于完整包</span>'}</div>`).join('')}</div>`+footer();}
L44.sentences['一次只启用一份。网站不会替你切换游戏里正在用的过滤器。请按完整文件名选择，不要选带 GoldFix、Bases_Shards 或 Materials 的旧派生版。']='一次只启用一份。网站不会替你切换游戏里正在用的过滤器。请从本页下载原版，不要混用历史金币修正或补材料派生版。';
const _tools44complete=tools;
tools=function(k,p){if(k==='builds')return buildDownloads44();return _tools44complete(k,p);};
const _fgRule44=fgRuleResults;
fgRuleResults=function(){const t=document.createElement('template');t.innerHTML=_fgRule44();t.content.querySelectorAll('.fg-card').forEach(card=>{
 const title=card.querySelector('h3');if(title&&/[A-Za-z]{3,}/.test(cn44(title.textContent))){const original=title.textContent;title.textContent='原版筛选规则 · 条件见下方';const d=card.querySelector('details');if(d){const p=document.createElement('p');p.dataset.r44Original='true';p.textContent=original;d.insertBefore(p,d.children[1]);}}
 // Unknown rule sample labels are raw match examples, not invented Chinese names.
 card.querySelectorAll('.fg-swatch,.fg-label').forEach(el=>{if(/[A-Za-z]{3,}/.test(cn44(el.textContent))){el.dataset.r44Original='true';const d=document.createElement('details');d.className='r43-proof';const u=document.createElement('summary');u.textContent='原规则匹配样例（保留原名）';d.append(u);el.replaceWith(d);d.append(el);}});
 });return r44HTML(t.innerHTML);};
const _fgRefresh44=fgRefresh;fgRefresh=function(){_fgRefresh44();r44Translate(document.querySelector('#fg-rules')||document.body);};

const _render44=render;
render=function(){const result=_render44();
 // Keep source passages byte-exact while localizing the visible reading surface.
 document.querySelectorAll('.r43-rawparagraph, .r43-proof pre, .r43-node-ids').forEach(e=>e.dataset.r44Original='true');
 document.querySelectorAll('.r43-proof').forEach(d=>{const s=d.querySelector(':scope > summary');if(s&&/原始节点记录/.test(s.textContent))for(const x of d.children)if(x!==s)x.dataset.r44Original='true';});
 if(current.section==='tools'&&current.slot==='filters'){
 document.querySelectorAll('#main-content code').forEach(e=>{if(e.closest('details'))return;const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent=e.textContent.includes('.filter')?'核对原版文件名':'核对文件校验值';d.append(su);e.replaceWith(d);d.append(e);e.dataset.r44Original='true';});
 }
 const unresolved=/\b(?:prolif|Opulent|Stardrinker|Origin of the fall|The last to fall|End of the Circle|All that glitters|reflective waters|almost paradise|a good fellow|Fallen skies|Runeseeker's Call)\b/i;
 const handled=new Set();document.querySelectorAll('#main-content p,#main-content tr,#main-content li').forEach(el=>{if(el.closest('details')||!unresolved.test(el.textContent))return;const target=el.tagName==='TR'?(el.closest('.table-scroll,.table-wrap')||el.closest('table')):el;if(!target||handled.has(target)||target.closest('details'))return;handled.add(target);if(target.tagName==='LI'){const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent='特殊符文原文（国服名称待核）';const body=document.createElement('div');body.dataset.r44Original='true';while(target.firstChild)body.append(target.firstChild);d.append(su,body);target.append(d);return;}const d=document.createElement('details');d.className='r43-proof r44-unverified-names';const su=document.createElement('summary');su.textContent='作者特殊符文／事件原清单（国服名称待核，不擅自意译）';d.append(su);target.replaceWith(d);target.dataset.r44Original='true';d.append(target);});
 document.querySelectorAll('#main-content p').forEach(el=>{if(el.closest('details'))return;if(/中文主体与历史记录：/.test(el.textContent)){const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent='历史来源文件与读取时间';d.append(su);el.replaceWith(d);el.dataset.r44Original='true';d.append(el);}});
 document.querySelectorAll('#main-content pre').forEach(el=>{if(el.closest('details')&&!el.classList.contains('fg-raw'))return;const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent='查看原始规则／数据（原文不改）';d.append(su);el.replaceWith(d);el.dataset.r44Original='true';d.append(el);});
 document.querySelectorAll('#main-content .c41-hash').forEach(el=>{if(el.closest('details'))return;const d=document.createElement('details');d.className='r43-proof';const su=document.createElement('summary');su.textContent='核对原文件校验值';d.append(su);el.replaceWith(d);el.dataset.r44Original='true';d.append(el);});
 r44Translate(document.body);
 document.querySelectorAll('.sidebar .version,.sidebar .sidebar-version').forEach(e=>{e.textContent='0.5.5 · R44 中文阅读';});
 // Legacy bilingual summary cards duplicated the same localized name.
 document.querySelectorAll('.r43-equip header .r43-zhname').forEach(e=>e.remove());
 document.querySelectorAll('.side-bottom').forEach(e=>{e.textContent='0.5.5 · R44 中文阅读';});
 const aside=document.querySelector('.sidebar .sidenote');if(aside)aside.textContent='完整装备 · 中文阅读';
 document.querySelectorAll('.sidebar small,.sidebar .status,.sidebar .version-tag').forEach(e=>{if(/R43/.test(e.textContent))e.textContent=e.textContent.replace('R43','R44').replace('原页采集核对','中文阅读');});
 document.title='冰霜射击攻略 · R44';
 document.documentElement.dataset.zhReady='true';return result;
};
// Searches update their own dialog without a full route render.
document.addEventListener('input',e=>{if(e.target.closest('#search-dialog'))queueMicrotask(()=>r44Translate(document.getElementById('search-dialog')));});
window.R44={cn:cn44,search:searchData,localization:L44,translate:r44Translate};
