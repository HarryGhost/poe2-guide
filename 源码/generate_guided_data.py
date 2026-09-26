from pathlib import Path
import json, copy
ROOT=Path(__file__).resolve().parent.parent
old=json.loads((ROOT/'data/Fubgun_异界后期打造.json').read_text())
early=json.loads((ROOT/'data/Early起步打造教学.json').read_text())
AUTHOR='https://mobalytics.gg/poe-2/builds/ice-shot-deadeye'
CUR='https://poe2db.tw/cn/Stackable_Currency'
OMEN='https://poe2db.tw/cn/Omen'
ESS='https://poe2db.tw/cn/Essence'
ABYSS='https://poe2db.tw/cn/Abyss'
MAT={m['id']:copy.deepcopy(m) for m in old['materials']}
for key,zh,en,effect,url in [
 ('normal-trans','蜕变石','Orb of Transmutation','白色普通装备变为蓝色，并加1条随机词缀。','Orb_of_Transmutation'),
 ('normal-aug','增幅石','Orb of Augmentation','给有空位的蓝装加1条随机词缀；不重掷已有词缀。','Orb_of_Augmentation'),
 ('normal-regal','富豪石','Regal Orb','蓝装变黄装，并增加1条随机词缀。不是补满全部。','Regal_Orb'),
 ('normal-exalt','崇高石','Exalted Orb','给有合法空位的黄装增加1条随机词缀，不保证类别。','Exalted_Orb'),
 ('wisdom','知识卷轴','Scroll of Wisdom','鉴定未鉴定的物品；先看清词缀，才决定是否加工。','Scroll_of_Wisdom'),
 ('perfect-regal','完美富豪石','Perfect Regal Orb','蓝装升黄并加1条随机词缀；最低词缀等级不等于必出顶级。','Perfect_Regal_Orb'),
 ('perfect-exalt','完美崇高石','Perfect Exalted Orb','给黄装加1条随机词缀；不是完美成品保证。','Perfect_Exalted_Orb'),
 ('greater-exalt','高级崇高石','Greater Exalted Orb','给黄装加1条随机词缀；最低词缀等级限制另看材料提示。','Greater_Exalted_Orb'),
 ('greater-chaos','高级混沌石','Greater Chaos Orb','随机删1条再加1条。也会删掉你想保留的未固定好属性。','Greater_Chaos_Orb')]:
 MAT[key]={'id':key,'zh':zh,'en':en,'effect':effect,'check':'读取完整物品提示；普通、强效/高级、完美不能只按图标互换。','url':'https://poe2db.tw/cn/'+url,'source':'currency'}
source_map={x['id']:x['url'] for x in old['sources']}
for m in MAT.values():
 m.setdefault('url',source_map.get(m.get('source'),CUR))

def st(id,title,before,action,expect,good,bad,materials=(),state=None,after=None,refs=None,kind='action',note='',nextid=None):
 return {'id':id,'title':title,'before':before,'action':action if isinstance(action,list) else [action], 'expect':expect,'good':good,'bad':bad,'materials':list(materials),'stateBefore':state or [],'stateAfter':after or [],'refs':refs or [CUR], 'kind':kind,'note':note,'next':nextid}

def R(id,title,phases,goal,start,steps,ref,source='Fubgun装备目标＋本站基础操作说明',entries=None):
 return {'id':id,'title':title,'phases':phases,'goal':goal,'start':start,'sourceLabel':source,'reference':ref,'steps':steps,'entries':entries or [{'label':'从准备开始','step':steps[0]['id'] if steps else 'ready'}], 'scope':'按你核对的装备状态阅读，不读取游戏、不模拟掉落、不保证出目标词缀。'}

# Concrete priorities are listed beside each operation, not hidden in a glossary.
TARGET={
 'bow':('弓','本地物理伤害提高 / 附加物理伤害 / 附加冰霜伤害；再看攻击速度','物理伤害提高','攻击速度提高','法术伤害、荆棘不是弓攻击点伤','同时比较弓上方物理/冰伤范围与每秒攻击次数；同一技能、同一组辅助试同档地图，检查冻结与耗蓝。不是只比＋等级。'),
 'quiver':('箭袋','攻击附加物理/冰霜伤害、弓技能伤害；后缀看攻速或投射物等级','攻击附加冰霜伤害','攻击速度提高','Early尚未转暴击时，不只为暴击伤害数字投入材料','换上前后查看同一主技能；点伤、攻速、等级都要看。投射物速度不自动等于伤害，需对应天赋。'),
 'body':('衣服','先最终物品闪避，再保住生命和实际缺少的抗性','最大生命','火焰/冰霜/闪电抗性中你缺的那项','荆棘不增加冰射伤害；不要把所有防御换成一条输出','先记下人物生命和三抗。换上后重新检查，再比较衣服上方最终闪避；不为多一点闪避损失必需抗性。'),
 'helmet':('Early头盔','生命、抗性、合适闪避；03转型才另做高护盾头','最大生命','你目前缺少的抗性','不用因为后面要护盾，就在Early先穿低防御的护盾底材','比较人物生命、三抗和最终物品防御；保持技能需求满足，别把03的护盾目标作为Early入场门槛。'),
 'gloves':('手套','攻击附加物理/冰伤、生命、抗性；再看攻速','攻击附加物理或冰霜伤害','攻击速度提高或你缺的抗性','法术附加伤害不是攻击附加伤害','输出改善但缺力量/智慧使辅助失效，不算升级；换装后看技能是否仍可用。'),
 'boots':('鞋子','先移动速度，再生命与抗性','移动速度提高','当前缺少的抗性','不要丢掉跑动能力，只为多一条用不到的词缀','换上后比较人物移动速度、生命、三抗；先解决跑动，再补齐防御。'),
 'amulet':('Early项链','先满足精魂和缺少的属性，再追投射物技能等级','精魂','缺少的力量/敏捷/智慧','不是所有Early项链都要先做＋3破溃','以装好辅助后的最终保留为准；检查常驻、技能需求与抗性，不因为多＋1级就丢失必需精魂。'),
 'belt':('腰带','生命、力量、缺少的抗性','最大生命','力量或缺少的抗性','先用黄腰带；猎首不是启动条件','换装后看力量是否还能撑住装备和辅助，再看生命与抗性。'),
 'rings':('戒指','缺少的抗性/属性优先，同时寻找生命和攻击附加物理/冰伤','最大生命或攻击附加冰霜伤害','当前缺少的抗性','两枚戒指可以分工，不必同样输出词条','换一枚就复查一次人物三抗和属性；若输出提升却让关键技能失效，先不换。')}
