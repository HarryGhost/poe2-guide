"""R23: atlas unlock guide and attributed, opt-in online source images.
The original game screenshots are NOT embedded or reconstructed. No generated tree edges.
Extends the R22 workbook; all existing character/build/filter content is retained.
"""
from pathlib import Path
import html, json, re
import endgame_r22 as core
ROOT = Path(__file__).resolve().parent.parent
DATE = '2026-09-28'
h = core.h
p = core.p
box = core.box
steps = core.steps
table = core.table
cards = core.cards
callout = core.callout
link = core.link

EXTRA_SOURCES = {
 'lazy': ('Lazy Exile：异界推进与分阶段原图', 'https://mobalytics.gg/poe-2/guides/endgame-atlas-progression-guide', '更新 2026-09-09；主树开荒/推进/成型截图。截图是作者方案，不是游戏逐点验证。'),
 'asmo': ('Asmodeus：开荒卡点与玩法选择', 'https://mobalytics.gg/poe-2/guides/endgame-progression-asmodeus', '更新 2026-06-13；只参考开荒思路。文中“秘藏无树”和旧要塞自动完成流程已被后续补丁覆盖。'),
 'fubgun': ('Fubgun：0.5 异界树与刷图方案', 'https://mobalytics.gg/poe-2/atlas-trees/fubgun-atlas-tree-strats', '更新 2026-09-10；使用原站方案切换器。成型方案不是 Early 第一颗点的教程。'),
 'lolabyss': ('Lolcohol：深渊任务入口', 'https://mobalytics.gg/poe-2/guides/abyss', '更新 2026-07-07；核对异界灵魂之井任务与原站入口截图，不把任务地图图当成天赋树图。'),
 'lolbreach': ('Lolcohol：裂隙任务入口', 'https://mobalytics.gg/poe-2/guides/breach', '更新 2026-07-09；任务地图截图用于识别据点，不证明人物的地图坐标完全相同。'),
}
core.SOURCES.update(EXTRA_SOURCES)
refs = core.refs
core.TABS = [('atlas-start','异界入门'),('atlas-unlock','前期解锁'),('atlas-images','加点图'),('atlas-passives','主树说明'),('atlas-activities','玩法与天赋'),('atlas-masters','大师选择'),('atlas-other','其他养成')]
TABS = core.TABS

IMAGES = [
 dict(id='main-early', title='① 主树开荒 · 先看这一张', kind='异界主树加点图', source='lazy', source_updated='2026-09-09',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Screenshot%202026-09-09%20195211.png', width=1000, height=559,
  use='刚进要塞、主树点数还少时。',
  read='从最下方起点看金色连线，再看作者红色 1 → 2 → 3 标记。数字是分阶段的目标顺序，不是只花三颗点；中间仍需前置小点。',
  limit='原作者从精华一侧向上走，再补地图供给。不要只找相似图标；在游戏内核对节点名、效果、连线和解锁条件。'),
 dict(id='main-progress', title='② 主树推进 · 点数增加后再看', kind='异界主树加点图', source='lazy', source_updated='2026-09-09',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Screenshot%202026-09-09%20155824.png', width=849, height=874,
  use='已经取得基础补图节点，向后续要塞任务推进时。',
  read='这张图展示作者往主树右侧继续扩展的结果，不是另一棵树，也不是新手一开始就要点满的图。',
  limit='图内未逐个展示多选项。增加怪物效能的效果会增加难度，本站建议打不稳时暂缓；不要把亮起的每个点当作立即必点。'),
 dict(id='main-late', title='③ 主树成型 · 作者保留未点的示例', kind='后期参考，不是开荒图', source='lazy', source_updated='2026-09-09',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Screenshot%202026-09-09%20164951.png', width=922, height=990,
  use='要塞推进和主要点数准备完成、开始研究具体刷图目标时。',
  read='金色为截图中已分配路线；红叉是原作者当时建议保留的位置，不是本站新增的禁点标记。',
  limit='原文对部分红叉的理由含特定刷法、当时的缺陷反馈和不确定判断。这里仅保留作者方案，不认定这些节点今天仍有缺陷，也不要求你永久不点。'),
 dict(id='hilda-first', title='大师识别 · 希尔达 Mighty Prey', kind='异界大师选项，不是人物技能', source='lazy', source_updated='2026-09-09',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Screenshot%202026-09-09%20135926.png', width=925, height=319,
  use='完成希尔达首个巨兽任务后，对照第一层大师选项。',
  read='截图用于找 Mighty Prey：给普通地图首领升级为强力地图首领的机会。先读英文与效果，不按中文名字猜图标。',
  limit='它使用大师任务解锁，不消耗人物天赋点；截图不是整套四层大师最终方案。'),
 dict(id='abyss-entry', title='深渊解锁 · 异界灵魂之井', kind='任务入口图，不是加点图', source='lolabyss', source_updated='2026-07-07',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Well_of_Souls_Endgame.png', width=1000, height=859,
  use='决定先学深渊、需要开始深渊自己的任务线时。',
  read='找 The Well of Souls。这里是异界上的任务据点，不是让你返回剧情第二章。',
  limit='截图只说明入口形态和名称；地图生成布局可能不同，不照抄相对坐标。'),
 dict(id='breach-entry', title='裂隙解锁 · 据点任务地图', kind='任务区域图，不是加点图', source='lolbreach', source_updated='2026-07-09',
  url='https://cdn.mobalytics.gg/uploads/images/poe-2/Breach_Questline.png', width=1000, height=626,
  use='决定推进裂隙任务和它自己的天赋时。',
  read='从 Monastery of the Keepers 的任务进入周边裂隙区域，按任务完成地图。此图帮助识别任务区域。',
  limit='截图没有展示裂隙天赋的已选节点，不能拿它代替裂隙加点图。'),
]
IMG = {x['id']:x for x in IMAGES}

