"""R8 additions: explicitly bound loadouts, keyed transitions and teaching examples.
No source .build files are modified. Rendered data is offline and inspectable.
"""
from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parent.parent
TRANSITIONS=json.loads((ROOT/'data/转换检查清单.json').read_text())
CASES=json.loads((ROOT/'data/打造教学实例.json').read_text())['cases']
def h(x): return html.escape(str(x if x is not None else ''),quote=True)
def link(url,label): return f'<a href="{h(url)}"'+(' target="_blank" rel="noopener noreferrer"' if str(url).startswith('https:') else '')+f'>{h(label)}</a>'
def table(headers,rows):
 return '<div class="table-wrap"><table class="data-table"><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
SLOT_HELP={
'弓':('物理/冰点伤、实际武器伤害；Early不先要求暴击。','bow'),
'衣服':('生命、抗性与物品闪避；普通荆棘不增加箭矢伤害。','body'),
'头盔':('01/02先生命与抗性；03开始才按整套条件准备护盾头。','helmet'),
'手套':('生命、抗性、攻击附加物理/冰伤；先填当前缺口。','gloves'),
'鞋':('先移动能力，再生命、抗性与合适防御。','boots'),
'箭袋':('适用攻击点伤/弓伤/攻速；黄装功能替代不等同特殊暗金。','quiver'),
'项链':('先满足当前属性与精魂；再考虑投射物等级。','amulet'),
'腰带':('生命、力量和抗性；不要求先取得猎首。','belt'),
'戒指Ⅰ':('生命、抗性、属性与攻击点伤按整套缺口分摊。','rings'),
'戒指Ⅱ':('不必与第一枚完全相同；换装后复查技能是否可用。','rings'),
'药剂 / 咒符':('常规药剂/咒符仍要满足等级与槽位；不是黄装。','flasks')}
def profile_gear(st):
 if not st['profiles']:return ''
 out='<div class="card-body"><div class="bound-label"><b>当前参考装备</b><span class="small">与上方属性、宝石等级同步切换</span></div><div class="controlrow"><label>整套参考 <select id="gear-profile-select" aria-label="装备与属性使用的整套参考">'+''.join(f'<option value="{i}">{h(p["label"])}</option>' for i,p in enumerate(st['profiles']))+'</select></label><a href="#attributes">查看 / 修改需求明细</a></div><p class="small muted" id="gear-profile-caption"></p><p class="notice warn small" id="profile-edited-note" hidden>你已手动修改需求值；当前为“该参考＋你的录入”，不是原作者面板。数值修改不会自动替换底材名称或改变游戏装备。</p></div>'
 for i,p in enumerate(st['profiles']):
  rows=[]
  for j,r in enumerate(p['rows']):
   if not (r['category'].startswith('装备') or r['category']=='药剂 / 咒符'):continue
   slot=r['category'].split(' · ')[-1]
   tip,target=SLOT_HELP.get(slot,('按当前需求选择；不因原件出现就必须购买。','bow'))
   if st['id'] in ('e03','e04','e05') and slot=='头盔':tip='高物品护盾与属性条件、幽灵舞步恢复一起核对，不只看护盾百分比。'
   if st['id'] in ('e04','e05') and slot=='弓':tip='武器伤害底座、命中与本地暴击一起核对；不是只有＋等级。'
   req=' / '.join(f'{name} <span data-bound-req="{i}:{j}:{key}">{h(r[key])}</span>' for name,key in [('力','str'),('敏','dex'),('智','int')])
   level=f'底材需求等级 {r["level"]}' if r.get('level') is not None else '等级按实际底材 / 词缀核对'
   label=r['label'].replace('：不另带三维需求的普通底材黄装','：无额外三维需求的常规黄装')
   rows.append([h(slot),'<b>'+h(label)+'</b><small class="block muted">'+h(level)+'</small>',req,h(tip)+'<br>'+link('craft.html#early-'+target,'看此部位的起步做法')])
  out+=f'<div class="profile-gear-panel" data-profile-gear="{i}" data-reference-id="{h(p["referenceId"])}"'+(' hidden' if i else '')+'>'+table(['部位','当前参考底材 / 功能件','本件属性需求','先看什么 / 怎么做'],rows)+'</div>'
 out+='<div class="card-body"><p class="small muted">上表是属性计算对应的参考，不是要求购买同名装备。无额外需求的首饰/功能件仍列入；需要其他武器组装备时，必须把其更高需求纳入明细。</p></div>'
 return out