ROUTES=[]
for item,(title,target,prefix,suffix,avoid,compare) in TARGET.items():
 steps=[
  st('ready','先拿备用装备，不点材料',f'当前想改善的是{title}。现用装备留着；备用物品已鉴定、能装备，未腐化、未镜像，没有未弄清的特殊词缀。',
     [f'在背包看{title}的名称颜色。蓝装看词缀分组，黄装先看是否已有升级。',f'保留目标：{target}。', '在“手里是什么状态”里跳到对应一步。已有合适黄装可以直接看最后验收。'],
     '你知道现在是白装、蓝装1条、蓝装2条，还是有空位的黄装。', '当前颜色和词缀状态能确认，才看对应材料。',
     '看不清前后缀时先展开“怎么认装备”；未鉴定先鉴定。别拿唯一能用的装备练手。',kind='prepare',refs=[AUTHOR,CUR],note=avoid),
  st('white','只有白装：蜕变一次',f'普通白色{title}，有意保留该底材；没有要保住的蓝/黄词缀。',
     f'右键【蜕变石】→左键备用{title}一次。不要按住Shift连续使用。',
     '装备变蓝，增加1条随机词缀。',f'出现“{prefix}”等本路线目标词缀：看下一步增幅。',
     '没出现当前需要的词缀：这次先停，另找合适底材或直接买蓝装。不要继续点蜕变试图重洗。',['normal-trans'],refs=[CUR],note='白装起步是可选的。已有好蓝装不必退回白装。'),
  st('augment','蓝装只有1条：增幅一次',f'普通蓝色{title}，只有1条你准备保留的随机词缀；另一侧有空位。',
     f'右键【增幅石】→左键备用{title}一次；点完把鼠标移回装备，读新属性。',
     '仍是蓝装，变成两条随机词缀（普通情况下一前一后）。',
     f'例如保留“{prefix}”，新增“{suffix}”，且对当前配置有帮助：看下一步。',
     '新增属性不合用，或者材料不能使用：停止追加；检查是否已有两条、腐化/镜像或词缀组限制。不要用贵材料试错。',['normal-aug'],
     [['已有随机词缀','要保住的一条'],['另一侧','空']], [['已有随机词缀','保留'],['新增随机词缀','看实际结果']],note='前后缀按高级说明分组看，不是数屏幕文字行。'),
  st('regal','蓝装两条都满意：富豪一次',f'蓝色{title}，恰好两条随机词缀都对当前配置有用；你决定走普通加词缀路线。',
     [f'先决定升黄方式：若准备使用适用的蓝装升黄精华，就不要在此点富豪。',f'决定走普通路线后：右键【富豪石】→左键备用{title}一次。'],
     '装备变黄，在原有两条外增加1条随机词缀。',
     '不要求第三条必定好。只要整件已经能改善当前配置，可以直接停在这里验收。',
     '第三条不满意：保留原来的好属性，不立刻混沌/剥离。后两种材料会随机删除好词缀。',['normal-regal'],
     [['前缀','1条'],['后缀','1条']], [['随机词缀合计','3条'],['前后缀分配','以结果为准']],note='富豪与“将魔法升级为稀有”的精华是分岔，不是先后连招。'),
  st('exalt','黄装还想补一条：崇高一次（可跳过）',f'普通黄装，有合法空位；现有词缀已值得保留，预算允许随机补1条。不是要求所有装备都做满。',
     [ '先核对剩余前缀/后缀；需要的属性必须还能在空位侧生成。',f'没有误开的双加或定向预兆时：右键普通【崇高石】→左键备用{title}一次。'],
     '随机词缀增加1条；不是把已有数值提高。',
     '当前需求得到改善就停止；仍有空位不代表必须继续投入。',
     '目标侧已满就不要点。结果一般也不紧接混沌“修一下”；在这件上停手，再比较旧装。',['normal-exalt'],note='普通装备通常最多3前缀＋3后缀；不适用于珠宝、药剂或特殊扩容物品。'),
  st('check','换上试用；不用凑满六条', '暂时停止加工，先确认新装备没有让属性需求或技能失效。',
     [compare,'在当前能稳定完成的地图比较；确认改善后，旧装备继续保留一段时间。'],
     '输出/生存/资源中至少解决实际缺口，其他关键条件仍满足。', '这轮结束。以后想进阶，再读对应作者工艺，不必现在全做。',
     '没有改善就换回原装；不是“材料已经花了，所以必须穿新装”。',kind='finish',refs=[AUTHOR],note='这是一套基础加工教学，不是作者对每个部位给出的确定性成品配方。')]
 entries=[{'label':'还没选好装备','step':'ready'},{'label':'白装，想试一次','step':'white'},{'label':'蓝装只有1条','step':'augment'},{'label':'蓝装已有2条','step':'regal'},{'label':'黄装，还有空位','step':'exalt'},{'label':'已有成品，先比较','step':'check'}]
 r=R('early-'+item,title,['early'],target,'挑当前能穿的备用装备；可自己捡，也可用自刷通货买合适蓝底。',steps,'craft-reference.html#early-'+item,entries=entries)
 r['helpful']=[prefix,suffix]; r['avoid']=avoid
 if item in ['bow','quiver']:r['alternative']='bow-noncrit' if item=='bow' else 'quiver-standard'
 if item=='amulet':r['alternative']='amulet'
 if item=='helmet':r['alternative']='helmet-stable'
 ROUTES.append(r)

