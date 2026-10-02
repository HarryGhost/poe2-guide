"use strict";
(function(){
function init(){
document.querySelectorAll('.n27 a[href^="#"],.n27-single-header a[href^="#"]').forEach(link=>link.addEventListener('click',ev=>{const id=decodeURIComponent(link.getAttribute('href').slice(1)),target=document.getElementById(id);if(!target)return;ev.preventDefault();let el=target;while(el){if(el.tagName==='DETAILS')el.open=true;el=el.parentElement;}try{history.replaceState(null,'','#'+encodeURIComponent(id));}catch(e){}target.scrollIntoView({block:'start',behavior:'instant'});}));
function calculate(){const old=document.getElementById('q-old'),next=document.getElementById('q-new'),out=document.getElementById('q-result');if(!old||!next||!out)return;const a=Number(old.value),b=Number(next.value);if(old.value===''||next.value===''||!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<0||a>20||b>20){out.textContent='请输入0至20之间的普通品质值；特殊品质不在此计算器范围。';return;}const r=(100+b)/(100+a);out.textContent=r.toFixed(4)+' 倍；物理部分相对'+(r>=1?'提高':'降低')+'约'+Math.abs((r-1)*100).toFixed(2)+'%。不是全技能伤害倍率。';}
for(const id of ['q-old','q-new'])document.getElementById(id)?.addEventListener('input',calculate);calculate();
const texts={
  "bow": "确认保留后，用磨刀石逐次补武器品质，普通目标20%；只提高物理部分，不给冰霜点伤直接乘20%。4条够用也能先收尾，不必等6条。",
  "quiver": "箭袋不是弓，不照弓的磨刀石步骤处理；先核对这件实际允许的加工与增幅规则，品质不当普通随机词缀。",
  "body": "确认保留后用护甲片补普通品质至20%，增强本地防御值；不直接提高生命或抗性。",
  "helmet": "确认保留后用护甲片补普通品质至20%。若以后考虑瓦尔护甲师注能装置，至少20%品质是前提，且应先做完需要的普通修改和孔位。",
  "gloves": "确认保留后评估护甲片品质；它提高本地防御，不直接提高手套上的攻击点伤或抗性。",
  "boots": "确认保留后评估护甲片品质；它提高本地防御，不把移动速度词缀直接再提高20%。",
  "amulet": "需要品质时用与目标词缀匹配的催化剂，不用磨刀石或护甲片。涉及消耗品质的后续工艺，要按每一步重新检查。",
  "belt": "需要品质时检查适用催化类型与实际收益；不是磨刀石对象。不要把品质当一条普通前后缀。",
  "rings": "需要品质时检查适用催化类型与实际收益；不是全部词缀一起提高，也不是磨刀石对象。",
  "flasks": "先升级合适的药剂底材；决定保留的常用药剂用玻璃弹珠补品质，逐次观察效果。不是用磨刀石或护甲片。",
  "charms": "先检查触发条件、充能和解除的异常状态。咒符按自身允许的道具规则处理，不照技能宝石或弓的品质材料。",
  "jewels": "普通天赋珠宝不照弓用磨刀石，也不照主动技能用棱镜；特殊催化、扩容等先查对应规则，未核实高阶方案仍只读。"
};
function slotQuality(){const el=document.getElementById('n27-slot-quality'),sel=document.getElementById('c-slot');if(!el)return;const key=sel?.value||location.hash.replace(/^#/,'').split('/')[1]||'bow';el.textContent=texts[key]||'先核对这个部位允许的品质材料，再处理孔位与装备后的属性。';}
document.getElementById('c-slot')?.addEventListener('change',()=>requestAnimationFrame(slotQuality));window.addEventListener('hashchange',()=>requestAnimationFrame(slotQuality));slotQuality();setTimeout(slotQuality,100);
document.querySelector('[data-n27-open-all]')?.addEventListener('click',()=>document.querySelectorAll('.n27-details').forEach(d=>d.open=true));
document.querySelector('[data-n27-close-all]')?.addEventListener('click',()=>document.querySelectorAll('.n27-details').forEach(d=>d.open=false));
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();