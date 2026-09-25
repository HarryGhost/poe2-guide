# -*- coding: utf-8 -*-
"""Offline, reproducible static-site generator. No external libraries or network required."""
from pathlib import Path
import json,html,copy,re,hashlib,shutil,collections
from content import *
BASE=Path(__file__).resolve().parent
OUT=Path('/tmp/gpt6/rebuild')
if (BASE.parent/'data/全站阶段与核算.json').exists():OUT=BASE.parent
D=json.loads((OUT/'data/六分支原始及中文映射.json').read_text())
STAGES=json.loads((OUT/'data/全站阶段与核算.json').read_text())
DICT=json.loads((OUT/'data/当前词典.json').read_text())
SOURCES=json.loads((OUT/'data/来源目录.json').read_text())
M={s['id']:s for s in STAGES}
VERSION='C全站阶段作业 · R5'
RES=[('roadmap','全部阶段与路线'),('compare','阶段变化对比'),('mechanics','机制与排障'),('craft','装备打造与涂膏'),('rewards','永久奖励核对'),('glossary','中英名称查询'),('reader','作者说明读本'),('sources','来源、下载与检查')]
PAGES={}
def h(v):return html.escape(str(v if v is not None else ''),quote=True)
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def ext(url,label):return f'<a href="{h(url)}" target="_blank" rel="noopener noreferrer">{h(label)} ↗</a>' if url.startswith('https://') else h(label)
def src(url,label='依据'):return '<span class="source-link">'+ext(url,label)+'</span>'
def tag(text,kind=''):return f'<span class="badge {kind}">{h(text)}</span>'
def details(title,body,id=''):
 idattr=(' id="'+str(id)+'"') if id else ''
 return '<details'+idattr+'><summary>'+h(title)+'</summary><div class="detail">'+body+'</div></details>'
def table(headers,rows,cls=''):
 return '<div class="table-wrap"><table class="data-table '+cls+'"><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def card(title,body,band='',extra=''):
 return f'<section class="card"><div class="card-head {band}"><h2>{title}</h2>{extra}</div>{body}</section>'
def checks(st,texts,prefix='task'):
 return '<div class="checklist">'+''.join(f'<label><input type="checkbox" data-check="{h(st+"-"+prefix+str(i))}"><span>{h(x)}</span></label>' for i,x in enumerate(texts))+'</div>'
def keyclass(key):return 'attack' if key in ['ice','la'] else 'burst' if key in ['bar','snipe'] else 'prep' if key in ['ita','mark','tornado','salvo','lr','fb','pounce'] else 'aura'
def keyel(st,key):
 s=next((x for x in st['skills'] if x['key']==key),None)
 if not s:return ''
 return f'<span class="key {keyclass(key)}" data-key-label="{h(key)}">{h(s["keybind"])}</span>'
def skillref(st,key):
 s=next((x for x in st['skills'] if x['key']==key),None)
 if not s:return ''
 return '<span class="skill-ref">'+keyel(st,key)+' <strong>'+h(s['zh'])+'</strong></span>'
def chain(st,keys):return ' <span class="muted">→</span> '.join(skillref(st,k) for k in keys if any(x['key']==k for x in st['skills']))
def nav(current):
 o='<a class="brand" href="index.html"><strong>冰射 · 阶段作业</strong><small>PoE2 / 0.5.5 · C 雪白深栏</small></a>'
 for kind,label in [('level','剧情练级 · 全部可看'),('end','异界进阶 · 全部可看')]:
  o+=f'<div class="nav-label">{label}</div>'
  for s in STAGES:
   if s['kind']!=kind:continue
   short={'l01':'1–14级 · 闪电起步','l02':'15–23级 · 闪电补强','l03':'24–30级 / 31级未转','l04':'取得宝石 · 转冰射','l05':'42–59级 · 剧情后段','l06':'60级＋ · 通关衔接','e01':'Early · 刚进异界','e02':'非暴击 · 中期补强','e03':'非暴击 · 混合防御','e04':'暴击 · 保留狙击','e05':'高配 · 冰射主输出','e06':'实装快照 · 只读核对'}[s['id']]
 cls = "active" if current==s["id"] else ""
 aria = ' aria-current="page"' if current==s["id"] else ''
 o+=f'<a class="stage-link {cls}" href="{s["file"]}"{aria}><span class="n">{s["number"]:02}</span><span>{short}</span></a>' 
 o+='<div class="nav-label">资料与工具</div>'
 for rid,title in RES:o+=f'<a class="stage-link {"active" if current==rid else ""}" href="{rid}.html">{title}</a>'
 o+='<div class="side-foot">不按进度解锁 · 全部随时查看<br>自刷通货，预算内购买/打造<br>资料核对：2026-09-25<br><a href="all.html">全部作业展开阅读</a></div>'
 return o
