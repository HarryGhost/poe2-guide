"""Restore teaching separately from immutable R43 captures and R44 localized UI."""
from pathlib import Path
import json,copy,sys,re
W=Path(__file__).parent;B=Path(sys.argv[1]) if len(sys.argv)>1 else W/'baseline'
idx=(B/'index.html').read_text();ref=re.search(r'<script src="(assets/content[^"]+)"',idx)[1];raw=(B/ref).read_text();D=json.loads(json.loads(raw.split('=',1)[1].strip().rstrip(';')))
L=json.loads((B/'data/R44_localization.json').read_text());C=json.loads((B/'data/R43_capture_overlay.json').read_text())
F='https://mobalytics.gg/poe-2/builds/ice-shot-deadeye';DB='https://poe2db.tw/cn/'
# Bare base fields. All numbers below describe unmodified bases, not captured finished items.
facts={}
def fact(en,zh,cat,level,str_,dex,int_,base,note=''):
 facts[en]=dict(name=zh,level=level,str=str_,dex=dex,int=int_,base=base,note=note,url=DB+cat,checked='2026-10-06')
fact('Zealot Bow','狂热弓','Bows',39,0,70,0,'物理31–47；每秒1.20次；基础暴击率5%')
fact('Obliterator Bow','毁灭者之弓','Bows',78,0,163,0,'物理62–115；每秒1.10次；基础暴击率5%','投射物射程降低50%，不能只比伤害上限。')
fact('Warmonger Bow','寻战之弓','Bows',77,0,163,0,'物理56–84；每秒1.20次；基础暴击率5%')
fact('Volant Quiver','飞矢箭袋','Quivers',61,0,0,0,'固有：投射物速度提高20–30%')
fact('Primed Quiver','精工箭袋','Quivers',51,0,0,0,'固有：攻击速度提高7–10%')
fact('Visceral Quiver','贯心箭袋','Quivers',65,0,0,0,'固有：攻击的暴击率提高20–30%','用于暴击方向的备选，不为非暴击过渡硬追。')
fact('Broadhead Quiver','宽矢箭袋','Quivers',1,0,0,0,'固有：攻击附加1–3物理伤害','低级临时底材；已有更好的成品就不用倒退。')
fact('Viper Cap','毒蝰帽','Helmets',38,0,54,0,'基础闪避179')
fact('Desert Cap','沙漠帽','Helmets',70,0,99,0,'基础闪避311')
fact('Ancestral Tiara','先祖冠冕','Helmets',80,0,0,115,'基础能量护盾109','转型比较的是做完的头盔自身护盾，不是109就达到转型目标。')
fact('Serpentscale Coat','蛇鳞外套','Body_Armours',36,0,59,0,'基础闪避260')
fact('Corsair Coat','海盗外套','Body_Armours',80,0,121,0,'基础闪避451；固有移动速度提高5%','基础衣服移动惩罚与固有提高是不同字段；不把5%当最终净移动收益。')
fact('Slipstrike Vest','滑击背心','Body_Armours',70,0,121,0,'基础闪避519')
fact('Spined Bracers','精纺护腕','Gloves',33,0,42,0,'基础闪避79')
fact('Grand Bracers','宏伟护腕','Gloves',70,0,87,0,'基础闪避155')
fact('Lizardscale Boots','蜥鳞靴','Boots',33,0,45,0,'基础闪避118')
fact('Cavalry Boots','骑兵长靴','Boots',70,0,93,0,'基础闪避233')
fact('Bladed Shoes','嵌刃便鞋','Boots',65,0,47,47,'基础闪避122；基础能量护盾37')
# Sources/conditional guidance are concise at card level; full reasoning is per-item.
slot={
 'bow':dict(title='弓',brief='先用当前能穿、实际伤害好的弓。狂热弓是较低需求过渡示例；毁灭者／寻战之弓是后续可比较的底材，不是进图门槛。',keep='先保本地物理伤害与有效冰霜点伤，再比较攻速；投射物等级会影响消耗，不能单看“＋等级”。',when='现用弓明显拖慢当前内容，而备用弓的基础和已有词缀更合适时，再考虑一次加工；有实际提升就可以先停。',acquire='先比较拾取、商店或可交易环境中的合格成品；没有合适蓝底，不要求从白装赌起。完整进阶弓配方的物等75只约束该配方。',stop='同样技能、辅助和站位下，清图、冻结与首领输出有改善，连续输出不频繁断蓝；达成当前目标就保留材料。',compare='已成品：用物品顶部物理上下限的平均值×每秒攻击次数，只得到武器物理伤害每秒值。冰霜等其他伤害、暴击、命中与技能机制另看；不要再乘一次品质、词缀或符文。'),
 'quiver':dict(title='箭袋',brief='起步在飞矢、精工和现有合用箭袋中比较；不为追指定底材放弃已有攻击点伤与攻速。卡迪罗是后期可选路线，不是升黄产物。',keep='攻击适用的物理／冰霜点伤、攻速、投射物速度、弓技能伤害与等级按需求取舍；不是所有候选都必须同时有。',when='先选有数条当前有效属性的成品。蓝件已有值得保留的词缀，且本次材料确实补短板时再加工；没有合适精华可保留现用或比较富豪分支。',acquire='普通箭袋靠拾取、成品比较或合格半成品加工；暗金另按其掉落／交易取得。作者普通箭袋先比较约3–4条好属性的建议不是每条固定满值。',stop='同一把弓和连接下实际输出更好、命中与属性不倒退。换暗金先看六种随机箭效果，不把全部效果当常驻。',compare='底材固有的投射物速度、攻速或暴击率是不同方向。比较整件当前有效属性；非暴击阶段不以暴击底材作为必要条件。'),
 'helmet':dict(title='头盔',brief='生命／闪避阶段先用可穿的生命抗性头；准备混合防御时才比较高基础护盾头，不因捡到智慧底材就先洗点。',keep='起步优先生命、闪避和所缺抗性；转混合后要有头盔自身能量护盾和配套恢复，保留装备需求与整套生存。',when='普通补装针对现有缺口；作者护盾头专用工艺另有物等和起手词缀条件。配套未准备好时，不先拆掉旧生命防御。',acquire='优先合用的现成头盔；转型件在备用底材上准备。作者约450头盔自身护盾是转型参考，不是角色总护盾或游戏硬门槛。',stop='生命、抗性和属性满足当前使用；混合阶段受击后护盾能恢复，不能只看城里满护盾。',compare='白底的基础护盾／闪避不是成品值。看头盔顶部最终防御，再结合衣服、幽灵舞步及实际预留判断转型；不能把仅有基础护盾的白头当达标。'),
 'body':dict(title='衣服',brief='先选当前可穿且最终闪避好的衣服；蛇鳞外套是过渡示例，海盗外套／滑击背心属于后续比较，不必等到80级底材才刷图。',keep='以最终物品闪避为底座，同时补全身需要的生命与抗性；混合防御也不能只堆护盾而丢掉闪避配套。',when='候选衣服的最终防御更好，且换下旧衣服后丢失的抗性已能补回，再决定加工或更换。',acquire='拾取、商店、可交易成品优先比较；值得留的蓝衣服再按实际缺口选择生命、防御或抗性材料。',stop='换装后实际闪避改善，生命、属性和抗性不出现新缺口；不为凑六条牺牲主要防御。',compare='白底闪避、局部平铺闪避、局部百分比与成品顶部闪避分开。比较成品时直接读顶部，勿再次乘下方百分比。'),
 'gloves':dict(title='手套',brief='能用的攻击点伤手套优先；精纺护腕可作较低需求过渡，宏伟护腕不是起步必须到手的唯一底材。',keep='对攻击生效的物理／冰霜点伤、攻速，与生命、实际缺抗一起比较；法术伤害不当作普通攻击点伤替代。',when='保留好攻击词缀的候选，再补生命或所缺一抗。缺攻速不能盲目使用急速精华，按该部位合法材料表操作。',acquire='先比较合用成品；普通加工只是另一条取得路线，不要求从白装做出作者全部词缀。',stop='实际输出改善，换下旧件后生命、抗性与属性仍可用；无明显提升不追追加词缀。',compare='高物等只影响可能的词缀，不保证成品更强。比较攻击适用词条与换装后的实际缺口，而非仅看黄装颜色。'),
 'boots':dict(title='鞋子',brief='先保移动速度，再补生存；蜥鳞靴是较低需求例子，骑兵长靴用于生命闪避方向，混合阶段再比较嵌刃便鞋。',keep='移动速度优先，生命、所缺抗性与实际防御配套兼顾；没移速的黄鞋不自动胜过好移速蓝鞋。',when='已有合用移速的蓝鞋，才比较身躯或对应单抗精华；移速本身不合适先换候选，急速精华不是鞋移速配方。',acquire='先看掉落／商店里可直接穿的移速鞋；不能为了作者后期底材名称牺牲当前移动和生存。',stop='移速、人物佩戴与整套防御均能满足。只是多了词缀而没有实际改善，就停止投入。',compare='移动速度词缀与底材防御分开；混合鞋的护盾和闪避必须结合全身。脱下旧鞋的抗性要先扣除，新增生命不能自动补回抗性。'),
 'amulet':dict(title='项链',brief='先满足实际智慧、精魂和技能需求，再追等级；星辉、日曜、海玉按缺口比较，不因作者示例是＋3就否定所有过渡件。',keep='实际需要的精魂与属性是启用条件；投射物等级和输出词缀在能持续使用技能之后比较。',when='当前项链不能满足技能／属性或输出确实受限时换。高投入等级＋精魂配方必须先满足专用起点，不能从任意白项链照做。',acquire='先找已有所需属性／精魂的成品或半成品；永恒精华不是定向智慧工具。涂膏另按实际节点与成本判断。',stop='换下旧项链后所有装备、辅助与常驻仍能用；等级提高却频繁断蓝，不算成功换装。',compare='“项链给予智慧”与“佩戴需要智慧”不同。先扣旧件贡献再加新件；所需精魂按整套实际预留，不拿单一示例当通用门槛。'),
 'belt':dict(title='腰带',brief='普通阶段保生命、力量和抗性；生皮或其他功能合适腰带均可。猎首是特定刷法升级，不是新手必须有的装备。',keep='保住生命、佩戴所需力量和当前抗性缺口，检查实际咒符槽；未触发暗金增益不计入基础生存。',when='现有腰带限制属性或生存时先补普通件；后期按稀有怪密度决定是否采用猎首，不在无小怪首领上预支刷图增益。',acquire='普通件先比较成品或合格蓝底；暗金走对应获取途径，不用普通精华升黄“制作”出暗金。',stop='生命或属性短板得到改善、技能装备不失效；不要为名称或物品稀有度牺牲咒符功能。',compare='换装先扣旧腰带力量、抗性与生命。来源里的暗金面板是示例，实际效果还要看触发和持续时间。'),
 'rings':dict(title='戒指',brief='两枚分别分担抗性、智慧、生命和攻击点伤；三相戒指是一个选择，不要求两枚做成完全相同。',keep='保住生命与攻击适用点伤，再按全身实际缺口分配抗性／智慧；不是每枚必须拥有全部候选。',when='先扣掉要换下的那一枚贡献，净提升明确再换。次级／普通身躯可比较，强效身躯不适用于戒指。',acquire='需要特定抗性或智慧时优先比较已有该词缀的成品；没有合适精华就保留现用品或普通升黄路线。',stop='两枚合计及全身火冰电、混抗和属性满足需要，输出与生命不倒退；不为镜像另一枚而多花材料。',compare='旧戒指火抗25%、新戒指35%，净增加10%，不是35%。左右戒指逐个计算，别把同名和同数值当成必须。')}