# Functional items and ordinary jewels must NOT inherit six-affix gear logic.
for item,title,target in [
 ('flasks','生命／魔力药剂','选当前等级可用的基础药剂；核对回复量、持续时间、充能消耗。先解决实战回复。'),
 ('charms','咒符','选需要防的异常：冻结看融冰咒符，减速看真银咒符，点燃看浸润咒符；以物品说明为准。'),
 ('jewels','普通珠宝','Early先找当前攻击可用的伤害、攻速或击杀回蓝等功能；并非所有词条都出现在所有珠宝底材。')]:
  isj=item=='jewels'; name='珠宝' if isj else title
  steps=[st('ready','先选功能，不先花钱升级颜色', '保留现用品，确认新物品的需求与类型。暗金/特殊珠宝不走这条。',
     [target,'未鉴定先用知识卷轴；白色可选蜕变，蓝色有空位才考虑增幅。'],
     '物品功能能解决自己的缺口，能装备/镶嵌。','再选择下一步。','用途不对就换底材，不为颜色投入材料。',kind='prepare',refs=[AUTHOR,CUR]),
   st('trans','白色普通物品：蜕变一次','物品是普通白色，材料明确允许使用。',
     '右键【蜕变石】→左键这件备用物品一次。','变蓝并新增1条随机词缀。','看是否符合功能目标；有价值再补另一条。','新增不合用就停，不继续重复蜕变。',['normal-trans']),
   st('aug','蓝色还有空位：增幅一次','普通蓝色物品仅有1条随机词缀，材料可用。',
     '右键【增幅石】→左键备用物品一次。','新增1条随机词缀，读完整说明确认用途。','功能更好就先用，不要求和作者数值一模一样。','已有2条或被限制使用就停。',['normal-aug'])]
  if isj:
   steps += [st('regal','两条都值得保留：富豪一次','普通蓝色基本珠宝；不是暗金/失落时空珠宝；当前两条都有用。',
     '右键【富豪石】→左键珠宝一次。','变黄并增加1条随机词缀。','三个有效词缀已可先用。','一般的结果不立刻混沌，避免删掉已有好属性。',['normal-regal']),
     st('exalt','普通黄珠宝3条：可补第4条','普通稀有基本珠宝，当前3条，仍有合法一侧空位。普通上限4，不套防具的6条。',
     '右键普通【崇高石】→左键珠宝一次。','增加第4条随机词缀。','适用词条够用就结束。','已4条或目标侧满了就不点；特殊扩容属于另一条高风险工艺。',['normal-exalt'])]
  steps += [st('check','功能正常就结束', '先不再加工，检查是否可以实际使用。',
     ['换到正确位置，检查实际功能和需求。','记得原物品保留；新物品没解决问题就换回。'],
     '当前功能更可靠，而不是单纯颜色变化。','这一轮可以结束。','不要把与功能无关的高数值当成升级。',kind='finish',refs=[AUTHOR,CUR],
     note='药剂、咒符通常停留在魔法品质；不要照防具流程用富豪/崇高升黄。' if not isj else '五词缀珠宝工艺未完成机制验证，完整原文仍可查，但不是本路线下一步。')]
  r=R('early-'+item,title,['early'],target,'自己掉落或预算内购买功能正确的底材/成品。',steps,'craft-reference.html#early-'+item)
  r['entries']=[{'label':x,'step':y} for x,y in [('先核对类型','ready'),('白色物品','trans'),('蓝色1条','aug'),('直接验收','check')]]
  r['avoid']='不套用普通装备的三前缀三后缀规则。';ROUTES.append(r)

def prepare_advanced(id,title,phase,goal,start):
 q=next(x for x in old['recipes'] if x['id']==id)
 return R(id,title,phase,goal,start,[],'craft-advanced.html#'+id,'Fubgun原工艺＋逐步操作解释；国服未实测'),q

def necro(side,bone,afterstate=None):
 sidecn='左旋' if side=='left' else '右旋'; typ='前缀' if side=='left' else '后缀'; bid={'颚骨':'jaw','肋骨':'rib','锁骨':'collar','头骨':'cranium'}[bone]
 return st('desecrate',f'用{sidecn}死灵＋遗存{bone}，先加未显现词缀',f'黄装仍有{typ}空位，尚无已有渎灵词缀，部位与骸骨对应；会使用已解锁的灵魂之井。',
  [f'把【{sidecn}死灵预兆】放在人物背包，右键激活；其他可能影响此操作的预兆先停用。',f'右键【遗存{bone}】→左键备用装备一次。不是先点光明、剥离或腐烂预兆。'],
  f'出现未显现的渎灵词缀，预期落在{typ}；现在还没选到最终属性。',
  '去下一步显现；不要在未看候选前继续崇高补满。',
  '没有空位、已有渎灵、材料不适用或界面和预期不同：停止，不换成其他骨头乱试。',
  ['necro-'+side,bid],after=afterstate,refs=[ABYSS,OMEN,CUR],note='“左/右旋”指前缀/后缀，不是鼠标左右键。')

