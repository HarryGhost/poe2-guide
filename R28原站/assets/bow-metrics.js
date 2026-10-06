/* Optional weapon-only arithmetic; never treats missing values as 0 or certifies a build. */
(()=>{'use strict';
const D=window.BOW_METRICS;if(!D)return;
function compute(x){
 for(const k of ['pmin','pmax','cmin','cmax','aps']){
  if(x[k]===undefined||x[k]===null||String(x[k]).trim()==='')return {error:'请填完整物理区间、冰伤区间和攻速。没有冰伤请填0和0。'};
  x[k]=Number(x[k]);if(!Number.isFinite(x[k])||x[k]<0)return {error:'数值不能为负或无效；照抄武器顶部的最终数值。'};
 }
 if(x.aps<=0)return {error:'每秒攻击次数必须大于0。'};
 if(x.pmin>x.pmax||x.cmin>x.cmax)return {error:'伤害下限不能大于上限，请检查两格是否填反。'};
 const pdps=(x.pmin+x.pmax)/2*x.aps,cdps=(x.cmin+x.cmax)/2*x.aps;
 if(!Number.isFinite(pdps+cdps))return {error:'输入数值过大，请按装备实际数字填写。'};
 return {pdps,cdps,total:pdps+cdps,physicalAverage:(x.pmin+x.pmax)/2};
}
function update(root){
 const values={};root.querySelectorAll('[data-bow-input]').forEach(el=>values[el.dataset.bowInput]=el.value);
 const out=root.querySelector('[data-bow-result]'),snap=D.snapshots[root.dataset.bowCalc];if(!out||!snap)return;
 const v=compute(values);if(v.error){out.textContent=v.error;out.classList.remove('has-result');return;}
 const ref=snap.cases.find(x=>x.quality===Number(values.ref))||snap.cases[0];
 const rel=(v.total/ref.physical_cold_dps-1)*100;
 const comparison=Math.abs(rel)<.15?'与你选择的示例情景接近':`${rel>=0?'比':'比'}示例情景${rel>=0?'高':'低'} ${Math.abs(rel).toFixed(1)}%`;
 out.classList.add('has-result');out.innerHTML=`<strong>物理DPS ${v.pdps.toFixed(1)} · 冰伤DPS ${v.cdps.toFixed(1)} · 两项合计 ${v.total.toFixed(1)}</strong><span>物理平均每击 ${v.physicalAverage.toFixed(1)}。合计${comparison}。</span><small>这不是角色DPS，也不代表合格/不合格。火、电、混沌未算；技能等级、额外箭、暴击和手感还要单独比较。</small>`;
}
document.addEventListener('input',e=>{const root=e.target.closest?.('[data-bow-calc]');if(root)update(root);});
document.addEventListener('change',e=>{const root=e.target.closest?.('[data-bow-calc]');if(root)update(root);});
window.__BOW_METRICS_R15={compute,update,data:D};
})();