# Same guidance is usable late, but stage-specific direction must override early equipment dependence.
stage_adjust={
 'bow':{'early':'当前可穿的伤害弓先用；较低需求例子是狂热弓。作者展示的毁灭者之弓不作为进图硬门槛。','late':'比较毁灭者之弓或寻战之弓的完整成品；暴击阶段同时保证伤害底座、本地暴击与配套箭袋。'},
 'helmet':{'early':'先用可穿的生命／闪避／抗性头；毒蝰帽等是过渡例子，沙漠帽是可比较的高阶闪避底材。','late':'准备高基础纯护盾头，如先祖冠冕；先看成品自身护盾与佩戴智慧，再和闪避衣服、幽灵舞步一起转。'},
 'body':{'early':'当前高闪避成品优先。蛇鳞外套是过渡参考；海盗外套、滑击背心按实际等级与属性能穿再比。','late':'海盗外套或其他合格高闪避成品都要看完整属性；不能为了同名丢失生命、抗性和恢复配套。'},
 'boots':{'early':'能穿的移速鞋先用。蜥鳞靴是过渡例子，骑兵长靴不是进入异界的前提。','late':'混合防御比较嵌刃便鞋等合格成品；先保移速、生命抗性，再看闪避与护盾。'},
 'quiver':{'early':'飞矢、精工与现有合用箭袋按有效属性比较；宽矢仅为临时低级备选。','late':'优先配套暴击黄箭袋或合适的卡迪罗；选暗金意味着随机箭机制变化，不是普通属性无条件升级。'}
}
guides={}
for st in D['stages']:
 sid=st['id'];guides[sid]={}
 for it in st['items']:
  uid=it['uid'];key='rings' if uid in ('ring1','ring2') else uid
  if key not in slot:continue
  g=copy.deepcopy(slot[key]);g['uid']=uid;g['source']=F;g['readonly']=sid=='e06';g['sourceLabel']='作者正文方向＋本站选择说明；不是作者额外已装备的一套物品'
  if key in stage_adjust:g['brief']=stage_adjust[key]['late' if sid in ('e03','e04','e05') else 'early']
  if key=='quiver' and sid=='e03':g['brief']=stage_adjust[key]['early']+' 本阶段仍是非暴击。'
  if key=='bow' and sid=='e03':g['brief']='仍按非暴击成品比较伤害和攻速；只有合格暴击弓与箭袋配套到位，才准备暴击树。'
  if key=='bow' and sid=='e02':g['brief']='仍是非暴击输出；可穿时比较毁灭者之弓／寻战之弓的成品，不用先追本地暴击。'
  if sid=='e06':g['brief']='作者实装独立只读。以下只说明如何阅读这件面板；不把有冲突的实装当成必经升级或制作方案。'
  g['bases']=[]
  for base in it.get('bases',[]):
   entry=copy.deepcopy(base);en=entry['en'];entry['current']=sid in entry.get('phases',[]);entry['later']=not entry['current'] and sid=='e01' and any(x in entry.get('phases',[]) for x in ('e02','e03','e04','e05'))
   if not(entry['current'] or entry['later']) or sid=='e06':continue
   if en in facts:
    f=facts[en];entry['name']=f['name'];entry['fact']=f;entry['url']=f['url']
   else:
    entry['fact']=None;entry['name']=L['names'].get(en,entry['name']);entry['url']=entry.get('wear',{}).get('source') if entry.get('wear') else F
   g['bases'].append(entry)
  # Late implicit-specific bases available in old data remain labelled supplementary, not imposed as defaults.
  t=D['equipmentTargets'].get(sid,{}).get(uid,{})
  g['supplement']=copy.deepcopy(t.get('supplement',[]));g['example']=copy.deepcopy(D['craftGuide41']['examples'].get(key))
  guides[sid][uid]=g
