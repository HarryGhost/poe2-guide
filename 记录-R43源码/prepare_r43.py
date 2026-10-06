"""Read-only comparison + presentation overlay. Does not modify captured or original files."""
from pathlib import Path
import json,re,hashlib,copy
W=Path(__file__).parent; C=W/'capture/fubgun_capture_2026-10-05'; B=W/'baseline'
D=json.loads((W/'old_data.json').read_text()); CAP=json.loads((C/'builds.json').read_text()); ATL=json.loads((C/'atlas.json').read_text())
# These are translations of supplied panel text, not additional game mechanics.
phrases={
'Critical Hit Chance for Attacks':'攻击暴击率','Critical Damage Bonus for Attack Damage':'攻击的暴击伤害加成','Critical Damage Bonus':'暴击伤害加成','Critical Hit Chance':'暴击率',
'Attack Speed with Bows':'弓类攻击速度','Attack Speed':'攻击速度','Arrow Speed':'箭矢速度','Attack Damage':'攻击伤害','Elemental Damage':'元素伤害','Projectile Damage':'投射物伤害','Physical Damage':'物理伤害',
'Evasion and Energy Shield':'闪避值与能量护盾','Armour, Evasion and Energy Shield':'护甲、闪避值与能量护盾','maximum Energy Shield':'最大能量护盾','Energy Shield':'能量护盾','Evasion Rating':'闪避值',
'Life Recovery from Flasks':'药剂的生命回复量','Stun Threshold':'晕眩门槛','Rarity of Items found':'物品稀有度','Movement Speed while Sprinting':'冲刺时的移动速度','Movement Speed':'移动速度','Projectile Speed':'投射物速度',
'Damage with Bow Skills':'弓技能伤害','Damage with Hits against Rare and Unique Enemies':'对稀有和传奇敌人的击中伤害','Amount Recovered':'回复量','Charges gained':'充能获取量','Charges':'充能','Duration':'持续时间',
'maximum Life':'最大生命','Fire and Chaos Resistances':'火焰与混沌抗性','all Elemental Resistances':'全部元素抗性','Chaos Resistance':'混沌抗性','Cold Resistance':'冰霜抗性','Fire Resistance':'火焰抗性','Lightning Resistance':'闪电抗性','all Attributes':'全部属性','Dexterity':'敏捷','Intelligence':'智慧','Strength':'力量','Spirit':'精魂'}
exact={
'All: +1 Suffix Modifier allowed':'所有部位：允许的后缀词缀数量 +1',
'Allocates (2-4) Sinister Jewel Sockets':'配置（2–4）个 Sinister Jewel Sockets（保留原名；不据此推定当前实际孔数）',
'Allocates Climate Change':'配置 Climate Change', 'Allocates Serrated Edges':'配置 Serrated Edges',
'60% increased effect of Socketed Augment Items':'已镶嵌增幅物品的效果提高 60%',
'Boots: Can roll Chronomancy modifiers':'鞋子：可生成 Chronomancy 词缀',
'Gloves: Can roll Marksman modifiers':'手套：可生成 Marksman 词缀',
'Bow: Bow Attacks fire an additional Arrow':'弓：弓类攻击额外发射 1 支箭矢',
'Corrupted':'已腐化',
'Each Arrow fired is a Crescendo, Splinter, Reversing, Diamond, Covetous, or Blunt Arrow':'每支发射的箭矢为 Crescendo、Splinter、Reversing、Diamond、Covetous 或 Blunt Arrow 之一（不是六种效果同时常驻）',
'Energy Shield Recharge starts on use':'使用时开始能量护盾充能',
'Grants Onslaught during effect':'效果期间获得猛攻',
'Grants Skill: Level (5-20) Cackling Companions':'授予技能：（5–20）级 Cackling Companions',
'Has (1-3) Charm Slot':'具有（1–3）个咒符槽',
'Helmet: Gain Armour equal to 35% of Life Lost from Hits in the past 8 seconds':'头盔：获得护甲，数值相当于过去 8 秒内击中所损失生命的 35%',
'Helmet: Raven-Touched':'头盔：Raven-Touched（保留原页效果名）',
'Limited to 1':'限定 1 颗',
'Lose 5% of maximum Life per second while Sprinting':'冲刺时每秒失去最大生命的 5%',
'Minions deal (30-50)% increased Damage':'召唤物造成的伤害提高（30–50）%',
'Possessed by Spirit Of The [Azmeri Spirit] for (10-20) seconds on use':'使用时被 [Azmeri Spirit] 之灵附身，持续（10–20）秒（面板未指定实际灵种）',
'Sceptre: Allies in your Presence have 8% increased Movement Speed':'权杖：存在范围内友军的移动速度提高 8%',
'This Flask cannot be Used but applies its Effect constantly':'无法主动使用此药剂，但其效果持续生效',
'Used when you are affected by a Slow':'受到缓速影响时使用','Used when you become Frozen':'被冻结时使用','Used when you become Ignited':'被点燃时使用','Used when you kill a Rare or Unique enemy':'击败稀有或传奇敌人时使用',
'When you kill a Rare monster, you gain its Modifiers for 60 seconds':'击败稀有怪物时，获得其词缀，持续 60 秒',
'Body Armour: 10% of Physical Damage prevented Recouped as Life':'衣服：防止的物理伤害有 10% 转为生命补偿',
}
context={'Armour':'护甲类装备','Body Armour':'衣服','Boots':'鞋子','Gloves':'手套','Helmet':'头盔','Martial Weapon':'近战／武技类武器（Martial Weapon）','Wand or Staff':'法杖或长杖','Sceptre':'权杖'}
# "Martial weapon" in the capture includes bows; avoid a translation suggesting melee only.
context['Martial Weapon']='武技武器'
def translate(s):
 if s in exact:return exact[s]
 if ': ' in s:
  p,tail=s.split(': ',1)
  if p in context:return context[p]+'：'+translate(tail)
 m=re.fullmatch(r'(.+?)% increased (.+)',s)
 if m and m[2] in phrases:return phrases[m[2]]+'提高 '+m[1]+'%'
 m=re.fullmatch(r'(.+?)% reduced (.+)',s)
 if m:
  f={'Charges per use':'每次使用消耗的充能','Projectile Range':'投射物射程',**phrases}.get(m[2]);
  if f:return f+'降低 '+m[1]+'%'
 m=re.fullmatch(r'\+(.+?) to (.+)',s)
 if m and m[2] in phrases:return phrases[m[2]]+' +'+m[1]
 m=re.fullmatch(r'\+(\d+) to Level of all Projectile Skills',s)
 if m:return '所有投射物技能等级 +'+m[1]
 m=re.fullmatch(r'Adds (.+?) to (.+?) (Physical|Cold|Fire|Lightning) [Dd]amage( to Attacks)?',s)
 if m:return ('攻击附加 ' if m[4] else '附加 ')+m[1]+' 至 '+m[2]+' '+{'Physical':'物理','Cold':'冰霜','Fire':'火焰','Lightning':'闪电'}[m[3]]+'伤害'
 m=re.fullmatch(r'(.+?)% of Recovery applied Instantly',s)
 if m:return '回复量的 '+m[1]+'% 立即生效'
 m=re.fullmatch(r'(.+?)% Chance to gain a Charge when you kill an enemy',s)
 if m:return '击败敌人时有 '+m[1]+'% 几率获得 1 点充能'
 m=re.fullmatch(r'Gain (.+?)% of Damage as Extra (Cold|Lightning) Damage',s)
 if m:return '获得相当于伤害 '+m[1]+'% 的额外'+{'Cold':'冰霜','Lightning':'闪电'}[m[2]]+'伤害'
 m=re.fullmatch(r'Notable Passive Skills in Radius also grant (.+)',s)
 if m:return '范围内的核心天赋额外给予：'+translate(m[1])
 m=re.fullmatch(r'Gain Deflection Rating equal to (.+?)% of Evasion Rating',s)
 if m:return '获得相当于闪避值 '+m[1]+'% 的偏转值'
 m=re.fullmatch(r'Recover (.+?)% of maximum (Life|Mana) on Kill',s)
 if m:return '击败敌人时恢复 '+m[1]+'% 最大'+('生命' if m[2]=='Life' else '魔力')
 m=re.fullmatch(r'\+(.+?)% Surpassing chance to fire an additional Projectile',s)
 if m:return '额外发射投射物的超越几率 +'+m[1]+'%（保留 Surpassing 原义，不按普通概率封顶）'
 return s