COMMON_DIALOG='''<dialog id="search-dialog"><div class="dialoghead"><h2>全站搜索</h2><button type="button" data-close="search-dialog" aria-label="关闭搜索">关闭</button></div><label for="site-search" class="small">阶段、技能、装备、机制、中文或英文名称</label><input id="site-search" type="search" placeholder="例如：感电、31级、卡迪罗、精魂" style="width:100%;margin-top:6px"><p id="search-count" class="small muted"></p><div class="search-results" id="search-results"></div></dialog><dialog id="key-dialog"><div class="dialoghead"><h2>设置网页显示的按键</h2><button type="button" data-close="key-dialog">关闭</button></div><p class="small muted">以下为建议键位，不是已核实的作者键位。只改网页提示，不改变游戏设置；同一技能的提示会同步。</p><div id="key-editor" class="keyeditor"></div><p id="key-error" class="small"></p><div class="controlrow"><button class="primary" id="key-save">保存网页键位</button><button id="key-reset">恢复建议</button></div></dialog><dialog id="copy-dialog"><div class="dialoghead"><h2>复制内容</h2><button data-close="copy-dialog">关闭</button></div><p class="small muted">浏览器未允许自动复制；选中文本后按 Ctrl+C。</p><textarea id="copy-text" rows="13" style="width:100%"></textarea></dialog><div id="toast" class="toast" role="status" aria-live="polite" hidden></div>'''
def shell(current,title,body,stage=None):
 data={'id':current,'version':VERSION,'stage':stage}
 return '<!doctype html><html lang="zh-CN" data-look="c"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="完整阶段作业与来源核对。全部阶段可自由访问，键位、属性与操作同页展示。"><title>'+h(title)+' · 锐眼冰射作业</title><link rel="stylesheet" href="assets/style.css"></head><body data-page="'+current+'" data-layout="stage-workbook-r5" data-density="compact"><a class="skip" href="#main">跳到正文</a><aside class="sidebar" id="sidebar" aria-label="全部阶段与资料">'+nav(current)+'</aside><div class="page"><header class="topbar"><div class="top-actions"><button class="menu-toggle" id="menu-toggle" aria-expanded="false" aria-controls="sidebar">目录</button><div class="crumb">'+h(title)+'</div></div><div class="top-actions"><button id="search-open">搜索 /</button><button id="density-toggle">舒适字号</button>'+(('<button id="keys-open">改键位</button>') if stage and not stage['readonly'] else '')+'<button id="print-btn">打印</button></div></header><main id="main" tabindex="-1"><noscript><div class="notice warn">JavaScript未启用：阶段与技能正文仍可读；完整属性表和全部原件请打开<a href="all.html">全部作业展开页</a>。</div></noscript>'+body+'<footer class="page-footer"><span>'+VERSION+' · 全站统一布局 · 2026-09-25<br>原始快照与中文资料对照；不等于国服实测毕业。</span><span><a href="roadmap.html">所有阶段</a> · <a href="sources.html#limits">核对边界</a> · <a href="#main">回顶部 ↑</a></span></footer></main></div>'+COMMON_DIALOG+'<script id="page-data" type="application/json">'+js(data)+'</script><script src="assets/search-index.js"></script><script src="assets/app.js"></script>'+('<script src="assets/catalog.js"></script><script src="assets/compare.js"></script>' if current=='compare' else '')+'</body></html>'
def overview_attrs(st):
 if st['readonly']:
  return '<div class="notice danger">此快照含升华冲突，不提供伪装成可用配置的三维/资源门槛。装备与技能原始记录全部保留；没有把未知值填成0。</div>'
 p=st['profiles'][0];r=[r for r in p['rows'] if r.get('skillKey') not in st['defaultDisabled']]
 values=[max(x[k] for x in r) for k in ['str','dex','int']]
 reserves=[x for x in st['reserve']];base=sum(60 if x=='mirage' else 0 if (st['id']=='e05' and x=='wd') else 30 for x in reserves)
 html='<div class="profilebar"><label for="profile-select">整套参考</label><select id="profile-select">'+''.join(f'<option value="{i}">{h(p["label"])}</option>' for i,p in enumerate(st['profiles']))+'</select><a href="#attributes">含装备 · 看计算明细</a></div><div class="metrics">'
 for k,v,zh in zip(['str','dex','int'],values,['力量','敏捷','智慧']):html+=f'<div class="metric"><strong id="total-{k}">{v}</strong><div>{zh}<small>整套面板需求</small></div></div>'
 html+=f'<div class="metric"><strong>{base}</strong><div><a href="#budget">精魂基础起算</a><small>{"另有生命保留，需核对" if st["id"]=="e05" else "非最终保留 · 展开核算"}</small></div></div></div>'
 html+='<p class="small muted" id="profile-caption">明确底材和基础宝石等级下的参考，不是你的实装扫描；数字已包含装备，不要求全从天赋获得。</p>'
 return html

def skills_html(st,full=False):
 o=''
 opts=[s for s in st['skills'] if s['optional']]
 if opts and not full:o+='<div class="optionalbar">'+''.join(f'<label><input type="checkbox" data-skill-enable="{h(s["key"])}" {"" if s["key"] in st["defaultDisabled"] else "checked"}>使用可选 {h(s["zh"])}</label>' for s in opts)+'<span class="muted">不使用的原连接也保留显示</span></div>'
 for n,s in enumerate(st['skills']):
  ch=''.join('<span class="support '+('active' if sp.get('active') else '')+'" data-support="'+h(sp.get('id',sp.get('key','')))+'">'+('〔主动〕' if sp.get('active') else '')+h(sp['zh'])+'</span>' for sp in s['supports']) or '<span class="muted">此快照未配置辅助</span>'
  inactive=s['key'] in st['defaultDisabled'];pre='已停用 · 可选' if inactive else '元技能内槽另配' if s['key'] in ['mirage','deadeye'] else ''
  o+=f'<div class="skill-row {"disabled" if inactive else ""}" data-skill="{h(s["key"])}" data-original-id="{h(s["id"])}"><div>{keyel(st,s["key"])}</div><div class="skill-name">{h(s["zh"])}<small data-skill-state="{h(s["key"])}">{pre}</small></div><div class="support-chain">{ch}</div>'
  if not full:o+=f'<button class="skill-detail-btn" data-skill-detail="detail-{st["id"]}-{n}" aria-expanded="false" aria-controls="detail-{st["id"]}-{n}" aria-label="展开{h(s["zh"])}说明">＋</button>'
  o+='</div>'
  extra=f'<p>{h(s["note"])}</p><p>{ext(s["url"],s["en"])} <code>{h(s["id"])}</code></p>'
  if s.get('interval'):extra+=f'<p>原导出显示区间：{h("–".join(map(str,s["interval"])))}。不是实际宝石等级，也不是点序。</p>'
  if s['supports']:extra+='<div class="support-list">'+''.join('<span>'+ext(sp['url'],sp['zh']+' / '+sp['en'])+'</span>' for sp in s['supports'])+'</div>'
  if full:o+='<div class="fulltext">'+extra+'</div>'
  else:o+=f'<div class="skill-extra" id="detail-{st["id"]}-{n}" hidden>{extra}</div>'
 return o

