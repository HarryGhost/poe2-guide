#!/usr/bin/env python3
"""Build a standalone offline guide plus complete non-JS snapshot reference.
Run: python _source/build.py (Python 3.9+, standard library only).
No network calls, no third-party dependencies. Original .build files are not rewritten.
"""
from pathlib import Path
import json,html,hashlib,collections
P=Path(__file__).resolve().parent; SITE=P.parent
D=json.loads((P/'data.json').read_text(encoding='utf-8'))
# Fail rather than silently rebuild against changed or missing source snapshots.
if [b.get('number') for b in D.get('branches',[])] != list(range(1,7)):
 raise ValueError('Expected the six numbered source snapshots, 01 through 06.')
for b in D['branches']:
 raw_bytes=(SITE/b['download']).read_bytes()
 if hashlib.sha256(raw_bytes).hexdigest()!=b['sha256'] or json.loads(raw_bytes)!=b['raw']:
  raise ValueError('Source snapshot mismatch: '+b['key'])
 if [x['id'] for x in b['nodes']] != [x['id'] for x in b['raw']['passives']]:
  raise ValueError('Passive row order mismatch: '+b['key'])
(SITE/'数据').mkdir(exist_ok=True)
(SITE/'数据/六分支原始及中文映射.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(SITE/'数据/全部分支逐项差异.json').write_text(json.dumps(D['diffs'],ensure_ascii=False,indent=2),encoding='utf-8')
esc=lambda x:html.escape(str(x),quote=True)
NAV=[('从当前开始',[('start','阶段总览'),('upgrade','进阶条件与差异'),('skills','技能与精魂'),('gear','装备与独狼替代'),('tree','天赋与武器组'),('combat','实战与排障')]),('需要时查阅',[('craft','打造与涂膏'),('pitfalls','机制防坑'),('glossary','中英术语')]),('文件与依据',[('downloads','下载当前构筑'),('sources','来源与检查')])]
nav='';i=0
for group,links in NAV:
 nav+=f'<div class="nav-label">{group}</div>'
 for slug,title in links:
  i+=1;nav+=f'<a class="nav-link" href="#{slug}"><span class="nav-num">{i:02}</span>{title}</a>'
css=(P/'style.css').read_text(encoding='utf-8');js=(P/'app.js').read_text(encoding='utf-8');content=(P/'content.html').read_text(encoding='utf-8')
payload=json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
page=f'''<!doctype html>
<html lang="zh-CN" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="PoE2 0.5.5锐眼冰射：01到05按条件进阶，06实装快照独立核对；技能、装备、天赋、操作与下载全站同步。"><title>锐眼冰射 · 六分支进阶指南</title><style>{css}</style></head>
<body><a class="skip" href="#main">跳到正文</a>
<aside class="sidebar" id="sidebar"><button type="button" id="menu-close" class="icon-btn menu-close">关闭目录</button><a class="brand" href="#start"><span class="brand-mark" aria-hidden="true">↗</span><span><strong>冰射进阶</strong><small>锐眼 · 0.5.5 · 六分支</small></span></a><nav aria-label="章节导航">{nav}</nav><div class="side-foot">01 → 05 按条件进阶<br>06 单独查阅，不是下一阶段<br>资料快照：2026-09-24<br><button type="button" id="reset-checks" class="btn smallbtn subtle" style="margin-top:13px;color:inherit;border-color:#46616b">清除任务勾选</button></div></aside>
<div id="nav-mask" class="mask" aria-hidden="true"></div><div id="main-wrap" class="main-wrap"><header class="topbar"><div class="actions" style="margin:0"><button type="button" class="icon-btn menu-button" id="menu-toggle" aria-expanded="false" aria-controls="sidebar">目录</button><span class="chapter-chip"><span class="longcrumb">六分支进阶指南 / </span><b id="page-name">阶段总览</b></span></div><div class="top-actions"><button class="icon-btn" id="search-open" type="button">搜索 /</button><button class="icon-btn" id="theme-toggle" type="button">深色</button></div></header>
<div class="global-bar"><div class="global-fields"><label class="current-label"><span class="field-label">当前查看BD · 全站同步</span><select id="current-bd" aria-label="当前查看BD"></select></label><label><span class="field-label">长期目标 · 不切换当前</span><select id="target-bd" aria-label="长期目标"><option value="0">先把当前配好</option><option value="4">04 · 保留狙击</option><option value="5">05 · 高配冰射</option></select></label><label class="mode-label"><span class="field-label">装备获取</span><select id="mode" aria-label="装备获取方式"><option value="ssf">独狼 · 自己刷</option><option value="trade">可交易 · 按缺口买</option></select></label></div><div class="global-note" id="global-note">当前与目标分开，所有章节跟随同一个当前BD。</div></div>
<main id="main" class="main" tabindex="-1"><noscript><div class="notice warn">此主界面需要JavaScript。所有记录另有无脚本完整版本：<a href="六分支完整资料.html">打开六分支完整资料</a>。</div></noscript>{content}<footer class="footer">原始构筑：Fubgun；原站与补充映射：DSH；本版内容组织、代码与检查：GPT。<br>基于用户上传的0.5.5六份快照。PoE2DB为国际服简体资料，不是国服全量客户端验证。<br>全站本地运行；不使用账号、分析追踪或外部脚本。源码与记录可追溯。</footer></main></div>
<div id="search-mask" class="modal-mask" hidden><div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-title"><div class="search-head"><div style="flex:1"><label id="search-title" for="global-search" class="field-label">全站搜索</label><input id="global-search" type="search" placeholder="中文 / 英文 / ID" autocomplete="off"></div><button class="btn" type="button" id="search-close">关闭</button></div><div class="search-results" id="search-results" aria-live="polite"></div></div></div>
<dialog id="copy-dialog" style="border:1px solid var(--line);background:var(--panel);color:var(--text);border-radius:12px;width:min(600px,90vw)"><h3>浏览器限制自动复制，请手动复制</h3><textarea id="copy-text" class="copy-area" readonly aria-label="当前完整技能连接"></textarea><div class="actions"><button type="button" id="copy-close" class="btn">关闭</button></div></dialog>
<div class="toast" id="toast" role="status" hidden></div><script type="application/json" id="guide-data">{payload}</script><script>{js}</script></body></html>'''
(SITE/'index.html').write_text(page,encoding='utf-8')
# Non-JS reference retains all records, including their raw row ordering and scopes.
ref=[]
ref.append('<header><div class="eyebrow">ALL SIX SNAPSHOTS / 无脚本全量资料</div><h1>六分支完整资料</h1><p>这里没有筛选隐藏：六份原件的全部装备、技能与天赋记录按序列出。不是完整坐标树或已验证的逐级加点顺序。</p><p><a href="index.html">返回交互进阶指南</a> · '+' / '.join(f'<a href="#b{b["number"]}">{b["number"]:02} {esc(b["key"])}</a>' for b in D['branches'])+'</p></header>')
for b in D['branches']:
 n=b['number'];p=b['profile']
 ref.append(f'<section id="b{n}"><hr><div class="eyebrow">{n:02} / {esc(b["key"])}</div><h2>{esc(b["label"])}</h2><p>{esc(p["overview"])}</p><p><b>阶段：</b>{esc(p["stage"])}<br><b>目标：</b>{esc(p["goal"])}</p><div class="notice {"danger" if n==6 else ""}">{esc(p["note"])}</div><p><a href="index.html#skills?bd={n}">在主站查看本分支</a> · <a href="{esc(b["download"])}" download>原始文件{ "（只读）" if n==6 else ""}</a> · <a href="{esc(b["annotatedDownload"])}" download>中文提示</a></p>')
 ref.append('<h3>本阶段条件与获取方式</h3><p><b>独狼：</b>'+esc(p['ssf'])+'<br><b>可交易：</b>'+esc(p['trade'])+'</p><ol>'+''.join('<li>'+esc(x)+'</li>' for x in p['gate'])+'</ol>')
 ref.append('<h3>完整技能连接</h3>')
 for i,s in enumerate(b['raw']['skills'],1):
  g=D['gems'][s['id']]
  ref.append(f'<article class="panel" data-static-skill="{esc(s["id"])}"><h4>{i:02}. {esc(g["zh"])} / {esc(g["en"])}</h4><code>{esc(s["id"])}</code><ol>')
  for x in s.get('support_skills',[]):
   m=D['gems'][x['id']];role='〔内嵌主动〕' if x['id'].split('/')[-1].startswith('SkillGem') else ''
   interval=esc(x.get('level_interval','未填写'))
   ref.append(f'<li>{role}{esc(m["zh"])} / {esc(m["en"])}<br><code>{esc(x["id"])}</code><br><small>原件显示区间：{interval}</small></li>')
  ref.append('</ol><p class="small muted">角色显示区间：'+esc(s.get('level_interval','未填写'))+'；不是实际宝石等级。</p></article>')
 ref.append('<h3>完整装备记录</h3><div class="gear-grid">')
 for i,e in enumerate(b['equipment']):
  r=e['raw'];ref.append(f'<article class="gear-card" data-static-gear="{i}"><div class="gear-label">{esc(r["inventory_id"])} ({r.get("slot_x",0)},{r.get("slot_y",0)})</div><h4>{esc(e["zh"])} / {esc(e["en"])}</h4><p class="gear-text">{esc(e["translation"])}</p><p class="small muted">显示区间 {esc(r.get("level_interval","未填写"))}</p><details><summary>原始英文</summary><div class="detail-body"><pre>{esc(r.get("additional_text") or r.get("unique_name") or "未填写")}</pre></div></details></article>')
 ref.append('</div><h3>完整天赋记录</h3><p class="small muted">原行号保留；中文待核对不当国服正式名；不把记录数当实际用点。</p><div class="table-wrap"><table class="node-table"><thead><tr><th>原行号</th><th>范围</th><th>中文映射</th><th>原始ID</th><th>状态</th></tr></thead><tbody>')
 for x in b['nodes']:ref.append(f'<tr data-static-node="{esc(x["id"])}"><td>{x["row"]}</td><td>{esc(x["scope"])}</td><td>{esc(x["zh"])}</td><td><code>{esc(x["id"])}</code></td><td>{esc(x["status"])}</td></tr>')
 ref.append('</tbody></table></div><h3>当前操作说明</h3><ol>'+''.join(f'<li><b>{esc(t)}</b>：{esc(v)}</li>' for t,v in p['combat'])+'</ol><p class="small muted">原件SHA-256：<code>'+b['sha256']+'</code></p></section>')
ref.append('<h2>来源与边界</h2><p>'+esc(D['scopeNote'])+'</p>')
ref.append('<ol>'+''.join(f'<li>[{esc(s["id"])}] <a href="{esc(s["url"])}">{esc(s["title"])}</a> — {esc(s["note"])}</li>' for s in D['sources'])+'</ol>')
full='<!doctype html><html lang="zh-CN" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>六分支完整资料 · PoE2 0.5.5</title><style>'+css+'</style></head><body><main class="main">'+''.join(ref)+'</main></body></html>'
(SITE/'六分支完整资料.html').write_text(full,encoding='utf-8')
(SITE/'.nojekyll').write_text('',encoding='utf-8')
print(f'Built index.html {len(page.encode()):,} bytes; complete reference {len(full.encode()):,} bytes.')