mods=json.loads((W/'modifiers.json').read_text()); tr={x:translate(x) for x in mods}; print('untranslated mods',[s for s,v in tr.items() if s==v])
namezh={}
for st in D['stages']:
 for i in st['items']:
  for r in i.get('records',[]):namezh[r.get('en')]=r.get('name')
namezh.update({'Emerald':'翡翠','Heart of the Well':'泉井之心','Against the Darkness':'抗衡黑暗','Voices':'Voices', 'Greater Iron Rune':'高级钢铁符文','Perfect Iron Rune':'完美钢铁符文'})
oldtrans={re.sub(r'^\d+\.\s*','',en):zh for br in D['branches'] for it in [] for en,zh in []}
# Author-specific decisions remain separate from observed slots.
notes={
'Early':{'referenceLevel':75,'brief':'非暴击；生命与闪避。先建立可用装备，不把高等级示例当入场门槛。','transition':'参考树 75 级。作者建议约 60–65 级进图后按需求补点；本套成型后逐步参考 non-crit Midgame，不要求整套重买。','jewelProse':'此分支的珠宝栏未配置具体物品。作者正文另建议 1 颗带击杀回蓝的 Sapphire；普通输出珠宝和后续特殊珠宝属于建议，不是本页已镶嵌清单。','skillNotes':['作者给出的连接按优先级排列；孔位不足时优先去掉末尾辅助。六连优先：Snipe → Ice Shot → Herald of Ice → Freezing Mark。','品质优先：Freezing Mark → Herald of Ice → Snipe → Ice Shot。不是所有宝石默认 20% 品质。','Elemental Armament 使用 II，不照阶别直接换 III。','Mirage Archer 可按精魂与偏好换成 Wind Dancer，连接 Blind II、Knockback；这是替代，不是两者都常驻。']},
'non-crit Midgame':{'referenceLevel':90,'brief':'延续非暴击生命／闪避配置，补连接、伤害和资源。','transition':'参考树 90 级；护盾头、闪避衣服和 Ghost Dance 恢复未到位，继续用本套。准备混合防御时，作者给头盔自身约 450 护盾的参考，非角色总护盾。','jewelProse':'珠宝栏未配置具体物品。作者正文建议 1 颗 2% 击杀回蓝珠宝；这不代表网页逐孔配置已给出。','skillNotes':['连接按优先级排列。六连优先：Snipe → Ice Shot → Herald of Ice；品质先 Freezing Mark。','pinnacle boss 可将 Ice Shot 的 Fork 换为 Freeze；与默认清图连接分开。','Mirage Archer 可换 Wind Dancer（Blind II、Knockback）。Elemental Armament 保持 II。','缺蓝备选：普通高回复魔力药剂＋击杀回蓝珠宝；或为 Conservative Casting 投入 3 点；或在实际有该常驻时用 Mana Remnants 替代 Wind Dancer，不把三种同时要求。']},
'non-crit Hybrid swap':{'referenceLevel':95,'brief':'非暴击；改为生命、闪避与能量护盾。','transition':'参考树 95 级。护盾头、高闪避衣服、混合鞋和 Ghost Dance 配套一起检查。作者允许先转暴击再转混合防御，并非只有一个强制顺序。','jewelProse':'此分支没有保存具体珠宝配置；正文的普通珠宝和特殊珠宝方向仍另列，不把建议写成作者实装。','skillNotes':['作者明确要求 Ghost Dance 20% 品质；实际预留仍看装好后的角色。','本套移除 Combat Frenzy，加入 Ghost Dance；不要继续预支旧产球来源。','默认仍保留 Ice-Tipped Arrows 和 Snipe。','精魂、属性与供蓝先配齐，再换天赋；不能只看城里总护盾。']},
'Crit Hybrid':{'referenceLevel':94,'brief':'暴击与混合防御；仍保留 Snipe 爆发。','transition':'参考树 94 级；高伤害暴击弓＋配套暴击箭袋到位再转。缺特殊辅助或不用 Snipe 单体不够时，可继续本套，不为编号更大强转。','jewelProse':'网页明确展示 Heart of the Well 与 Against the Darkness；以下为两颗各自面板和绑定，不等于三个孔都已插满。','skillNotes':['默认连接保留 Snipe；pinnacle boss 可将 Rakiata’s Flow 移入 Snipe，替换 Elemental Armament II。','有 Garukhan’s Resolve 时，作者允许替换 Snipe 的 Inexorable Critical I；单颗不能同时占两组。','取得 Rakiata’s Flow 后，作者允许从 Snowpiercer 改向 Beastial Skin；先检查路线连通和现有属性。','作者给出 147 精魂配套情景；Ghost Dance 20% 品质时为 25 精魂。最终仍按实际品质、预留转换与效率检查。']},
'Uber Endgame':{'referenceLevel':96,'brief':'高配暴击；默认冰射承担首领输出。','transition':'参考树 96 级；默认不配置 Snipe。关键特殊辅助、魔力残片与预留配套齐后再整体转换；Live Gear 不是必经的下一阶段。','jewelProse':'网页展示两颗特殊珠宝。Against the Darkness 此处只明确展示额外冰伤；正文的双额外伤害是后续目标，不混成这一颗已经有两条。','skillNotes':['默认没有 Snipe，但正文仍有 Barrage → Snipe 与换辅助的旧段落；此处明确保留源内不一致，不自动加回默认技能。','Wind Dancer 的这套配法依赖 Atziri’s Communion；Khatal’s Rejuvenation 配套 Dialla’s Desire，缺少时不能原样照搬。','作者有 Headhunter 与 Mageblood 的不同刷法备选；Mageblood 不是当前装备栏已展示的那一件。','头盔正文建议 Thin Ice；当前装备配置未写入对应头盔涂膏，按正文建议另列。']},
'Live Gear':{'referenceLevel':None,'brief':'作者实装只读对照；源内冲突单独列出，不当成必经升级。','transition':'作者正文允许在能承受伤害和防御损失后研究 Pathfinder。现采集尚不证明全部导出、升华与授予技能同时合法，旧冲突限制保留。','jewelProse':'当前可见 7 颗，其中 4 颗 Emerald 属性各不相同；第 1、6 颗绑定未在显式已点列表找到，另有 1 条未展示绑定。不要按图标数推算实际合法孔数。','skillNotes':['面板可见的本体等级已直接列出；未设置品质或内嵌等级保持未设置。','头盔涂膏正文为 Zarokh’s Gift，材料 Potent Melancholy、Potent Ferocity、Potent Contempt 各 1；正文不是现有孔位已经验收的证明。','Pathfinder 正文列 Relentless Pursuit / Running Assault / Path Seeker / Traveller’s Wisdom；与现有图、导出冲突并列，不代替作者改树。','Warmonger Bow 的实际悬浮面板未显示保存的 7 条词缀；仅可作为冲突记录查看，不提供基于该面板的伤害保证。']}}
# Passive reference levels are source prose, never used to synthesize spendable counts.
keyzh={'Essence Dowsing':'精华探源','Well-equipped Opponents':'精良对手','Evolving Throngs':'演化蜂群','The Chosen Path':'选中之路','Crystalline Patterns':'水晶纹样','Nemesis Rising':'宿敌崛起','Grass Mastery':'草原专精','Forest Mastery':'森林专精','Desert Mastery':'沙漠专精','Swamp Mastery':'沼泽专精','Water Mastery':'水域专精','Mountain Mastery':'山地专精','The Journey Ahead':'前方旅途','Vile Treasures':'污秽宝藏'}
choicezh={
'Greater Essence of Abrasion and Perfect Essence of Abrasion':'强效磨蚀精华与完美磨蚀精华组','Dexterity':'敏捷需求装备方向','Vivid Spirits':'Vivid 灵种','Seeking Shrines':'Seeking 神龛','No additional Prefix Modifiers':'不增加额外前缀词缀','When a Monster is Possessed by a Sacred Spirit it is also Possessed by another random Spirit':'怪物被 Sacred Spirit 附身时，也被另一种随机灵附身','10% increased Magic Pack Size':'魔法怪群规模提高 10%',
'25% chance Shrine Buffs are instead applied to the Boss when activated, granting an additional reward':'激活时有 25% 几率改为给首领施加神龛增益，并给予额外奖励','An additional Shrine':'额外 1 座神龛','An additional Rogue Exile':'额外 1 个流放者','Rogue Exiles':'流放者方向','Jewellery':'首饰方向','Greater Essence of Battle and Perfect Essence of Battle':'强效战斗精华与完美战斗精华组',
'15% increased Effectiveness of Rare Monsters in your Maps':'地图中的稀有怪物效能提高 15%','15% increased Effectiveness of Monsters':'怪物效能提高 15%','15% increased Rare Monsters':'稀有怪物数量提高 15%','Grass':'草原','Desert':'沙漠','Forest':'森林','10% chance Exalted Orbs drop as Chaos Orbs':'崇高石有 10% 几率改为掉落混沌石','Chests contain 15% increased Currency':'宝箱内通货数量提高 15%','6% increased Rarity of Items found':'物品稀有度提高 6%','Tainted':'Tainted 类型',
'Skills from Ritual Altars deal 50% increased Damage, Ritual Altars offer 10% increased number of Favours':'仪式祭坛技能伤害提高 50%；祭坛提供的恩惠数量提高 10%','15% increased Effectiveness of Monsters in your Maps':'地图中的怪物效能提高 15%','Summoning Circle Bosses are Powerful':'召唤法阵首领为 Powerful（强力）类型','Amanamu':'Amanamu','Omens':'预兆','Abyss Pits are scattered throughout Areas with Abysses':'深渊坑散布于有深渊的区域','Delirium Fog spreads to +4 Maps':'迷雾额外扩散至 4 张地图','Lavish Wombgifts':'Lavish Wombgifts','30% increased Effectiveness of Rare Breach Monsters':'稀有裂隙怪物效能提高 30%','Consume an additional Breachstone to add Modifiers to all revealed Maps':'额外消耗 1 颗裂隙石，为所有已揭示地图添加词缀','100% increased damage of skills created':'所生成技能的伤害提高 100%','10% chance for an additional Verisium Remnant':'有 10% 几率出现额外的 Verisium 遗迹','1% increased Quantity of Items dropped by Monsters per Runic Modifier':'每个符文词缀使怪物掉落物品数量提高 1%','Remnant':'遗迹方向','Explosives only wait for 50% of Monsters to be slain before continuing':'炸药只等待 50% 怪物被击败后便继续引爆','25% chance to add an additional Runic Modifier':'有 25% 几率额外添加 1 个符文词缀','Primal Spirits':'Primal 灵种','An additional Azmeri Spirit':'额外 1 个阿兹莫里之灵','A Summoning Circle':'1 个召唤法阵','Summoning Circles':'召唤法阵方向','Rare Monster Packs in your Maps have a 50% increased chance to have an Additional Rare Monster':'地图中的稀有怪群出现额外稀有怪物的几率提高 50%（不是最终几率 50%）','5% chance Greater Currencies are upgraded to Perfect Currencies':'高级通货有 5% 几率升级为完美通货','50% increased Quantity of Tablets found':'碑牌掉落数量提高 50%','6% increased Pack Size':'怪群规模提高 6%','Azmeri Spirits no longer dematerialise when there are no players nearby':'阿兹莫里之灵在附近没有玩家时不再消散','An additional Strongbox':'额外 1 个保险箱','Water':'水域','10% increased Rarity of Items found':'物品稀有度提高 10%','Ulaman':'Ulaman','Delirium Fog spread to Maps has 50% increased chance to spread to an additional Map, Delirium Fog spread to additional Maps has 25% chance to spread to each connected Map':'迷雾扩散时，向额外地图扩散的几率提高 50%；扩散至额外地图的迷雾有 25% 几率继续扩散至各相邻地图','Add a Modifier to one revealed Map':'为 1 张已揭示地图添加词缀','Strongboxes':'保险箱方向','Rare Monsters have 30% increased chance of Monster Modifiers':'稀有怪物具有怪物词缀的几率提高 30%','Mountain':'山地','50% increased chance to find Lineage Supports':'血脉辅助掉落几率提高 50%'}
CATEGORIES={'mainTree':'主树','breachTree':'裂隙','expeditionTree':'先祖秘藏','deliriumTree':'迷雾','ritualTree':'仪式','bossTree':'首领','pinnacleBossTree':'终局首领','abyssalTree':'深渊','incursionTree':'神庙'}
uidmap={'mainHand':'bow','offHand':'quiver','leftRing':'ring1','rightRing':'ring2','helmet':'helmet','body':'body','gloves':'gloves','boots':'boots','amulet':'amulet','belt':'belt','flask1':'life_flask','flask2':'mana_flask','charm1':'charm1','charm2':'charm2','charm3':'charm3'}
rawcmp=json.loads((W/'raw_compare.json').read_text()); prepared=[]
def pp(panel):
 panel=copy.deepcopy(panel)
 for m in panel['modifiers']:m['zh']=translate(m['text'])
 return panel