def rotation(st):
 if st['readonly']:
  return '<div class="card-body"><p>这份实装包含变形与内嵌印记，但升华字段冲突未解决。</p><p>不把其他阶段的手法强套到06；下方可以查看全部原始连接、装备和节点。</p><a class="btn" href="e05.html">回05高配对照</a></div>'
 sid=st['id'];n=st['number']
 clear=CLEAR.get(sid,'主要用冰霜射击清图。常驻与元技能按取得条件开启，不需要每群重按全部工具。')
 steps=BOSS.get(sid)
 if not steps:
  steps=[]
  if n<=3:steps.append(('按目标布置工具',['tornado','ita','mark'],'工具有实际利用空间再布置；确认印记与主输出武器组。'))
  else:steps.append(('先布工具与印记',['tornado','mark'],'04狙击带盲点时，确认致盲实际生效；不是持续伤害每跳都算击中。' if n==4 else '05没有狙击，之后爆发回到冰射；不要再套04的最后一发。'))
  steps.append(('确认状态',['ice'],'确认目标已经冻结，再接狙击爆发。' if n<=4 else '按印记与高配冰射机制持续输出，观察资源是否稳定。'))
  steps.append(('进入爆发',['bar','snipe'] if n<=4 else ['bar','ice'],'弹幕后不夹其他攻击；狙击要在完美窗口直接命中冻结目标。' if n<=4 else '弹幕强化冰射，不再释放原件没有的狙击。'))
  steps.append(('回复并重复',['ice'],'印记消耗、冷却、蓝量与地面效果都重新看；持续站桩不是必选。'))
 o='<div class="rotation-section"><span class="rotation-label">清普通怪</span><p class="small">'+h(clear)+'</p><span class="rotation-label boss">耐打精英 / 首领</span><div class="steps">'
 for title,keys,note in steps:o+='<div class="step"><div><strong>'+h(title)+'</strong><div class="flow">'+chain(st,keys)+'</div><p>'+h(note)+'</p></div></div>'
 o+='</div><p class="action-note">'+('普通怪不用每次完整连招；危险先躲，再重建状态。' if n<3 and st['kind']=='level' else '冻结成功再爆发；弹幕后不要夹另一发攻击。' if (st['kind']=='level' or n<5) else '05是高配冰射，不要混入04的狙击连接。')+'</p><p class="small muted">建议键位仅作网页提示，可自行修改。'+src(st['source'],'作者阶段说明')+'</p></div>'
 return o

def upgrades(st):
 if st['readonly']:return ''
 if st['kind']=='level':slots='狙击 → 冰霜射击 → 冰冻印记 → 寒冰之捷';quality='冰冻印记 → 寒冰之捷 → 狙击'
 else:slots='狙击 → 冰霜射击 → 寒冰之捷 → 冰冻印记';quality='冰冻印记 → 寒冰之捷 → 狙击 → 冰霜射击'
 if st['id'] in ['l01','l02']:
  return details('缺孔与资源：当前先用好已有技能','<p><b>当前：</b>优先让闪电箭矢清怪、引雷针处理首领；辅助不足时可以调配已有宝石，不必先凑满所有孔。</p><p>冰冻印记、狙击和冰射尚未进入本阶段配置，不为了后期顺序现在就消耗材料。后续开孔/品质顺序在对应阶段页单列。</p><p>'+src(st['source'],'作者本阶段说明')+'</p>')
 if st['id']=='e05':slots='本配置没有狙击；优先检查冰射，再处理寒冰之捷、冰冻印记。';quality='本配置没有狙击；按当前技能实际收益选择。原文通用优先级不强套。'
 return details('孔位与品质：先把材料花在哪里',f'<p><b>辅助孔：</b>{slots}。</p><p><b>品质：</b>{quality}。</p><p>已有并正在使用的技能才进入顺序。作者通常从原连接末端减配；如果删除冻结导致冻不住，需要明确放回并接受伤害/清图取舍。高阶辅助不是无条件替换低阶。</p><p>六连在此指1个主动配5个辅助；元技能内嵌主动不是辅助。'+src(st['source'],'原作者说明')+'</p>')

def equipment_html(st):
 if st['kind']=='level':
  base=st['original']['gear'];rows=[]
  for item,a,b in base:rows.append([h(item),h(a),h(b)])
  rows.extend([['衣服 / 头盔','生命、抗性和适合当前阶段的防御。普通荆棘不增加箭矢伤害。','不用为了后期混合防御提前放弃现有生命/闪避。'],['手套 / 箭袋 / 戒指','看“攻击附加物理/元素伤害”及所需属性、抗性；蓝装也可能比黄装更适合。','属性足够、真实输出或生存改善才换；不只看稀有度。'],['鞋 / 腰带 / 药剂','鞋有移速；腰带补生命/力量等缺口；药剂随可取得等级升级。','保留现用装备，自刷通货预算内决定买底材、买成品或小预算打造。']])
  return table(['部位 / 资源','现在看什么','避免浪费'],rows)
 rows=[]
 for eq in st['original']['equipment']:
  slot=eq['raw']['inventory_id'];tips=GEAR_HELP.get(slot,('原件装备','按实际词条核对','不混其他分支。'))
  slotname=tips[0].split('：')[0]
  rawtext=h(eq['translation']).replace('\n','<br>')
  unique='unique_name' in eq['raw']
  source=ext(eq['url'],eq['en'])
  info=details('原件完整已导出词条',rawtext+'<p class="small muted">'+source+'；未导出词条、品质与符文不补造。</p>')
  status='原件暗金 · 功能替代不等效' if unique else '稀有/普通功能件 · 不绑定此名称'
  if slot=='Flask1' or slot=='Charm1':status='原件暗金 · 普通/魔法替代' if unique else '普通/魔法功能件 · 不是黄装'
  rows.append([h(slotname)+'<br><b>'+h(eq['zh'])+'</b><br>'+tag(status),h(tips[1]),h(tips[2])+info])
 return table(['原件部位与名称','优先词条 / 作用','自己刷、购买或打造'],rows)

