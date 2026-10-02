"""R39: passive-tree jewels; original builds, skill links and filters are not changed."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
F='https://mobalytics.gg/poe-2/builds/ice-shot-deadeye'
SOURCES=[
 {'id':'fubgun','title':'Fubgun 0.5.5 正文：树上珠宝与升级次序','url':F,'kind':'作者原文','use':'明确的一颗回蓝蓝玉、普通珠宝词缀方向、泉井之心与抗衡黑暗；不是六阶段逐孔实装。'},
 {'id':'sapphire','title':'蓝玉：人物天赋珠宝基底','url':'https://poe2db.tw/cn/Sapphire','kind':'游戏数据条目','use':'确认基底和物品类别；“蓝玉”不表示魔法稀有度。'},
 {'id':'emerald','title':'翡翠：人物天赋珠宝基底','url':'https://poe2db.tw/cn/Emerald','kind':'游戏数据条目','use':'确认基底与用途；不把任意作者通用词缀强行归到同一底材。'},
 {'id':'well','title':'泉井之心：词缀池、限定数量及来源','url':'https://poe2db.tw/cn/Heart_of_the_Well','kind':'游戏数据条目','use':'双额外伤害的可选类型和数值区间；示例物品不是作者实装。'},
 {'id':'darkness','title':'抗衡黑暗：范围词缀与限定数量','url':'https://poe2db.tw/cn/Against_the_Darkness','kind':'游戏数据条目','use':'核心天赋的额外伤害词缀；按实物范围验收，不固定整个版本的孔位坐标。'},
 {'id':'alliance','title':'绝境同盟：抗衡黑暗的定向掉落条件','url':'https://poe2db.tw/cn/The_Desperate_Alliance','kind':'游戏数据条目','use':'丝克玛试炼遗物、首领强化与消耗条件；不是普通通关必掉。'},
 {'id':'delirium','title':'惊悸迷雾：液化憎恶的蓝玉工艺效果','url':'https://poe2db.tw/cn/Delirium','kind':'游戏数据条目','use':'可给稀有基本蓝玉增加击杀回魔后缀，但会随机移除词缀；不作为无风险步骤。'}
]

def make_guide(root:Path,D:dict)->dict:
 g={'version':'R39','checked':'2026-10-02','scope':'人物天赋树的珠宝；不含技能／辅助宝石、装备符文、深渊之眼或异界配置。',
    'basis':'六份用户0.5.5快照负责节点证据；本次核对的作者正文负责建议；数据库负责物品定义。网页内容不回写原BD。',
    'sources':SOURCES,'stages':{},'catalog':{},'specialIds':['well','darkness'],
    'boundary':'六份构筑没有逐孔珠宝物品记录。能核对节点ID和节点数，不能由此证明每孔已插哪颗、实物词缀或正确覆盖位置。'}
 catalog={
 'mana':{'id':'mana','zh':'击杀回蓝的蓝玉','en':'Sapphire · Mana on Kill','kind':'普通功能珠宝','special':False,
  'qty':'作者明确建议准备1颗；占用一个已分配的人物珠宝槽。','goal':'核心是击败敌人时恢复魔力，其他词缀再补当前有效伤害或资源。不要只按蓝玉名字买。',
  'mods':['魔力在击败敌人时恢复；液化憎恶的蓝玉后缀数据为1–2%。这是可选获取效果，不是作者规定的最低掷值。','附带词缀按实际物品确认；不要求这颗兼有全部输出词缀。'],
  'when':'01起的刷图供蓝。即使换阶段，也先保留，直到实测其他供蓝足以替代。',
  'get':'拾取或在可交易环境取得带相应词缀的成品。自行加工可比较液化憎恶对稀有基本蓝玉的效果，但它会随机移除一条词缀，先核对物品资格和可承受损失。',
  'socket':'普通人物珠宝槽；先点出槽再放入。具体使用哪个ID未在原件指定，不需要按范围凑周围天赋。',
  'limits':'没有击杀就不会触发这条回蓝；无小怪首领不能仅靠它续航。蓝玉是基底名，不是“蓝色装备”，也不是未切割技能宝石。',
  'fallback':'未取得时保留现有供蓝，不能先移除魔力药剂或已有印记供蓝。取得后分别验收清图和首领。',
  'sourceIds':['fubgun','sapphire','delirium']},
 'ordinary':{'id':'ordinary','zh':'普通输出珠宝（如翡翠）','en':'Rare / Magic Jewels · Emerald','kind':'普通输出珠宝','special':False,
  'qty':'按剩余已分配槽位准备，不把全套清单的每一行都额外加一颗。',
  'goal':'非暴击阶段看有效攻击／投射物／元素伤害、攻击速度等；04开始暴击配置具备后，再比较攻击暴击率与攻击暴击伤害。',
  'mods':['通用筛选方向：攻击伤害、投射物伤害、元素伤害、攻击速度；移动速度和箭袋加成要读实际适用范围。','04/05再比较攻击暴击率、攻击暴击伤害加成；别把“法术暴击”误当弓攻击暴击。','这是候选方向，不是一颗珠宝必须或能够同时具有的固定词缀清单。不同基底、生成来源和词缀占位分别核对。'],
  'when':'早期先用两三条真正适用的属性作过渡；两三条是本站筛选建议，不是物品等级或强制门槛。',
  'get':'优先比较已有掉落或合适成品。可从普通珠宝页看低投入处理；作者的高投入翡翠扩容工艺保留只读，不默认照做。',
  'socket':'普通人物珠宝槽；先解决当前短板，不为一颗一般珠宝强行多绕天赋点。',
  'limits':'没有统一“毕业词缀＋固定数值”；作者高投入翡翠的20%攻击暴伤起手不等于Early最低要求。普通珠宝不能无条件套用防具六词缀流程。',
  'fallback':'特殊珠宝暂缺就留有效普通珠宝；只是过渡，不宣称相同伤害。',
  'sourceIds':['fubgun','emerald']},
 'well':{'id':'well','zh':'泉井之心','en':'Heart of the Well','kind':'暗金人物珠宝 · 宝钻','special':True,
  'qty':'限定1颗；与抗衡黑暗分别占槽，不是所有暗金珠宝合计只能1颗。',
  'goal':'作者目标是两条“获得相当于伤害的额外伤害”。不是随便一颗同名泉井之心都满足。',
  'mods':['元素类型的额外伤害：冰霜／火焰／闪电，每条数据区间9–15%。','混沌类型的额外伤害：数据区间7–13%。','以上是可选词缀池，不是四条同时存在。作者未在六份快照里指定固定两种组合与掷值；其余词缀按实际用途比较。'],
  'when':'作者升级次序在完善非暴击配置时已提到它，不必把它锁到05才看；起步仍可用普通珠宝。',
  'get':'来源数据标为深渊；可交易环境也可按实际两条词缀找成品。不能承诺一次深渊必掉或固定价格。',
  'socket':'放入已分配的人物珠宝槽。所述双额外伤害是珠宝自身属性，不按周围核心天赋数量再乘一遍。原件未指定它对应哪个槽。',
  'limits':'限定1颗；不凭名字、颜色、未揭示状态或数据库示例确认目标。随机词缀可能是召唤生物等与你无关的效果。',
  'fallback':'继续用现有有效普通珠宝；不要为拿到“名字正确”的低适配品先拆掉必要的回蓝珠宝。',
  'sourceIds':['fubgun','well']},
 'darkness':{'id':'darkness','zh':'抗衡黑暗','en':'Against the Darkness','kind':'暗金范围珠宝 · 失落的宝钻','special':True,
  'qty':'限定1颗；放入一个人物珠宝槽后，还要核对范围内的实际已分配节点。',
  'goal':'作者先考虑“范围内核心天赋提供额外冰霜伤害”，后续再追双额外伤害组合。不是只买两条任意加成。',
  'mods':['目标行作用于范围内核心天赋：获得相当于伤害2–4%的额外冰霜伤害。','其他可选额外伤害类型有火焰、闪电、混沌，单行数据区间均为2–4%。','词缀写“小型天赋”的，只对相应小型节点生效；不能当作核心天赋的目标行。数据池不是同一颗珠宝拥有全部效果。'],
  'when':'放到已有足够适用核心天赋覆盖的孔位才比较收益。来源是作者升级方向，不代表05原件已记录具体插装。',
  'get':'定向来源是丝克玛试炼中使用绝境同盟遗物，再击败扎洛卡，时空之灵。该遗物会被消耗并强化首领，不是普通通关默认必掉；也可按实际词缀比较成品。',
  'socket':'必须看实物半径，逐一核对范围内已点出的合格核心天赋。原件没有完整树坐标、珠宝—槽位绑定与半径截图，因此不画伪造圈、不宣称某个ID是作者最佳孔。',
  'limits':'限定1颗；两条词缀、作用对象和半径都要看。普通规则下只圈住但未分配的节点不能直接计收益；特殊“未分配节点”词缀另按实物解释。不要把数据库某件示例半径当所有历史版本固定半径。',
  'fallback':'没有合适覆盖就继续普通珠宝；为了范围多绕的天赋点要一并比较，不强行放在剩下的随便一个孔里。',
  'sourceIds':['fubgun','darkness','alliance']}
 }
 g['catalog']=catalog
 configs={
 'e01':{'focus':'先处理刷图回蓝，再补普通输出；特殊珠宝可阅读，不作为进异界前置。','plans':[['起步准备',[['mana',1],['ordinary',1]]]],'next':'下一阶段仍是2个不同槽，不能把升级清单当作额外新增孔。'},
 'e02':{'focus':'维持非暴击有效词缀；完善配置时可以用泉井之心替换普通珠宝。','plans':[['过渡',[['mana',1],['ordinary',1]]],['已有合适泉井之心',[['mana',1],['well',1]]]],'next':'换入泉井之心是替换1颗，不是变成3颗；三孔要到有第三个节点的对应原件。'},
 'e03':{'focus':'混合防御阶段有3个不同孔位；供蓝之外逐步补普通输出或泉井之心。','plans':[['尚无合适暗金',[['mana',1],['ordinary',2]]],['已有合适泉井之心',[['mana',1],['well',1],['ordinary',1]]]],'next':'新增jewel_slot1961。可比较合适抗衡黑暗，但不自动认定应放在新增的那个孔。'},
 'e04':{'focus':'暴击配置具备后，普通珠宝再比较攻击暴击相关词缀；特殊范围珠宝仍先验覆盖。','plans':[['暴击过渡',[['mana',1],['well',1],['ordinary',1]]],['缺泉井之心',[['mana',1],['ordinary',2]]]],'next':'原件仍为3个不同槽。有合适抗衡黑暗时从现有三颗里替换，不无条件多加第四颗。'},
 'e05':{'focus':'双特殊珠宝是作者后期方向，但两颗各占一孔；回蓝需求与抗衡黑暗覆盖要同时成立。','plans':[['仍需击杀回蓝，且两颗暗金适配',[['mana',1],['well',1],['darkness',1]]],['其他供蓝已单独验证足够',[['well',1],['darkness',1],['ordinary',1]]],['抗衡黑暗尚无合适覆盖',[['mana',1],['well',1],['ordinary',1]]]],'next':'三种是互斥准备示例，不是叠加采购表；不能只因升到05就移除回蓝珠宝。'},
 'e06':{'focus':'只读原始快照；保留武器组重复记录，不生成第六阶段采购或改树指令。','plans':[],'next':'5个不同ID、6条记录；jewel_slot1960在公共与武器组2重复出现，不能据此购买第6颗。'}
 }
 for i,(s,b) in enumerate(zip(D['stages'],D['branches']),1):
  name=['01_Early.build','02_noncrit_Midgame.build','03_noncrit_Hybrid.build','04_Crit_Hybrid.build','05_Uber_Endgame.build','06_Live_Gear_冲突勿导入.build.txt'][i-1]
  rel='R28原站/构筑文件/'+name;p=root/rel;raw=json.loads(p.read_text());rows=[]
  for j,n in enumerate(raw['passives'],1):
   if n['id'].startswith('jewel_slot'):
    rows.append({'id':n['id'],'exportIndex':j,'weaponSet':n.get('weapon_set'),'scope':'武器组'+str(n['weapon_set']) if n.get('weapon_set') else '公共记录（未标专属武器组）'})
  unique=list(dict.fromkeys(r['id'] for r in rows));rec={'id':s['id'],'label':s['label'],'readonly':s['readonly'],'sourceFile':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':rows,'uniqueIds':unique,'uniqueCount':len(unique),'recordCount':len(rows),'installedJewels':None,'fixedPositions':None,**configs[s['id']]}
  # Each plan is capacity-checked here; the assumed allocations are never written back to the build.
  rec['plans']=[{'title':n,'items':[{'id':k,'qty':q} for k,q in items],'total':sum(q for _,q in items),'provenance':'本站准备示例，不是原件逐孔实装'} for n,items in rec['plans']]
  assert all(p['total']<=rec['uniqueCount'] for p in rec['plans'])
  assert all(r['id'] in catalog for p in rec['plans'] for r in p['items'])
  rec['inventoryJewels']=[v for v in raw['inventory_slots'] if 'jewel' in v.get('inventory_id','').lower()]
  assert not rec['inventoryJewels']
  g['stages'][s['id']]=rec
 return g

def markdown(g:dict)->str:
 lines=['# R39｜人物天赋珠宝清单','','这是放进人物天赋树珠宝槽的物品，不是技能、辅助宝石或装备符文。','',
 '核对：2026-10-02。六份0.5.5原件未修改；作者正文建议与本站准备示例分别标记。','',
 '## 先看需要哪几类','','| 珠宝 | 数量与用途 | 主要目标 |','| --- | --- | --- |']
 for x in g['catalog'].values():lines += [f'| {x["zh"]} / {x["en"]} | {x["qty"]} | {x["goal"]} |']
 lines+=['','作者明确要求和升级方向：'+F,'',
 '## 原件的孔位记录，不是已经装好的珠宝数量','','| 阶段 | 不同珠宝槽ID数 | 原始记录条数 | 已记录ID |','| --- | ---: | ---: | --- |']
 for s in g['stages'].values():lines += [f'| {s["label"]}'+('（只读）' if s['readonly'] else '')+f' | {s["uniqueCount"]} | {s["recordCount"]} | '+', '.join(s['uniqueIds'])+' |']
 lines += ['',g['boundary'],'','06的jewel_slot1960在公共记录与武器组2各出现一次。5个不同ID不等于已验证5颗同时生效，更不是需要第6颗。导出数组序号不是人物等级、加点顺序或地图坐标。','',
 '## 按阶段准备（本站示例，不是作者逐孔实装）','']
 for s in g['stages'].values():
  lines+=['### '+s['label']+(' · 只读' if s['readonly'] else ''),'',s['focus'],'']
  for p in s['plans']:lines += ['**'+p['title']+'：**'+' ＋ '.join(str(i['qty'])+'颗'+g['catalog'][i['id']]['zh'] for i in p['items'])+f'，合计{p["total"]}颗。','']
  lines += [s['next'],'','原件：`'+s['sourceFile']+'`','SHA-256：`'+s['sha256']+'`','']
 lines+=['## 普通和特殊珠宝，逐件看','']
 for x in g['catalog'].values():
  lines+=['### '+x['zh']+' / '+x['en'],'', '**类别与数量：**'+x['kind']+'；'+x['qty'],'','**要找的目标：**'+x['goal'],'']
  for m in x['mods']:lines += ['- '+m]
  for key,label in [('when','什么时候准备'),('get','获取方式'),('socket','镶嵌位置'),('limits','避免误用'),('fallback','没有时怎么办')]:lines += ['','**'+label+'：**'+x[key]]
  lines+=['','来源：'+'；'.join(next(s['url'] for s in g['sources'] if s['id']==id) for id in x['sourceIds']),'']
 lines += ['## 抗衡黑暗：怎样验收范围','','先点出当前树上合适的珠宝槽，再在游戏中预览实物半径。核对两条词缀分别写的是核心还是小型天赋，只数范围内已经分配且符合描述的节点。未点的节点或圈外节点，不直接计入普通范围词缀收益。','',
 '示例（仅解释，不是作者实装）：一条核心天赋额外冰霜3%，覆盖3个已分配的合格核心，则这条带来9%的额外冰霜比例。它不等于整套实际DPS必增9%，也不能把所有圈内小点都一起算。泉井之心所述自身额外伤害，不按这个节点数重复乘。','',
 '缺少完整坐标与逐孔物品绑定，因此本版不画假位置、不编种子或“最佳孔”。条目里提供原件ID，方便与游戏逐项核对。','',
 '## 换装检查','','确认是人物天赋树珠宝槽；先分配槽再插。先保留旧珠宝，比较现有词缀、必要供蓝、条件覆盖和总槽数。武器组1与2分别看生效状态；清图与无小怪首领分别试。限定数量按物品自身看，品质也不统一要求20。','',
 '## 本轮纠正与验证边界','','R38中“需要哪些宝石”“特殊宝石”此前回答成技能／辅助宝石，理解偏了。本版将人物天赋珠宝放到人物天赋旁，并单列特殊人物珠宝。原技能清单保留为“技能/辅助宝石清单”，血脉辅助标为“非天赋珠宝”，不再混用入口。精华步骤、原BD、异界和金币修正不动。','',
 '程序能验证原件节点、去重、清单容量和网页联动，不能证明玩家已分配这些点或游戏实际收益。未实测国服客户端、工艺、掉落或线上部署。','',
 '## 来源与用途','']
 for s in g['sources']:lines += ['**'+s['title']+'（'+s['kind']+'）**：'+s['use'],'',s['url'],'']
 return '\n'.join(lines)+'\n'