MECHANIC_GUIDES = [
 dict(id='abyss',name='深渊', choices=['Currency Abyss','Abyss Rares'], instruction='先看 Currency Abyss。Abyss Rares 是另一种奖励目标，不能把两张树混成同一套。', note='先做任务和低投入遭遇；作者成型碑牌与强度配置后面再抄。', source='fubgun'),
 dict(id='breach',name='裂隙', choices=['Breach Rares'], instruction='在 Atlas Tree Variants 切到 Breach Rares，再向下找到 Atlas Tree。', note='这是稀有怪刷图方案，不是裂隙任务第一颗点的教学。', source='fubgun'),
 dict(id='expedition',name='先祖秘藏', choices=['Expedition'], instruction='切到 Expedition，分别查看其树和配套地图/碑牌说明。', note='0.5.4 已新增独立树；宏大先祖秘藏任务首领奖励对应点数，不沿用“秘藏没有树”的旧文。', source='fubgun'),
 dict(id='ritual',name='驱灵仪式', choices=['Ritual Belts'], instruction='切到 Ritual Belts。', note='作者此变体针对腰带，不等于所有仪式奖励的通用开荒加点。', source='fubgun'),
 dict(id='delirium',name='惊悸迷雾', choices=['Deli Rush'], instruction='切到 Deli Rush，先读进入要求，再看树。', note='这是特定速刷目标，不是刚解锁涂膏就要照抄的高强度配置。', source='fubgun'),
 dict(id='temple',name='瓦尔神庙', choices=[], instruction='本次没有取得可靠的 0.5.5 神庙已分配整树截图。保留本站节点说明与 PoE2DB 节点资料。', note='不拿神庙房间布局、人物天赋或其他玩法的图冒充神庙天赋。', source='atlas'),
]
GUIDE = {x['id']:x for x in MECHANIC_GUIDES}

# Static visible content does not contact any third party. Loading a source image is explicit.
def figure(ident, compact=False):
 x=IMG[ident]; src=core.SOURCES[x['source']]
 return f'''<figure class="r23-figure {'r23-compact' if compact else ''}" id="{h(ident)}" data-r23-figure="{h(ident)}">
  <figcaption><span class="r23-label">{h(x['kind'])}</span><h3>{h(x['title'])}</h3><p><b>什么时候看：</b>{h(x['use'])}</p></figcaption>
  <div class="r23-picture" data-r23-frame>
    <div class="r23-online-note"><span class="r23-picture-word">原站截图</span><p>尚未联网加载 · 不是空白天赋树</p><button type="button" data-r23-load="{h(ident)}">联网显示这张原图</button><p class="small">图片来自 Mobalytics CDN；不会自动打开外站脚本。</p></div>
    <img data-r23-src="{h(x['url'])}" width="{x['width']}" height="{x['height']}" alt="{h(x['title']+'；'+x['read'])}" referrerpolicy="no-referrer" decoding="async" hidden>
  </div>
  <div class="r23-picture-actions"><button type="button" data-r23-zoom="{h(ident)}" disabled>放大查看</button><a href="{h(x['url'])}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">直接打开原图 ↗</a><a href="{h(src[1])}" target="_blank" rel="noopener noreferrer">作者攻略 ↗</a></div>
  <p class="r23-image-status" data-r23-status role="status">正文可离线读；这张原图需联网，未内嵌进整合包。</p>
  <div class="r23-reading"><p><b>怎么看：</b>{h(x['read'])}</p><p><b>不要误用：</b>{h(x['limit'])}</p></div>
  <p class="eg-ref">原图来源：{h(src[0])} · 原文更新 {h(x['source_updated'])} · 本次查看 {DATE}。原图未修改。</p>
 </figure>'''