def profile_snapshot(st):
 if not st['profiles']:return ''
 p=st['profiles'][0]
 names=[r['label'] for r in p['rows'] if r['category'].startswith('装备')][:5]
 return '<div class="profile-snapshot" aria-live="polite"><b id="profile-reference-name">'+h(p['statusLabel'])+'</b><span id="profile-gem-summary">基础宝石 '+str(p['gemlevel'])+' 级；升华技能另列</span><span id="profile-gear-summary">'+h(' / '.join(names))+'</span><a href="#gear">查看对应全身装备 ↓</a></div>'

def transition_html(st,stage_map,checks_func):
 if st['id']=='e06':return '<div class="card-body"><p>06为冲突快照，不是下一阶段。只读资料始终开放；不提供直接转入或自动修复步骤。</p>'+link('sources.html#conflict','查看冲突说明')+'</div>'
 if st['id']=='e05':return '<div class="card-body"><b>没有必须进入的06阶段。</b><p>继续补当前配置的实际短板；不把作者实装快照当作线性升级终点。</p>'+link('compare.html?from=e04&to=e05','回看04→05的原件差异')+'</div>'
 t=next(x for x in TRANSITIONS if x['fromStage']==st['id'])
 nxt=stage_map[t['toStage']]
 out=f'<div class="card-body transition-card" data-transition="{h(t["id"])}" data-from-stage="{st["id"]}" data-to-stage="{nxt["id"]}"><p class="transition-label"><b>{h(st["label"])} → {h(nxt["label"])}</b></p><h3>{h(t["title"])}</h3>'
 out+=checks_func(st['id'],t['checks'],'transition-'+t['id']+'-r8-')
 out+='<div class="notice"><b>条件不足时：</b>'+h(t['hold'])+'</div>'
 c=t['changes']
 out+='<details><summary>这一步的技能差异（按原件对比）</summary><div class="detail">'
 for k,title in [('added','新增'),('removed','移除'),('supportChanged','连接改变')]:out+='<p><b>'+title+'：</b>'+h('、'.join(c[k]) or '无')+'</p>'
 out+='<p class="small muted">这是两个快照的差异，不是无条件执行的删技能指令；缺少前置条件时继续当前配置。</p></div></details>'
 out+='<div class="controlrow">'+link(nxt['file'],'查看下一阶段 →')+' · '+link('compare.html?from='+st['id']+'&to='+nxt['id'],'装备、技能、天赋完整对比')+'</div><p class="small muted">'+h(t['basis'])+' '+link(t['source'],'依据')+'。旧版错位清单的勾选不继承；不锁定任何阶段。</p></div>'
 return out