for j,b in enumerate(CAP['builds']):
 q=copy.deepcopy(b);q['stage']='e%02d'%(j+1);q['notes']=notes[b['name']]
 for i in q['equipment']:
  i['uid']='weapon2' if i['weapon_group']=='Set 2' else uidmap[i['slot']];i['zhName']=namezh.get(i['name'],''); i['panel']=pp(i['panel']);src=i['source_configuration']['commonItem']
  i['storedDescriptions']=[e['description'] for e in (src.get('explicitDescriptions') or []) if e.get('description')];i['sourceRequirements']=src.get('requirements')
  z=next(t for t in rawcmp if t['build']==b['name'] and t['slot']==i['slot'] and t['set']==i['weapon_group']);i['oldRecord']=z
  i['sourcePanelCaution']=[]
  if b['name']=='Live Gear' and not z['stored_desc_equal']:i['sourcePanelCaution'].append('保存描述与旧 .build 不一致；本页面板、当前保存值和旧记录分别保留，不把保存值当面板实装掷值。')
  if b['name']=='Live Gear' and i['uid']=='bow':i['sourcePanelCaution'].append('两次展开均只显示基础弓面板，保存字段另有 7 条词缀。不能把 56–84 当作配置完成后的武器伤害，也不代算最终 DPS。')
  for chk in i.get('crosschecks',[]):
   if chk['result'] in ['different','mismatch','conflict','source_panel_difference']:i['sourcePanelCaution'].append(f"{chk['field']}：保存值 {chk['source']}；面板 {chk['panel']}。两者不一致。")
  valid_prefixes={'body':['Body Armour','Armour'],'helmet':['Helmet','Armour'],'gloves':['Gloves','Armour'],'boots':['Boots','Armour'],'mainHand':['Bow','Martial Weapon'],'offHand':[],'leftRing':[],'rightRing':[],'amulet':[],'belt':[],'flask1':[],'flask2':[],'charm1':[],'charm2':[],'charm3':[]}
  for m in i['panel']['modifiers']:
   prefix=m['text'].split(': ',1)[0]
   if ': ' in m['text'] and prefix in ['Body Armour','Boots','Helmet','Gloves','Armour','Bow','Martial Weapon'] and prefix not in valid_prefixes.get(i['slot'],[]):
    m['zh']='〔原页标签 '+prefix+'〕'+translate(m['text'].split(': ',1)[1])
    i['sourcePanelCaution'].append('原页面板带有 '+prefix+' 部位标签，与当前栏位不一致；保留原文，不据此改变装备类别或套用未核实效果。')
  for s in i['socketed_items']:s['panel']=pp(s['panel'])
  # The captured image and full DOM are available locally; no external image requirement.
  i['imageEvidence']=next((e['file'] for e in i['evidence'] if e['file'].endswith('.jpg')),None)
  i['textEvidence']=next((e['file'] for e in i['evidence'] if e['file'].endswith('.json') and 'public-data' not in e['file']),None)
 for x in q['jewels']:
  x['panel']=pp(x['panel']);x['zhName']=namezh.get(x['name'],'');x['imageEvidence']=next((e['file'] for e in x['evidence'] if e['file'].endswith('.jpg')),None)
 q['treeImage']=next(e['file'] for e in q['passive_tree']['evidence'] if e['file'].endswith('.jpg'))
 q['treePriorities']=q['passive_tree']['allocations'].get('mainTree',{}).get('source_priority_list') or []
 prepared.append(q)
