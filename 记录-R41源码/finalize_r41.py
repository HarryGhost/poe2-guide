from pathlib import Path
import json, hashlib, shutil, re, zipfile, html as htmlmod
from urllib.parse import urlparse, unquote
W=Path('/mnt/data/work_R41');S=Path('/mnt/data/poe2_Fubgun_C_R41');B=W/'baseline';OUT=Path('/mnt/data')
A=json.loads((W/'atlas41.json').read_text());C=json.loads((W/'craft41.json').read_text());R=json.loads((W/'build_result.json').read_text())
def write(name,text):
 (S/name).write_text(text.strip()+'\n',encoding='utf-8');(OUT/name).write_text(text.strip()+'\n',encoding='utf-8')
craft='''# R41｜装备打造：按手中状态一步步做

日期：2026-10-03。以R40工程与用户Fubgun 0.5.5构筑快照为基础。本文是普通装备加工的操作解释；不是保证毕业的配方。

## 打开后先看哪里

全身装备目标 → 选择阶段与部位 → 装备目标 → 一步步做 → 换上前检查。

“投入与材料”标签已取消。剧情或普通补装可以直接打开“装备打造_一步步做.html”。先保留现用装备，使用备用件；不要为了跟步骤而处理唯一能用的物品。

## 先分清这次做什么

**过渡件／日常补装**：一次补一条当前缺的属性，够用就停。按手里实际白装、蓝装或黄装选择状态，不要求一定从白装做起。

**作者进阶配方**：按明确的底材、物等、已有词缀和配套条件开工。非暴击弓、暴击弓、护盾头、箭袋等各自独立；在作者配方里选步骤，不会因为点击一种普通精华就换成起步路线。需要改做过渡件，必须显式切换“这次要做哪一种”。

06实装冲突仍只读。暗金装备本身不套普通升黄流程；只有主动选择普通稀有替代时才进入相应模板。药剂、咒符、人物珠宝仍按各自规则。

## 普通装备：什么时候用什么

|手中状态|此时材料与操作|操作后怎么判断|
|---|---|---|
|未鉴定／不清楚|先确认实际稀有度、词缀组及能否佩戴，不点制作材料|数显性词缀组，不把固有、品质、符文或说明行数当词缀数量。|
|白装|合适且值得尝试的备用底材，用普通蜕变石一次|读新增属性；有用才继续，没用就停或换候选。|
|一词蓝装|可以直接穿；也可选择适用精华或富豪升黄。增幅只是另一个可选动作|先增幅会随机补第二条，不是精华的必需前置。|
|一／二词蓝装，选择精华|先选要补生命、抗性、物理点伤等哪一项，再看仅适用此目的的次级／普通／强效选项，最后只用选定的一颗|有合法空位、无同组冲突、材料允许且能穿再点。普通升黄精华只执行一次；不要先富豪再点它。|
|一／二词蓝装，选择富豪|只用富豪一次，随机新增一条并升黄|不保证补到指定属性；黄装颜色不是提升证明。|
|两词黄装|先比较是否已经可用；需要且符合前后缀容量、词缀组与预算时，才用普通崇高石尝试第三条|结果有用就验收；不满意不自动接混沌或剥离删改。|
|三／四／五词黄装|同样逐次验收，再决定是否用普通崇高石补一条|每次都允许停止，不强制填到六条。|
|六词普通黄装|停止普通加词流程|没有“补第七条”按钮；特殊改造不属于这里。|
|暗金、腐化、镜像或特殊受限状态|停止这个通用模板|按该物品明确规则或只读说明处理。|

这里的蜕变、增幅、富豪、崇高均指当前步骤写出的具体普通材料。不要把高阶材料的词缀限制、完美／特殊精华的删除替换工艺混进来。

## 一条可以从头走到尾的例子：已有移速的蓝鞋

前提：备用鞋上已有合用移速，没有同组生命词缀，当前缺生命，物品与材料提示允许，做完仍能穿。

选择鞋子 → 蓝装一条 → 补生命 → 次级身躯精华 → 只点一次。该档参考数据为增加30–39生命；这一步不补移速。结果应读成两词黄装后先比较，够用直接穿，不够且愿意继续才检查条件并尝试第三条。已有黄装不能回头再点这颗普通升黄精华。

没有身躯精华时，继续用好蓝鞋或比较掉落／商店；不是要求先去买齐材料。急速精华不是鞋子移速配方。

## 精华档位怎样选

短期过渡且次级数值已能解决缺口，先比较次级；底材值得继续使用、次级不足且普通档可用，再比较普通；明确需要更高结果、底材和预算都合格才比较强效。不是进异界自动全换强效，更不是“先把低阶合到最高”。适用部位会改变，例如戒指不能套用强效身躯。

选项只决定本次保证的对应词缀，不保证其余属性、最高掷值或制作总价。新加入的三种次级元素点伤精华只用于说明31级前的候选分支，数据掉落等级25，不能当16级必备；作者后期物理弓路线不能因此换料。

## 作者进阶路线：材料跟着步骤，不跨配方串用

|明确要做的配方|该配方蓝装升黄步骤|开始前关键区别|
|---|---|---|
|非暴击物理弓|强效磨蚀精华|先有合格物理提高前缀和后缀，并满足原配方底材、物等和词缀条件。|
|暴击弓|强效寻觅精华|加本地暴击率，不是先磨蚀再寻觅；同时核对暴击转型配套。|
|混合防御护盾头|强效增强精华|底材及已有平铺护盾符合配方；不在无护盾底材上凭空造护盾。|

每条路线逐步列“动作前／现在用什么／怎么操作／点完看什么／不符合时怎么办”。未满足原前提时停在检查步骤。亵渎、预兆、揭示等仍必须按该配方的实际条件执行，不能把一步看懂当成整件必成。

## 值得做吗：按部位看比较例子
'''
for slot,x in C['examples'].items():
 craft+=f"\n### {x['title']}\n\n{x['example']}\n\n{x['caution']}\n\n下一步：{x['next']}\n\n来源身份：{x['source']}\n"