def reveal(target,afterstate=None):
 return st('reveal','到灵魂之井看候选，再选一条','装备带有未显现渎灵词缀；已经可以进入渎灵显现界面。',
  ['可选：准备使用【深渊回响预兆】时，在开始本次显现前放进背包并右键激活；不用就跳过。',
   '打开【灵魂之井 / Well of Souls】的显现功能，放入这件装备并查看候选。',
   '读完所有候选后，再选择并确认；不要仅凭颜色或T数字。'],
  '未显现词缀变成你选定的具体词缀。',target,
  '没有目标时：有本次回响机会才重掷；否则接受确实有用的次选，或先不确认停下来核对。已经确认后不能用回响改数值。',
  [],after=afterstate,refs=[ABYSS,OMEN],note='回响是可选材料，且每次消耗；不是永久重掷。中文菜单逐屏未做国服验收，以“显现渎灵词缀”的功能识别。')

def finish(title='对比旧装备，合用就停'):
 return st('finish',title,'当前加工先结束，所有需要的技能与装备需求仍满足。',
 ['装备后复查三抗、生命/护盾、力量/敏捷/智慧和精魂。','输出件用同一技能、同一地图难度比较；防御件同时看全身防御，不只看装备一条数值。'],
 '改善原本的缺口，且没有使核心技能失效。','保存旧装备后使用新装备。并非必须六条都好或全是T1。',
 '没有改善就换回；不要因为投入过材料就继续无上限返工。',kind='finish',refs=[AUTHOR])

def double_finish(before,after):
 return st('finish-mods','可选收尾：一次补两条',before,
 ['先确认至少有两个合法空位；把【强效崇高预兆】放背包并右键激活。',
  '确认没有会改动添加侧的其他预兆；默认选作者允许的【高级崇高石】，右键它，再左键装备一次。高预算可以改用【完美崇高石】，不是两种都点。'],
 '预兆使这一次崇高尝试添加两条随机词缀。','有用就保留；可不做这一步直接试用。',
 '空位不足、目标侧已经满，或不能接受随机结果：不做。点后没中目标也不自动接混沌。',
 ['double','greater-exalt'],after=after,refs=[OMEN,CUR],note='“强效崇高预兆”和“高级崇高石”是两个不同物品，前者不直接点在装备上。')

for crit in (False,True):
 id='bow-crit' if crit else 'bow-noncrit'; essence='seeking' if crit else 'abrasion'
 title='暴击弓｜准备04/05' if crit else '非暴击弓｜Early之后的进阶'
 r,q=prepare_advanced(id,title,['crit','high'] if crit else ['mid','early'],('保留物理提高，加入本地暴击和伤害前缀。' if crit else '物理提高＋物理点伤＋冰伤等伤害前缀；不是Early必备高配。'), '作者使用物品等级75的弓；毁灭者之弓/寻战之弓按人物实际等级和敏捷能装备再选。')
 r['steps']=[st('ready','找对蓝底；这一步不花精华',r['start'],
 ['先保留现用弓。买或拾取一把未腐化、未镜像的备用蓝弓，已有“物理伤害提高”前缀。','若只有这一条，先用增幅石补成一前一后；这里不先富豪。'],
 '蓝弓有2条随机词缀：物理提高前缀＋1条后缀。',
 '确认是本地物理提高，不是已有物理点伤。后缀与即将添加的暴击率不冲突。' if crit else '确认尚无物理点伤词缀，预留其合法前缀位置。',
 '没有这种蓝底：先按Early普通路线做能用的装备；不在唯一现用弓上洗。',
 [],[['前缀1','物理伤害提高'],['后缀1','现有后缀（暴击路线不能已占同组）']],refs=[AUTHOR,ESS],kind='prepare'),
 st('essence','用'+MAT[essence]['zh']+'一次', '蓝弓恰好一前一后：前缀是物理伤害提高，后缀不占将添加的词缀组。人物能穿，且材料提示为魔法升稀有。',
 ['右键【'+MAT[essence]['zh']+'】→左键这把蓝弓一次。','点完先核对新增词缀和名称颜色，不连续用第二种精华。'],
 '变黄，并新增本地暴击率后缀。' if crit else '变黄，并新增物理点伤前缀。',
 '预期为1前缀＋2后缀，仍有伤害前缀空位。' if crit else '预期为2前缀＋1后缀，仍留一条前缀空位。',
 '已经被你富豪升黄，或后缀/前缀同组冲突：不要用这一步；返回核对状态。',
 [essence], after=([['前缀','物理提高'],['后缀','原有后缀＋本地暴击']] if crit else [['前缀','物理提高＋物理点伤'],['后缀','原有后缀']]),refs=[MAT[essence]['url'],ESS]),
 necro('left','颚骨'),reveal('优先选高物理点伤；作者也接受高阶元素点伤。没有物理点伤不是自动判定报废。' if crit else '优先选附加冰霜伤害；作者也接受高阶其他元素点伤。不要把法术伤害或不适用的附加伤害当作同一效果。'),
 double_finish('显现已完成；暴击弓典型为2前2后，非暴击弓典型为3前1后。先数实际占位，不按模板强推。',
 [['成品','以实际新增词缀为准，不保证目标后缀']]),finish()]
 r['entries']=[{'label':'还没选蓝底','step':'ready'},{'label':'已是合格2词缀蓝弓','step':'essence'},{'label':'已精华升黄','step':'desecrate'},{'label':'已有未显现词缀','step':'reveal'},{'label':'已显现，考虑收尾','step':'finish-mods'}]
 ROUTES.append(r)

