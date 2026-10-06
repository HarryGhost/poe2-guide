'use strict';
(()=>{
const PAGE=JSON.parse(document.getElementById('page-data').textContent),S=PAGE.stage;
const $=(q,r=document)=>r.querySelector(q),$$=(q,r=document)=>Array.from(r.querySelectorAll(q));
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const STORAGE='poe2-c-stage-workbook-r5';
let saved={};try{const x=JSON.parse(localStorage.getItem(STORAGE)||'{}');if(x&&typeof x==='object'&&!Array.isArray(x))saved=x;}catch(e){}
for(const k of ['keys','checks','stages'])if(!saved[k]||typeof saved[k]!=='object'||Array.isArray(saved[k]))saved[k]={};
function persist(){try{localStorage.setItem(STORAGE,JSON.stringify(saved));}catch(e){toast('当前浏览器不能保存本地记录；页面仍可阅读和操作。');}}
function toast(msg){const e=$('#toast');e.textContent=msg;e.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>{e.hidden=true},3500);}
let focusBefore=null;
function showDialog(id){const d=$('#'+id);if(!d)return;focusBefore=document.activeElement;if(!d.open){if(typeof d.showModal==='function')d.showModal();else d.setAttribute('open','');}setTimeout(()=>{(d.querySelector('input,textarea')||d.querySelector('button')||d).focus()},0);}
function closeDialog(id){const d=$('#'+id);if(!d)return;d.close?d.close():d.removeAttribute('open');if(focusBefore&&focusBefore.isConnected)focusBefore.focus();}
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>closeDialog(b.dataset.close)));
$$('dialog').forEach(d=>d.addEventListener('cancel',()=>{if(focusBefore&&focusBefore.isConnected)focusBefore.focus()}));
$('#print-btn').addEventListener('click',()=>window.print());
function density(){document.body.dataset.density=saved.density==='comfortable'?'comfortable':'compact';$('#density-toggle').textContent=saved.density==='comfortable'?'紧凑字号':'舒适字号';}
$('#density-toggle').addEventListener('click',()=>{saved.density=saved.density==='comfortable'?'compact':'comfortable';density();persist()});density();
$('#menu-toggle').addEventListener('click',()=>{const v=$('#sidebar').classList.toggle('open');$('#menu-toggle').setAttribute('aria-expanded',String(v))});
document.addEventListener('click',e=>{if(innerWidth<=700&&!e.target.closest('#sidebar')&&!e.target.closest('#menu-toggle')){$('#sidebar').classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false')}});
// Always available global search: local data, no API, no hidden progression.
const normalize=s=>String(s).toLocaleLowerCase().replace(/\s+/g,' ').trim();
function search(){const q=normalize($('#site-search').value),words=q.split(' ').filter(Boolean);let results=(window.SEARCH_INDEX||[]).filter(x=>!q||words.every(w=>normalize(x.title+' '+x.text).includes(w)));$('#search-count').textContent=q?`找到 ${results.length} 项，最多显示80项`:'输入关键词。下面是完整阶段入口。';if(!q)results=results.filter(x=>/^(l|e)\d{2}\.html$/.test(x.url));$('#search-results').innerHTML=results.slice(0,80).map(x=>`<a class="search-item" href="${esc(x.url)}"><b>${esc(x.title)}</b><p>${esc(x.text.slice(0,145))}${x.text.length>145?'…':''}</p></a>`).join('')||'<p class="muted">没有匹配内容。试试中文技能名、英文或节点ID。</p>';}
$('#search-open').addEventListener('click',()=>{showDialog('search-dialog');search();$('#site-search').focus()});$('#site-search').addEventListener('input',search);
document.addEventListener('keydown',e=>{if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!/input|textarea|select/i.test(e.target.tagName)&&!e.target.isContentEditable){e.preventDefault();$('#search-open').click();}});
// Read only tables still work without JS; search is an enhancement.
$$('[data-filter-table]').forEach(input=>{const target=document.getElementById(input.dataset.filterTable);function run(){const q=normalize(input.value);let n=0;$$('tbody tr',target).forEach(tr=>{tr.hidden=q&&!normalize(tr.textContent).includes(q);if(!tr.hidden)n++});const c=$(`[data-filter-count="${input.dataset.filterTable}"]`);if(c)c.textContent=`显示 ${n} 行`;}input.addEventListener('input',run);if(PAGE.id==='glossary')input.value=new URLSearchParams(location.search).get('q')||'';run();});
$$('[data-check]').forEach(c=>{c.checked=!!saved.checks[c.dataset.check];c.addEventListener('change',()=>{saved.checks[c.dataset.check]=c.checked;persist()})});
async function copy(text){try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw new Error('unavailable');await navigator.clipboard.writeText(text);toast('已复制。')}catch(e){$('#copy-text').value=text;showDialog('copy-dialog');$('#copy-text').focus();$('#copy-text').select();}}
// Expand target details for direct internal links; no inaccessible anchors inside collapsed blocks.
function revealAnchor(){let hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch(e){return;}if(!hash)return;const el=document.getElementById(hash);if(!el)return;if(el.tagName==='DETAILS')el.open=true;let p=el.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}setTimeout(()=>el.scrollIntoView({block:'start'}),70);}
window.addEventListener('hashchange',revealAnchor);revealAnchor();
if(!S){window.__GUIDE_TEST={page:PAGE.id,stage:null};return;}
let st=saved.stages[S.id];if(!st||typeof st!=='object'||Array.isArray(st))st={};saved.stages[S.id]=st;
if(!st.enabled||typeof st.enabled!=='object'||Array.isArray(st.enabled))st.enabled={};
if(!st.profiles||typeof st.profiles!=='object'||Array.isArray(st.profiles))st.profiles={};
if(!st.budget||typeof st.budget!=='object'||Array.isArray(st.budget))st.budget={};
function isEnabled(k){if(typeof st.enabled[k]==='boolean')return st.enabled[k];return !S.defaultDisabled.includes(k);}
function key(k){const sk=S.skills.find(x=>x.key===k);return typeof saved.keys[k]==='string'&&saved.keys[k].trim()?saved.keys[k]:sk?sk.keybind:'';}
function paintKeys(){$$('[data-key-label]').forEach(e=>e.textContent=key(e.dataset.keyLabel));}
function renderKeys(){const manual=S.skills.filter(s=>!['常驻','升华'].includes(s.keybind));$('#key-editor').innerHTML=manual.map(s=>`<label>${esc(s.zh)}<input type="text" maxlength="18" data-key-edit="${esc(s.key)}" value="${esc(key(s.key))}" aria-label="${esc(s.zh)}网页键位"></label>`).join('');$('#key-error').textContent='';}
if($('#keys-open'))$('#keys-open').addEventListener('click',()=>{renderKeys();showDialog('key-dialog')});
$('#key-save').addEventListener('click',()=>{const inputs=$$('[data-key-edit]');if(inputs.some(x=>!x.value.trim())){$('#key-error').textContent='按键不能为空。可写“未绑定”，但不要丢掉技能对应关系。';return;}const vals=inputs.map(x=>normalize(x.value));if(new Set(vals).size!==vals.length){$('#key-error').textContent='有两个技能使用相同键位；请确认并改为不同按键。';return;}inputs.forEach(x=>saved.keys[x.dataset.keyEdit]=x.value.trim());persist();paintKeys();closeDialog('key-dialog');toast('只更新网页提示，游戏按键不会改变。')});
$('#key-reset').addEventListener('click',()=>{S.skills.forEach(s=>delete saved.keys[s.key]);persist();renderKeys();paintKeys()});paintKeys();
$$('[data-skill-detail]').forEach(b=>b.addEventListener('click',()=>{const x=document.getElementById(b.dataset.skillDetail);x.hidden=!x.hidden;b.setAttribute('aria-expanded',String(!x.hidden));b.textContent=x.hidden?'＋':'−';}));
function paintEnabled(){S.skills.forEach(s=>{const row=$(`[data-skill="${s.key}"]`);if(!row)return;const en=isEnabled(s.key);row.classList.toggle('disabled',!en);const txt=$(`[data-skill-state="${s.key}"]`);if(txt)txt.textContent=!en?'已停用 · 原连接保留':s.optional?'可选工具':s.key==='mirage'||s.key==='deadeye'?'元技能内槽另配':'';const c=$(`[data-skill-enable="${s.key}"]`);if(c)c.checked=en;});}
$$('[data-skill-enable]').forEach(c=>c.addEventListener('change',()=>{st.enabled[c.dataset.skillEnable]=c.checked;persist();paintEnabled();renderAttrs();if(c.dataset.skillEnable==='pounce'&&c.checked)toast('启用巨狼猛扑需要额外护符/变形配置，当前整套参考不再完整。');}));paintEnabled();
$$('[data-copy]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.copy==='skills'){const lines=[`${S.label} / ${S.title}`,S.skills.map(s=>`${!isEnabled(s.key)?'〔已停用可选〕':''}[${key(s.key)}] ${s.zh}：${s.supports.map(x=>(x.active?'〔主动〕':'')+x.zh).join(' → ')||'未配置辅助'}`).join('\n'),'建议键位，仅作网页提示。'];copy(lines.join('\n'));}else{const c=$('.card-head.combat').parentElement;copy(`${S.label} / ${S.title}\n${$('.rotation-section',c)?.innerText||c.innerText}`)}}));
// Attribute model: per-attribute max(equipment max, all active max, cumulative supports), not total gear addition.
let profileIndex=Number.isInteger(st.profileIndex)&&st.profileIndex>=0&&st.profileIndex<S.profiles.length?st.profileIndex:0;
function pstate(){const p=S.profiles[profileIndex];if(!p)return null;let v=st.profiles[p.id];if(!v||typeof v!=='object'||Array.isArray(v))v={};st.profiles[p.id]=v;if(!v.edits||typeof v.edits!=='object'||Array.isArray(v.edits))v.edits={};if(!Array.isArray(v.extra))v.extra=[];return v;}
function getRows(){const p=S.profiles[profileIndex];if(!p)return [];const v=pstate();return p.rows.map((r,i)=>({...r,...(v.edits[i]&&typeof v.edits[i]==='object'?v.edits[i]:{}),idx:i})).concat(v.extra.map((r,i)=>({...r,idx:p.rows.length+i})));}
function validNumber(v,max=9999){if(v===null||v===undefined||String(v).trim()==='')return false;return Number.isFinite(Number(v))&&Number(v)>=0&&Number(v)<=max;}
function syncProfileUI(){
 const p=S.profiles[profileIndex];if(!p)return;
 const v=pstate(),edited=Object.keys(v.edits).length>0||v.extra.length>0;
 for(const sel of ['#profile-select','#gear-profile-select'])if($(sel))$(sel).value=String(profileIndex);
 $$('[data-profile-gear]').forEach(el=>el.hidden=Number(el.dataset.profileGear)!==profileIndex);
 if($('#profile-reference-name'))$('#profile-reference-name').textContent=p.statusLabel+(edited?' · 含你的录入':'');
 if($('#profile-gem-summary'))$('#profile-gem-summary').textContent=`核算基础宝石 ${p.gemlevel} 级；词缀增级另按实际需求核对`;
 const gear=p.rows.filter(r=>r.category.startsWith('装备')).slice(0,5).map(r=>r.label).join(' / ');
 if($('#profile-gear-summary'))$('#profile-gear-summary').textContent=gear;
 if($('#gear-profile-caption'))$('#gear-profile-caption').textContent=p.label+'。下面这套底材与上方三维数字同源；作者原始词条另行展开。';
 if($('#profile-edited-note'))$('#profile-edited-note').hidden=!edited;
 if($('#profile-caption'))$('#profile-caption').textContent=`${p.label}。${edited?'已修改需求值，当前按你的录入核算。':'按本参考全身装备、主动/内嵌技能及辅助合并核算。'}不是你的装备扫描，不要求这些数值全部从天赋取得。`;
 const rows=getRows();
 $$('[data-bound-req]').forEach(el=>{const [pi,ri,kind]=el.dataset.boundReq.split(':');if(Number(pi)!==profileIndex)return;const n=rows[Number(ri)]?.[kind];el.textContent=validNumber(n)&&Number.isInteger(Number(n))?String(n):'待核对';});
 $$('[data-gem-key]').forEach(el=>{
  const k=el.dataset.gemKey,sk=S.skills.find(q=>q.key===k);
  const match=p.rows.find(r=>r.skillKey===k&&r.category==='主动 / 常驻');
  const nested=p.rows.find(r=>r.skillKey===k&&r.category==='内嵌主动');
  if(k==='deadeye')el.textContent='升华技能'+(nested?' · 内嵌冰射 '+nested.level+'级':'');
  else if(match)el.textContent='参考宝石 '+match.level+'级'+(nested?' · 内嵌冰射 '+nested.level+'级':'');
  else el.textContent=sk?.optional?'可选：需求单独核对':'宝石等级按所选核算表';
 });
}
function changeProfile(value){const n=Number(value);if(!Number.isInteger(n)||n<0||n>=S.profiles.length)return;profileIndex=n;st.profileIndex=n;persist();renderAttrs();}
function calculateAttrs(){if(!S.profiles.length)return null;let rows=getRows().filter(r=>!r.skillKey||isEnabled(r.skillKey));let result={str:0,dex:0,int:0,valid:true,drivers:{}};if(S.kind==='level'&&isEnabled('pounce')&&S.skills.some(s=>s.key==='pounce')){result.valid=false;result.reason='启用了额外护符/变形工具，当前参考未覆盖该武器与技能需求。';}
for(const k of ['str','dex','int']){if(rows.some(r=>!validNumber(r[k])||!Number.isInteger(Number(r[k])))){result.valid=false;result.reason='有需求行为空、负数、小数或无效值；不能按0合计。';}result[k]=Math.max(0,...rows.filter(r=>validNumber(r[k])).map(r=>Number(r[k])));result.drivers[k]=rows.filter(r=>Number(r[k])===result[k]&&result[k]>0).map(r=>r.label).slice(0,3);}
for(const k of ['str','dex','int']){const e=$('#total-'+k);if(e)e.textContent=result.valid?String(result[k]):'待核对';}
const box=$('#attr-result');if(box){box.classList.toggle('error',!result.valid);box.textContent=result.valid?`当前参考面板总需求：力量 ${result.str} / 敏捷 ${result.dex} / 智慧 ${result.int}。来源：力量＝${result.drivers.str.join('、')||'无额外要求'}；敏捷＝${result.drivers.dex.join('、')||'无额外要求'}；智慧＝${result.drivers.int.join('、')||'无额外要求'}。`:result.reason;}
syncProfileUI();return result;}
function renderAttrs(){if(!S.profiles.length||!$('#attr-rows'))return;const p=S.profiles[profileIndex];$('#profile-select').value=String(profileIndex);$('#profile-caption').textContent=p.label+'。'+p.kind;$('#profile-notes').innerHTML=p.notes.map(t=>'<p class="small muted">'+esc(t)+'</p>').join('');
const rows=getRows();$('#attr-rows').innerHTML=rows.map(r=>{const disabled=r.skillKey&&!isEnabled(r.skillKey);return `<tr data-attr-row="${r.idx}" ${disabled?'style="opacity:.62"':''}><td>${esc(r.label)}${disabled?'<br><b>可选停用，不计入</b>':''}</td><td>${esc(r.category)}</td>${['str','dex','int'].map(k=>`<td><input class="numeric-input" type="number" min="0" max="9999" step="1" data-attr-index="${r.idx}" data-attr-kind="${k}" value="${esc(r[k])}" ${disabled?'disabled':''} aria-label="${esc(r.label)}${({str:'力量',dex:'敏捷',int:'智慧'})[k]}"></td>`).join('')}<td>${esc(r.note||'自定义需求，按游戏需求栏填写。')} ${r.url?`<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">依据 ↗</a>`:''}</td></tr>`}).join('');
$$('[data-attr-index]').forEach(inp=>inp.addEventListener('input',()=>{const idx=Number(inp.dataset.attrIndex),kind=inp.dataset.attrKind,v=pstate();if(idx<p.rows.length){if(!v.edits[idx])v.edits[idx]={};v.edits[idx][kind]=inp.value;}else v.extra[idx-p.rows.length][kind]=inp.value;inp.setAttribute('aria-invalid',String(!validNumber(inp.value)||!Number.isInteger(Number(inp.value))));calculateAttrs();persist();}));calculateAttrs();}
if($('#profile-select')){$('#profile-select').addEventListener('change',e=>changeProfile(e.target.value));if($('#gear-profile-select'))$('#gear-profile-select').addEventListener('change',e=>changeProfile(e.target.value));$('#attr-reset').addEventListener('click',()=>{delete st.profiles[S.profiles[profileIndex].id];persist();renderAttrs();toast('已恢复当前参考的需求数据，技能启用选择未改变。')});$('#attr-extra').addEventListener('click',()=>{const v=pstate();v.extra.push({label:'其他装备 / 技能需求 '+(v.extra.length+1),category:'自定义',str:'',dex:'',int:'',note:'填写新增装备/技能的需求；辅助额外需求应加到“辅助累计”原行。',url:''});persist();renderAttrs();$('#attr-rows tr:last-child input')?.focus()});renderAttrs();}
// Separate reservation currencies; life reservation is never silently counted as spirit.
function restoreBudget(){if(!$('#budget-rows'))return;for(const e of $$('[data-reserve-on]'))if(typeof st.budget[e.dataset.reserveOn+'-on']==='boolean')e.checked=st.budget[e.dataset.reserveOn+'-on'];for(const e of $$('[data-reserve-value]'))if(Object.hasOwn(st.budget,e.dataset.reserveValue))e.value=String(st.budget[e.dataset.reserveValue]);for(const id of ['spirit-total','spirit-other'])if(Object.hasOwn(st.budget,id))$('#'+id).value=String(st.budget[id]);$('#budget-confirmed').checked=st.budget.confirmed===true;}
function calcBudget(){if(!$('#budget-result'))return null;let spirit=0,life=0,valid=true;$$('[data-reserve-value]').forEach(e=>{const on=$(`[data-reserve-on="${e.dataset.reserveValue}"]`).checked;e.disabled=!on;if(!on)return;const max=e.dataset.reserveType==='life'?100:9999;const ok=validNumber(e.value,max);e.setAttribute('aria-invalid',String(!ok));if(!ok)valid=false;else if(e.dataset.reserveType==='life')life+=Number(e.value);else spirit+=Number(e.value);});const other=$('#spirit-other').value,total=$('#spirit-total').value;if(!validNumber(other)||!validNumber(total))valid=false;spirit+=validNumber(other)?Number(other):0;const confirmed=$('#budget-confirmed').checked,box=$('#budget-result');let msg='';if(!valid)msg='尚未填全：请填写精魂总量、各项最终保留；生命保留留空不能当0。';else if(life>=100)msg=`生命保留合计 ${life}%：不可按这组值直接开启，请先核对。`;else msg=`${confirmed?'已录入最终值':'仅按基础/当前录入值试算'}：精魂需 ${spirit}，现有 ${total}，${Number(total)>=spirit?'剩余 '+(Number(total)-spirit):'缺少 '+(spirit-Number(total))}；生命保留 ${life}%。${!confirmed?' 未确认最终值，不能据此认定整套已满足。':''}`;box.textContent=msg;box.classList.toggle('error',!valid||life>=100||(valid&&Number(total)<spirit));return {valid,spirit,life,total:validNumber(total)?Number(total):null,confirmed};}
if($('#budget-rows')){restoreBudget();$$('[data-reserve-value],[data-reserve-on],#spirit-total,#spirit-other,#budget-confirmed').forEach(e=>e.addEventListener('input',()=>{if(e.dataset.reserveValue)st.budget[e.dataset.reserveValue]=e.value;else if(e.dataset.reserveOn)st.budget[e.dataset.reserveOn+'-on']=e.checked;else if(e.id==='budget-confirmed')st.budget.confirmed=e.checked;else st.budget[e.id]=e.value;persist();calcBudget()}));calcBudget();}
if($('#node-search')){function nodes(){let n=0;const q=normalize($('#node-search').value),scope=$('#node-scope').value;$$('#node-records tbody tr').forEach(tr=>{const vals=$$('td',tr);tr.hidden=(scope!=='all'&&vals[1]?.textContent!==scope)||(q&&!normalize(tr.textContent).includes(q));if(!tr.hidden)n++});$('#node-count').textContent=`显示 ${n} / ${S.nodes.length} 条记录（不是点数）`;}$('#node-search').addEventListener('input',nodes);$('#node-scope').addEventListener('change',nodes);nodes();}
$$('[data-node-jump]').forEach(b=>b.addEventListener('click',()=>{const box=$('#node-records');if(!box)return;box.open=true;$('#node-search').value=b.dataset.nodeJump;$('#node-scope').value='all';$('#node-search').dispatchEvent(new Event('input'));box.scrollIntoView({block:'start',behavior:'smooth'});$('#node-search').focus({preventScroll:true});}));
window.__GUIDE_TEST={page:PAGE.id,stage:S.id,calculateAttrs,calcBudget,profileIndex:()=>profileIndex,enabled:isEnabled};
})();