def examples_page():
 out='<header class="page-head"><div><div class="eyebrow">EARLY / 打造实例</div><h1>看到一件装备，下一步怎么做？</h1><p>先看状态、再选材料；结果不好时也有明确的停手办法。</p></div></header>'
 out+='<div class="notice">以下是本站教学示例，不是Fubgun实装、不是随机工艺模拟，也不表示有固定成功率。作者的8条完整工艺继续保留在 '+link('craft-advanced.html','进阶工艺库')+'。</div>'
 out+='<nav class="case-nav" aria-label="选择打造示例">'+''.join(link('#'+c['id'],str(i+1)+' · '+c['title']) for i,c in enumerate(CASES))+'</nav>'
 out+='<details><summary>先认前缀、后缀与“装备等级”</summary><div class="detail"><p>普通蓝装通常最多一前一后；普通黄装通常最多三前缀三后缀。特殊扩容、腐化、破溃或其他机制另算，不能只数说明文字行。复合词缀可能一条占位却显示多行。</p><p>物品等级（ilvl）影响可出现的词缀；需求等级决定人物能否装备。两者不是人物等级，也不是同一个数字。</p><p>本文只对指定状态解释材料操作；实际使用前，读国服物品和材料提示。'+link('https://poe2db.tw/cn/Exalted_Orb','物品/材料数据参考')+'</p></div></details>'
 for c in CASES:
  out+=f'<article class="case-panel section" id="{c["id"]}" data-case="{c["id"]}"><div class="card-head skill"><h2>{h(c["title"])}</h2><span class="badge">{h(c["stage"])}</span></div><div class="case-grid"><section class="card"><div class="card-body"><h3>① 先确认这件装备的状态</h3><p>{h(c["state"])}</p></div>'
  out+=table(['位置','已有属性 / 空位','怎么理解'],[[h(x) for x in r] for r in c['affixes']])
  out+='<div class="card-body"><h3>② 再决定材料与操作</h3><p>'+h(c['action'])+'</p><p class="notice warn"><b>别这样做：</b>'+h(c['avoid'])+'</p></div></section><section class="card"><div class="card-body"><h3>③ 做完以后，分情况处理</h3></div>'
  out+=table(['结果','下一步'],[[h(x) for x in r] for r in c['outcomes']])
  out+='<div class="card-body"><h3>④ 停手条件</h3><p>'+h(c['stop'])+'</p><p>'+link(c['next'],'接着看对应部位 / 工艺')+'</p><p class="small muted">作用核对：'+' · '.join(link(u,t) for t,u in c['links'])+'</p></div></section></div></article>'
 out+='<section id="bow-math" class="section card"><div class="card-head combat"><h2>弓的面板比较：不要把百分比再乘一次</h2></div><div class="card-body"><p>从装备上方读取最终物理伤害范围和每秒攻击次数。计算是“平均物理伤害 × 每秒攻击次数”；上方数值已经反映物品本地词缀时，不要再乘一次“物理伤害提高”。</p><p class="small muted">这里只比较物理部分的面板量，不是完整冰射/狙击DPS：未计元素点伤、转伤、命中、暴击、额外箭与敌人防御，不能直接据此判定哪把弓更强。</p><div class="bow-compare-grid">'
 for key,label in [('a','现用弓'),('b','备用弓')]:
  out+=f'<fieldset><legend>{label}</legend><label>物理最小值 <input type="number" min="0" step="0.01" data-bow="{key}" data-field="min" placeholder="填面板"></label><label>物理最大值 <input type="number" min="0" step="0.01" data-bow="{key}" data-field="max" placeholder="填面板"></label><label>每秒攻击次数 <input type="number" min="0.01" step="0.01" data-bow="{key}" data-field="aps" placeholder="如1.20"></label><output id="bow-{key}-result">未填完整</output></fieldset>'
 out+='</div><p id="bow-math-result" class="notice" aria-live="polite">填完两把弓后显示物理面板差异；不输出“必定更强”的结论。</p><button type="button" id="bow-math-demo">载入纯算术示例（非真实装备）</button><button type="button" id="bow-math-clear">清空</button><p class="small muted">示例仅用于演示：较高的每秒物理量未必有更高单次伤害；冻结速度和狙击爆发仍要按实际技能检验。</p></div></section>'
 return out

KEY_NODES=json.loads((ROOT/'data/关键天赋点位核对.json').read_text())['nodes']
def key_nodes(st):
 if not st['nodes'] or st['readonly']:return ''
 ids={n['id'] for n in st['nodes']}
 applicable=[x for x in KEY_NODES if x['id'] in ids]
 if not applicable:return ''
 out='<details id="verified-node-help"><summary>这份原件实际点了什么？已核对关键点与用途</summary><div class="detail"><p class="small muted">只显示当前原件中确实出现的点。下面不是加点顺序，不提供未经核验的地图坐标；中文来自国际服数据的简体展示。</p>'
 for n in applicable:
  rows=[v for v in st['nodes'] if v['id']==n['id']]
  scope='、'.join(dict.fromkeys(v['scope'] for v in rows))
  out+='<div class="verified-node"><h3>'+h(n['zh'])+' <span class="badge">'+h(scope)+'</span></h3><p>'+h(n['effect'])+'</p><p class="small muted">'+h(n['condition'])+'</p><div class="controlrow"><button type="button" class="tiny" data-node-jump="'+h(n['id'])+'">定位原始记录</button><code>'+h(n['id'])+'</code> '+link(n['url'],'名称和效果来源')+'</div></div>'
 absent=[x['zh'] for x in KEY_NODES if x['id'] not in ids]
 if absent:out+='<p class="small"><b>这份没有这些已查点：</b>'+h('、'.join(absent))+'。不能把别的阶段收益搬过来。</p>'
 if 'bow13' not in ids:out+='<p class="small">这份原件未分配 <code>bow13</code>（飞羽流矢）；作者网页的条件建议不能当成此快照已经生效。</p>'
 out+='<p class="notice warn small">仍缺完整连线图和合法逐级点序。没有核验的部分不能据此整树洗点；按客户端实际通路和可用点数核对。</p></div></details>'
 return out