r,q=prepare_advanced('quiver-standard','黄箭袋｜常规进阶',['mid','crit','high'],'点伤/弓伤害＋攻速/等级等词缀。已经有好箭袋就不必重做。','作者起点物品等级75；蓝箭袋一前一后都适合当前阶段。')
r['steps']=[st('ready','找两条已经满意的蓝箭袋',r['start'],
 ['前缀目标：攻击附加物理/冰霜伤害，或弓技能伤害。后缀目标：攻速、投射物等级；转暴击后再重视暴击。',
 '可直接买这样的蓝底。自己从白底找时，作者用高级/完美蜕变和增幅；没有命中目标就换底材，不在同一蓝装反复点蜕变。'],
 '1条好前缀＋1条好后缀。','符合才用下一步完美富豪。','只有一条适用，另一条完全无用：先停，不靠后续昂贵材料救底材。',kind='prepare',refs=[AUTHOR,CUR]),
 st('regal','完美富豪一次；先看第三条','未腐化两词缀蓝箭袋；明确要做作者这条较高投入路线。',
 '右键【完美富豪石】→左键箭袋一次。','变黄，新增1条随机词缀。作者希望是好后缀，但不保证。','第三条有用且仍有后缀位，再看渎灵。',
 '第三条差：新手默认保留半成品先比较，不用高级混沌盲赌。作者的随机替换分支在原文保留，可能删掉前两条好属性。',['perfect-regal'],refs=[AUTHOR,CUR]),
 necro('right','颚骨'),reveal('优先找未重复词缀组、当前真正需要的攻速/等级/暴击后缀；不是每个候选都一定包含这些。'),
 double_finish('已显现，至少有两个合法总空位；某侧空位决定新增落点，不能只按“还差两条”判断。',[['新增','2条随机属性，实际前后缀依状态']]),finish()]
r['entries']=[{'label':'从好蓝底开始','step':'ready'},{'label':'两条已满意','step':'regal'},{'label':'富豪后仍有后缀位','step':'desecrate'},{'label':'已有未显现词缀','step':'reveal'}];ROUTES.append(r)

r,q=prepare_advanced('helmet-stable','护盾头｜03转型开始',['hybrid','crit','high'],'平铺护盾＋百分比护盾＋复合护盾，再补后缀。','作者起点物品等级78；选择纯护盾底材并核对智慧与人物等级。')
r['steps']=[st('ready','先找高平铺护盾蓝头',r['start'],
 ['找本地“最大能量护盾＋数字”的高阶前缀，不是只找百分比；作者以T1为起点。','蓝头已增幅为两词缀，另一条是可保留的后缀。可直接购买蓝底，不要求自己无限蜕变。'],
 '1条平铺护盾前缀＋1条后缀。','已有好平铺，才进入强效增强路线。','只有百分比没有平铺：不直接照这条；原文另一路线可以看，但别混成同一件。',kind='prepare',refs=[AUTHOR,CUR]),
 st('essence','强效增强精华一次','蓝色纯护盾头，两词缀；无同组防御提高词缀冲突。',
 '右键【强效增强精华 / Greater Essence of Enhancement】→左键头盔一次。',
 '变黄并加对应本地防御提高前缀；保留原平铺护盾。','核对头盔上方最终护盾与词缀占位，再渎灵。','不要换成项链使用的完美强化精华；材料效果或名字不一致先停。',['enhance-greater'],after=[['前缀','平铺护盾＋本地防御提高'],['后缀','原有1条']],refs=[MAT['enhance-greater']['url'],ESS]),
 necro('left','肋骨'),reveal('选复合百分比护盾词缀；一条复合词缀可能显示两行。最终物品护盾改善即可考虑先用，不要求三条全T1。'),
 st('suffix','后缀补强：先决定投入','显现已完成，读实际前后缀。作者按前缀质量决定用多少材料。',
 ['复合护盾一般：有空位时可用【高级崇高石】一次，再观察。','复合护盾很好且有两个合法空位：作者允许【强效崇高预兆】＋【完美崇高石】一次；不能两种方案都不看结果接着用。'],
 '增加随机后缀/词缀，未必是抗性。','当前护盾与抗性够用就停；作者约450物品护盾的转型建议不是保过线。',
 '剩余空间不符、预算不足或继续做会超支：保持半成品先用，不拿混沌“修好”。',['greater-exalt'],refs=[AUTHOR,CUR,OMEN]),
 st('quality','可选最后一步：品质收尾','普通词缀与所需插槽均已处理，且接受可能腐化造成的后续加工限制。',
 '按材料完整提示，右键【瓦尔护甲师注能装置】→左键头盔一次；每次后先观察，不无限连点。',
 '品质可能提高，也可能腐化。','只在不再需要常规返工时考虑；这一步可以不做。','还想修改词缀或不愿承担腐化，就跳过。普通瓦尔宝珠不是替代品。',['infuser'],refs=[CUR],kind='optional'),finish()]
r['entries']=[{'label':'找平铺护盾蓝头','step':'ready'},{'label':'好蓝头已准备','step':'essence'},{'label':'已精华升黄','step':'desecrate'},{'label':'准备显现','step':'reveal'},{'label':'只看品质收尾','step':'quality'}];ROUTES.append(r)

