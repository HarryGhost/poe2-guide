'use strict';
(()=>{
const $=s=>document.querySelector(s),esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const stages=window.CATALOG||[],byId=id=>stages.find(x=>x.id===id),a=$('#compare-from'),b=$('#compare-to');if(!a||!b)return;
const params=new URLSearchParams(location.search);a.value=byId(params.get('from'))?params.get('from'):'e03';b.value=byId(params.get('to'))?params.get('to'):'e04';
function chain(s){return s.supports.map(x=>(x.active?'〔主动〕':'')+x.zh).join(' → ')||'未配置辅助'}
function section(t,s){return `<section class="card"><div class="card-head"><h2>${esc(t)}</h2></div><div class="card-body">${s}</div></section>`;}
function render(){const A=byId(a.value),B=byId(b.value),result=$('#compare-result');if(!A||!B)return;if(A.id===B.id){result.innerHTML='<div class="notice">选择了同一个配置，没有跨配置变化。</div>';return;}
let out=`<div class="notice ${A.readonly||B.readonly?'danger':''}"><b>${esc(A.label)} → ${esc(B.label)}</b>。${A.readonly||B.readonly?'包含06冲突快照：只读差异，不作为转换指令。':'这是两份记录的差异，不是逐步洗点或保证可以直接转换。'}</div><p><a class="btn" href="${A.file}">完整查看起点</a> <a class="btn" href="${B.file}">完整查看终点</a></p>`;
const mapA=new Map(A.skills.map(x=>[x.key,x])),mapB=new Map(B.skills.map(x=>[x.key,x]));let parts=[];for(const k of new Set([...mapA.keys(),...mapB.keys()])){const x=mapA.get(k),y=mapB.get(k);if(x&&y&&JSON.stringify(x.supports.map(s=>s.zh))===JSON.stringify(y.supports.map(s=>s.zh)))continue;parts.push(`<div class="diff-card"><h3>${esc((y||x).zh)} <span class="badge ${!x?'ok':!y?'warn':''}">${!x?'新增':!y?'移除':'辅助变化'}</span></h3><p class="small"><b>原：</b>${x?esc(chain(x)):'本配置没有'}</p><p class="small"><b>新：</b>${y?esc(chain(y)):'本配置移除'}</p></div>`);}
out+=section('技能与辅助变化',parts.length?'<div class="diff-grid">'+parts.join('')+'</div>':'<p>主技能与辅助名称组合相同。基于原始记录，不推断等级、品质和资源相同。</p>');
if(A.kind==='end'&&B.kind==='end'){
 const eqmap=s=>new Map(s.original.equipment.map(e=>[e.raw.inventory_id+':'+(e.raw.slot_x||0)+':'+(e.raw.slot_y||0),e]));const ea=eqmap(A),eb=eqmap(B);let eq=[];for(const k of new Set([...ea.keys(),...eb.keys()])){const x=ea.get(k),y=eb.get(k);if(x&&y&&x.translation===y.translation)continue;eq.push(`<div class="diff-card"><h3>${esc(k)}</h3><p class="small"><b>原：</b><br>${esc(x?.translation||'未填写').replace(/\n/g,'<br>')}</p><p class="small"><b>新：</b><br>${esc(y?.translation||'未填写').replace(/\n/g,'<br>')}</p></div>`)}out+=section('装备已导出词条变化',eq.length?'<div class="diff-grid">'+eq.join('')+'</div>':'<p>已导出的装备提示没有变化；未导出的词条/符文/品质不推断。</p>');
 const scope=s=>{const m={};for(const r of s.nodes){(m[r.scope]||(m[r.scope]=new Map())).set(r.id,r);}return m},sa=scope(A),sb=scope(B);let text='<p class="small muted">集合比较去重仅用于差异显示，原件没有删除重复项。节点换组会一边移出一边移入，不能相加当洗点费用。</p>';for(const sk of new Set([...Object.keys(sa),...Object.keys(sb)])){const x=sa[sk]||new Map(),y=sb[sk]||new Map();const rem=[...x].filter(([id])=>!y.has(id)).map(([,v])=>v),add=[...y].filter(([id])=>!x.has(id)).map(([,v])=>v);text+=`<details><summary>${esc(sk)}：移出 ${rem.length} / 移入 ${add.length}</summary><div class="detail"><p><b>移出：</b>${rem.map(v=>`${esc(v.zh)} <code>${esc(v.id)}</code>`).join('；')||'无'}</p><p><b>移入：</b>${add.map(v=>`${esc(v.zh)} <code>${esc(v.id)}</code>`).join('；')||'无'}</p></div></details>`;}out+=section('天赋分组差异',text);
}else out+=section('天赋与装备的边界','<p>剧情原件尚未取得完整节点连线；这里只比较已核对技能，不能据此生成准确洗点顺序。</p><p>请打开两页的整套参考装备、天赋条件和“下一阶段”说明。参考底材变化不是作者实装的逐件替换指令。</p>');
if(B.fallback)out+='<div class="notice warn">终点60+是延续42–59的明示方案，不冒充已读取的作者60+原版。</div>';
result.innerHTML=out;try{history.replaceState(null,'',`compare.html?from=${A.id}&to=${B.id}`)}catch(e){}
}
$('#compare-run').addEventListener('click',render);a.addEventListener('change',render);b.addEventListener('change',render);$('#compare-swap').addEventListener('click',()=>{const v=a.value;a.value=b.value;b.value=v;render()});render();window.__COMPARE_TEST={render};
})();