# Compare captured configurations to preceding branch, not all branches to Early.
def signature(i):return json.dumps({'n':i['name'],'m':sorted(m['text'] for m in i['panel']['modifiers']),'top':i['panel']['top_stats'],'r':[s['name'] for s in i['socketed_items']],'a':i['anointment']},sort_keys=True,ensure_ascii=False)
for n,b in enumerate(prepared):
 for i in b['equipment']:
  olditem=next((x for x in prepared[n-1]['equipment'] if x['uid']==i['uid']),None) if n and n!=5 else None
  i['comparedTo']=prepared[n-1]['name'] if n and n!=5 else None
  i['diffFromPrevious']=None if not i['comparedTo'] else ('same' if olditem and signature(olditem)==signature(i) else 'changed' if olditem else 'new')
masterzh=json.loads((W/'localization43.json').read_text())
skillzh={x['en']:x['zh'] for x in D['gemGuide']['info'].values()};skillzh['Concentrated Area']='范围集中'
for v in ATL['variants']:
 for master in v['masters']:
  for option in master['candidate_options']:option['zhEffects']=masterzh[option['name']]
 v['id']=next(t['id'] for t in D['variants'] if t['name']==v['name']);v['treeImage']=next(e['file'] for e in v['atlas_tree']['evidence'] if e['file'].endswith('.jpg'))
 for x in v['keystone_selections']:
  x['zhName']=keyzh.get(x['node_name'],''); x['zhChoice']=choicezh[x['author_selected']['selection_description']]
  x['groups']=[CATEGORIES.get(k,k) for k,al in v['atlas_tree']['allocations'].items() if x['node_id'] in (al.get('selected_node_ids') or [])]
(w:=W/'overlay43.json').write_text(json.dumps({'release':'R43','captured':'2026-10-05','notesDate':'2026-10-05','builds':prepared,'atlas':ATL['variants'],'modTranslations':tr,'skillTranslations':skillzh,'nameTranslations':namezh,'commonProse':CAP['common_author_text'],'rawCompare':rawcmp},ensure_ascii=False,separators=(',',':')))
print('written',w,w.stat().st_size)