# High-investment amulet: break every resource-consuming operation into an explicit state.
r,q=prepare_advanced('amulet','＋3与精魂项链｜高投入',['crit','high'],'＋3真正破溃固定，再做精魂与防御；不是普通＋3就能清理。','作者使用物品等级80；追顶阶抗性时用82。必须是已锁定＋3投射物等级的稀有项链。')
r['steps']=[st('ready','确认“＋3已经锁定”','物品可加工，＋3投射物技能等级明确为破溃固定词缀，不是普通随机词缀。',
 ['在高级说明确认“破溃/固定”的标记，不能只凭文字是金色。','不想自己赌破溃，可买已锁好的底材；仅有普通＋3的项链不要进入下一步。'],
 '后续普通随机移除不会把固定的＋3当成一般可变词缀。','确认固定后，才允许清理。','无法确认破溃：保留原项链不动。不要用剥离试验它会不会掉。',kind='prepare',refs=[AUTHOR,CUR]),
 st('annul','只留下固定＋3和另一条','明确已固定＋3；能够接受其余所有非固定词缀丢失，且不是唯一现用项链。',
 ['右键【剥离石】→左键项链一次，读剩余随机词缀数。','仍多于2条才考虑再做一次；到“固定＋3＋另一条”立刻停止。'],
 '总共2条词缀，其中1条是固定＋3。','到2条就去下一步，不要再剥。','原有精魂/抗性很值钱而不想丢：不清理，换另一件底材。不要按文字行数剥。',['annul'],refs=[AUTHOR,CUR],note='这里允许删除其他词缀，是因为明确从重做底材开始，不是让你清掉现用品。'),
 st('spirit','混沌一次一次找精魂','稀有项链恰好2条：固定＋3＋唯一可变词缀；预算已决定。',
 '右键普通【混沌石】→左键项链一次，读那条可变词缀。每次后先看结果。',
 '只剩一个非固定词缀可被替换，但新词缀类别仍随机。','出现你准备接受的精魂（作者目标T1/T2），就停止混沌。','没出精魂可在事先预算内再试；预算耗尽就停。若不止一个可变词缀，不能认为只换某条。',['chaos'],after=[['前缀','精魂'],['后缀','固定＋3投射物']],refs=[AUTHOR,CUR]),
 st('filler','加一条准备牺牲的后缀','恰好固定＋3后缀＋精魂前缀；另一后缀位空着。',
 ['背包右键激活【右旋崇高预兆】，先停用其他崇高效果预兆。','右键普通【崇高石】→左键项链一次。'],
 '增加1条非固定后缀。它下一步要被移除，不需要很好。','现在为1前缀＋2后缀，其中＋3固定。','不是这个状态就不继续。不要先补满后缀或贪图留下新后缀。',['exalt-right','normal-exalt'],refs=[AUTHOR,OMEN,CUR]),
 st('defence','只移除填充后缀，补防御前缀','前缀只有精魂；后缀为固定＋3和唯一可删除填充词缀。材料提示必须匹配本操作。',
 ['背包右键激活【右旋结晶预兆】。','右键【完美强化精华 / Perfect Essence of Enhancement】→左键项链一次。'],
 '填充后缀被替换，加入项链全局防御提高前缀；固定＋3与精魂保留。','现在2前缀＋1后缀，才看抗性。','若有多条可删后缀、已有同组前缀或材料提示不同，停止；普通/强效同系列精华不能替代。',['crystal-right','enhance-perfect'],refs=[OMEN,MAT['enhance-perfect']['url']],note='作者简写未给等阶；此处按稀有替换机制消歧为Perfect，国服提示不一致时不要执行。'),
 st('quality','先补对应催化品质到20%','要用催化崇高提高某类词缀机会；当前没有该轮消耗过的品质。',
 ['选择作者对应元素的催化剂（Tul / Xoph / Esh，逐项读材料改变哪一类）。','右键催化剂→左键项链，逐次查看品质；到20%停止。'],
 '项链有20%对应类别催化品质。','再做下一步一次崇高；不是品质本身保证抗性。','不清楚当前国服催化剂对应元素就先不买；不是任意品质材料都能替代。',['catalyst'],refs=[AUTHOR,OMEN],note='这几种催化剂的精确国服名称未逐项核验，保留英文消歧；本轮不指定未验证的购买简称。'),
 st('resist','一次定向后缀；品质会耗尽','后缀有位，催化品质20%；精魂与防御前缀保持。',
 ['背包激活【右旋崇高预兆】和【催化崇高预兆】，逐一确认本次效果。','右键【完美崇高石】→左键项链一次。'],
 '加一个随机后缀，同时消耗催化品质；不保证抗性。','该后缀满意且还有位：第二次要先回“补品质”，每轮重新准备两种预兆。','普通坏后缀不能用光明预兆安全定向删除；接受结果/暂停/买半成品。不要用剥离赌删坏词。',['exalt-right','catalysing','perfect-exalt'],refs=[AUTHOR,OMEN,CUR],note='最多做实际后缀空位允许的次数；网页不读取你的词缀。'),
 necro('left','锁骨'),reveal('只选当前能改善生命/防御/资源的适用前缀。Fubgun未指定唯一最终前缀，不强造一个词条。'),finish()]
r['steps'][-3]['before']='前缀仍有最后1个位，其余属性已满意；当前没有渎灵词缀。不是把普通坏后缀改成渎灵。'
r['entries']=[{'label':'先核对破溃底材','step':'ready'},{'label':'固定＋3，其他可以清掉','step':'annul'},{'label':'已是固定＋3＋1条','step':'spirit'},{'label':'已有精魂和固定＋3','step':'filler'},{'label':'防御前缀已完成','step':'quality'},{'label':'后缀满意，留1前缀','step':'desecrate'}];ROUTES.append(r)

