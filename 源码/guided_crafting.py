"""R9 step worksheets. Generates the front door and a complete no-JavaScript copy."""
from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/打造按步操作_R9.json').read_text())
def h(x):return html.escape(str(x),quote=True)
def j(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def link(url,label):return '<a href="'+h(url)+'" target="_blank" rel="noopener noreferrer">'+h(label)+' ↗</a>'
def matbtn(mid):
 m=DATA['materials'][mid]
 return '<button type="button" class="g-material" data-g-material="'+h(mid)+'">'+h(m['zh'])+' <span aria-hidden="true">?</span></button>'
def static_step(r,s,i):
 k='只读说明 · 不要照此环动手' if s['kind']=='boundary' else '可跳过' if s['kind']=='optional' else ''
 return '<section class="g-static-step" id="'+h(r['id']+'--'+s['id'])+'"><h3>'+str(i+1)+'. '+h(s['title'])+'</h3>'+('<p class="g-boundary">'+h(k)+'</p>' if k else '')+'<p><b>操作前：</b>'+h(s['before'])+'</p><ol>'+''.join('<li>'+h(a)+'</li>' for a in s['action'])+'</ol><p><b>点完看什么：</b>'+h(s['expect'])+'</p><p><b>结果符合：</b>'+h(s['good'])+'</p><p><b>不符合就停：</b>'+h(s['bad'])+'</p>'+('<p><b>材料：</b>'+ '；'.join(h(DATA['materials'][m]['zh'])+' / '+h(DATA['materials'][m]['en']) for m in s['materials'])+'</p>' if s['materials'] else '')+('<p class="small muted">'+h(s['note'])+'</p>' if s['note'] else '')+'<p class="small">'+ ' · '.join(link(u,'依据'+str(n+1)) for n,u in enumerate(s['refs']))+'</p></section>'
def all_body():
 o='<div class="g-intro"><span class="g-eyebrow">FUBGUN · EARLY 起步到高投入</span><h1>打造步骤 · 全部展开</h1><p>这是完整阅读版，不需要脚本、不按进度解锁。日常边玩边查，用<a href="craft.html">单步操作页</a>。所有示意都是教学状态，不读取你的装备。</p></div><nav class="g-all-index">'
 for r in DATA['routes']:o+='<a href="#'+h(r['id'])+'">'+h(r['title'])+'</a>'
 o+='</nav>'
 for r in DATA['routes']:
  o+='<article class="g-static-route" id="'+h(r['id'])+'"><header><h2>'+h(r['title'])+'</h2><p>'+h(r['goal'])+'</p><p class="small">'+h(r['sourceLabel'])+' · <a href="'+h(r['reference'])+'">完整原文/旧版解释</a> · <a href="craft.html#'+h(r['id'])+'">回单步查看</a></p></header><p><b>起点：</b>'+h(r['start'])+'</p>'
  o+=''.join(static_step(r,s,i) for i,s in enumerate(r['steps']))+'</article>'
 o+='<section id="materials" class="g-static-route"><h2>材料名称与作用</h2>'
 for m in DATA['materials'].values():o+='<div class="g-static-step" id="mat-'+h(m['id'])+'"><h3>'+h(m['zh'])+'</h3><p>'+h(m['en'])+'</p><p>'+h(m['effect'])+'</p><p class="small">'+h(m['check'])+' '+link(m['url'],'资料')+'</p></div>'
 return o+'</section>'
def body():
 d=DATA;r=d['routes'][0]
 return '''<div class="g-intro"><span class="g-eyebrow">FUBGUN · EARLY 起步到高投入</span><h1>打造不用一口气读完。<br class="g-mobile-only">现在只看这一步。</h1><p>选要做的装备，再选它现在的状态。网页只告诉你怎么做，不会操作游戏；全部步骤随时可看。</p></div>
 <div class="g-toolbar" aria-label="阅读方式"><a href="craft-steps-all.html">全部20条路线展开</a><a href="craft-advanced.html">作者8条进阶原文</a><a href="craft-reference.html">原Early逐部位说明</a><a href="craft-examples.html">看具体结果实例</a></div>
 <div id="g-root">
 <section class="g-selector" aria-label="选择打造任务">
  <label for="g-phase"><span>① 看哪个阶段</span><select id="g-phase">'''+''.join('<option value="'+h(p['id'])+'">'+h(p['name'])+'</option>' for p in d['phases'])+'''</select></label>
  <label for="g-route"><span>② 要做哪件装备</span><select id="g-route"></select></label>
  <label for="g-entry"><span>③ 手里的装备是什么状态</span><select id="g-entry"></select></label>
 </section>
 <div id="g-route-intro" class="g-route-intro"></div>
 <details class="g-help"><summary>我分不清白/蓝/黄装、前后缀、物品等级；先看这里</summary><div class="g-help-grid">
 <div><b>先按名称颜色选</b><p>白色＝普通；蓝色＝魔法；黄色＝稀有。暗金不走这些普通升色步骤。未鉴定先用知识卷轴。</p></div>
 <div><b>不是数文字行</b><p>普通蓝装最多2条随机词缀。把鼠标移到背包物品，按游戏提示的高级物品说明键（常见为Alt）查看；分开看前缀和后缀。复合词缀可能有两行。键位/界面不符时先查游戏设置，不能靠数行猜。</p></div>
 <div><b>物品等级不等于需求等级</b><p>工艺说“物品等级75”，不是你人物到75就算满足。高级说明里的物品等级影响词缀；能不能穿还要看人物等级和力量/敏捷/智慧。</p></div>
 <div><b>预兆与通货放的位置不同</b><p>预兆在人物背包里右键激活。通货通常右键后左键装备。“左旋/右旋”指词缀侧，不是让你换一个鼠标键。</p></div>
 </div><p class="small muted">这是国际服资料对应的功能说明，未逐屏验证国服菜单；没有看清状态，先不要点消耗材料。药剂/咒符、珠宝不套普通防具六词缀规则。</p></details>
 <div class="g-reading-bar"><b id="g-step-count"></b><span>按真实状态跳步；编号不是必须依次加工</span><button id="g-copy-route" type="button">复制本路线</button><button id="g-print-route" type="button">打印本路线</button></div>
 <nav id="g-step-nav" class="g-step-nav" aria-label="本路线全部步骤"></nav>
 <div id="g-main" class="g-main" aria-live="polite"></div>
 <div id="g-print-content"></div>
 <details id="g-full" class="g-full"><summary>展开当前路线的所有步骤 · 不删内容</summary><div id="g-full-content"></div></details>
 <div class="g-footnote"><p id="g-source-note"></p><p>绿色表示“结果符合时怎么看”，不是收益或成功率承诺。前提不符/结果不符先停，不用混沌或剥离盲目补救。</p><p>本次按步骤重写的是打造。其余R8配置原值保留；国服名称、天赋连线与实际游戏验证的既有边界仍在<a href="sources.html#limits">核对说明</a>。</p></div>
 </div>
 <noscript><p class="notice warn">当前单步导航需要JavaScript；所有正文都在<a href="craft-steps-all.html">无需脚本的完整操作页</a>，不需要联网。</p></noscript>
 <dialog id="g-material-dialog"><div class="dialoghead"><h2 id="g-material-title"></h2><button type="button" id="g-material-close">关闭</button></div><div id="g-material-body"></div></dialog>
 <dialog id="g-copy-dialog"><div class="dialoghead"><h2>复制操作清单</h2><button type="button" id="g-copy-close">关闭</button></div><p>自动复制不可用时，选中下方文本，按Ctrl+C。</p><textarea id="g-copy-text" rows="14" aria-label="操作清单文本"></textarea></dialog>
 <script id="guided-craft-data" type="application/json">'''+j(d)+'</script>'