def attributes_html(st):
 if st['readonly']:return '<div class="card-body">06未提供可用整套需求结论，不能把不明武器/升华的快照作为有效面板目标。前五个异界页面均有完整参考计算；此页只保留数据。</div>'
 p=st['profiles'][0]
 html='<div class="card-body"><p><b>这里算的是人物面板总属性，不是需要从天赋额外点出的数值。</b>每项分别取“装备最高需求、主技能与元技能内槽最高需求、辅助累计需求”的最大值；装备之间不累加。</p><p class="small muted">所有装备部位都在表中。默认数字来自明确参考配置；不是强制换成指定底材。改了基础宝石等级、底材、额外技能，按游戏需求栏逐行修改。</p><div id="profile-notes"></div><details id="attribute-ledger"><summary>展开逐项需求与修改（装备没有省略）</summary><div class="detail"><div class="table-wrap"><table class="data-table" id="attr-table"><thead><tr><th>整套装备 / 技能</th><th>类别</th><th>力量</th><th>敏捷</th><th>智慧</th><th>来源与前提</th></tr></thead><tbody id="attr-rows"></tbody></table></div><div class="controlrow"><button id="attr-reset">恢复本参考</button><button id="attr-extra">添加其他需求行</button><span class="small muted">清空数值会标记未完成，不当成0。</span></div></div></details><div id="attr-result" class="budget-result" aria-live="polite"></div></div>'
 return html

def budget_html(st):
 if st['readonly']:return ''
 o='<div class="card-body"><p class="small">三维需求与精魂保留是两回事。下面的默认值是各技能<b>基础起算</b>，不是装完所有辅助/特殊效果后的最终保留；把游戏技能面板最终值填入，才能判断预算。</p><div id="budget-rows">'
 for k in st['reserve']:
  skill=next(x for x in st['skills'] if x['key']==k);life=st['id']=='e05' and k=='wd';val='' if life else 60 if k=='mirage' else 30
  o+=f'<div class="budget-row" data-resource="{k}"><label><input type="checkbox" data-reserve-on="{k}" checked> {h(skill["zh"])}</label><span>{"生命比例 %" if life else "精魂"}</span><input type="number" min="0" max="{100 if life else 9999}" step="0.1" value="{val}" data-reserve-value="{k}" data-reserve-type="{"life" if life else "spirit"}" aria-label="{h(skill["zh"])}最终保留"></div>'
 o+='</div><div class="controlrow"><label>你的精魂总量 <input id="spirit-total" type="number" min="0" max="9999" placeholder="未填"></label><label>其他精魂保留 <input id="spirit-other" type="number" min="0" max="9999" value="0"></label></div><label class="small"><input type="checkbox" id="budget-confirmed"> 已把各项改成我装好辅助后的游戏最终保留</label><div id="budget-result" class="budget-result" aria-live="polite">未录入完整最终值。</div><p class="small muted">蜃影神射由升华给予；额外效果若在客户端显示保留，填入“其他”。缺精魂时先保实际依赖的防御，非必要常驻可暂缓。此工具不模拟特殊保留规则。</p></div>'
 return o

def nodes_html(st,full=False):
 if not st['nodes']:
  return '<div class="card-body"><p>本地没有作者这一等级分支的完整坐标、连线与逐级点序。上面的优先级是按需求安排，不是假造的逐点树。</p><p>'+ext(st['source'],'打开作者当前等级分支天赋')+' · <a href="e01.html#tree">查看Early目标记录</a></p><p class="small muted">原导出数组顺序不能冒充合法加点顺序；没有实测洗点数，不按“第几行”点天赋。</p></div>'
 o=''
 if not full:o+='<div class="card-body"><div class="controlrow"><label>范围 <select id="node-scope"><option value="all">全部</option>'+''.join('<option>'+h(x)+'</option>' for x in sorted(set(n['scope'] for n in st['nodes'])))+'</select></label><input type="search" id="node-search" placeholder="节点中文 / 原始ID"><span id="node-count" class="find-count"></span></div><div class="node-scroll">'
 rows=[]
 for n in st['nodes']:
  rows.append([str(n['row']),h(n['scope']),h(n['zh']),'<code>'+h(n['id'])+'</code>',h(n['status'])+' '+(ext(n['url'],'依据') if n.get('url') else '')])
 o+=table(['原行','范围','中文映射','原始ID','核对状态'],rows)
 if not full:o+='</div><p class="small muted">原顺序和重复记录全部保留；记录数不等于人物消耗点数。DSH映射待核实，不能当国服正式名已全量验证。</p></div>'
 return o

def tree_section(st):
 typ='early' if st['kind']=='level' else ['noncrit','noncrit','hybrid','crit','uber','uber'][st['number']-1]
 priorities=PRIORITIES[typ]
 body='<div class="card-body"><div class="rulelist">'+''.join('<div class="ruleitem"><b>'+h(str(i+1)+'．'+x)+'</b></div>' for i,x in enumerate(priorities))+'</div><p class="small muted">这些是当前需求优先级，不是已验证的节点连通顺序。'+src(st['source'],'作者阶段依据')+'</p></div>'
 asc='<p><b>零点射击 → 无限弹药 → 聚风 → 蜃影神射</b>是本套锐眼的升华安排；达到对应试炼与点数条件再取得，不按普通等级自动获得。</p><p>主动“狙击”和升华里同名的Far Shot不是同一个对象；原件选Point Blank / 零点射击。</p>'
 if st['readonly']:asc='<p>06所有升华节点属于Ranger3系列，与文件头Ranger1冲突；不得据此确认正常锐眼升华。保留原始记录，不猜测修复。</p>'
 body+=details('升华与武器组：怎么避免点错组',asc+'<p>作者主输出用Ⅰ，冰冻印记用Ⅱ；技能绑定与装备共用需要在游戏面板核对。剧情尚未取得足够武器专精点时，不按后期整套强配。原件未保存逐技能武器绑定。</p><p>施放印记后检查回到Ⅰ输出，技能失效先查武器与属性要求；跨组地面效果的快照时点没有国服实测，不填固定最终倍率。</p>')
 if st['nodes']:
  stats=st['original']['counts'];body+=details('完整原始节点清单：按范围查询，不把行号当点序',nodes_html(st),id='node-records')
 else:body+=nodes_html(st)
 return body