# Routes with unresolved state prerequisites remain readable but explicitly stop at the gap.
r,q=prepare_advanced('quiver-advanced','破溃箭袋｜接合格半成品',['crit','high'],'已有锁定点伤后再做弓伤，避免把不明“1/3”直接当概率。','作者ilvl75路线的自制破溃起点有省略。可从已破溃高点伤的合格半成品开始。')
r['steps']=[st('ready','先确认到底锁了哪一条','高点伤前缀已破溃；不是仅有＋2等级或任意破溃箭袋。',
 ['直接检查固定词缀身份。原文“1/3”不能代替破溃宝珠至少4词缀的使用条件。','购买符合状态的半成品，是避开不明起步环节的一种方法；不要把普通高点伤箭袋当作已锁。'],
 '点伤前缀固定，其他词缀状态已逐条记录。','还需核对下一步唯一可删前缀。','锁错词或不确定就停止；本页不补造破溃成功率。',kind='prepare',refs=[AUTHOR,CUR]),
 st('filler','准备唯一可删除的填充前缀','固定点伤之外，恰好还有1条可删除前缀；目标弓伤害词缀组尚未占用。',
 ['已有该状态就不加材料。','没有填充前缀时，只有确认下一颗崇高的合法新增侧为前缀，才讨论补1条；不确定则选状态已经匹配的半成品。'],
 '前缀侧：固定点伤＋1条可删填充；另留合法位置。','与示意完全一致，再看浮夸步骤。','有两条可删好前缀：无法保证删的是哪条；不要赌。',kind='prepare',refs=[AUTHOR,CUR],note='不是用鼠标点中某一条词缀就会指定它。'),
 st('hysteria','浮夸精华替换填充前缀','固定点伤＋唯一可删填充前缀；弓伤害组不冲突；稀有箭袋可加工。',
 ['背包右键激活【左旋结晶预兆】。','右键【浮夸精华】→左键箭袋一次。'],
 '在这个明确状态下，移除填充前缀并加入箭袋指定弓伤害前缀。','核对固定点伤仍在、弓伤已加，再准备收尾。','前置状态不同，不执行；不是整件装备必成或任意黄箭袋都可做。',['crystal-left','hysteria'],refs=[OMEN,MAT['hysteria']['url']]),
 st('prefix','只剩最后前缀可加时，再崇高一次','后缀已满或已经确认定向前缀；还有1个目标前缀空位。',
 '右键【完美崇高石】→左键箭袋一次。',
 '增加随机前缀；可能是你不想要的命中。','结果合用就保存；不满意也不要盲目移除其他普通好属性。','两侧都有空位又没确认定向时，不能称为“只加前缀”。',['perfect-exalt'],refs=[AUTHOR,CUR]),
 st('redo','只重做“已经显现的渎灵后缀”','你要改的那1条明确是渎灵后缀；没有其他渎灵/特殊状态；其余属性满意。',
 ['在背包激活【光明预兆】；再右键【剥离石】→左键箭袋一次。','确认只移除了该渎灵词缀，并重新读后缀空位；下一步才是重新右旋死灵＋颚骨。'],
 '移除原渎灵后缀，留出再渎灵的位置。','按后面渎灵和显现步骤逐轮做；每轮重新花材料。','目标是普通后缀而非渎灵：不要点剥离。光明不能保护式删除任意垃圾词缀。',['light','annul'],refs=[OMEN,CUR]),
 necro('right','颚骨'),reveal('目标为适用的攻速/暴击等后缀；每轮先定预算，不把回响理解为无限重掷。'),finish()]
r['entries']=[{'label':'核对半成品','step':'ready'},{'label':'已满足唯一可删前缀','step':'hysteria'},{'label':'只剩1前缀空位','step':'prefix'},{'label':'只想重做渎灵后缀','step':'redo'}];ROUTES.append(r)

r,q=prepare_advanced('helmet-random','护盾头｜另一条随机路线',['hybrid','crit','high'],'保留好蓝底，把另一护盾前缀的随机机会留给渎灵/崇高。','原文未指明每个抗性/稀有度精华的等阶；这不是同前一条混着做。')
r['steps']=[st('ready','起点可为高平铺或高百分比','物品等级78的好蓝头；一条高阶本地护盾前缀，另一条后缀也值得保留。',
 ['先分清是平铺＋护盾、百分比护盾还是复合护盾。','准备两词缀蓝底；没有好蓝底就用前一条较清楚的路线。'],
 '1条好护盾前缀＋1条好后缀。','下一步需自行核对确切材料。','底材和防御差，不因一个T1就投入。',kind='prepare',refs=[AUTHOR]),
 st('essence','先确定精华版本；不能把简称直接照点','原文只说抗性或稀有度精华，未明确等阶。',
 ['只考虑提示为“魔法升稀有”的精华，且它在护甲上指定的词缀是你需要的属性。','核对已有后缀与目标组不冲突、人物能满足升黄后需求，再按这颗材料提示使用一次。'],
 '保留好护盾蓝底，变黄并加你预先核对的实用属性。','已确认材料并得到预期状态，才读后续。','不会判断材料等阶/词缀组：不执行这一环；改用“护盾头较可控路线”或买对应半成品。',kind='boundary',refs=[AUTHOR,ESS],note='不是默认每种精华均可互换。本路线保留完整说明，但不能称为无前提照抄。'),
 necro('left','肋骨'),reveal('找好阶级的复合护盾；回响在开始显现前准备，不能先确认词缀再用回响抬数值。'),
 double_finish('显现后实际还有至少两个合法空位，并愿意接受两条随机属性。',[['新增','按前后缀空位随机决定']]),finish()]
ROUTES.append(r)

r,q=prepare_advanced('emerald','翡翠珠宝｜高投入原文解释',['high'],'作者的扩容珠宝工艺有未验证环节，不拿普通4条珠宝硬点到5条。','攻击暴击伤害加成已破溃固定的普通类型翡翠珠宝；不是暗金或失落时空珠宝。')
r['steps']=[st('ready','先认起点与固定词缀',r['start'],
 ['作者目标20%攻击暴击伤害加成，注意不是法术暴伤。','普通3–4条适用珠宝就能先用；后面的扩容工艺不是进入04/05的前置条件。'],
 '锁定词缀身份明确。','阅读下一步了解成本；不是要求现在动手重做好珠宝。','固定的不是攻击暴伤，或仍需要这颗现用品，就停止。',kind='prepare',refs=[AUTHOR,CUR]),
 st('crit','混沌找暴击率；其他词缀也可能丢','固定暴伤已经确认，剩余可变词缀允许损失且有预算。',
 '每次只使用1颗混沌石，出现需要的暴击率后立即停下来。',
 '固定词缀之外的属性仍被随机替换。','保留暴击率后再核对原文要求的4词缀状态。','不是只改某条垃圾；有不愿丢的未固定好属性时不要做。',['chaos'],refs=[AUTHOR,CUR]),
 st('capacity','扩容与后续：仅作原文解释，先不要照做','作者要求4词缀珠宝，再用强效的液化轻蔑添加允许额外词缀的工艺。',
 ['原文后面还有渎灵攻速、左旋剥离、移除扩容工艺后再加到5条及凶残收尾。','“删除扩容后仍可维持5词缀”的当前国服机制未验证；完整原文可以查看，但此处不提供执行指令。'],
 '需要先有同版本容量规则与可复现状态，才能安全解释余下工艺。','当前替代：用适用的3–4词缀珠宝，或核查后购买已经做好的成品。','不要为了网页写“5条”，就在普通满4条珠宝上试点液化/剥离。',kind='boundary',refs=[AUTHOR,CUR],note='未确认的是后续容量机制，不是隐藏后期内容。原文8步在同页链接完整保留。'),finish('先用普通有效珠宝，不被未验证步骤卡住')]
