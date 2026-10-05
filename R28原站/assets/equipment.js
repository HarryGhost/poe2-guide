/* R14: equipment-first navigation. No game actions, network requests, or progression locks. */
(()=>{'use strict';
const root=document.getElementById('equipment-app'),D=window.EQUIPMENT_GUIDE;if(!root||!D)return;
const $=s=>root.querySelector(s),$$=s=>[...root.querySelectorAll(s)],P=new Map(D.phases.map(p=>[p.id,p]));
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let phase='e01',selected=null,ignore=false;
const RETURN='poe2-equip-return-r14';
function safeURL(hash,push=false){try{(push?history.pushState:history.replaceState).call(history,null,'','#'+hash);}catch(_){/* file or sandbox restriction: content still works */}}
function phaseData(){return P.get(phase);}
function setExpanded(uid,on){const b=root.querySelector('[data-eq-item="'+uid+'"]'),tr=document.getElementById('detail-'+uid),row=document.getElementById('row-'+uid);if(!b||!tr)return;
 b.setAttribute('aria-expanded',String(on));b.innerHTML=(on?'收起':'查看')+'<span aria-hidden="true"> '+(on?'−':'＋')+'</span>';tr.hidden=!on;row?.classList.toggle('is-open',on);
 if(on&&!tr.firstElementChild?.innerHTML){const it=phaseData().items.find(x=>x.uid===uid);const continuable=!phaseData().readonly&&!it.unique&&['bow','quiver','body','helmet','gloves','boots','amulet','belt','rings'].includes(it.slot);
 const shortcut=continuable?`<p class="eq-four-help"><b>已经做出4条合用词缀？</b> <a href="craft.html?target=${encodeURIComponent(it.uid)}#${phase}/${it.slot}/early-${it.slot}/finish-four">继续补第5／6条 →</a> <small>先核对总数和前后缀；作者特殊工艺需要留位时，不走普通追加。</small></p>`:'';
 tr.innerHTML='<td colspan="6">'+it.detailHtml+shortcut+'</td>';}
}
function openItem(uid,{push=true,scroll=true}={}){
 if(!phaseData().items.some(x=>x.uid===uid))return;
 const old=selected;if(old)setExpanded(old,false);selected=old===uid?null:uid;
 if(selected)setExpanded(selected,true);if(push)safeURL(phase+(selected?'/'+selected:''),true);
 $('#eq-live').textContent=selected?phaseData().label+'：已展开'+phaseData().items.find(x=>x.uid===selected).title+'专属攻略':'已回到全身目标表';
 window.dispatchEvent(new Event('r28-context'));
 if(selected&&scroll){const tr=document.getElementById('row-'+selected);requestAnimationFrame(()=>{const r=tr.getBoundingClientRect();if(r.top<54||r.top>innerHeight-150)tr.scrollIntoView({block:'start',behavior:'instant'});});}
}
function renderTable(items,utility){return '<div class="eq-table-wrap"><table class="eq-table"><caption>'+(utility?'药剂、咒符与珠宝':esc(phaseData().label)+' · 全身10个装备位置')+'</caption><colgroup><col class="col-slot"><col class="col-base"><col class="col-stats"><col class="col-level"><col class="col-priority"><col class="col-action"></colgroup><thead><tr><th>部位</th><th>目标装备 / 可用替代</th><th>基础 / 成品参照</th><th>物品等级 / 佩戴</th><th>先后建议</th><th>专属</th></tr></thead><tbody>'+items.map(it=>`<tr class="eq-row" data-eq-row="${it.uid}" id="row-${it.uid}"><th scope="row">${esc(it.title)}</th><td><b>${esc(it.name)}</b><small>${esc(it.alternative)}</small></td><td><b>${esc(it.goal)}</b><small>${esc(it.example)}</small></td><td><b>${esc(it.craftShort)}</b><small>佩戴：${esc(it.wearShort)}</small></td><td><span class="eq-priority">${esc(it.priority[0])}</span><small>${esc(it.priority[1])}</small></td><td><button type="button" class="eq-open" data-eq-item="${it.uid}" aria-expanded="false" aria-controls="detail-${it.uid}" aria-label="查看${esc(it.title)}专属攻略">查看<span aria-hidden="true"> ＋</span></button></td></tr><tr class="eq-detail-row" id="detail-${it.uid}" hidden><td colspan="6"></td></tr>`).join('')+'</tbody></table></div>';}
function render(next,uid=null,{push=false,scroll=false}={}){
 phase=P.has(next)?next:'e01';selected=null;const p=phaseData();
 $$('[data-eq-phase]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.eqPhase===phase)));
 $('#eq-focus').textContent=p.description;$('#eq-stage-work').href=p.skillFile;$('#eq-isolated').hidden=!p.readonly;
 $('#eq-main-table').innerHTML=renderTable(p.items.filter(x=>!x.utility),false);$('#eq-utility-table').innerHTML=renderTable(p.items.filter(x=>x.utility),true);$('#eq-profile').innerHTML=p.profileHtml;
 root.dataset.phase=phase;document.title=p.label+' · 全身装备目标 · Fubgun 0.5.5';
 if(uid&&p.items.some(x=>x.uid===uid))openItem(uid,{push:false,scroll});
 if(push)safeURL(phase+(selected?'/'+selected:''),true);
 $('#eq-live').textContent=p.label+'：全部装备已同步，其他阶段仍可查看。';window.dispatchEvent(new Event('r28-context'));
}
function fromHash(initial=false){let a=[];try{a=decodeURIComponent(location.hash.slice(1)).split('/');}catch(_){}
 if(['eq-setcheck','eq-ilvl-guide'].includes(a[0])){if(!root.dataset.phase)render('e01');const el=document.getElementById(a[0]);if(el){el.open=true;requestAnimationFrame(()=>el.scrollIntoView({block:'start'}));}return;}
 if(P.has(a[0]))render(a[0],a[1]||null,{scroll:!initial});else render('e01');
 if(initial){try{let x=JSON.parse(sessionStorage.getItem(RETURN)||'null');if(x&&x.phase===phase&&x.uid===selected&&Date.now()-x.time<15*60*1000){sessionStorage.removeItem(RETURN);requestAnimationFrame(()=>window.scrollTo({top:x.y,behavior:'instant'}));}else if(selected){requestAnimationFrame(()=>document.getElementById('row-'+selected)?.scrollIntoView({block:'start',behavior:'instant'}));}}catch(_){if(selected)requestAnimationFrame(()=>document.getElementById('row-'+selected)?.scrollIntoView({block:'start',behavior:'instant'}));}}
}
root.addEventListener('click',e=>{
 const button=e.target.closest('button');
 if(button?.dataset.eqPhase){render(button.dataset.eqPhase,null,{push:true});root.scrollIntoView({block:'start',behavior:'instant'});return;}
 if(button?.dataset.eqItem){openItem(button.dataset.eqItem);return;}
 if(button?.dataset.eqClose){let uid=button.dataset.eqClose;if(selected===uid)openItem(uid,{scroll:false});const btn=$('[data-eq-item="'+uid+'"]');btn?.focus({preventScroll:true});document.getElementById('row-'+uid)?.scrollIntoView({block:'nearest',behavior:'instant'});return;}
 const go=e.target.closest('a.eq-go, a[href^="craft.html?"]');
 if(go){try{sessionStorage.setItem(RETURN,JSON.stringify({phase,uid:selected,y:scrollY,time:Date.now()}));}catch(_){}}
 // A plain click on a row opens it; text selection never causes a surprise expansion.
 if(!e.target.closest('a,button,input,select,summary')&&!String(window.getSelection())){const row=e.target.closest('[data-eq-row]');if(row)openItem(row.dataset.eqRow);}
});
window.addEventListener('hashchange',()=>{if(!ignore)fromHash();});window.addEventListener('popstate',()=>fromHash());
fromHash(true);
window.__EQUIPMENT_R14={state:()=>({phase,selected}),select:(p,uid)=>render(p,uid),data:D};
})();
