/* All content is static HTML; JS only focuses one stage/slot, never unlocks content. */
(()=>{'use strict';
const root=document.getElementById('early-workbook');if(!root)return;
const expanded=root.dataset.expanded==='true';
const panels=[...root.querySelectorAll('[data-stage-panel]')];
const items=[...root.querySelectorAll('[data-early-item]')];
const stageLinks=[...document.querySelectorAll('[data-craft-stage]')];
const itemLinks=[...document.querySelectorAll('[data-early-choice]')];
let currentStage='early',currentItem='bow';
const legacy=['bow-noncrit','bow-crit','quiver-standard','quiver-advanced','amulet','helmet-stable','helmet-random','emerald','craft-basics','craft-materials','craft-other','craft-extras','craft-coverage'];
function sync(){
 panels.forEach(p=>p.hidden=!expanded&&p.dataset.stagePanel!==currentStage);
 items.forEach(i=>i.hidden=!expanded&&i.dataset.earlyItem!==currentItem);
 stageLinks.forEach(a=>{const yes=a.dataset.craftStage===currentStage;a.classList.toggle('active',yes);if(yes)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')});
 itemLinks.forEach(a=>{const yes=a.dataset.earlyChoice===currentItem;a.classList.toggle('active',yes);if(yes)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')});
}
function resolve(){
 let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
 if(!id){currentStage='early';currentItem='bow';sync();return;}
 if(legacy.includes(id)||id.startsWith('mat-')){
   location.replace('craft-advanced.html#'+encodeURIComponent(id));return;
 }
 if(id.startsWith('stage-')&&panels.some(p=>p.dataset.stagePanel===id.slice(6)))currentStage=id.slice(6);
 if(id.startsWith('early-')&&items.some(p=>p.dataset.earlyItem===id.slice(6))){currentItem=id.slice(6);currentStage='early';}
 sync();
}
stageLinks.forEach(a=>a.addEventListener('click',()=>{currentStage=a.dataset.craftStage;sync();}));
itemLinks.forEach(a=>a.addEventListener('click',()=>{currentStage='early';currentItem=a.dataset.earlyChoice;sync();}));
window.addEventListener('hashchange',resolve);resolve();
const prior=new Map();
window.addEventListener('beforeprint',()=>{panels.forEach(p=>p.hidden=false);items.forEach(i=>i.hidden=false);document.querySelectorAll('details').forEach(d=>{prior.set(d,d.open);d.open=true;})});
window.addEventListener('afterprint',()=>{prior.forEach((v,d)=>d.open=v);prior.clear();sync();});
window.__EARLY_CRAFT={get stage(){return currentStage},get item(){return currentItem},stages:panels.map(p=>p.dataset.stagePanel),items:items.map(i=>i.dataset.earlyItem),expanded};
})();