unique={
 "Cadiro's Gambit":dict(zh='卡迪罗的赌局',brief='每支箭随机取一种箭矢效果，不是六种同时常驻；先有合格弓与整体暴击配套再比较。',why='随机清图与暴击功能来自六种箭，不应只看面板里列了六个名字就同时累加。',get='比较实际掉落或交易到的暗金。缺它时用具备有效攻击点伤、攻速及暴击方向的普通箭袋；不承诺两者完全等效。',check='改用暗金后在相同内容检查清图与单体；不预设六种等概率，也不把某次随机高伤作为稳定收益。',url=DB+'Cadiros_Gambit'),
 'Headhunter':dict(zh='猎首',brief='击败稀有怪才取得其词缀增益；稀有怪多的刷法与无小怪首领要分开判断。',why='增益有触发条件和持续时间。没有击败稀有怪时，不把借来的增益计入基础属性。',get='按实际取得的暗金比较；没有时仍可用生命、力量与抗性合格的普通腰带。',check='先确认脱下旧腰带后能穿装备、三抗与生命仍够用，再评估刷法收益。',url=DB+'Headhunter'),
 "Lavianga's Spirits":dict(zh='拉维安加之灵',brief='效果持续生效，但回复量有降低；不是按一下救急或无条件无限魔力。',why='需要比较持续魔力消耗与实际恢复，尤其没有击杀和小怪的首领场景。',get='有合适普通／魔法魔力药剂即可先用，不用等这件暗金才解决供蓝；同时核对印记、回蓝珠宝及技能消耗。',check='对同一目标连续使用主技能并观察魔力是否持续下降；不要因为“常驻”就忽略回复惩罚。',url=DB+'Laviangas_Spirits'),
 'Nascent Hope':dict(zh='新生希望',brief='受到冻结而触发时开始能量护盾充能，不是每次受击立刻回满护盾。',why='触发、充能与实际护盾系统要同时存在。蓝量、护盾恢复和咒符充能是不同机制。',get='未取得时先用能应对冻结风险的合适普通咒符；替代品不等于拥有它的护盾效果。',check='咒符槽开放、有充能且实际触发；不要主动承受危险来假定它一直生效。面板“击杀获得充能”指咒符充能，不是角色能量球。',url=DB+'Nascent_Hope'),
 'The Fall of the Axe':dict(zh='落刃时刻',brief='受减速影响时触发，猛攻只在对应效果期间获得。',why='不能把阶段性猛攻当作一直存在的攻速／移动收益。',get='缺它时选择当前最需要的异常防护咒符；先满足生存，再比较额外增益。',check='槽位、充能、触发条件与持续时间一起核对，不只看“猛攻”二字。',url=DB+'The_Fall_of_the_Axe'),
 'Rite of Passage':dict(zh='仪式通道',brief='击败稀有或传奇敌人时触发，附身效果按你实际物品的词缀，不能把所有灵体效果都算上。',why='面板可能显示特定灵体或随机灵体；条件性收益不等于全程常驻。',get='资料列其与阿兹莫里之灵掉落有关；能交易时比较实物，不能保证一次遇到就掉。缺少时优先普通防护咒符。',check='已开放槽位、有充能，且实际附身对应你所需效果。不要为了凑作者同名物品先丢异常防护。',url=DB+'Rite_of_Passage'),
 "Hysseg's Claw":dict(zh='西赛格之爪',brief='只在作者实装的第二武器组中阅读，不能当作前五套冰射的通用副手或必备。',why='它的物品类别、授予技能及需求要与武器切换和变形条件一同核对；原采集存在需求值冲突。',get='本版不提供据此洗点或加工的执行建议；完整原面板与冲突证据保留。',check='未完成实装冲突核验，不把武器、授予技能和天赋同时判为合法。',url=DB+'Hyssegs_Claw')}