def next_html(st):
 idx=STAGES.index(st);nextst=STAGES[idx+1] if idx<10 else None
 if st['readonly']:return '<div class="card-body"><p>06是只读快照，不接到05之后当必经阶段。</p><a class="btn" href="e05.html">返回05</a> <a class="btn" href="sources.html#conflict">查看冲突证据</a></div>'
 if st['id']=='e05':return '<div class="card-body"><p>05之后没有“必须转06”的任务。保留现有可用配置，逐项验证具体首领和难度。</p><p>继续升级实际短板，不因作者实装改变就再次换树。</p><a class="btn" href="compare.html?from=e04&to=e05">查看04→05完整差异</a></div>'
 gates=TASKS.get(nextst['id'],nextst['original'].get('profile',{}).get('gate',[]))
 return '<div class="card-body"><p><b>下一阶段：</b>'+h(nextst['label']+' / '+nextst['title'])+'</p><p>'+h(GATES[nextst['id']])+'</p>'+checks(st['id'],gates,'next')+'<div class="controlrow"><a class="btn primary" href="'+nextst['file']+'">查看下一阶段 →</a><a class="btn" href="compare.html?from='+st['id']+'&to='+nextst['id']+'">只看要改什么</a></div><p class="small muted">勾选仅记录自己的检查，不解锁或隐藏任何页面。装备和技能未齐，可以继续当前阶段。</p></div>'

def stage_body(st):
 tagstr=tag('只读 · 冲突隔离','danger') if st['readonly'] else tag('60+延续方案，非作者原版','warn') if st['fallback'] else tag('全部连接同页可见','ok')
 o='<header class="page-head"><div><div class="eyebrow">'+('LEVELING' if st['kind']=='level' else 'ENDGAME')+' / '+h(st['label'])+'</div><h1>'+h(st['title'])+'</h1></div><div class="chips">'+tagstr+tag('按条件切换，不按等级解锁')+'</div></header>'
 o+='<div class="notice '+('danger' if st['readonly'] else 'warn' if st['fallback'] else '')+'"><b>这页什么时候用：</b>'+h(GATES[st['id']])+'</div>'
 o+=overview_attrs(st)
 o+='<nav class="local-nav" aria-label="本页内容"><a href="#skills">技能＋手法</a><a href="#gear">装备先换什么</a><a href="#tree">天赋与升华</a><a href="#attributes">完整属性</a><a href="#budget">精魂核算</a><a href="#next">下一步变化</a><a href="#original">完整说明/原件</a></nav>'
 skillhead='<span class="small">'+str(len(st['skills']))+'组</span>'
 o+='<div class="workspace" id="skills">'+card('技能连接 · 主动与全部辅助',skills_html(st)+upgrades(st),'skill',skillhead)+card('怎么按 · 清怪与首领',rotation(st),'combat','<button class="tiny no-print" data-copy="combat">复制手法</button>' if not st['readonly'] else '')+'</div>'
 tasks=TASKS.get(st['id'],st['original'].get('profile',{}).get('tasks',[]))
 if not st['readonly']:o+=card('现在只做这三件事','<div class="card-body">'+checks(st['id'],tasks)+'</div>',extra='<button class="tiny no-print" data-copy="skills">复制全部连接</button>')
 o+='<div class="section" id="gear">'+card('装备 · 先补真实缺口，再决定买还是做',equipment_html(st))+'</div>'
 o+='<div class="twocol section"><div id="tree">'+card('天赋 · 先后顺序与原始记录',tree_section(st))+'</div><div id="next">'+card('下一阶段 · 准备好再转',next_html(st))
 has_snipe=any(sk['key']=='snipe' for sk in st['skills'])
 output_check='分清命中、冻结、完美释放和弹幕强化对象；不要只堆狙击面板。' if has_snipe else '先检查武器实际伤害、命中和当前辅助的触发条件；不要套用别的阶段的狙击手法。'
 o+=card('卡住时，先查这四件事','<div class="card-body"><div class="rulelist"><div class="ruleitem"><b>技能变灰</b><p>核对人物等级、属性、武器类型与当前武器组，不先整树洗点。</p></div><div class="ruleitem"><b>伤害不稳定</b><p>'+h(output_check)+'</p></div><div class="ruleitem"><b>没有蓝</b><p>检查消耗、药剂和恢复条件；击杀回蓝不等于首领供蓝，印记偷取还要有对应物理击中。</p></div><div class="ruleitem"><b>总是死亡</b><p>先看生命、抗性、受击后防御与恢复，危险动作先躲。</p></div></div><p class="small"><a href="mechanics.html">打开完整机制与排障 →</a></p></div>')+'</div></div>'
 o+='<div class="section" id="attributes">'+card('整套属性核算 · 装备、主动、元技能内槽、辅助全部计入',attributes_html(st))+'</div>'
 o+='<div class="section" id="budget">'+card('资源预算 · 精魂与生命分开',budget_html(st) or '<div class="card-body">06冲突快照仅查原件，不给可运行的资源结论。</div>')+'</div>'
 original='<p>'+src(st['source'],'作者对应页面（国际服）')+' · <a href="reader.html">中文说明读本</a> · <a href="all.html#'+st['id']+'">本阶段全部记录展开</a></p>'
 if st['kind']=='level':
  s=st['original'];original+='<p><b>原说明：</b>'+h(s['intro'])+'</p><p><b>原任务：</b>'+h('；'.join(s['tasks']))+'</p><p><b>原供蓝：</b>'+h(s['mana'])+'</p><p><b>原天赋边界：</b>'+h(s['tree'])+'</p><p>'+h(s['sourceNote'])+'</p>'
 else:
  b=st['original'];p=b['profile'];file=Path(b['download']).name
  original+=f'<p><a class="btn" href="构筑文件/{h(file)}" download>{"下载只读原始快照" if st["readonly"] else "下载本分支原始.build"}</a> <a href="sources.html#builds">全部构筑与校验说明</a></p>'
  original+=f'<p><b>原件SHA-256：</b><code>{h(b["sha256"])}</code></p><p><b>范围：</b>{h(p["overview"])}</p><p><b>原始记录：</b>装备{len(b["raw"]["inventory_slots"])}条，技能{len(b["raw"]["skills"])}组，天赋{len(b["raw"]["passives"])}条（不是点数）。</p>'
  original+=details('完整原始JSON', '<pre>'+h(json.dumps(b['raw'],ensure_ascii=False,indent=2))+'</pre>')
 o+='<div class="section" id="original">'+card('完整解释与原始依据 · 不删除，不混抄', '<div class="card-body">'+original+'</div>')+'</div>'
 return o

