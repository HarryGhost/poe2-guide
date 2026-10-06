/* One scheme drives the image, master group and setup; no changes to game data. */
(()=>{'use strict';function boot(){
 const root=document.querySelector('[data-r26-workspace]');if(!root)return;
 const tabs=[...root.querySelectorAll('[data-r26-tab]')];
 let panel=new URLSearchParams(location.search).get('panel')||root.dataset.r26Panel||'masters';
 if(!['masters','setup','gems'].includes(panel))panel='masters';
 function showPanel(key,focus=false){panel=key;tabs.forEach(b=>{let yes=b.dataset.r26Tab===key;b.setAttribute('aria-selected',String(yes));b.tabIndex=yes?0:-1;if(yes&&focus)b.focus();});root.querySelectorAll('[role=tabpanel]').forEach(e=>e.hidden=e.id!=='r26-pane-'+key);}
 tabs.forEach((b,i)=>{b.addEventListener('click',()=>showPanel(b.dataset.r26Tab));b.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();let n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;showPanel(tabs[n].dataset.r26Tab,true);}});});
 function select(id){if(!root.querySelector('[data-ag-pick="'+CSS.escape(id)+'"]'))return;root.querySelectorAll('[data-r26-bundle]').forEach(e=>{e.hidden=e.dataset.r26Bundle!==id;if(!e.hidden&&!e.dataset.r26Seen){let first=e.querySelector('.r26-slot');if(first)first.open=true;e.dataset.r26Seen='true';}});root.querySelectorAll('[data-ag-current]').forEach(e=>{const v=window.FUBGUN_ATLAS_IMAGES_R25?.variants.find(x=>x.id===id);if(v)e.textContent=v.name;});root.querySelectorAll('.r26-panel-body').forEach(e=>e.scrollTop=0);root.dataset.r26Selected=id;const bar=root.querySelector('.r26-selectbar'),btn=root.querySelector('[data-ag-pick="'+CSS.escape(id)+'"]');if(bar&&btn&&bar.scrollWidth>bar.clientWidth){const a=bar.getBoundingClientRect(),b=btn.getBoundingClientRect();bar.scrollLeft+=b.left-a.left-(bar.clientWidth-btn.offsetWidth)/2;}}
 const idFromHash=()=>decodeURIComponent(location.hash.slice(1)).replace(/^variant-/,'');
 window.addEventListener('fubgun:select',e=>select(e.detail.id));window.addEventListener('fubgun:variant',e=>select(e.detail.id));window.addEventListener('hashchange',()=>select(idFromHash()));
 showPanel(panel);select(root.querySelector('[data-ag-pick][aria-pressed=true]')?.dataset.agPick||'expedition');
 // Opening one effect closes neighbouring rows, keeping the selected master's group readable.
 root.querySelectorAll('.r26-slot').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)d.parentElement.querySelectorAll('.r26-slot').forEach(other=>{if(other!==d)other.open=false;});}));
 document.documentElement.dataset.r26Ready='true';
}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();})();