craft+='\n## 依据与验证边界\n\n普通加工步骤为本站解释，作者专用路线保留来源身份；不是玩家装备扫描或收益测试。具体资料日期与0.5.5用户快照区分，游戏内适用性仍须核对。\n\n'
for url in C['sources']:craft+='- '+url+'\n'
craft+='- https://poe2db.tw/cn/Lesser_Essence_of_the_Body\n'
for x in C['extraEssences'].values():craft+='- '+x['url']+'\n'
write('R41_装备打造_按当前状态操作.md',craft)

atlas=f'''# R41｜异界大节点：点亮之后具体选什么

核对日期：{A['checked']}。入口：异界与产出 → 大节点选什么；七套方案与开荒加点图旁也有“大节点选哪项”标签。

## 先分清本表是什么

这里处理的是异界树上打开后还要选择一项效果的大节点，不是人物力量／敏捷／智慧节点，不是人物珠宝，也不是顶部大师配置。先解锁、点亮节点，再对照同名选项；一个节点的候选并非同时获得。

**{A['boundary']}**

覆盖范围：{A['scope']} 所有建议都是按当前装备备料或刷法目标整理的可选方案，不证明作者本人逐项如此选择，也不修改作者原图。多选节点可更换选项的规则与大师系统分开说明。

## 与装备制作直接对应的选择

|正在准备什么|在哪个节点选什么|不能混淆什么|
|---|---|---|
|非暴击物理弓|精华探源 → 磨蚀组|只是提高相应精华组出现的机会，不保证每图掉强效磨蚀。|
|暴击弓|水晶纹样 → 寻觅组|寻觅不在精华探源里。精华探源可另为其他装备选身躯；这不是暴击弓需要第二颗升黄精华。|
|混合防御护盾头|精华探源 → 强化／增强组；找相应底材可比较精良对手的智慧需求装备|不是直接提高人物智慧或护盾。|
|血脉辅助|森林专精与污秽宝藏中各选对应的血脉辅助项（已解锁且符合场景时）|不是未切割宝石，也不是人物天赋珠宝。|

## 已解锁六种地貌节点后的日常补装起点

下面是补装建议，不是Fubgun已确认实装；地貌、任务、区域等级必须同时满足。缺点继续原任务，不为本表绕路硬点。\n'''
for n in A['nodes']:
 if n['id'] in ['grass','desert','mountain','water','swamp','forest']:
  atlas+=f"\n**{n['name']}：{n['options'][n['pick']]}。** {n['why']} 变更时机：{n['change']}\n"