# Resource pages, using the SAME sidebar, typography, cards and C palette (no legacy interface).
def reshead(title,lead):return '<header class="page-head"><div><div class="eyebrow">REFERENCE / 随时查阅</div><h1>'+h(title)+'</h1><p>'+h(lead)+'</p></div></header>'
def roadmap():
 o=reshead('全部阶段 · 有方向，不强制逐个洗点','等级、宝石和装备条件一起决定当前用哪份；所有阶段随时可看。')
 for kind,title in [('level','先完成剧情'),('end','再按条件进入异界进阶')]:
  o+='<div class="section-title"><h2>'+title+'</h2></div><div class="link-grid">'
  for st in STAGES:
   if st['kind']!=kind:continue
   o+='<article class="mini-card"><div class="eyebrow">'+h(st['label'])+'</div><h3>'+h(st['title'])+'</h3><p>'+h(GATES[st['id']])+'</p><div class="controlrow"><a class="btn" href="'+st['file']+'">整套作业</a><a href="all.html#'+st['id']+'">全部记录</a></div></article>'
  o+='</div>'
 o+=card('这份网站的阅读方式','<div class="card-body"><p>每阶段顶部先判断能不能用，再看完整属性参考，技能和手法并排。长解释可以展开，但技能辅助名称默认全部显示。</p><p>你不需要汇报等级才能查看下一阶段。当前页仅是书签；没有注册、服务器进度或自动改游戏配置。</p><p>05不是只换几件装备的04；06有原件冲突，不是线性第六阶段。01 Early也不是1级剧情天赋脚本。</p></div>')
 return o

def mechanics():
 o=reshead('机制与排障 · 把配置背后的原因讲清楚','按你遇到的问题查；名字、原始ID与版本边界保留，避免把旧攻略收益算进来。')
 o+='<nav class="local-nav">'+''.join('<a href="#'+k+'">'+h(title.split('；')[0].split('，')[0])+'</a>' for k,title,*_ in MECHANICS)+'</nav>'
 for k,title,text,label,url in MECHANICS:o+='<div class="section" id="'+k+'">'+card(h(title),'<div class="card-body"><p>'+h(text)+'</p><p class="small">'+ext(url,label+' / 简体数据')+'</p></div>')+'</div>'
 o+=card('一次换装之后，按这个顺序验收','<div class="card-body">'+checks('mechanics',['先看装备和所有技能是否可用，别漏元技能内槽。','检查生命、三抗、混抗与保留后可用资源。','在当前稳定难度测冻结和完整循环，不拿一次最高伤害当平均。','无击杀补给时再测药剂与供蓝，确定不是依赖刷小怪。'])+'</div>')
 return o

def craft():
 o=reshead('装备与打造 · 自己赚通货，预算内选最划算的升级','自己刷、买底材、买成品和打造是工具，不是固定阵营。不使用无法核实的价格或保证成功的概率。')
 for step,title,text in CRAFT:o+=card(h(step+'｜'+title),'<div class="card-body"><p>'+h(text)+'</p></div>')
 o+=card('材料名称别弄错',table(['材料','用途与边界','依据'],[
 ['强效磨蚀精华','弓的物理点伤方向；不是普通磨蚀精华或保证毕业。',ext('https://poe2db.tw/cn/Greater_Essence_of_Abrasion','Greater Essence of Abrasion')],
 ['强效寻觅精华','本地暴击方向；不是普通寻觅精华。',ext('https://poe2db.tw/cn/Greater_Essence_of_Seeking','Greater Essence of Seeking')],
 ['完美蜕变石','不是“完美点金”；操作前看当前稀有度与材料提示。',ext('https://poe2db.tw/cn/Perfect_Orb_of_Transmutation','Perfect Orb of Transmutation')],
 ['高级崇高石','保留等阶；不写成普通崇高石。',ext('https://poe2db.tw/cn/Greater_Exalted_Orb','Greater Exalted Orb')],
 ['高级钢铁符文','按弓或防具查看实际效果，原件未导出的孔数不补造。',ext('https://poe2db.tw/cn/Greater_Iron_Rune','Greater Iron Rune')]]))
 o+=card('项链涂膏：锯齿锋缘 / Serrated Edges','<div class="card-body"><p>节点ID <code>melee31</code>。原网页建议这项涂膏，不是要求额外花天赋点走过去。当前简体资料所列材料：液化偏执＋液化憎恶＋稀释的液化贪婪。</p><p>操作前让游戏预览确认目标节点，不按旧颜色或截图直接购买。前期缺材料先不涂；保住武器、抗性和供蓝。</p><p>'+ext('https://poe2db.tw/cn/Serrated_Edges','名称与材料依据')+' · '+ext('https://mobalytics.gg/poe-2/builds/ice-shot-deadeye','作者打造正文')+'</p></div>')
 uniques=[('卡迪罗的赌局','特殊箭效果，不是每箭同时六种。黄箭袋可维持基本链路，效率不等价。','https://poe2db.tw/cn/Cadiros_Gambit'),('拉维安加之灵','持续药剂效果伴随相应代价；普通/魔法魔力药剂＋实际恢复可替代基础供蓝。','https://poe2db.tw/cn/Laviangas_Spirits'),('新生希望','普通融冰咒符保解冻，但额外护盾充能不能继续当存在。','https://poe2db.tw/cn/Nascent_Hope'),('落刃时刻','普通真银咒符处理对应减速，失去的猛攻收益不能计入。','https://poe2db.tw/cn/The_Fall_of_the_Axe'),('猎首','只在相应高配原件出现；无稀有怪击杀不把偷取增益当常驻。','https://poe2db.tw/cn/Headhunter')]
 o+=card('暗金有替代，但不是相同强度',table(['名称','没有时怎样办','来源'],[[h(a),h(b),ext(u,'数据条目')+'<br>国服确切掉落池未确认，不设为按时必得。'] for a,b,u in uniques]))
 o+=card('购买前只核对这四项','<div class="card-body">'+checks('craft',['装备的需求和当前整套属性能否满足。','换掉旧装备之后，抗性、精魂或其他属性是否会掉线。','交易中检查成品完整词条和底材，不只看名字。','本轮花费是否在自己已刷通货预算内；失败仍保留能玩的旧装。'])+'</div>')
 return o