ROUTES.append(r)

# Current Chinese data maps elemental catalysts; amounts are not a drop/price claim.
for mid,zh,en,typ,slug in [
 ('tul','托沃催化剂',"Tul's Catalyst",'冰霜','Tuls_Catalyst'),
 ('xoph','索伏催化剂',"Xoph's Catalyst",'火焰','Xophs_Catalyst'),
 ('esh','艾许催化剂',"Esh's Catalyst",'闪电','Eshs_Catalyst')]:
 MAT[mid]={'id':mid,'zh':zh,'en':en,'effect':'给戒指或项链添加'+typ+'类别催化品质；会取代其他催化品质。','check':'要配合催化崇高时，按该步骤先补到20%，每次消耗后需重新补。提高该类出现机会不保证抗性。','url':'https://poe2db.tw/cn/'+slug,'source':'currency'}
a=next(x for x in ROUTES if x['id']=='amulet')
sq=next(x for x in a['steps'] if x['id']=='quality')
sq['action']=['本轮选一种：托沃催化剂（冰霜）、索伏催化剂（火焰）、艾许催化剂（闪电）。按你希望偏向的类别选，不是三种混用。','右键所选催化剂→左键项链，每次后查看品质；到20%停止。']
sq['materials']=['tul','xoph','esh']
sq['note']='三种材料为三选一；中文来自当前国际服数据的简体展示，实际国服提示不匹配时停止。'
sq['bad']='不是任意品质材料都能替代。换另一种催化剂会取代原品质类型，别混着点。'
sq['refs']=[CUR,OMEN]+[MAT[x]['url'] for x in ('tul','xoph','esh')]
# Step cards use one exact material by default, not ambiguous grouped old labels.
MAT['normal-chaos']={'id':'normal-chaos','zh':'混沌石','en':'Chaos Orb','effect':'随机删除稀有装备1条可修改词缀，再增加1条随机词缀。','check':'不是只删除坏属性；只有明确只剩一个可修改词缀时，才能限定被替换的对象。','url':'https://poe2db.tw/cn/Chaos_Orb','source':'currency'}
MAT['preserved-jaw']={'id':'preserved-jaw','zh':'遗存颚骨','en':'Preserved Jawbone','effect':'给符合条件的稀有武器或箭袋增加未显现的渎灵词缀。','check':'需合法词缀空位；不要把其他部位的骸骨、低阶啃噬颚骨或已显现词缀当作相同状态。','url':'https://poe2db.tw/cn/Preserved_Jawbone','source':'currency'}
for rr in ROUTES:
 for ss in rr['steps']:
  ss['materials']=[{'chaos':'normal-chaos','jaw':'preserved-jaw'}.get(mm,mm) for mm in ss['materials']]
# Make all ids and step links valid; allow direct reading without progress locks.
for r in ROUTES:
 for i,s in enumerate(r['steps']):
  s['next']=r['steps'][i+1]['id'] if i+1<len(r['steps']) else None
 r.setdefault('avoid','每一步只在实际装备与“操作前”完全匹配时执行；随机结果不符合就停，不连点补救。')
 r.setdefault('helpful',[])
 for s in r['steps']:
  for m in s['materials']:assert m in MAT,(r['id'],m)
 assert len({s['id'] for s in r['steps']})==len(r['steps']),r['id']

D={'version':'R9 / 打造照做版','date':'2026-09-26','default':'early-bow',
 'phases':[{'id':'early','name':'01 Early起步'},{'id':'mid','name':'02 非暴击补强'},{'id':'hybrid','name':'03 混合防御'},{'id':'crit','name':'04 暴击装备'},{'id':'high','name':'05 高投入'},{'id':'all','name':'全部路线'}],
 'materials':MAT,'routes':ROUTES,
 'evidence':[{'label':'原始依据','url':AUTHOR,'note':'Fubgun 0.5.5原文工艺；已上传原文完整保留，未引入其他作者配方。'},
 {'label':'材料机制','url':CUR,'note':'国际服游戏数据中文展示；不是国服逐屏实测。'},
 {'label':'精华类型','url':ESS,'note':'区分魔法升稀有与稀有移除再增加。'},
 {'label':'预兆与激活','url':OMEN,'note':'右键在背包激活；本次效果触发时消耗。'},
 {'label':'渎灵与灵魂之井','url':ABYSS,'note':'未显现→候选→确认的不同阶段；具体国服菜单位置未逐屏核验。'}],
 'limitations':['按装备状态给操作，不扫描游戏，不模拟随机词缀或保证成品。','护盾头随机路线精华简称、珠宝扩容等未知点保留警示；不能把阅读按钮当作游戏验证。','只有打造页改为按步操作，其他R8阶段数据保持；已有天赋与国服核验缺口不因此补齐。']}
(ROOT/'data/打造按步操作_R9.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('routes',len(ROUTES),'steps',sum(len(r['steps']) for r in ROUTES),'materials',len(MAT))