atlas+='\n## 分组详情\n\n每组默认以“日常补装”为起点。带成熟玩法名的变更只在配套齐、难度能承受时考虑；网页可切换目标后直接看到该项。以下为文字清单，不是额外天赋点或完整树坐标。\n'
profile_names={p['id']:p['name'] for p in A['profiles']}
for group in A['groups']:
 atlas+=f"\n### {group['name']}\n"
 for n in A['nodes']:
  if n['group']!=group['id']:continue
  atlas+=f"\n#### {n['name']}\n\n**日常补装建议：{n['options'][n['pick']]}。**\n\n前提：{n['gate']}\n\n原因：{n['why']}\n\n什么时候换：{n['change']}\n"
  shifts=[]
  for pid,ix in n.get('profiles',{}).items():
   if pid in profile_names:
    shifts.append(f"{profile_names[pid]}：{n['options'][ix]}")
  if shifts:atlas+='\n按目标变更：'+'；'.join(shifts)+'。\n'
  if n['id']=='essence':atlas+='\n暴击弓例外说明：本节点选身躯用于其他护甲的生命缺口，暴击弓的寻觅须在“水晶纹样”选择；两者不是对同一把弓连续点两颗精华。\n'
  atlas+='\n其他候选：'+'；'.join(x for i,x in enumerate(n['options']) if i!=n['pick'])+'。\n'
atlas+=f'''\n## 来源与边界\n\n官方说明用于多选节点可切换与大师系统分工：{A['official']}\n\n节点名称、候选效果及解锁条件：{A['source']}\n\nFubgun方案对照：https://mobalytics.gg/poe-2/atlas-trees/fubgun-atlas-tree-strats 。用户已保存的七套原图和配套记录仍按原文件阅读；本次未获取作者未展开选项的确切逐节点选择。\n\n当前数据与建议保存在data/R41-atlas-choices.json。未做游戏内点选、掉落收益或国服逐字名称实测。本表不是全游戏所有节点覆盖声明。\n'''
write('R41_异界大节点选择说明.md',atlas)