def glossary():
 rows=[]
 seen=set()
 for g in list(DICT['levelTerms'].values())+list(DICT['gems'].values()):
  key=g.get('id',g.get('key',g['en']))
  if g['zh']+'|'+g['en'] in seen:continue
  seen.add(g['zh']+'|'+g['en']);rows.append([h(g['zh']),h(g['en']),'<code>'+h(key)+'</code>',h(g.get('note',''))+' '+ext(g['url'],'简体数据')])
 for en,g in DICT['gearNames'].items():rows.append([h(g['zh']),h(en),'装备 / 底材',ext(g['url'],'简体数据')])
 for nid,g in DICT['nodeNames'].items():rows.append([h(g['zh']),h(g.get('en','')), '<code>'+h(nid)+'</code>',h(g.get('status','待核对'))+' '+(ext(g.get('url',''),'依据') if g.get('url') else '')])
 o=reshead('中英名称查询','技能、辅助、底材与节点放在同一张可搜索表；“有中文映射”不代表已在国服客户端逐项确认。')
 o+='<div class="controlrow"><input type="search" data-filter-table="glossary-table" placeholder="中文 / 英文 / 原始ID"><span class="find-count" data-filter-count="glossary-table"></span></div><div id="glossary-table">'+table(['中文','英文现名','类别 / ID','说明 / 核对状态'],rows)+'</div>'
 return o

def rewards():
 data=D['leveling']['rewards'];o=reshead('永久奖励核对','按已经走过的章节检查；勾选是自己的备忘录，不会解锁内容。选择奖励不能把所有分支重复累加。')
 o+='<div class="notice warn">以下按作者国际服练级正文整理。地图/首领部分保留英文消歧，国服实际任务文本与领取记录为准；没有把它们相加成一个保证全角色通用的总数。</div>'
 rows=[]
 for i,r in enumerate(data):
  # Preserve all source columns without inventing localized locations.
  vals=list(r.values()) if isinstance(r,dict) else list(r)
  rows.append(['<label><input type="checkbox" data-check="reward-'+str(i)+'"> 已核对</label>']+[ext(str(v),'查看出处') if str(v).startswith('https://') else h(str(v)) for v in vals])
 keys=list(data[0]) if data and isinstance(data[0],dict) else ['章节','位置','奖励','说明']
 names={'act':'章节','chapter':'章节','location':'地图/位置','reward':'奖励','note':'说明','source':'来源','zone':'区域','boss':'首领','nameStatus':'名称核对状态'}
 o+=table(['记录']+[h(names.get(k,k)) for k in keys],rows)
 o+='<p>'+ext('https://mobalytics.gg/poe-2/builds/ice-shot-deadeye-leveling-guide','作者Permanent Buffs原文')+'</p>'
 return o

def reader():
 o=reshead('作者长说明 · 按用途整理的中文读本','长说明不是背景故事：它解释换技能、属性、操作、武器组、装备与材料顺序。原始文本另行完整保留。')
 o+='<nav class="local-nav">'+''.join('<a href="#r'+str(i)+'">'+h(t.split('：')[-1])+'</a>' for i,(t,_) in enumerate(TRANSLATED_PROSE))+'</nav>'
 for i,(title,text) in enumerate(TRANSLATED_PROSE):o+='<div id="r'+str(i)+'" class="section">'+card(h(title),'<div class="card-body source-body"><p>'+h(text)+'</p>'+src(D['sources'][1 if i<5 else 0]['url'],'作者原文')+'</div>')+'</div>'
 for f in sorted((OUT/'原文资料').glob('*.txt')):
  text=f.read_text(errors='replace');o+=details('完整原始文本：'+f.name,'<p>导航、评论与作者正文可能混在抓取文本中；评论不是作者的正式指令。</p><p><a download href="原文资料/'+h(f.name)+'">下载原始文本</a></p><pre>'+h(text)+'</pre>')
 return o