def image_tools():
 return '<div class="r23-online-bar"><div><b>真实原图，按阶段看</b><p>文字和站内导航离线可用；图片需联网。先显示①，不必一次加载所有图。</p></div><button type="button" data-r23-load-all>联网显示本页全部原图</button></div>'

def modal():
 return '''<dialog id="r23-image-dialog" class="r23-image-dialog" aria-labelledby="r23-image-title"><div class="r23-viewer-head"><h2 id="r23-image-title">原图放大</h2><div><button type="button" data-r23-size="100">适应窗口</button><button type="button" data-r23-size="160">放大 1.6 倍</button><button type="button" data-r23-size="230">放大 2.3 倍</button><button type="button" data-r23-close>关闭</button></div></div><p class="small">放大后在图内横向、纵向滚动；按 Esc 关闭。原图未改动节点和连线。</p><div class="r23-viewer-scroll"><img id="r23-viewer-img" alt="" referrerpolicy="no-referrer"></div></dialog>'''

def head(current,title,sub):
 return core.header(current,title,sub).replace('ATLAS WORKBOOK / R22','ATLAS WORKBOOK / R23')

def nav_group(current): return core.nav_group(current)

def bridge(current):
 if current in ('equipment','e01','l06','roadmap','after-quests','rewards'):
  return '<div class="eg-bridge"><div><b>异界怎么玩、点数怎么拿？</b><span>先看解锁步骤，再对照原图；与人物 BD 分开。</span></div><div><a href="atlas-unlock.html">前期解锁 →</a><a href="atlas-images.html#main-early">开荒加点图 →</a><a href="atlas-activities.html">选择玩法 →</a></div></div>'
 if current in ('coverage','sources'):
  return '<div class="eg-bridge"><div><b>R23 新增：前期解锁与加点原图入口</b><span>主树截图、各玩法原站方案、版本差异分开说明；图片需联网，正文离线可读。</span></div><a href="atlas-sources.html#r23-scope">本轮范围与来源 →</a></div>'
 return ''

def pick_panel():
 return box('现在主玩什么：先推进，卡住再补装备',
  callout('本站给你的起步安排','先做要塞任务和地图供给；需要停下来补装备时，优先试<b>低投入深渊</b>，不喜欢再试裂隙。这是学习安排，不是锁定玩法，也不是“全社区公认最赚钱”。')+
  p('Asmodeus 的开荒思路重视深渊的通用材料；Lazy Exile 更强调先赶主线和点数。这两个建议可合成：<b>顺畅就推进，打不稳就停下来补强</b>。不用先同时完成六条任务线。')+
  p('Fubgun 的方案适合成型后选择收益目标。不要把多碑牌、高词缀地图和高强度迷雾的配置，直接搬到 Early。')+
  refs('asmo','lazy','fubgun'),'r23-main-choice')

