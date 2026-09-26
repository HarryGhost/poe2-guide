"""Fubgun crafting reader, generated from preserved source + individually labelled checks.
No network or third-party modules needed. Source text and model data are not overwritten.
"""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/Fubgun_异界后期打造.json').read_text())
SOURCES={x['id']:x for x in DATA['sources']}
MATERIALS={x['id']:x for x in DATA['materials']}
def h(t):return html.escape(str(t),quote=True)
def para(t):return '<p>'+h(t)+'</p>'
def refs(ids):
 return '<span class="craft-refs">'+ ' · '.join('<a href="'+h(SOURCES[i]['url'])+'" target="_blank" rel="noopener noreferrer">'+h('作者' if i=='author' else SOURCES[i]['title'])+' ↗</a>' for i in dict.fromkeys(ids))+'</span>'
def badge(t,cl=''):return '<span class="badge '+cl+'">'+h(t)+'</span>'
def check_list(id,items):return '<div class="checklist">'+''.join('<label><input type="checkbox" data-check="r6-'+id+'-'+str(i)+'"><span>'+h(t)+'</span></label>' for i,t in enumerate(items))+'</div>'
def details(title,body):return '<details><summary>'+h(title)+'</summary><div class="detail">'+body+'</div></details>'
def table(headers,rows):return '<div class="table-wrap"><table class="data-table"><thead><tr>'+''.join('<th>'+h(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def card(title,body,band=''):return '<section class="card"><div class="card-head '+band+'"><h2>'+h(title)+'</h2></div>'+body+'</section>'
def recipe_html(r,expanded=False):
 id=r['id'];o='<article class="craft-recipe section" id="'+id+'" data-recipe="'+id+'">'
 o+='<header class="craft-title"><div><div class="eyebrow">FUBGUN / '+h(r['stage'])+'</div><h2>'+h('工艺 '+str(r['number'])+' · '+r['title'])+'</h2><p>'+h(r['goal'])+'</p></div>'+badge(r['status'],'warn' if r['number'] in [4,5,7,8] else '')+'</header>'
 o+='<div class="notice '+('danger' if r['id']=='emerald' else 'warn')+'"><b>这一条最容易错：</b>'+h(r['critical'])+'</div>'
 o+='<div class="craft-workspace"><div class="craft-main">'
 steps='<div class="craft-steps">'
 for i,s in enumerate(r['steps']):
  steps+='<section class="craft-step"><div class="craft-step-top"><span class="craft-step-number">'+str(i+1)+'</span><h3>'+h(s['title'])+'</h3></div>'
  steps+='<div class="craft-step-body"><p><b>怎么做：</b>'+h(s['action'])+'</p><p class="craft-result"><b>做完看什么：</b>'+h(s['result'])+'</p>'
  if s['risk']:steps+='<p class="craft-risk"><b>别继续的情况：</b>'+h(s['risk'])+'</p>'
  steps+=refs(s['refs'])+'</div></section>'
 steps+='</div>'
 o+=card('步骤在这里 · 每一步重新核对物品状态',steps,'skill')
 o+=card('到哪里停，不要把可用装备做没','<div class="card-body">'+para(r['stop'])+'<p><b>购买/自做的选择：</b>'+h(r['buy'])+'</p></div>','combat')
 o+='</div><aside class="craft-aside" aria-label="'+h(r['title'])+'准备清单">'
 o+=card('先准备什么','<div class="card-body"><p><b>底材与等级：</b>'+h(r['base'])+'</p>'+check_list(id,r['preflight'])+'<p class="small muted">勾选只是个人备忘，不会解锁步骤，也不代表游戏状态已自动验证。</p></div>')
 items=''
 for mid in r['materials']:
  m=MATERIALS[mid]
  items+='<li><a href="#mat-'+mid+'">'+h(m['zh'])+'</a></li>'
 o+=card('本条材料 · 点名称看用途','<div class="card-body"><ul class="craft-material-links">'+items+'</ul><p class="small muted">“预兆”先在背包激活，再执行它指定的下一次操作；材料名称不是连点顺序。</p>'+refs(['omens'])+'</div>')
 o+='</aside></div>'
 trans=''.join(para(t) for t in r['sourceTranslation'])
 trans+='<p class="small muted">译自用户上传原文对应小节。文中“作者认为/原文说”保留原意；本页步骤补充了前置条件与已发现的省略，不冒充作者逐字原话。</p><p>'+refs(['author'])+'</p>'
 eng='<pre class="craft-original">'+h(r['sourceEnglish'])+'</pre>'
 if expanded:o+=card('作者原文完整译文（与操作补充区分）','<div class="card-body">'+trans+'</div>')+details('英文原文对照',eng)
 else:o+=details('原文到底写了什么？打开这一节完整中文译文',trans)+details('查看对应英文原文（用户提供的源文件）',eng)
 o+='</article>'
 return o

def modules_footer():
 o='<section class="section" id="craft-basics"><div class="section-title"><h2>步骤里看不懂的词，直接在这里查</h2></div>'
 o+=details('第一次执行后期工艺：操作前做这4个检查',
  '<p><b>1．先看状态：</b>拿备用装备，读清楚稀有度、物品等级、前缀/后缀、破溃或渎灵标记和空位；不要按文字行数猜词缀数。</p>'
  '<p><b>2．先读材料提示：</b>确认目标是蓝装升黄、黄装加词缀，还是黄装删除并替换。材料不允许使用时不要换一颗名称接近的硬做。</p>'
  '<p><b>3．预兆在操作前准备：</b>放在背包并按其提示激活，确认本次对应的是加前缀、加后缀、显现重掷还是定向剥离。预兆本身不代替崇高石、剥离石或骨材。</p>'
  '<p><b>4．每一步只执行一次再看结果：</b>先记下旧状态。骨材的添加与显现选择分开判断；若当前客户端界面与下文条件不符，保留装备停下，不把文本步骤当自动化脚本。</p>'+refs(['currency','omens']))
 o+=table(['词','这里具体指什么','怎样避免误操作'],[
 ['物品等级 ilvl','底材允许生成哪些层级词缀的条件之一，不等于人物等级或装备需求等级。','作者ilvl75/78/80/82是各路线前提，不表示一到人物等级就自动能做。'],
 ['前缀 / 后缀','同一件装备两类随机词缀空间。本地物理伤害、抗性等分别属于特定词缀。','看游戏高级物品说明；不要按文字上下半段或行数猜。左右旋指词缀侧，不是鼠标左右键。'],
 ['T1 / T2 / T3','作者对词缀阶级的称呼；同类通常T1为最高档。','区分数值浮动和词缀档位；完美通货限定最低词缀等级，不保证目标T1。'],
 ['渎灵 → 显现','用对应部位骨材添加渎灵属性，再在游戏的显现流程中选候选。','先激活正确预兆，再使用相应材料；回响用于显现候选，光明配剥离只移除渎灵词缀。'],
 ['破溃固定','一条属性被锁定，不能按普通可变词缀处理。','物品只是拥有+3不等于+3已锁定；破溃宝珠本身仍是随机选词条。'],
 ['点伤 / %伤害','点伤是附加的具体伤害区间；本地物理百分比放大武器相应物理底座。','箭袋/戒指写“攻击附加伤害”，不能当成武器本地DPS直接相加比较。'],
 ['底材 / 半成品 / 成品','底材是选定基底和起步状态；半成品已完成部分好词缀；成品是你愿意停止加工并使用的组合。','不是必须六词缀或三T1才叫能用；按当前伤害、资源和防御一起判断。']])
 o+=refs(['currency','omens','fracture'])+'</section>'
 o+='<section class="section" id="craft-materials"><div class="section-title"><h2>30项材料对照 · 名称、作用、使用条件</h2></div><div class="controlrow"><label for="craft-material-filter">查材料</label><input id="craft-material-filter" type="search" placeholder="中文、英文，如：光明 / Enhancement"></div><div class="craft-glossary">'
 for m in DATA['materials']:
  body='<p class="small"><b>'+h(m['en'])+'</b></p><p><b>作用：</b>'+h(m['effect'])+'</p><p class="craft-risk"><b>使用前：</b>'+h(m['check'])+'</p>'+refs([m['source']])
  o+='<details class="craft-material" id="mat-'+m['id']+'"><summary>'+h(m['zh'])+'</summary><div class="detail">'+body+'</div></details>'
 o+='</div><p id="craft-material-count" class="small muted"></p><p class="small muted">材料和效果依据国际服游戏数据简体展示；未逐项在腾讯客户端验收。原文有简写时保留英文，不能拿同系列低阶物品替代。</p></section>'
 o+='<section class="section" id="craft-other"><div class="section-title"><h2>衣服、手套、鞋、戒指、腰带：作者给了目标，没有写独立配方</h2></div><p>以下直接对照上传的01/03/04/05装备记录。加工建议明确属于整理补充，不混入lowK，不把护盾头或项链工艺移植成Fubgun未写的配方。</p>'
 stages=json.loads((ROOT/'data/全站阶段与核算.json').read_text())
 for slot in DATA['otherSlots']:
  o+=card(slot['label']+' · 要追什么','<div class="card-body"><p><b>目标：</b>'+h(slot['target'])+'</p><p><b>当前为什么这样选：</b>'+h(slot['why'])+'</p><p><b>编辑补充：</b>'+h(slot['route'])+'</p>'+refs(['author'])+'</div>')
  rows=[]
  for sid in ['e01','e03','e04','e05']:
   st=next(x for x in stages if x['id']==sid)
   eq=next((e for e in st['original']['equipment'] if e['raw']['inventory_id']==slot['id']),None)
   if eq:rows.append(['<a href="'+sid+'.html#gear">'+h(st['label'])+'</a>',h(eq['zh']),h(eq['translation']).replace('\n','<br>')])
  o+=details('看这件装备在四个原始快照中具体写了什么',table(['阶段','底材/装备','原始词条译文（不是全部必需同时达到）'],rows))
 o+='</section>'
 o+='<section class="section" id="craft-coverage"><div class="section-title"><h2>来源覆盖与尚未核实的工艺点</h2></div>'
 o+=table(['作者小节/部位','保留范围','本次怎么处理'],[[h(x) for x in r] for r in DATA['coverage']])
 o+='<div class="notice warn">'+'<br>'.join(h(x) for x in DATA['limits'])+'</div>'
 o+='<p><a href="原文资料/Fubgun_Crafting_Guide_中文操作版.md" download>下载完整中文操作版 Markdown</a> · <a href="原文资料/Fubgun_Crafting_Guide_原文完整节选.txt" download>下载作者英文打造段落</a> · <a href="data/Fubgun_异界后期打造.json" download>下载结构化内容</a></p>'
 o+=table(['来源','用于核对什么'],[['<a href="'+h(x['url'])+'" target="_blank" rel="noopener noreferrer">'+h(x['title'])+' ↗</a>',h(x['scope'])] for x in DATA['sources']])+'</section>'
 return o

def render(expanded=False):
 o='<header class="page-head"><div><div class="eyebrow">FUBGUN / ADVANCED CRAFTING · R7</div><h1>8条进阶工艺 · 先核对适用条件</h1><p>R6保留的8条作者路线，供底材与预算具备后使用；Early起步请先看新手部位作业。</p></div></header>'
 o+='<div class="craft-scope"><b>来源锁定：Fubgun，不混入lowK。</b><span>公开作者指南＋你上传的六份异界快照；全部后期路线一直开放。</span><a href="'+('craft-advanced.html' if expanded else 'craft-all.html')+'">'+('返回紧凑选择版' if expanded else '所有路线全部展开 / 打印')+'</a></div>'
 o+='<nav class="craft-choices" aria-label="八条后期打造路线">'
 for r in DATA['recipes']:
  o+='<a href="#'+r['id']+'" data-craft-choice="'+r['id']+'"><span class="craft-choice-num">'+'工艺 '+str(r['number'])+'</span><span><b>'+h(r['title'])+'</b><small>'+h(r['stage'])+'</small></span></a>'
 o+='</nav><nav class="local-nav" aria-label="打造资料导航"><a href="#craft-basics">前后缀怎么读</a><a href="#craft-materials">30项材料用途</a><a href="#craft-other">其余部位目标</a><a href="#craft-extras">暗金与涂膏</a><a href="#craft-coverage">原文覆盖与来源</a></nav>'
 if not expanded:o+='<p class="small muted craft-display-note">这里的“工艺1–8”不是BD编号，也不要求依次做完。八条始终可选；需要连续阅读，使用上方“全部展开”。</p>'
 o+='<div id="craft-recipes" data-expanded="'+str(expanded).lower()+'">'+''.join(recipe_html(r,expanded) for r in DATA['recipes'])+'</div>'
 o+=modules_footer()
 return o

def write_markdown():
 s=['# Fubgun｜异界与后期打造操作版 R7（进阶工艺库）','',DATA['scope'],'','数据核对日期：'+DATA['date'],'','完整译文来自用户上传的英文原文；操作分解、前提和补正单独标注。国服游戏内未实测。','']
 for r in DATA['recipes']:
  s+=['## '+str(r['number'])+'．'+r['title'],'','阶段：'+r['stage'],'','目标：'+r['goal'],'','底材：'+r['base'],'','**重要：'+r['critical']+'**','','### 开始前']+['- '+x for x in r['preflight']]+['','### 操作分解（整理补充）']
  for i,x in enumerate(r['steps']):s+=['','#### '+str(i+1)+'．'+x['title'],'','怎么做：'+x['action'],'','做完看什么：'+x['result'],'','风险/停下条件：'+x['risk'],'','依据：'+'；'.join(SOURCES[k]['title']+' '+SOURCES[k]['url'] for k in x['refs'])]
  s+=['','### 何时停/可以买什么','',r['stop'],'',r['buy'],'','### 对应作者段落完整中文译文','']+r['sourceTranslation']+['','### 对应英文原文','','```text',r['sourceEnglish'],'```','']
 s+=['## 材料对照','']
 for m in DATA['materials']:s+=['### '+m['zh']+' / '+m['en'],'',m['effect'],'','使用前：'+m['check'],'','依据：'+SOURCES[m['source']]['url'],'']
 s+=['## 其他部位：作者目标与编辑建议','']
 for x in DATA['otherSlots']:s+=['### '+x['label'],'','目标：'+x['target'],'','原因：'+x['why'],'','编辑补充：'+x['route'],'']
 s+=['## 边界','']+DATA['limits']
 (ROOT/'原文资料/Fubgun_Crafting_Guide_中文操作版.md').write_text('\n'.join(s),encoding='utf-8')
