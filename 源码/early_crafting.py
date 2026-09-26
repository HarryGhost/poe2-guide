"""Early-first teaching pages. Uses preserved Fubgun targets and labelled editorial advice."""
from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/Early起步打造教学.json').read_text())
RECIPES=json.loads((ROOT/'data/Fubgun_异界后期打造.json').read_text())['recipes']
STAGES=json.loads((ROOT/'data/全站阶段与核算.json').read_text())
EARLY=next(s for s in STAGES if s['id']=='e01')
def h(x):return html.escape(str(x),quote=True)
def link(url,t):return '<a href="'+h(url)+'">'+h(t)+'</a>'
def para(t):return '<p>'+h(t)+'</p>'
def card(t,body,band=''):
 return '<section class="card"><div class="card-head '+band+'"><h2>'+h(t)+'</h2></div><div class="card-body">'+body+'</div></section>'
def det(t,body):
 return '<details><summary>'+h(t)+'</summary><div class="detail">'+body+'</div></details>'
def table(head,rows):
 return '<div class="table-wrap"><table class="data-table"><thead><tr>'+''.join('<th>'+h(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def refs():
 return '<p class="small muted">装备方向：<a href="'+DATA['source']+'" target="_blank" rel="noopener noreferrer">Fubgun异界篇 / 国际服作者</a>；基础通货：<a href="https://poe2db.tw/cn/Stackable_Currency" target="_blank" rel="noopener noreferrer">游戏数据简体展示</a>。普通加工步骤为编辑补充，不是作者逐字配方。</p>'
def stage_links():
 return '<nav class="early-stage-nav" aria-label="打造阶段，全部自由查看">'+''.join('<a data-craft-stage="'+p['id']+'" href="#stage-'+p['id']+'"><b>'+h(p['label'])+'</b></a>' for p in DATA['plans'])+'<a href="e06.html">06 实装冲突 · 只读</a></nav>'
def item_html(it):
 o='<article id="early-'+it['id']+'" data-early-item="'+it['id']+'" class="early-item"><div class="early-item-head"><h2>'+h(it['title'])+' · '+h(it['priority'])+'</h2><span class="badge">01 Early</span></div>'
 o+='<div class="early-workspace"><div class="early-instructions">'
 stepbody=''
 for i,(title,action,result,risk) in enumerate(it['steps']):
  stepbody+='<section class="early-step"><h3><span>'+str(i+1)+'</span>'+h(title)+'</h3><p>'+h(action)+'</p><p class="small"><b>结果判断：</b>'+h(result)+'</p><p class="small early-caution"><b>别踩坑：</b>'+h(risk)+'</p></section>'
 o+=card('现在怎么做',stepbody,'skill')+'</div><aside class="early-readout">'
 o+=card('目标与准备',para(it['target'])+'<p><b>从什么开始：</b>'+h(it['start'])+'</p>','combat')
 o+=card('这阶段不要求',para(it['avoid']))
 adv=link('craft-advanced.html#'+it['advanced'],it.get('advancedText','查看对应高阶工艺')) if it.get('advanced') else link('craft-advanced.html#craft-other','看作者其它部位目标与来源')
 o+=card('以后怎么升级',para(it['later'])+'<p>'+adv+'</p>')
 original=[e for e in EARLY['original']['equipment'] if e['raw']['inventory_id'] in it['slots']]
 if original:
  rows=[[h(e['zh'])+'<br><small>'+h(e['en'])+'</small>',h(e['translation']).replace('\n','<br>')] for e in original]
  o+=det('作者Early原件怎么写？不是最低门槛',
   '<p class="small">以下逐条取自上传的Early文件。展示底材和数值不是进入异界必需同时达到；未列的词条不等于不需要。</p>'+table(['原件名称','原词条译文'],rows))
 else:o+=det('原件没有珠宝实装，不能补猜',para('只保留作者正文的方向；没有原始珠宝词条、种子和插入位置，不会伪造一颗“必需珠宝”。'))
 o+='</aside></div>'+refs()+'</article>'
 return o
def early_panel(expanded=False):
 p=DATA['plans'][0]
 o='<section id="stage-early" data-stage-panel="early" class="early-panel"><div class="early-overview">'
 o+='<div><span class="eyebrow">当前教程 / 刚进入异界</span><h2>'+h(p['title'])+'</h2><p>'+h(p['summary'])+'</p></div>'
 o+='<div class="early-priority"><b>怎么排优先级</b><p>'+h(p['focus'])+'</p></div></div>'
 o+='<div class="early-distinction"><b>不要误会：</b>作者的展示装备不等于最低门槛。先保证当前能用，装备逐件升级；ilvl75只约束相应进阶工艺。 <a href="e01.html">打开Early完整技能/天赋作业 →</a></div>'
 o+='<nav class="early-item-nav" aria-label="Early装备部位">'+''.join('<a data-early-choice="'+it['id']+'" href="#early-'+it['id']+'">'+h(it['title'])+'</a>' for it in DATA['items'])+'</nav>'
 o+='<p class="small muted">先点一个部位，直接看目标、操作与停手条件。所有部位都能立即打开，不需要勾选解锁。<a href="craft-early-all.html">全部展开</a></p>'
 o+='<div class="early-items">'+''.join(item_html(it) for it in DATA['items'])+'</div></section>'
 return o
def later_panels():
 o=''
 for p in DATA['plans'][1:]:
  body=para(p['summary'])+'<p><b>优先准备：</b>'+h(p['focus'])+'</p><p><b>暂时别做：</b>'+h(p['wait'])+'</p><p><b>下一阶段条件：</b>'+h(p['ready'])+'</p><p>'+link(p['page'],'查看本BD完整作业')+' · '+link('craft.html#stage-early','回Early起步')+'</p>'
  o+='<section id="stage-'+p['id']+'" data-stage-panel="'+p['id']+'" class="early-panel">'+card(p['label']+' / '+p['title'],body,'skill')+'<div class="early-recipe-grid">'
  for rid in p['routes']:
   r=next(r for r in RECIPES if r['id']==rid)
   o+='<a class="mini-card" href="craft-advanced.html#'+rid+'"><b>'+h(r['title'])+'</b><p>'+h(r['base'])+'</p><small>先读前置条件，再做。不是阶段编号要求全做。</small></a>'
  o+='</div>'+refs()+'</section>'
 return o
def footer():
 o='<section class="section" id="early-basics">'
 basics=table(['材料 / 操作','可以对什么用','这一步的结果','新手要避开的误解'],[
 ['普通蜕变石','可加工白装','变蓝并随机增加1条词缀','不是重复洗同一蓝装；没有指定好词条保证。'],
 ['普通增幅石','仍有合法随机词缀空位的蓝装','随机增加1条','不要按文字行数当词缀数；特殊物品规则另查。'],
 ['普通富豪石','可以升稀有的蓝装','升黄并增加1条词缀','和蓝装升黄精华是分支选择；不用于药剂和咒符做黄装。'],
 ['普通崇高石','有合法空位、值得投入的黄装','随机增加1条词缀','不会把所有原有数值同时提高；不保证你想要的那条。'],
 ['强效磨蚀精华','符合本体及词缀条件的蓝弓等适用物品','对应弓的物理点伤升黄路线','先读完整工艺；没有材料也能用Early，不是必要门票。']])
 o+=det('第一次打造：材料名字与鼠标操作', '<p>每次只执行1次：先右键准备使用的材料，再左键目标备用装备；游戏提示不允许时停止，不换名字相近的材料硬做。点完先看颜色、需求、词缀与原有属性，再决定下一步。</p>'+basics+refs())
 o+=det('别把3种“等级”混在一起','<p><b>人物等级：</b>你的角色等级。<b>装备需求等级：</b>你能否穿这件装备。<b>物品等级 ilvl：</b>影响可生成的词缀等条件。</p><p>作者的非暴击弓工艺以ilvl75为起点；这不代表人物75级，也不表示所有Early可用弓都必须ilvl75。底材、词缀可能另有需求，要读物品提示。</p>')
 o+=det('为什么普通加工不是固定“必成配方”？','<p>本页把作者装备目标与通货的基本效果结合，提供低投入的备用件补强建议。随机词条、词缀组、前后缀空位和材料规则决定实际结果；没有把“增幅→富豪→崇高”写成必出目标属性。</p><p>白装不一定比蓝/黄成品更值得做。可以直接捡成品、买半成品或买可用装备；这都不违背Fubgun路线。不强迫你从零做满每个部位。</p>')
 o+='</section>'
 rows=[]
 for p in DATA['plans']:
  rows.append([link('#stage-'+p['id'],p['label']),h(p['focus']),h(p['wait'])])
 o+='<section class="section" id="craft-stage-map">'+det('全部阶段总览：现在就能查看后面做什么',table(['阶段','装备工作重点','不当成入场要求'],rows)+'<p>这是按照作者分支与装备方向整理的工作顺序，不要求每个人依次重做所有装备。06是冲突快照，不是线性第六步。</p>')+'</section>'
 o+='<section class="section" id="craft-library"><div class="section-title"><h2>作者8条进阶工艺 · 全部一直开放</h2><a href="craft-all.html">完整展开版</a></div><div class="early-recipe-grid">'
 for r in RECIPES:o+='<a class="mini-card" href="craft-advanced.html#'+r['id']+'"><b>'+h(r['title'])+'</b><small>'+h(r['stage'])+'</small></a>'
 o+='</div><p class="small muted">这里是工艺库，不是8个阶段。原文及译文完整保留；某些高投入工艺有未确认前提，不作为保证成功步骤。</p></section>'
 o+=det('来源和这轮仍未解决的边界',
  '<p>主BD：Fubgun 0.5.5 Early（国际服作者）；装备原件：用户上传的01_Early.build。基础材料：游戏数据简体展示，不等于腾讯客户端逐项核验。</p><p>新增的是Early起步的教学层和明确进阶入口，没有改动原始天赋、装备或技能数据。历史缺少的完整天赋连线、合法逐级点序、国服导入与高级工艺实测仍未完成。</p><p>'+link('sources.html#limits','完整边界')+' · '+link('data/Early起步打造教学.json','本页完整数据')+'</p>')
 return o
def render(expanded=False):
 o='<header class="page-head"><div><div class="eyebrow">FUBGUN / EARLY-FIRST CRAFTING · R7</div><h1>从Early开始：装备怎么拿、怎么做、做到哪停</h1><p>仍按第一次玩的新手讲解。先把非暴击、生命/闪避这一套做能用，再按条件进入后面的工艺。</p></div></header>'
 o+='<div class="craft-scope"><b>不是31级剧情教程，也不是一上来做最高配。</b><span>Fubgun路线；自己刷通货，预算内购买/打造。</span><a href="'+('craft.html' if expanded else 'craft-early-all.html')+'">'+('返回紧凑版' if expanded else 'Early全部展开')+'</a></div>'
 o+=stage_links()
 o+='<div id="early-workbook" data-expanded="'+str(expanded).lower()+'">'+early_panel(expanded)+later_panels()+'</div>'
 o+='<nav class="local-nav"><a href="#early-basics">基础材料与三种等级</a><a href="#craft-stage-map">全部阶段顺序</a><a href="#craft-library">8条进阶工艺</a></nav>'
 return o+footer()
def write_markdown():
 lines=['# 从Early开始的Fubgun装备打造 · R7','','这是异界起步，不是31级剧情；按第一次玩的新手讲解。作者目标与编辑普通加工建议分开。','']
 for p in DATA['plans']:lines+=['## '+p['label'],p['summary'],'优先：'+p['focus'],'不当门槛：'+p['wait'],'']
 for it in DATA['items']:
  lines+=['## Early｜'+it['title'],'目标：'+it['target'],'起点：'+it['start'],'']
  for i,(t,a,r,k) in enumerate(it['steps']):lines+=['### '+str(i+1)+'. '+t,a,'结果判断：'+r,'风险：'+k,'']
  lines+=['后续：'+it['later'],'不要：'+it['avoid'],'']
 lines+=['## 来源','作者目标：'+DATA['source'],'基础通货：https://poe2db.tw/cn/Stackable_Currency','八条进阶原文与译文继续保留，见craft-all.html。']+DATA['limits']
 (ROOT/'原文资料/Early起步打造_中文操作说明.md').write_text('\n'.join(lines),encoding='utf-8')