def unlock_body():
 o=head('atlas-unlock','前期解锁：你下一张地图为什么打','先把入口、主树点、玩法点分清。这里不是人物技能加点，也不是要求你从此只玩一种玩法。')
 o+=cards([('atlas-unlock.html#r23-route','先做这些','主线解锁清单','完成一项，再看下一项；已经做过的跳过。'),('atlas-images.html#main-early','拿到点后','先看①开荒原图','主树的前期连线，和后期刷钱方案分开。'),('atlas-unlock.html#r23-main-choice','卡住怎么办','试低投入深渊','先能打完，再增加难度；随时可以换玩法。')])
 o+=box('“主玩一种”不是只能玩一种',p('异界是整体系统，普通地图是日常载体；裂隙、深渊等是地图里的额外内容，也有各自后续任务。<b>主玩深渊只表示你主要花时间刷它，不会把裂隙或神庙锁掉。</b>')+p('人物天赋、异界主树、各玩法专用点、大师任务选项分开；不要在人物升级界面找深渊点。主树普通分配与多选项切换也不同，没有把握的危险节点先留着。')+refs('p050'))
 o+=box('按你的当前进度继续，不必全部重做',steps([
  ('完成首张地图','完成地图首领后回去推进多里亚尼 / Farrow 对话，启用藏身处地图装置。已经正常从藏身处开图就跳过。'),
  ('希尔达首个巨兽任务','到 Hilda’s Campsite 接第一份任务；完成后看第一层 Mighty Prey，服务前期地图阶级推进。'+link('atlas-images.html#hilda-first','看选项原图。')),
  ('第一座先驱塔 → 远古之门','跟任务完成 Precursor Tower，再去 Ancient Gateway 进入要塞；不是在普通地图里无目标刷点。'),
  ('要塞地图 → 先补主树供给','朝 Burning Monolith 推进，取得主树点后先看开荒图①。前置小点、任务锁与地图条件按实际界面核对。'),
  ('东、西门 → 东、西 Enigma','先开两侧门，再做两侧任务碎片；两边做完回 Burning Monolith 推进灰烬仲裁者。指南示例门槛为门 T5+、Enigma T10+；进入前以任务面板要求为准。'),
  ('打不稳：暂停提高强度','缺伤害、经常倒地或没有图，就回能稳定完成的地图；试灵魂之井任务，补装备和材料，然后回来继续要塞。不要强行一路冲到 T15。'),
  ('后续：任务版与重复首领分清','推进起源塔等后续主线。0.5.5 中，非任务版起源核心的神性仲裁者击杀，才为地图拥有者完成整座要塞；不是首次任务击杀就全部给完。')]),'r23-route')
 o+=refs('lazy','asmo','p055')
 o+=pick_panel()
 o+=box('各玩法先到哪里找任务',table(['玩法','任务入口 / 识别名','现在要做多少'],[
  ('深渊','异界灵魂之井 / The Well of Souls','想补装备时先做；'+link('atlas-abyss.html#r23-picture-guide','入口图与加点方案')),
  ('裂隙','守护者修道院 / Monastery of the Keepers','作为另一种连续清怪体验；'+link('atlas-breach.html#r23-picture-guide','查看任务与方案')),
  ('迷雾','Withered Willow','先了解任务与涂膏解锁，不急着叠高强度。'),
  ('先祖秘藏','Ruins of Kingsmarch / Farrow 相关任务','后面再学宏大先祖秘藏；独立树来自任务首领。'),
  ('仪式 / 神庙','Caer Tarth / Lira Vaal','入口先知道，不要求本轮同时推进。')])+refs('lolabyss','lolbreach','lazy','p054'),'r23-entries')
 o+=box('到这里，前期的目标就明确了',core.checks('r23-unlock',['首张地图与藏身处地图装置已可用','希尔达第一任务已完成或已明确暂缓','已经知道第一座塔和要塞入口在哪里','拿到主树点时先查看开荒图①','打不稳时先补装备，没有一次叠多种强度','分清主树点、玩法点和人物点']))
 o+=box('旧攻略里这两处别照抄',p('Asmodeus 的文章早于 0.5.4：其中“先祖秘藏没有独立树”已过时；0.5.5 也改变了要塞自动完成条件。这里保留其学习思路，具体制度以对应补丁为准。')+refs('p054','p055'))
 return o+'</div>'

def guide_card(g):
 src=core.SOURCES[g['source']]
 label='打开 Fubgun 原站加点页' if g['source']=='fubgun' else '打开节点资料（不是已点截图）'
 variants=' / '.join(g['choices']) if g['choices'] else '已点整树截图：未取得'
 return f'''<article class="r23-guide-card" id="guide-{h(g['id'])}"><div><span class="r23-label">{h(g['name'])}</span><h3>{h(variants)}</h3></div><p>{h(g['instruction'])}</p><p class="r23-caution">{h(g['note'])}</p><div class="r23-picture-actions"><a href="{h(src[1])}" target="_blank" rel="noopener noreferrer">{label} ↗</a><a href="atlas-{h(g['id'])}.html#nodes">本站中文点序与前提 →</a></div><p class="eg-ref">互动树在原站查看；本站未将它保存成静态截图，也没有伪造导入码。</p></article>'''

