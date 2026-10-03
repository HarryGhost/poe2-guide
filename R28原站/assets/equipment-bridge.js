/* Keep the selected whole-outfit target beside the original R13 step tool. */
(()=>{'use strict';const D=window.EQUIPMENT_GUIDE,root=document.getElementById('craft-app');if(!D||!root)return;
let wrap=document.createElement('section');wrap.className='eq-craft-bridge';wrap.id='eq-craft-context';wrap.setAttribute('aria-label','本件装备的目标与返回入口');root.prepend(wrap);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let queryTarget=new URLSearchParams(location.search).get('target');
function update(){const s=window.__CRAFT_R13?.state();if(!s)return;const p=D.phases.find(p=>p.id===s.phase);if(!p)return;
 const candidates=p.items.filter(i=>i.slot===s.slot),it=candidates.find(i=>i.uid===queryTarget)||candidates[0];if(!it)return;
 wrap.dataset.phase=p.id;wrap.dataset.uid=it.uid;
 wrap.innerHTML=`<a class="eq-back" href="equipment.html#${p.id}/${it.uid}">← 回全身目标 · ${esc(it.title)}</a><div><b>${esc(p.label)}：${esc(it.name)}</b><span>${esc(it.goal)}<small> ${esc(it.unique?'本工具只加工黄装替代，不制造此暗金。':'数值与完整底材在原专属页，返回后仍是这一件。')}</small></span></div>`;
 const more=document.createElement('div');more.className='r28-mini-progress';more.innerHTML=`词缀够用后：<a href="runes.html?stage=${p.id}&slot=${it.uid}#work">给这件做品质、开孔、镶嵌与首饰强化 →</a>`;wrap.append(more);
 window.__EQUIPMENT_BRIDGE={phase:p.id,uid:it.uid,slot:s.slot};}
window.addEventListener('craft-context-change',update);window.addEventListener('hashchange',()=>requestAnimationFrame(update));root.addEventListener('change',()=>requestAnimationFrame(update));update();
})();