arrows=[
 ['渐强箭','额外连锁6次，每次连锁使该投射物伤害提高60%。','Crescendo_Arrows'],
 ['裂片箭','分裂向6个目标，用于多目标覆盖；不是同一目标固定多中6次。','Splinter_Arrows'],
 ['回转箭','穿透所有目标并返回；击中次数还取决于目标与路径。','Reversing_Arrows'],
 ['金刚箭','该箭的击中必定暴击，并获得60%暴击伤害加成。','Diamond_Arrows'],
 ['贪婪箭','被该箭击败的敌人掉落物品稀有度提高600%，不是所有掉落或通货数量提高。','Covetous_Arrows'],
 ['钝击箭','晕眩积累提高600%，不等于必定立即晕眩。','Blunt_Arrows']]
J={
 'mana':dict(title='缺蓝先怎么选',body='刷图缺蓝可先准备一颗有击杀回蓝词缀的蓝玉；作者正文在供蓝备选中举2%击杀回蓝。没有击杀的首领不能只靠它，仍要测药剂、印记及持续消耗。',get='优先拾取或比较已有该词缀的珠宝成品；蓝玉这个底材名称本身不保证回蓝。不要在唯一可用珠宝上先赌删改。',fallback='暂时没有时，先用合格魔力药剂与现有恢复，按实际消耗调整连接；不要为了插差珠宝花很多绕路点。',check='先确认人物树有已分配且能用的珠宝孔，再比较回蓝与其余有效词条；不是装备增幅孔、也不是技能辅助孔。',url=F),
 'ordinary':dict(title='普通输出珠宝怎么选',body='非暴击阶段比较攻击、投射物、当前有效元素伤害与弓攻速；转暴击之后才额外比较攻击暴击率与攻击暴击伤害。法术限定词缀不能当成攻击收益。',get='拾取或比较成品，先有几条真正有效属性即可。取得更好珠宝时替换现有孔，不按不同图标数量增加孔位。',fallback='缺特殊珠宝时继续用合适的普通输出／资源珠宝；具体取舍按短板，不强行追与后期四颗翡翠完全相同的组合。',check='普通珠宝不照普通防具的六词缀工艺操作；品质和精炼材料另查物品类别，宝石匠棱镜不用于人物珠宝。',url=F),
 'well':dict(title='泉井之心：看自身词缀',body='它的额外伤害来自珠宝自身合适词缀，不按附近大点数量放大。作者后期目标可追两条额外伤害；当前展示有几条就按面板读，不能自动补第二条。',get='来自深渊相关取得途径；也可在可交易环境比较实物。不是拿普通珠宝按通用精华升黄就能做出该暗金。',fallback='没有合适的就继续普通输出珠宝。缺此珠宝不需要为了展示同名先买无用词缀组合。',check='限定1颗；占用一个实际已分配孔。各属性掷值范围不是必得最高值，不把其他候选也同时算入。',url=DB+'Heart_of_the_Well'),
 'darkness':dict(title='抗衡黑暗：看覆盖与已点节点',body='额外伤害词缀要看实际半径内已分配的对应核心天赋。小天赋的其他效果和核心天赋的额外伤害分开；孔离节点近不代表都生效。',get='对应特殊遗物“绝望的联盟”与扎罗克试炼路线，或可交易的成品；遗物条件、消耗与实际实物要先核对，不当普通随机珠宝掉落保证。',fallback='只有单条合用额外冰伤也可以作为比较对象；双额外伤害是后续目标。没有合适覆盖位置时继续普通珠宝，不先退点凑半径。',check='限定1颗。示例：若实物写每个覆盖核心天赋获得3%额外伤害，覆盖且已分配3个，合计该词缀为9%；这不是最终技能伤害固定提高9%。实际位置、半径及节点状态以游戏内核对。',url=DB+'Against_the_Darkness',acquireUrl=DB+'The_Desperate_Alliance')}