def images_body():
 o=head('atlas-images','异界加点图：先看开荒，不先抄满树','真实作者截图、互动加点入口和中文说明放在一起。这里只收异界／玩法天赋，不收人物技能树。')
 o+=callout('你现在先看①','刚进入异界，先看下方<b>①主树开荒</b>。缺的是深渊／裂隙专用树时，跳到“各玩法加点入口”，不要拿主树图当子树。')
 o+=core.mini_nav([('main-early','①开荒'),('main-progress','②推进'),('main-late','③成型'),('r23-mechanics','各玩法原站树'),('hilda-first','希尔达选项')])
 o+=image_tools()
 o+='<div class="r23-gallery">'+figure('main-early')+figure('main-progress')+'</div>'
 o+=figure('main-late')
 o+=box('各玩法加点：去原站选对方案',p('Fubgun 页面上先找 <b>Atlas Tree Variants</b>，选择下面对应的英文标题，再往下看 <b>Atlas Tree</b>。这些是不同刷图目标，不是人物 BD 分支。')+p('本轮已核对页面列出的方案名称；互动树的全部已选节点和多选项未在本环境展开验收。<b>它们只作为原站查看入口，不冒充六份已验证的离线加点图。</b>')+'<div class="r23-guide-grid">'+''.join(guide_card(g) for g in MECHANIC_GUIDES)+'</div>'+refs('fubgun','atlas'),'r23-mechanics')
 o+=figure('hilda-first')
 o+=box('怎样对照，才不会点错',p('<b>先看阶段 → 再看树的名字 → 看起点和金线 → 核对节点效果 → 最后看多选项。</b>主树的红色编号不是总点数，后期红叉不是永久禁点。没有达到任务条件时先推进，不跨线点核心。')+p('截图只能显示作者当时的选点外观；图标不够清楚时打开原图，在游戏内看名称与效果。'+link('atlas-passives.html','本站主树说明')+'和'+link('atlas-activities.html','各玩法说明')+'是新手建议，不保证与作者高投入方案完全一致。'))
 o+=box('图片与版本状态',p('三张主树图和一张大师选项图来自 Lazy Exile 2026-09-09 的攻略；本次仅添加原图地址、出处和阅读说明，未改动原图。深渊／裂隙入口图分别放在对应玩法页。')+p('<b>原图需联网，当前整合包未含图片原始字节。</b>本次浏览检索可以打开原图；运行环境未能下载或联网渲染这些图片，故离线图片缓存与真实外站加载未验收。页面支持失败提示及直接打开原图，不会拿占位内容冒充成功。')+refs('lazy','lolabyss','lolbreach'))
 return o+modal()+'</div>'

def page_image_panel(kind):
 g=GUIDE[kind]
 body=guide_card(g)
 if kind=='abyss':
  body=p('从异界灵魂之井任务开始，普通地图里的深渊遭遇不等于已完成任务拿点。')+refs('lolabyss')+figure('abyss-entry',True)+body
 elif kind=='breach':body=figure('breach-entry',True)+body
 return box('看图找入口，再看本玩法的树',body,'r23-picture-guide')

def insert_after_header(body, extra):
 end=body.find('</header>')
 return body[:end+9]+extra+body[end+9:] if end>=0 else extra+body