report='''# R41｜逐步打造与异界大节点：修改与检查

日期：2026-10-03。实际基线：R40完整交付包。此次修改网站流程，不修改原构筑、原技能或过滤器规则。

## 一、不是再追加“投入与材料”

单件页改成“装备目标／一步步做／换上前检查”。保持先看完整成品目标，再主动进入制作。普通补装和作者进阶配方分开，材料在具体操作步骤内出现，取消独立材料目录作为操作入口的做法。

普通补装按白装、蓝一词、蓝二词、黄二至六词和特殊状态分支；每次用一颗后先验收。一次只为一个目的选择适用精华；富豪是另一条升黄分支，增幅可选而非强制。一词蓝升两词黄后可继续比较是否补第三条，也可直接停手。没有强制做满六条或不满意就删改的连续操作。

作者非暴击弓、暴击弓、护盾头等有自己的起点与步骤；当前选择不会因为点击普通精华被偷偷换成起步路线。只读工艺、06冲突、暗金和特殊物品限制保留。

补充九类装备的具体比较例子；31级前加入三种有依据的次级元素点伤精华候选，说明掉落等级，不反写为16级必备或后期作者配方。并非整个精华库覆盖。

## 二、修复此前Review的实际流程问题

“这件怎么做”真正切换标签并保留部位、阶段；明确写01的成长入口固定去01，不受上次浏览05影响；专用配方不再混用通用次级材料表；补上两词黄装后续；更换部位和路线清除不合法材料状态。

旧tab=plan／steps链接兼容转到新步骤标签。药剂、咒符、人物珠宝与普通装备分开。特殊暗金目标不无条件套黄装工艺，武器组共用和独立配置的限制保留。

## 三、异界大节点不再只有亮点图

新增主树、精华与底材、六种地貌与城市及玩法树的30个相关多选节点。每条写建议选项、原因、解锁条件、改选时机与候选项。可以按普通补装、物理弓、暴击弓、护盾头及成熟刷法切换。

原七套方案改为加点原图／大节点选哪项／大师配置／地图碑牌／操作减配／来源记录，开荒页也有选项标签。不是继续把所有说明堆到加点图底部。

**明确边界：保存的作者截图没有展开这些选择，不能据此证明作者逐项选了什么。新增表是基于可核对节点效果的本站补充建议，不是作者实装恢复或原图改版。** 同时不把大师、人物珠宝或人物三属性混成这张表。

## 四、原版过滤器

现行下载页只提供01／02／03／04四份保存的原版快照，实际下载指向“原版过滤器_从这里选”。四份字节和原哈希一致，不修改颜色、声音、显示隐藏、底材、碎片或金币。

旧filters目录仍保留七份历史文件，含三个派生／补充版本，便于追溯；它们不再是当前下载推荐，也不能称为原版。旧补充版直达参数会显示说明后转到原版选项，不假冒原件。原版快照不代表已重新核实作者在线最新文件。

## 五、本轮实际检查

|项目|结果与范围|
|---|---|
|真实点击、状态选择与回归|86个检查通过、0失败；含目标转步骤、01固定跳转、蓝1→黄2→可补第3条、暴击弓专用材料、戒指限制、Atlas节点入口、全部7套来源页和原版过滤器下载。|
|页面视图扫描|388种视图，没有渲染异常、重复ID、失效data-scroll或桌面整页横向溢出。324个单件视图＋42个Atlas标签＋8节点组＋4开荒标签＋10其他页面。|
|宽度检查|关键制作／Atlas页面在390、768、1024、1440、1920宽度检查；属于上述交互检查范围，不另冒充游戏测试。|
|独立重建|从同一R40在独立输出目录重建，777个生成输出逐字节一致。此数不包含后加文档、源码副本、检查记录和最终清单。|
|原业务数据|既有顶层字段除release外均一致，新增内容另存craftGuide41与atlasChoices41；原配方原始记录、BD、技能、珠宝、异界原业务数据不回写。|
|原档案与过滤器|R28档案492份、旧filters中的7份均保持原字节；四份现行原版副本也与原件一致。|

这些计数是程序和页面检查，不是游戏实验数量，也不是“攻略已绝无遗漏”的依据。检查明细见R41检查目录。

### 失败尝试没有删掉

首次点击测试的内存副本添加虚拟base URL，导致原生hash链接跳向虚拟站点。移除测试副本的base后重跑，未为测试改写网站原生跳转。

第一次广泛视图扫描发现21个失效来源锚点视图（7套Atlas×3标签），原因是来源已挪入标签而旧入口仍滚动。实际修复来源链接为同方案来源标签，完整重跑扫描与点击检查。初次记录保留为view-scan-before-source-link-fix.json，不计为最终通过。

### 浏览器与游戏边界

真实尝试本地HTTP和file导航均被环境策略以ERR_BLOCKED_BY_ADMINISTRATOR阻止。最终点击／状态检查将实际生成的HTML/CSS/JS加载到about:blank内存文档，保留原生hash行为；不是用户域名或真实部署验收。截图为最终生成页面，没有用伪造游戏界面替代验证。

未执行游戏客户端点词、掉落、工艺收益、首领战或线上发布。未扫描用户角色。网页按钮是阅读步骤，不会执行游戏操作。

## 六、未在本轮解决的项目

完整中文人物天赋动态连线与合法逐级点序、06实装冲突、部分高风险工艺前提、所有辅助最低刻印Tier、国服逐项名称与实际游戏表现仍未完成。剧情旧详稿仍保留：本轮修了制作和选项路径，没有宣称已把全部剧情材料搬成一页完整任务线。已知三张Lazy旧图网络依赖仍在。

## 七、使用和维护

完整解压打开index.html；部署需保留所有相对路径和新哈希资源，不是只替换首页。当前清单SHA256SUMS_R41.txt；历史清单只作追溯。

R41维护源码中的build_r41.py接受完整R40目录和独立输出目录。不能用R37旧脚本覆盖当前包，也不能把R41再次当R40输入重复叠补。最终文档／检查／清单为发布收尾文件，与777份生成输出的独立重建统计分开。
'''
write('R41_修改与检查说明.md',report)