def sources():
 o=reshead('来源、构筑下载与检查','网站界面已统一；数据覆盖、浏览器测试、翻译验证和国服实战是不同检查层级。')
 o+='<div class="section" id="builds">'+card('六份原始构筑 · 逐份选择，禁止混抄',table(['分支','原始文件','中文提示','完整性'],[[h(s['label']),'<a download href="构筑文件/'+h(Path(s['original']['download']).name)+'">'+('只读文本' if s['readonly'] else '原始 .build')+'</a>','<a download href="构筑文件/'+h(Path(s['original']['annotatedDownload']).name)+'">中文提示'+('（只读）' if s['readonly'] else '')+'</a>','<code>'+h(s['original']['sha256'])+'</code>'] for s in STAGES if s['kind']=='end']))+'</div>'
 o+='<div class="notice">.build是构筑提示JSON，不是游戏自动洗点/自动穿装备脚本。国际服默认BuildPlanner目录不当作WeGame国服已实测目录；使用客户端提供的导入入口。元技能内槽手工核对。</div>'
 o+='<div id="conflict" class="section">'+card('06冲突：保留数据，不伪造修复','<div class="card-body"><p>Live Gear文件头为 <code>Ranger1</code>，但其升华节点为 <code>AscendancyRanger3*</code>。这只能证明导出内部不一致，不能据此断言作者实际转职，也不能只改头部就认为修好。</p><p>06文件改用 <code>.build.txt</code>隔离，内容与源文件字节相同。01–05未发现同样升华前缀冲突。</p></div>')+'</div>'
 limits=[('完整原始记录','六份装备、主技能/内槽、天赋与武器组全量保留；不可用名字覆盖原始ID。'),('页面范围','六个剧情作业、六个异界作业以及全部资料工具统一C配色和紧凑结构，不跳回旧版页面。'),('整套属性','提供明确装备底材、基础宝石等级和辅助的参考核算；不是原作者实装面板，也不是玩家当前装备扫描。06冲突不造数。'),('60+剧情','作者独立60+配置未成功取得；采用已核对42–59配置延续完成剧情，显著标明，不冒充作者原版。'),('天赋连线/点序','原文件只有节点ID，缺完整静态连线及合法逐级点序。本地保留记录和条件优先级，不以数组行序编造加点。'),('国服名称','简体资料与DSH待核对映射分别标注；不是全部客户端名称已验证。'),('国服导入/游戏机制','未登录国服做导入、实际计点、战斗或全部首领实测；浏览器检查不等于这些验证。'),('掉落与价格','未确认国服确切掉落池的不指定刷取首领；没有编造实时价格、打造成功率、保过最高难度结论。')]
 o+='<div class="section" id="limits">'+card('已完成什么 / 哪些仍是资料边界',table(['项目','状态与边界'],[[h(a),h(b)] for a,b in limits]))+'</div>'
 o+=card('原始数据与本轮核算', '<div class="card-body"><div class="link-grid">'+''.join('<a class="mini-card" download href="data/'+h(f.name)+'">'+h(f.name)+'</a>' for f in sorted((OUT/'data').glob('*.json')))+'</div><p class="small">可维护源码位于“源码”目录。检查与预览目录含实际测试结果和截图，SHA256清单用于核验文件。</p></div>')
 o+=card('资料来源（国际服作者 / 数据中文展示）',table(['标记','来源','类型'],[[h(x['id']),ext(x['url'],x.get('title',x['id'])),'国际服作者' if 'mobalytics' in x['url'] else '国际服官方' if 'pathofexile.com' in x['url'] else '国际服数据简体展示'] for x in SOURCES]))
 return o

def compare():
 o=reshead('切换前只看变化 · 两份配置独立比较','技能、装备与节点一起核对；节点移组不等于增加两倍洗点费用。原件顺序不是操作顺序。')
 opts=''.join('<option value="'+s['id']+'">'+h(('剧情 ' if s['kind']=='level' else '异界 ')+s['label'])+'</option>' for s in STAGES)
 o+='<div class="controlrow"><label>从 <select id="compare-from">'+opts+'</select></label><label>到 <select id="compare-to">'+opts+'</select></label><button id="compare-run" class="primary">比较</button><button id="compare-swap">交换</button></div><div id="compare-result"></div>'
 return o

def all_body():
 o=reshead('全部作业展开 · 无需脚本也能阅读','所有阶段连接、装备、天赋、操作与参考需求一次收录。为了全文搜索，此页会很长；日常看左侧单阶段作业。')
 for st in STAGES:
  o+='<article class="fullblock section" id="'+st['id']+'"><h2>'+h(st['label']+' / '+st['title'])+'</h2><p>'+h(GATES[st['id']])+'</p><p><a class="btn" href="'+st['file']+'">回紧凑作业页</a> '+src(st['source'],'作者页面')+'</p>'+card('全部技能连接与说明',skills_html(st,True),'skill')+card('操作说明',rotation(st),'combat')+card('装备原件/阶段方向',equipment_html(st))+card('天赋记录',nodes_html(st,True))
  for p in st['profiles']:
   rows=[[h(r['label']),h(r['category']),str(r['str']),str(r['dex']),str(r['int']),h(r['note'])+' '+ext(r['url'],'依据')] for r in p['rows']]
   o+=card('完整属性参考：'+h(p['label']),table(['条目','类别','力量','敏捷','智慧','前提'],rows))
  o+='</article>'
 return o

for st in STAGES:
 body=stage_body(st);PAGES[st['file']]=shell(st['id'],st['label']+' · '+st['title'],body,st)
PAGES['index.html']=PAGES['l03.html']
for rid,func in [('roadmap',roadmap),('compare',compare),('mechanics',mechanics),('craft',craft),('rewards',rewards),('glossary',glossary),('reader',reader),('sources',sources),('all',all_body)]:PAGES[rid+'.html']=shell(rid,dict(RES).get(rid,'全部作业展开'),func())
for f,content in PAGES.items():(OUT/f).write_text(content,encoding='utf-8')
for name in ['style.css','app.js','compare.js']:
 if (BASE/name).exists():shutil.copy2(BASE/name,OUT/'assets'/name)
# Broad search includes every stage, mechanic, original equipment and all vocab; no network.
index=[]
for st in STAGES:
 index.append(dict(title=st['label']+' · '+st['title'],text=GATES[st['id']],url=st['file']))
 for sk in st['skills']:index.append(dict(title=sk['zh']+' · '+st['label'],text=sk['en']+' '+sk['note']+' '+' '.join(sp['zh']+' '+sp['en'] for sp in sk['supports']),url=st['file']+'#skills'))
 if st['kind']=='end':
  for eq in st['original']['equipment']:index.append(dict(title=eq['zh']+' · '+st['label'],text=eq['translation']+' '+eq['en'],url=st['file']+'#gear'))
for k,t,txt,label,url in MECHANICS:index.append(dict(title=t,text=txt,url='mechanics.html#'+k))
for i,(t,txt) in enumerate(TRANSLATED_PROSE):index.append(dict(title=t,text=txt,url='reader.html#r'+str(i)))
for k,g in DICT['nodeNames'].items():index.append(dict(title=g['zh']+' / '+k,text=g.get('en','')+' '+g.get('status',''),url='glossary.html?q='+k))
(OUT/'assets/search-index.js').write_text('window.SEARCH_INDEX='+js(index)+';\n')
(OUT/'assets/catalog.js').write_text('window.CATALOG='+js(STAGES)+';\n')
(OUT/'data/页面清单.json').write_text(json.dumps({'version':VERSION,'pages':list(PAGES),'stage_pages':[s['file'] for s in STAGES],'layout':'stage-workbook-r5','date':'2026-09-25'},ensure_ascii=False,indent=2))
print('Built',len(PAGES),'HTML pages')
