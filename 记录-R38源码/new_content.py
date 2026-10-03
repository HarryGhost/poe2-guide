"""R38 editorial additions. Original source snapshots are deliberately left intact."""
from copy import deepcopy
from collections import Counter, defaultdict
DATE='2026-10-02'
AUTHOR='https://mobalytics.gg/poe-2/builds/ice-shot-deadeye'
GGG='https://www.pathofexile.com/forum/view-thread/3826682'
DB='https://poe2db.tw/'

def apply(D):
    essence={}
    def add(k,zh,en,side,effect,slots,why,limit):
        essence[k]=dict(id=k,zh=zh,en=en,side=side,effect=effect,slots=slots,why=why,limit=limit,url=DB+'cn/'+en.replace(' ','_'))
    armour=['body','helmet','gloves','boots']; jewellery=['amulet','belt','rings']
    add('abrasion','强效磨蚀精华','Greater Essence of Abrasion','前缀',{'bow':'附加 (16–24) 至 (28–42) 物理伤害'},['bow'],'非暴击物理底弓补本地点伤；作者进阶路线用它配合已有本地物理提高。','不能给箭袋、戒指补物理点伤；已有同组本地物理点伤时先停止核对。')
    add('haste','强效急速精华','Greater Essence of Haste','后缀',{'bow':'攻击速度提高 14–16%'},['bow'],'已有合用伤害前缀，且缺攻速时的普通替代选择，不与磨蚀连续使用。','只在适用武器上加攻速；不用于鞋子补移速，也不用于手套或箭袋加攻速。')
    add('seeking','强效寻觅精华','Greater Essence of Seeking','后缀',{'bow':'+(3.11–3.8)% 本地暴击率'},['bow'],'04/05暴击弓的作者路线；先确定要转暴击，再与箭袋、天赋及整套配置配合。','这是本地暴击率加值，不是暴击伤害。与强效磨蚀同为升黄分支，不能在同一件蓝弓上先后使用。')
    add('enhancement','强效增强精华','Greater Essence of Enhancement','前缀',{x:'该物品护甲、闪避值与能量护盾提高 68–79%' for x in armour},armour,'先有合适的平铺防御，再加对应本地百分比防御；03起护盾头的作者稳定路线使用此精华。','不凭空给没有护盾基础的底材造出护盾；已有同组百分比防御时不能照抄。不能保证成品防御总值。')
    life_hi={x:('+(100–119) 最大生命' if x in ['body','helmet','belt'] else '+(85–99) 最大生命') for x in armour+['amulet','belt']}
    add('body-greater','强效身躯精华','Greater Essence of the Body','前缀',life_hi,list(life_hi),'需要生命，并愿意用一个前缀解决时。','不适用于戒指；已有同组生命词缀时停止核对。高阶不代表所有部位都适用。')
    life_normal={x:('+(85–99) 最大生命' if x in ['body','helmet','belt'] else '+(70–84) 最大生命') for x in armour+jewellery}
    add('body-normal','身躯精华','Essence of the Body','前缀',life_normal,list(life_normal),'戒指要精华保生命时用普通身躯；其他适用部位可作为较低投入选择。','普通身躯可用于戒指，强效身躯不行；为做戒指不要先把普通身躯合成强效。')
    for k,zh,en,eff in [('fire','强效绝缘精华','Greater Essence of Insulation','+(31–35)% 火焰抗性'),('cold','强效熔解精华','Greater Essence of Thawing','+(31–35)% 冰霜抗性'),('lightning','强效接地精华','Greater Essence of Grounding','+(31–35)% 闪电抗性'),('chaos','强效摧灭精华','Greater Essence of Ruin','+(16–19)% 混沌抗性')]:
        add(k,zh,en,'后缀',{x:eff for x in armour+jewellery},armour+jewellery,'按整套缺口只选择其中一种；不是让同一件连用四颗。','已有同组对应抗性、该后缀无合法位置，或当前已升黄时，不按这条执行。')
    add('infinite','强效永恒精华','Greater Essence of the Infinite','后缀',{x:'+25–27 力量／敏捷／智慧中的一种（结果不由你指定）' for x in armour+jewellery+['quiver']},armour+jewellery+['quiver'],'只在能接受随机属性结果时考虑；它不是定向智慧精华。','只能接受智慧才能穿装／用宝石时，不把此精华当确定解法。已有属性的词缀组限制仍要核对。')
    add('battle','强效战斗精华','Greater Essence of Battle','前缀',{'quiver':'+(237–346) 命中值','gloves':'+(237–346) 命中值'},['quiver','gloves'],'确实缺命中且愿意用一个前缀时，作为普通升黄选项。','不能保证投射物等级、弓伤、物理点伤或攻速；命中已足够就不为“用精华”硬加。')
    resist=['fire','cold','lightning','chaos']
    slots={
        'bow':dict(name='弓',route='early-bow',options=['abrasion','haste','seeking'],default='abrasion',start='普通物理底弓先保住有用的本地物理提高前缀与一条合用后缀；已有相同目标词缀组就不再强塞。',choice='非暴击优先比较物理点伤缺口；转暴击后再看强效寻觅。没有合适精华或预算不足，富豪仍是可选随机分支。',stop='基础物理太低、精华与现有词缀冲突，或目标不是当前阶段需要的属性就停。作者物等75的进阶路线，不套成所有过渡蓝弓的最低门槛。',advanced=[('bow-noncrit','作者非暴击完整工艺：磨蚀 → 预留渎灵前缀 → 显现后收尾'),('bow-crit','作者暴击完整工艺：寻觅；不与磨蚀升黄叠用')]),
        'quiver':dict(name='箭袋',route='early-quiver',options=['battle','infinite'],default='battle',start='优先保住当前阶段需要的弓相关有效词缀；先确认是否真的缺命中或可接受随机属性。',choice='没有相符的缺口就用原富豪分支，或直接找合格半成品。这里没有用普通精华保“弓物理点伤／攻速／投射物等级”的通用配方。',stop='只是想多一条输出属性，却拿命中／随机属性精华凑数时停止。磨蚀、急速和寻觅不能从弓规则套到箭袋。',advanced=[('quiver-standard','作者普通箭袋路线：富豪与随机补词缀'),('quiver-advanced','浮夸精华是另一个高投入替换路线；保留只读限制')]),
        'body':dict(name='衣服',route='early-body',options=['enhancement','body-greater']+resist,default='enhancement',start='选择符合当前生命／混合防御阶段的底材；要走百分比防御，就先有合用平铺防御，并留目标前缀。',choice='防御不足看强效增强；生命或抗性不足分别选身躯或对应抗性，不把全部候选都当必选。',stop='后期转防御体系时不能只看生命涨了多少；需要预留防御前缀却被生命占用就暂停，回看本阶段成品目标。',advanced=[]),
        'helmet':dict(name='头盔',route='early-helmet',options=['enhancement','body-greater']+resist,default='enhancement',start='Early按当前防御底材处理；03起要护盾头时先有平铺护盾前缀，再判断百分比护盾位置。',choice='护盾头优先读作者稳定路线；Early补生命／抗性不等于已经完成后期护盾转型。',stop='闪避帽上的强效增强不会变出护盾头；已有同组百分比防御时停止，不直接覆盖。',advanced=[('helmet-stable','03起护盾头的稳定工艺：强效增强与后续预留'),('helmet-random','随机替换工艺另列，风险与稳定路线不同')]),
        'gloves':dict(name='手套',route='early-gloves',options=['body-greater','enhancement','battle']+resist,default='body-greater',start='先保住所需防御／伤害基础及合用后缀，按生命、防御、命中或抗性缺口选一颗。',choice='强效战斗只保证命中；强效增强只处理本地防御，二者都不是保证攻速或物理点伤。',stop='不要把强效急速在武器上的攻速效果套到手套；目标伤害词缀没保住时先另找蓝底。',advanced=[]),
        'boots':dict(name='鞋子',route='early-boots',options=['body-greater','enhancement']+resist,default='body-greater',start='先找到有可接受移动速度的蓝鞋，再考虑生命／防御／抗性；移动速度和生命／防御都要核对前缀位置。',choice='这组普通升黄候选不保证移速。现有蓝鞋移速不够时，先换起点，而不是指望强效急速补移速。',stop='为补生命而把需要的前缀位置用完、或移速不达目标就停。浮夸精华给移速属于黄装随机删除替换，不作为新手默认。',advanced=[]),
        'amulet':dict(name='项链',route='early-amulet',options=['body-greater','infinite']+resist,default='body-greater',start='先看本阶段项链是否要保技能等级／精魂及智慧缺口；确定保留词缀与后续空位。',choice='普通升黄解决生命或抗性；强效永恒只能随机属性，不保证智慧，更不能保证＋3投射物等级或精魂。',stop='当前必须定向补智慧时不赌随机属性；需要做高级＋3与精魂工艺时，不先用普通路线把位置填满。',advanced=[('amulet','＋3与精魂的完美强化路线另看；不是普通升黄下一步')]),
        'belt':dict(name='腰带',route='early-belt',options=['body-greater','infinite']+resist,default='body-greater',start='先确认腰带底材及实际咒符槽条件；蓝装保留已有有效属性，再按生命、抗性、随机属性缺口选。',choice='强效身躯在腰带上是100–119生命档；强效永恒不是保证力量。暗金腰带不使用这些升黄步骤。',stop='咒符槽不足不会因普通身躯／抗性精华自动解决；成品暗金目标另按获取方式处理。',advanced=[]),
        'rings':dict(name='戒指',route='early-rings',options=['body-normal','infinite']+resist,default='body-normal',start='两枚戒指分别对照目标；先保住有用点伤或需要的后缀，选精华前检查生命／抗性的同组冲突。',choice='缺生命选普通“身躯精华”，对应70–84生命；强效身躯不能用于戒指。普通磨蚀也不能照弓的规则给戒指保物理点伤。',stop='不能接受属性随机时不靠强效永恒保智慧；抗性按整套缺口分摊，不让两枚都机械重复同一套候选。',advanced=[])
    }
    D['essenceGuide']={'version':'R38','checked':DATE,'source':AUTHOR,'ruleSource':GGG,'catalog':essence,'slots':slots,
       'scope':'本站按游戏数据补充的普通蓝装升黄决策；并非作者逐部位新发布的固定毕业配方。保留原作者进阶路线与只读限制。',
       'rules':['普通／强效精华：魔法蓝装升级稀有并添加该精华对应词缀；它与富豪是使用前二选一。','完美／特殊精华：对稀有装备进行删除、替换的另一类操作；不是这里升黄后的通用连招。','每次只选一颗。名称、阶级、物品类别与目标词缀组都相符才使用；颜色和文字行数不能代替前后缀判断。','下面的区间是对应数据范围，不是必得最高值；低阶替代要重新核对部位和效果，不默认高阶一定更合适。']}
    # Add material records; never overwrite baseline materials.
    for k,m in essence.items():
        D['materials']['r38-'+k]={'zh':m['zh'],'en':m['en'],'effect':'；'.join((slots[s]['name'] if s in slots else s)+'：'+e for s,e in m['effect'].items()),'check':m['limit'],'url':m['url'],'source':'R38 精华选择补充'}
    for slot,g in slots.items():
        rec=D['executionViews']['routes'][g['route']];r=rec['route'];r['essenceSlot']=slot
        for st in r['steps']:
            if st['id']=='augment':st['next']='essence-choice'
            if st['id']=='regal':
                st.update(title='已选富豪分支：随机升黄一次',action=['确认不使用上方任何蓝装升黄精华，再用普通富豪石一次。','这次只增加一条随机词缀；升黄后不要返回精华升黄步骤。'],note='富豪与精华二选一；两条路线升黄后都先验收，再决定是否补第4条。',next='rare-review')
        dec={'id':'essence-choice','title':'蓝装两条：先选精华或富豪，暂不点材料','before':g['start'],'action':[g['choice'],'上方表格点“选择这颗的升黄步骤”，或点击下方“选择富豪随机分支”。两者只做一条。'],'expect':'仍保持蓝装；这一步只决策，不消耗材料。','good':'精华能补当前缺口且条件合法才选；没有适合精华可选富豪，也可直接使用蓝装。','bad':g['stop'],'materials':[],'refs':[AUTHOR,GGG],'kind':'decision','next':None,'choices':[{'id':'regal','label':'选择富豪随机分支'},{'id':'check','label':'先不投入，查看验收'}]}
        ess={'id':'essence','title':'已选精华分支：核对后只升黄一次','before':'必须先从本页部位表选择具体精华；备用装备已鉴定、未腐化／镜像、当前为魔法蓝装，两条词缀值得保留，目标词缀能合法添加。','action':['在本页表中选择明确的精华后，核对背包物品与此处名称完全一致。','使用前确认没有冲突词缀组；右键该精华，再左键备用蓝装一次；不要先用富豪，也不要连续点。'],'expect':'蓝装升级为黄装，保留原有词缀并新增对应精华词缀；以实际物品分组和数值为准。','good':'确认精华词缀与预期一致、原有好属性仍在。先比较整件是否足够用，再看黄装验收。','bad':'不能使用、缺失选择、效果不是当前需要，或已经升黄：立刻停，不换另一颗蓝装升黄精华继续点。','materials':[],'refs':[GGG],'kind':'action','next':'rare-review','note':'这是普通升黄分支；不能把完美／特殊精华放进这里。'}
        review={'id':'rare-review','title':'升黄后先验收：停手或补词缀','before':'本次精华或富豪已完成，装备已是黄装；重新核对词缀总数、前后缀和后续工艺预留。','action':['已明显改善当前短板：直接去品质、插槽与换装验收；不强迫加满6条。','愿意继续且普通黄装确有3条、目标侧仍有合法空位、没有渎灵等预留要求：选择下方补第4条。'],'expect':'不会自动接富豪、第二颗升黄精华或随机删除。','good':'确认预算与空位后，才进入对应黄装补词缀步骤。','bad':'有高级工艺预留、特殊容量、目标侧已满或新词缀不符合预期就停止。','materials':[],'refs':[AUTHOR,GGG],'kind':'decision','next':None,'choices':[{'id':'check','label':'已经够用，去验收'},{'id':'exalt','label':'确认合法空位，再补第4条'}]}
        idx=next(i for i,x in enumerate(r['steps']) if x['id']=='regal');r['steps'][idx:idx]=[dec,ess,review]
        for ent in r['entries']:
            if ent['step']=='regal':ent.update(step='essence-choice',label='蓝装已有2条：先选精华或富豪')
        r['entries'][4:4]=[{'step':'essence','label':'已经选好具体精华：核对后升黄'},{'step':'regal','label':'明确不要精华：富豪随机升黄'},{'step':'rare-review','label':'刚升黄：先验收再决定'}]
        rec['changes'].append('R38：'+g['name']+'在升黄前接入逐颗精华选择，富豪为并列分支；升黄后先验收，不自动继续投入。')
    # Exact snapshot gem IDs, not a second edited build definition.
    gems=D['gems'];by_en={v['en']:k for k,v in gems.items()}
    active={
      'Ice Shot':('skill',9,None,'主技能与两个元技能内分别放一颗冰霜射击；不是一颗在三处同时镶嵌。'),
      'Snipe':('skill',3,None,'01–04首领技能；05原件已移除。不要和升华同中文名节点混淆。'),
      'Tornado Shot':('skill',11,None,'辅助输出机制；按原件完整连接，不只准备冰霜射击。'),
      'Ice-Tipped Arrows':('skill',5,None,'01–03原件使用；04起未记录。'),
      'Freezing Mark':('skill',7,None,'01–05单独施放；06改为内嵌主动，只读。作者01–05放武器组Ⅱ。'),
      'Barrage':('skill',5,None,'技能宝石，不是辅助；按阶段核对蓄能与冷却。'),
      'Pounce':('skill',3,None,'普通技能宝石，需要对应变形武器（Talisman，不是项链）；06只读才有。不是武器免费授予，也不是01–05必备。'),
      'Herald of Ice':('spirit',4,30,'需在技能界面启用；检查碎冰触发条件及实际精魂占用。'),
      'Combat Frenzy':('spirit',8,30,'01/02启用；03原件已由幽灵舞步替代，不把两者继续相加。'),
      'Ghost Dance':('spirit',4,30,'03起使用；需要与护盾／闪避防御配置相配合。品质／效率会改变实际预留。'),
      'Wind Dancer':('spirit',4,30,'04起使用；05起原件连接阿兹里的圣礼，可能改为生命预留，缺它不能沿用相同资源预算。'),
      'Mana Remnants':('spirit',4,30,'05起使用；需要生成并拾取残片，不是装上就无条件回蓝。'),
      'Mirage Archer':('meta',8,60,'精魂元技能，内嵌冰霜射击是主动宝石。品质／效率影响精魂；检查武器组与技能启用。'),
      'Mirage Deadeye':('granted',None,None,'锐眼升华授予的元技能；不刻印、不购买这个技能本身。其内嵌冰霜射击与辅助仍需另备。')
    }
    specials={
     "Garukhan's Resolve":dict(effect='对合适的自用攻击改变暴击判定，并将该技能暴击率上限限制为50%；不是“装上必暴”，也不是投射物分叉。',get='数据列定向来源：扎米尔，刀锋之主。需要取得实际掉落／成品，不在普通未切割辅助菜单刻印。',condition='要求等级65；只支持符合条件的自用攻击，不给幻影等代理技能照搬。05/06原件放主冰霜射击。',fallback='缺它时优先保留04的整套暴击连接（快速攻击II＋冻结等），不是随便换一颗就等价于05。',source=DB+'us/Garukhans_Resolve'),
     "Rakiata's Flow":dict(effect='所辅助技能的击中把敌人的元素抗性按正负反转处理；不是普通穿透或减抗的同义词。',get='数据列定向来源：马诺基，天命者。非普通刻印。',condition='05/06主冰霜射击使用；120%消耗倍率，需重新检查耗蓝。不能假定在所有抗性情景都相同增伤。',fallback='没有时维持04整套配置，先比较整套输出与供蓝；普通冰霜穿透不视为完全等价替代。',source=DB+'cn/Rakiatas_Flow'),
     "Atziri's Communion":dict(effect='将受支持持续技能的精魂预留改为生命百分比预留：精魂数值的66%作为生命百分比。不是免费启用。',get='数据列定向来源：阿兹里，红女王。非普通刻印。',condition='05/06连接风舞者；换上后检查生命实际预留及生存。不把所有常驻技能一起自动改掉。',fallback='缺它，风舞者仍走精魂预留；重新分配启用技能，不照抄有此辅助时的剩余精魂。',source=DB+'cn/Atziris_Communion'),
     "Khatal's Rejuvenation":dict(effect='拾取被辅助技能生成的残片后获得卡哈塔的复苏增益；未拾取时不能把增益当常驻。',get='数据列定向来源：扎米尔，刀锋之主。非普通刻印。',condition='只用于生成残片的技能；05/06连接魔力残片，仍要检查残片生成、拾取与增益触发。',fallback='缺它可保留原来的供蓝方案并暂空该辅助位，但不把缺失效果计入恢复能力，也不保证整套续航不变。',source=DB+'cn/Khatals_Rejuvenation'),
     "Dialla's Desire":dict(effect='被辅助技能＋1等级、＋5%品质，并改变消耗倍率；不代表整个人物所有宝石一起提高。',get='数据列全局掉落；不写固定首领或必掉概率。非普通刻印。',condition='05/06连接魔力残片。检查实际被辅助技能面板，不把效果加到主冰霜射击。',fallback='可先留空并按没有等级／品质加成的魔力残片核算；不声称普通辅助能完整复刻它。',source=DB+'cn/Diallas_Desire'),
     "Olroth's Conviction":dict(effect='给技能额外的符文结界（Runic Ward）消耗，并使其额外强化2次使用；需要相应符文结界资源。',get='数据列定向来源：畸变者；不要仅从宝石名字猜掉落首领。非普通刻印。',condition='仅06只读原件的弹幕连接；01–05没有，不纳入执行版毕业必备清单。',fallback='不迁入01–05；没有符文结界条件或06冲突未解决时，不按此连接执行。',source=DB+'cn/Olroths_Conviction')
    }
    info={}
    for k,g in gems.items():
        en=g['en'];m={'id':k,'zh':g['zh'],'en':en,'url':g['url'],'kind':'support','cutTier':None,'spirit':None,'condition':g.get('note','') or '在本页列出的技能位置镶嵌，并检查该技能标签、属性需求与实际孔位。','get':'使用符合刻印要求的未切割辅助宝石，选择完全相同名称与阶别；罗马数字不是材料等级。','level':'原件没有统一指定本体等级／品质；按角色属性、消耗与启用条件逐步提升。'}
        if en in active:
            kind,tier,spirit,condition=active[en];m.update(kind=kind,cutTier=tier,spirit=spirit,condition=condition,url=DB+'us/'+en.replace(' ','_'))
            m['get']='升华授予；这个技能本身不购买、不刻印。' if kind=='granted' else ('未切割精魂宝石' if kind in ('spirit','meta') else '未切割技能宝石')+f'：刻印菜单 Tier {tier} 起解锁；可用对应或更高等级材料，仍须满足角色与属性要求。'
        if en in specials:m.update(kind='lineage',get=specials[en]['get'],condition=specials[en]['condition'],url=specials[en]['source'],special=specials[en])
        if en=='Elemental Armament II':m.update(cutTier=2,get='未切割辅助宝石：对应刻印 Tier 2；必须选元素军械II，不自动升III。',condition='本构筑明确使用II。III有“不能施加元素异常状态”的限制，会破坏需要冻结等异常的使用场景。',url=DB+'us/Elemental_Armament_II')
        if en=='Elemental Focus':m['condition']='仅按原件放狙击／寒冰之捷等位置；不要从清单上拿去替换需产生冻结的主冰霜射击辅助。'
        info[k]=m
    stage_records={}
    for branch,stage in zip(D['branches'],D['stages']):
        ids=[];uses=defaultdict(list);chains=[];order=[]
        for s in branch['skills']:
            chain={'id':s['id'],'zh':gems[s['id']]['zh'],'parts':[]}
            for idx,p in enumerate([s]+s.get('support_skills',[])):
                k=p['id'];kind=info[k]['kind'];label=gems[s['id']]['zh']
                if k not in order:order.append(k)
                ids.append(k);uses[k].append(label+('（内嵌主动）' if idx>0 and kind=='skill' else ''))
                if idx>0:chain['parts'].append({'id':k,'zh':gems[k]['zh'],'embedded':kind=='skill','special':kind=='lineage'})
            chains.append(chain)
        counts=Counter(ids);rows=[]
        for k in order:
            rows.append({'id':k,'qty':counts[k] if info[k]['kind']!='granted' else 0,'occurrences':counts[k],'uses':uses[k]})
        stage_records[stage['id']]={'id':stage['id'],'label':stage['label'],'readonly':stage['readonly'],'rows':rows,'chains':chains,'counts':dict(counts),'gemTotal':sum(r['qty'] for r in rows),'types':sum(r['qty']>0 for r in rows),'baseSpirit':sum(info[s['id']]['spirit'] or 0 for s in branch['skills']),'sourceFile':branch['sourceFile'],'sha256':branch['sha256']}
    for i,(sid,s) in enumerate(stage_records.items()):
        prev=stage_records.get('e0'+str(i));s['changes']=[]
        if prev and not s['readonly']:
            for k in dict.fromkeys(list(prev['counts'])+list(s['counts'])):
                if info[k]['kind']=='granted':continue
                a=prev['counts'].get(k,0);b=s['counts'].get(k,0)
                if a!=b:s['changes'].append({'id':k,'before':a,'after':b,'delta':b-a})
    D['gemGuide']={'checked':DATE,'source':AUTHOR,'ruleSource':GGG,'lineageSource':DB+'cn/Lineage_Supports','info':info,'stages':stage_records,'specialIds':[by_en[x] for x in specials],
      'kinds':{'skill':'技能宝石（含内嵌主动）','spirit':'精魂技能宝石','meta':'精魂元技能宝石','support':'普通辅助宝石','lineage':'特殊／血脉辅助宝石','granted':'升华授予 · 不买宝石本身'},
      'notes':['清单统计当前阶段原件的完整配置，不是刚进异界就必须一次全部装齐；缺技能解锁、孔位、精魂或属性时先保留过渡配置。','同名宝石按不同镶嵌位置累加；从上一个阶段保留下来的宝石可以继续用，不需要每个阶段重新买一整套。','辅助名称里的II／III是辅助阶别，未切割宝石的刻印Tier和宝石本体等级是另一回事；不能简单把II理解为任意2级材料。','原件中的31–100等区间是角色显示区间，不是宝石等级。没有原件依据的20级／20品质不代填为作者要求。','下面的精魂是未计品质、效率与特殊辅助的基础值，只供逐技能核算；最终以游戏技能界面的实际预留为准。','所有连接沿用上传快照；本页只做准备清单和来源补充，没有改动BD，也不把06原件冲突解除。']}
    D['release']={'version':'R38','date':DATE,'basis':'R37.1 已取回上线包；新增九类精华执行分支与六阶段宝石清单','type':'保留原人物／异界／过滤器数据和金币修正；不代表用户站点已经部署或游戏实测'}
    return D