intro='''# 冰射攻略 R41

打开index.html。新版以R40为基础，实际修改装备制作流程及异界多选大节点说明。

先看全身装备目标，再进入某件“一步步做”。已取消“投入与材料”；普通补装与作者进阶配方分开。独立快捷入口：装备打造_一步步做.html；异界大节点_选什么.html。

过滤器只按原版使用：现行下载页提供四份保存的作者原版快照，文件也在“原版过滤器_从这里选”。不修改原版颜色、声音、金币、底材或碎片规则。旧filters目录含历史派生版，不能因编号01／03就当原版，不建议从该历史目录自行混选。

异界新增选项表是本站按目标整理的补充建议，不是作者截图已经确认的逐项选值。六份BD快照及原图未改；06仍只读。

见R41_装备打造_按当前状态操作.md、R41_异界大节点选择说明.md、R41_修改与检查说明.md。测试不等于游戏实测，也未部署用户网站。
'''
(S/'00_先读我.md').write_text(intro,encoding='utf-8')
(S/'README_上线.md').write_text(intro+'\n## 发布\n\n将解压后的完整目录放到静态网站发布目录，使index.html位于入口；需要全部相对路径资源。不要只覆盖首页。旧构筑与R28档案仍保存；游戏过滤器需要玩家主动选择，本网站不会切换游戏设置。\n\n当前校验清单为SHA256SUMS_R41.txt。原始过滤器是保存的快照，非宣称作者当前在线最新版。\n',encoding='utf-8')

maint=S/'R41维护源码';maint.mkdir(exist_ok=True)
for f in ['build_r41.py','additions41.js','additions41.css','craft41.json','atlas41.json','test_flows41.py','test_scan41.py','finalize_r41.py']:
 shutil.copy2(W/f,maint/f)
# Editorial JSON generator independent of prior workdir (content.json was unused).
edit=(W/'new_data.py').read_text().replace("W=Path('/mnt/data/work_R41');D=json.loads((W/'content.json').read_text())","W=Path(__file__).resolve().parent")
(maint/'new_data.py').write_text(edit)
(maint/'README.md').write_text('''# R41 维护

构建需要Python 3.10+，标准库即可。将完整R40解压到单独目录，运行：

```sh
python build_r41.py --baseline /path/to/R40 --output /path/to/new/R41
```

输出不得等于输入、在输入内或为输入父目录；现有输出目录会清空，务必指定独立可删除目录。输入必须是未叠补的R40。craft41.json和atlas41.json为新增编辑数据；new_data.py为其生成源。

该命令产生777份可重复的站点文件，不包含发布收尾时添加的说明、维护源副本、检查副本与最终校验清单。finalize_r41.py是本次发布环境的收尾脚本，含/mnt/data路径，换机器须先调整目录，不能不看直接执行。

测试需要Node、Python Playwright及Chromium。test_flows41.py、test_scan41.py保留本次/mnt/data/work_R41检查环境路径和/usr/bin/chromium位置；换机器须设置相同工作目录或修改W与浏览器位置。content.json为输入R40数据的提取，build_result.json由构建脚本生成。真实网站部署应另做网络导航检查，内存文档验证不替代上线。

不要覆盖或重新生成任何原版.filter内容。新增Atlas建议另存字段，不得写回作者原图选值。
''',encoding='utf-8')
checks=S/'R41检查';checks.mkdir(exist_ok=True)
for p in (W/'checks').iterdir():
 if p.is_file():shutil.copy2(p,checks/p.name)
nav=json.loads((W/'test/smoke.json').read_text())['navigation']
(checks/'真实导航限制.json').write_text(json.dumps(nav,ensure_ascii=False,indent=2))
shutil.copy2(W/'build_result.json',checks/'当前构建资源.json')

# Check preserved archive/file bytes after documentation updates.
protected={}
for folder in ['R28原站','filters']:
 fs=[p for p in (B/folder).rglob('*') if p.is_file()]
 bad=[str(p.relative_to(B)) for p in fs if (S/p.relative_to(B)).read_bytes()!=p.read_bytes()]
 assert not bad,(folder,bad)
 protected[folder]={'files':len(fs),'changed':bad}
changes=[];same=0
for p in B.rglob('*'):
 if not p.is_file():continue
 q=S/p.relative_to(B)
 if q.exists() and p.read_bytes()==q.read_bytes():same+=1
 else:changes.append(str(p.relative_to(B)))
