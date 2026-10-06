/* Fubgun bundle state only: never modifies game, source website or build files. */
(()=>{'use strict';function init(){const D=window.FUBGUN_ATLAS||window.FUBGUN_ATLAS_R24;if(!D||!document.querySelector('.f24-area'))return;
 const KEY='poe2-fubgun-atlas-r24',vs=new Map(D.variants.map(v=>[v.id,v]));let state={variant:'',checks:{}};
 try{const v=JSON.parse(localStorage.getItem(KEY)||'null');if(v&&typeof v==='object'){state.variant=vs.has(v.variant)?v.variant:'';state.checks=v.checks&&typeof v.checks==='object'?v.checks:{}}}catch(_){}
 const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(state))}catch(_){}};
 function render(){const v=vs.get(state.variant),name=v?v.name:'尚未选择';
 document.querySelectorAll('[data-f24-select]').forEach(s=>s.value=state.variant);
 document.querySelectorAll('[data-f24-name]').forEach(el=>el.textContent=name);
 document.querySelectorAll('[data-f24-status]').forEach(el=>el.textContent=v?`网页当前核对：${v.name}。${v.status}。本地可看原图；悬浮文字仍以原站为准。勾选只记核对进度。`:'尚未选方案。先看完整清单；没有预设必须主刷的玩法。');
 document.querySelectorAll('[data-f24-pick]').forEach(b=>{const yes=b.dataset.f24Pick===state.variant;b.setAttribute('aria-pressed',String(yes));const c=b.closest('.f24-variant');if(c)c.classList.toggle('is-selected',yes);b.textContent=yes?'本轮已选 · '+vs.get(b.dataset.f24Pick).name:'选择 '+vs.get(b.dataset.f24Pick).name});
 const checks=state.checks[state.variant]||{};document.querySelectorAll('[data-f24-check]').forEach(c=>{c.checked=!!checks[c.dataset.f24Check];c.disabled=!state.variant});
 document.querySelectorAll('[data-f24-progress]').forEach(el=>{const n=Object.values(checks).filter(x=>x===true).length;el.textContent=state.variant?`${name}：已勾选 ${n}/5 项。只记录你的核对进度，不证明游戏适配已通过。`:'先选择本轮方案再记录；全部说明仍可直接阅读。'});
 }
 function choose(id){state.variant=vs.has(id)?id:'';save();render();window.dispatchEvent(new CustomEvent('fubgun:variant',{detail:{id:state.variant}}))}
 window.addEventListener('fubgun:select',e=>{if(e.detail&&vs.has(e.detail.id)&&state.variant!==e.detail.id)choose(e.detail.id)});
 document.querySelectorAll('[data-f24-select]').forEach(s=>s.addEventListener('change',()=>choose(s.value)));
 document.querySelectorAll('[data-f24-pick]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.f24Pick)));
 document.querySelectorAll('[data-f24-check]').forEach(c=>c.addEventListener('change',()=>{if(!state.variant)return;if(!state.checks[state.variant])state.checks[state.variant]={};state.checks[state.variant][c.dataset.f24Check]=c.checked;save();render()}));
 document.querySelectorAll('[data-f24-clear]').forEach(b=>b.addEventListener('click',()=>{if(state.variant)delete state.checks[state.variant];save();render()}));
 window.addEventListener('storage',e=>{if(e.key===KEY){try{const v=JSON.parse(e.newValue||'null');state=v&&typeof v==='object'?{variant:vs.has(v.variant)?v.variant:'',checks:v.checks||{}}:{variant:'',checks:{}};render()}catch(_){}}});render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