def transform(rid, body):
 body=body.replace('ATLAS WORKBOOK / R22','ATLAS WORKBOOK / R23')
 if rid=='atlas-start':
  body=body.replace('选一种玩法深入','先体验，再决定主刷').replace('各玩法有自己的点数与任务，不是人物技能。','不是只能选一种；先推进要塞，卡住再补装备。')
  body=insert_after_header(body,cards([('atlas-unlock.html','接着上次的问题','前期具体先解锁什么','从首图、希尔达到要塞；已完成的步骤跳过。'),('atlas-images.html#main-early','有点数之后','查看带编号的开荒图','和高投入刷钱树分开，不混人物加点。')]))
 elif rid=='atlas-passives':
  body=insert_after_header(body,box('需要图片？先对照这张开荒原图',figure('main-early',True)+p(link('atlas-images.html','查看推进图、成型图与各玩法原站加点入口 →')),'r23-main-picture'))+modal()
  body=body.replace('未取得客户端坐标连线与逐点花费验证，因此不绘制伪装成实树的连线图','已加入作者真实截图；尚未取得客户端坐标连线与逐点花费验证，因此不自行编造连线图')
 elif rid=='atlas-activities':
  old='先把普通地图打稳。清群怪快、能保持移动，可从裂隙开始；更喜欢打完再挑奖励，可试驱灵仪式。先祖秘藏重在读符文；迷雾与深渊额外强度较多，先低投入熟悉。神庙是独立建设节奏，不必第一天硬追高阶布局。'
  new='先推进要塞和地图供给；需要补装备时优先试低投入深渊，不喜欢再试裂隙。主刷只表示主要花时间，不会锁住其他玩法。不要把成型刷钱树当开荒默认，也不用先完成六条任务线。'
  body=body.replace(old,new)
  body=insert_after_header(body,pick_panel()+p(link('atlas-images.html#r23-mechanics','看各玩法加点图／互动树入口 →')))
 elif rid.startswith('atlas-') and rid[6:] in GUIDE:
  body=insert_after_header(body,page_image_panel(rid[6:]))
  if rid[6:] in ('abyss','breach'):body+=modal()
 elif rid=='atlas-masters':
  body=insert_after_header(body,box('先认希尔达首任务选项',figure('hilda-first',True),'r23-hilda-picture'))+modal()
 elif rid=='atlas-sources':
  body=insert_after_header(body,box('R23 实际新增与未完成项',p('新增前期解锁页与加点图页，更新玩法选择口径；加入三张主树原图、一张大师选项原图、两张任务入口原图的联网查看控件，以及五类玩法的 Fubgun 原站方案入口。')+p('<b>六张图是原站引用，不是离线内嵌。</b>未取得神庙已分配整树截图，未在游戏验证逐点连线；Fubgun 互动树未导出或逐项核对。新手建议不是社区投票结论，也没有保证通货收益。')+p('原构筑、过滤器不改字节。原 R22 报告保留作历史记录；本次另见 '+link('data/R23验收记录.json','R23 验收记录')+'、'+link('data/R23图片与攻略来源.json','原图与攻略出处清单')+'。')+refs('lazy','fubgun','asmo','p054','p055'),'r23-scope'))
 return body

def pages():
 out=[(rid,title,transform(rid,body)) for rid,title,body in core.pages()]
 out.extend([('atlas-unlock','前期解锁与主刷建议',unlock_body()),('atlas-images','异界加点原图与方案入口',images_body())])
 return out

def search_entries():
 out=[]
 for rid,title,body in pages():
  # Keep attribution and image statuses out of the result snippets; targets remain precise.
  text=html.unescape(re.sub('<[^>]+>',' ',body))
  out.append(dict(title=title+' / R23异界工作区',text=text,url=rid+'.html'))
 for n in core.MAIN_NODES:
  out.append(dict(title='异界主树 / '+n['name'],text=' '.join(n.values()),url='atlas-passives.html#'+n['id']))
 for a in core.ACTIVITIES:
  for i,n in enumerate(a['nodes'],1):
   out.append(dict(title=a['name']+'天赋 / '+n['name'],text=' '.join(n.values()),url='atlas-'+a['id']+'.html#'+(n['id'] or 'node-'+str(i))))
 for x in IMAGES:
  dest='atlas-images.html#'+x['id']
  if x['id'] in ('abyss-entry','breach-entry'):dest='atlas-'+x['id'].split('-')[0]+'.html#'+x['id']
  out.append(dict(title='加点图片 / '+x['title'],text=x['kind']+' '+x['use']+' '+x['read'],url=dest))
 return out

def write_data():
 core.write_data()
 data=dict(version='C R23',checked_at=DATE,build_baseline='R22 / Fubgun 0.5.5',image_delivery='opt-in remote original URLs; NOT offline cached',image_assets_in_zip=False,images=IMAGES,mechanic_guides=MECHANIC_GUIDES,sources={k:dict(title=v[0],url=v[1],scope=v[2]) for k,v in EXTRA_SOURCES.items()},boundaries=['原图通过浏览检索查看，下载失败；包内无原图字节','新手路线不是玩家统计或作者毕业树','Fubgun互动树未导出、未逐节点验收','神庙已点整树图未取得','国服与游戏内未实测'])
 (ROOT/'data/R23图片与攻略来源.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