G=dict(version='R45',date='2026-10-06',scope='恢复被采集显示层覆盖的配装教学；保持作者当前面板与原件独立。',source=F,guides=guides,baseFacts=facts,unique=unique,arrows=[dict(name=n,effect=e,url=DB+u) for n,e,u in arrows],jewels=J,
 boundary='页面面板取自2026年10月5日采集，基于0.5.5攻略。底材基础与机制解释于2026年10月6日对照简体数据；不倒写作者原件，不宣称腾讯国服逐字实测。',
 compareRule='裸底材数值用于找候选；当前采集面板用于看作者示例；可选补位用于解决你的短板，三者不相加。装备物品等级、人物佩戴等级与材料条件分别核对。',
 unchanged=['作者原始构筑','四份现行原版过滤器及历史文件','采集装备与珠宝面板','镶嵌与已选异界绑定','原始截图与档案'],
 remaining=['作者实装的弓与保存字段、部分需求、珠宝孔及升华仍有原来源冲突，保持只读。','完整机器连线与合法逐级点序、全部异界未选候选仍没有足够原始数据；不从截图编造。','少数旧先祖秘藏事件或符文专名未核定，保留可读规则和逐项原名对照，不藏整段操作。','尚无国服客户端逐项名称、掉落、工艺收益及实战验证。'])
(W/'guide45.json').write_text(json.dumps(G,ensure_ascii=False,indent=2))
print('guide45',len((W/'guide45.json').read_bytes()),'scoped',sum(len(v) for v in guides.values()))
