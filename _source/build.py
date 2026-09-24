#!/usr/bin/env python3
"""Build the offline site from local, reviewable sources (Python 3.9+; standard library only)."""
from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'index.html'

def main() -> None:
    data = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
    assert len(data['branches']) == 6, 'Six frozen source variants are required.'
    for b in data['branches']:
        assert len(b['nodes']) == len(b['raw']['passives']), b['key']
        assert len(b['equipment']) == len(b['raw']['inventory_slots']), b['key']
    nav_groups = [
        ('从现在开始', [('start','从这里开始'),('route','阶段路线'),('skills','技能怎么配'),('build','装备先换什么'),('tree','天赋与武器组'),('combat','实战与排障')]),
        ('需要时再看', [('craft','打造与涂膏'),('solo','独狼与交易'),('trap','机制与防坑'),('faq','新手问答')]),
        ('工具与依据', [('glossary','中英术语查询'),('dl','构筑文件下载'),('sources','来源与修正')])
    ]
    nav = ''
    for group, links in nav_groups:
        nav += f'<div class="nav-label">{group}</div>'
        for slug, title in links:
            nav += f'<a class="nav-link" href="#{slug}"><span class="nav-num" aria-hidden="true">{[s for _, ls in nav_groups for s, _ in ls].index(slug)+1:02}</span>{title}</a>'
    css=(ROOT/'style.css').read_text(encoding='utf-8')
    content=(ROOT/'content.html').read_text(encoding='utf-8')
    js=(ROOT/'app.js').read_text(encoding='utf-8')
    # Prevent user-supplied strings from closing the JSON script element.
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    page=f'''<!doctype html>
<html lang="zh-CN" data-theme="dark">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark light"><meta name="description" content="PoE2 0.5.5锐眼冰霜射击与狙击：新手阶段行动、固定分支技能、装备阶梯、独狼替代与逐条来源核对。"><title>锐眼冰射＋狙击 · 新手行动指南</title><style>{css}</style></head>
<body>
<a class="skip" href="#main">跳到正文</a>
<aside class="sidebar" id="sidebar"><button type="button" class="icon-btn menu-close" id="menu-close" aria-label="关闭章节导航">关闭目录</button><a class="brand" href="#start"><span class="brand-mark" aria-hidden="true">↗</span><span><b>冰射 · 狙击</b><span class="small">锐眼 / 0.5.5 快照</span></span></a><nav aria-label="主要章节">{nav}</nav><div class="side-foot"><b>固定主线，按条件养成。</b><br>04号保留狙击；06号已隔离。<br>资料核对：2026-09-24<br><button type="button" class="btn smallbtn subtle" id="reset-progress" style="margin-top:12px">清除勾选记录</button></div></aside>
<div class="mask-nav" id="nav-mask" aria-hidden="true"></div>
<div class="page" id="page-container"><header class="topbar"><button class="icon-btn menu-button" id="menu-toggle" type="button" aria-label="打开章节导航" aria-controls="sidebar" aria-expanded="false">目录</button><div class="crumb"><span class="longcrumb">新手行动指南 / </span><strong id="current-section">从这里开始</strong> <span class="badge" id="header-mode">独狼</span></div><div class="top-actions"><button class="icon-btn" type="button" id="search-open" aria-label="搜索全站内容">搜索 <span class="longcrumb" aria-hidden="true">/</span></button><button class="icon-btn" type="button" id="theme-toggle" aria-label="切换为浅色主题">浅色</button></div></header>
<main class="main" id="main" tabindex="-1"><noscript><div class="not-js">JavaScript未启用：正文仍可阅读，但阶段选择、筛选和计算工具不可用。原始主文件：<a href="Build-Fubgun/04_Crit_Hybrid.build" download>04 Crit Hybrid</a>；<a href="数据/六分支原始及中文映射.json" download>完整数据</a>。</div></noscript>{content}<footer class="footer">原构筑：Fubgun · 原站结构与补充词典：DSH · 本次重构、内容复核与测试：GPT。<br>基于用户上传的0.5.5快照；PoE2DB为国际服数据简体展示。游戏导入、完整天赋连线与全部国服译名尚未客户端验证。<br>纯静态、本地保存偏好；没有账号、分析追踪、CDN或联网接口。</footer></main></div>
<div class="modal-mask" id="search-mask" hidden><div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-title"><div class="search-head"><label class="small" id="search-title" for="global-search">全站搜索</label><input id="global-search" type="search" autocomplete="off" placeholder="中文 / 英文 / ID"><button class="icon-btn" id="search-close" aria-label="关闭搜索" type="button">关闭</button></div><div class="search-results" id="search-results" aria-live="polite"></div></div></div>
<div class="toast" id="toast" role="status" hidden></div>
<script type="application/json" id="guide-data">{payload}</script><script>{js}</script></body></html>'''
    OUT.write_text(page,encoding='utf-8')
    print(f'Built: {OUT.name} ({len(page.encode("utf-8")):,} bytes)')

if __name__ == '__main__':
    main()