assert sorted(changes)==sorted(['index.html','00_先读我.md','README_上线.md']),changes
# Actual resource references in current entry exist; all explicit local doc/newfilter refs from additions exist.
html=(S/'index.html').read_text();refs=re.findall(r'(?:src|href)=[\"\']([^\"\']+)[\"\']',html)
missing=[]
for ref in refs:
 if ref.startswith(('#','data:','http:','https:','mailto:','javascript:')):continue
 ref=unquote(urlparse(htmlmod.unescape(ref)).path)
 if ref and not (S/ref).exists():missing.append(ref)
assert not missing,missing
for f in ['R41_异界大节点选择说明.md','R41_修改与检查说明.md']:
 assert (S/f).exists()
report_protect={'baseline_files_unchanged':same,'baseline_files_modified':changes,'protected_folders':protected,'current_entry_missing_local_refs':missing,'current_assets':R}
(checks/'发布前原件与资源检查.json').write_text(json.dumps(report_protect,ensure_ascii=False,indent=2))

handoff='''# 冰射攻略｜R41 接续记录

2026-10-03；从实际R40增量构建。当前工程/mnt/data/poe2_Fubgun_C_R41/。

用户最新要求：装备打造不能让用户从材料表拼流程；取消“投入与材料”，按具体状态告诉什么时候用什么。异界大节点必须写出选择框内选哪项。过滤器严格保留作者原版，不再改颜色、声音或规则。

已实际完成：3标签装备页、普通白蓝黄状态完整出口、蓝1→黄2→第三条可选、作者专用配方材料不串线、完整目标按钮/01固定链接/失效来源链接修复、具体比较案例、3种前期元素精华候选；Atlas 30相关多选节点建议与原图旁标签；现行下载只提供四份原版。

边界：Atlas建议不是作者截图逐项选值恢复；原图没展示选框，不能推定精确作者配置。六份原BD、原工艺原记录、技能、珠宝、异界业务字段与原文件不改。06只读。R28档案492份、旧过滤器7份字节保持；四份原版副本逐字节核对。旧补充过滤器是历史资料，不能再推荐或称原版。

验证：86项点击与状态回归、388视图扫描完成；777生成输出独立重建一致。两次真实HTTP/file导航被环境阻止，最终交互使用真实生成HTML/CSS/JS内存文档，无虚拟base。保留首次测试副本base错误和初次21个来源锚点问题记录，修复后重跑。不是游戏实测或用户域名发布。

剩余：完整人物天赋动态连线及合法逐级点序、06冲突、部分高级工艺前提、辅助最低Tier全量核实、全剧情任务线彻底整合、国服/实战；三张Lazy历史图仍网络依赖。不能称整站绝无遗漏。

维护源码和新增数据在包内R41维护源码。后续从本实际R41继续；build_r41.py仅接受完整R40作为输入生成本版，不向R41反复叠加，也不用R37旧脚本回退。当前发布的文件及SHA-256见同目录发布核验JSON和ZIP交付链接。
'''
write('冰射攻略_接续记录_R41_20261003.md',handoff)
for src,dst in [('R41_过渡鞋子_具体操作_1440.png','R41_打造流程_预览.png'),('R41_异界大节点_地貌选择_1440.png','R41_异界大节点_预览.png')]:shutil.copy2(W/'checks'/src,OUT/dst)

# Manifest and final ZIP. Manifest self is intentionally excluded.
manifest=S/'SHA256SUMS_R41.txt'
paths=sorted([p for p in S.rglob('*') if p.is_file() and p!=manifest],key=lambda p:p.relative_to(S).as_posix())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest.write_text('\n'.join(sha(p)+'  '+p.relative_to(S).as_posix() for p in paths)+'\n',encoding='utf-8')
zip_path=OUT/'poe2_Fubgun_R41_逐步打造与异界大节点_上线包.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(S.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(S).as_posix())
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 rows=z.read('SHA256SUMS_R41.txt').decode().splitlines()
 for line in rows:
  digest,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
 names=z.namelist()
final={'date':'2026-10-03','archive':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':sha(zip_path),'archive_files':len(names),'manifest_entries':len(rows),'crc_ok':True,'all_manifest_hashes_match':True,'baseline_files_unchanged':same,'baseline_files_modified':changes,'protected':protected,'verification':'内存文档交互；非游戏/线上部署实测'}
(OUT/'R41_发布核验.json').write_text(json.dumps(final,ensure_ascii=False,indent=2));print(json.dumps(final,ensure_ascii=False,indent=2))
