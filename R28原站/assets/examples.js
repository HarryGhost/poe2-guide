'use strict';
(()=>{
 const $=(s)=>document.querySelector(s),$$=(s)=>Array.from(document.querySelectorAll(s));
 const cases=$$('[data-case]'),validIds=cases.map(e=>e.id);
 let selected=validIds[0];
 function apply(){
  let hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch(e){}
  if(validIds.includes(hash))selected=hash;
  cases.forEach(p=>p.hidden=p.id!==selected);
  $$('.case-nav a').forEach(a=>{const on=a.hash==='#'+selected;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
 }
 window.addEventListener('hashchange',apply);apply();
 function read(key){
  const vals={};
  for(const f of ['min','max','aps']){
   const el=$(`[data-bow="${key}"][data-field="${f}"]`),s=el.value.trim();
   if(!s)return {valid:false,reason:'未填完整'};
   const n=Number(s);if(!Number.isFinite(n)||n<0||(f==='aps'&&n<=0)||n>1e9){el.setAttribute('aria-invalid','true');return {valid:false,reason:'请填写有效的非负伤害与大于0的攻速'};}
   el.removeAttribute('aria-invalid');vals[f]=n;
  }
  if(vals.max<vals.min)return {valid:false,reason:'最大伤害不能小于最小伤害'};
  return {valid:true,average:(vals.min+vals.max)/2,rate:(vals.min+vals.max)/2*vals.aps};
 }
 const fmt=n=>Number(n.toFixed(2)).toLocaleString('zh-CN');
 function math(){
  const a=read('a'),b=read('b');
  for(const [k,r] of [['a',a],['b',b]])$(`#bow-${k}-result`).textContent=r.valid?`单次平均物理 ${fmt(r.average)}；每秒物理面板量 ${fmt(r.rate)}`:r.reason;
  let t='请补齐两把弓的有效面板数据；空白不会按0计算。';
  if(a.valid&&b.valid){
   const delta=b.rate-a.rate,pct=a.rate>0?`（${delta>=0?'+':''}${fmt(delta/a.rate*100)}%）`:'（现用值为0，不算百分比）';
   t=`备用弓的每秒物理面板量比现用弓 ${delta>=0?'高':'低'} ${fmt(Math.abs(delta))} ${pct}；单次平均物理 ${b.average===a.average?'相同':b.average>a.average?'较高':'较低'}。这只比较物理面板，不构成完整输出或换装结论。`;
  }
  $('#bow-math-result').textContent=t;return {a,b};
 }
 $$('[data-bow]').forEach(x=>x.addEventListener('input',math));
 $('#bow-math-demo').addEventListener('click',()=>{for(const [k,vals] of Object.entries({a:{min:100,max:200,aps:1.2},b:{min:90,max:190,aps:1.4}})){for(const [f,v] of Object.entries(vals))$(`[data-bow="${k}"][data-field="${f}"]`).value=v;}math();});
 $('#bow-math-clear').addEventListener('click',()=>{$$('[data-bow]').forEach(e=>{e.value='';e.removeAttribute('aria-invalid')});math();});
 let printOpen=[];
 window.addEventListener('beforeprint',()=>{printOpen=$$('details').map(d=>[d,d.open]);cases.forEach(c=>c.hidden=false);$$('details').forEach(d=>d.open=true)});
 window.addEventListener('afterprint',()=>{apply();printOpen.forEach(([d,o])=>d.open=o)});
 math();window.__CRAFT_EXAMPLE_TEST={math,selected:()=>selected};
})();
