"""Incremental R43 publisher. Input R42 and capture are immutable; output must be new."""
from pathlib import Path
import json,hashlib,shutil,re,sys,argparse
W=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Build R43 into a NEW directory. R42, capture and filters remain untouched.')
parser.add_argument('output',type=Path)
parser.add_argument('--baseline',type=Path,default=W/'baseline')
parser.add_argument('--capture',type=Path,default=W/'capture/fubgun_capture_2026-10-05')
parser.add_argument('--overlay',type=Path,default=(W/'overlay43.json' if (W/'overlay43.json').exists() else W.parent/'data/R43_capture_overlay.json'))
a=parser.parse_args();BASE=a.baseline.resolve();CAP=a.capture.resolve();OUT=a.output.resolve()
if OUT==BASE or OUT.is_relative_to(BASE) or OUT==CAP or OUT.is_relative_to(CAP):raise SystemExit('Output must be outside source/capture directories')
if not (BASE/'SHA256SUMS_R42.txt').is_file():raise SystemExit('Need actual R42 baseline, not an older site')
if 'capture43.' in (BASE/'index.html').read_text():raise SystemExit('Do not apply R43 twice')
if not (CAP/'builds.json').is_file() or not (CAP/'atlas.json').is_file():raise SystemExit('Capture incomplete')
if OUT.exists():raise SystemExit('Output exists: use a new directory')
shutil.copytree(BASE,OUT);shutil.copytree(CAP,OUT/'采集证据_20261005')
(OUT/'R43维护源码').mkdir();(OUT/'R43检查').mkdir(exist_ok=True)
for f in ['prepare_r43.py','extension_r43.js','style_r43.css','build_r43.py','inspect_data.py','localization43.json','test_r43.py']:
 shutil.copy2(W/f,OUT/'R43维护源码'/f)
# Add only presentation data; original JSON fields and raw files remain preserved.
source=a.overlay.read_text(); data='window.FUBGUN_CAPTURE43='+source+';\n'; dh=hashlib.sha256(data.encode()).hexdigest()[:12];dp=f'assets/capture43.{dh}.js'; (OUT/dp).write_text(data)
(OUT/'data/R43_capture_overlay.json').write_text(source)
app=(BASE/'assets/app.e6b3f5c187d0.js').read_text(); boot="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';"
assert app.count(boot)==1
app=app.replace(boot,(W/'extension_r43.js').read_text()+'\n'+boot)
app=app.replace("crumb+' · Fubgun 冰射 · R42'","crumb+' · Fubgun 冰射 · R43'")
app=app.replace("version:'R42',created:","version:'R43',created:").replace('Fubgun_网页准备记录_R42.json','Fubgun_网页准备记录_R43.json')
# Correct breadcrumb on independent crafting routes as well as menu grouping.
app=app.replace("const labels={guide:'成长路线',gear:'装备与打造',character:'人物配置',atlas:'异界与产出',tools:'查询与下载'};", "if(['early-craft','craft-timing','supplies'].includes(page)||(page==='item'&&params.get('tab')&&params.get('tab')!=='target'))group='craft';const labels={guide:'剧情与资料',gear:'装备总览',craft:'装备打造',character:'人物配置',atlas:'异界攻略',tools:'剧情与资料'};")
ah=hashlib.sha256(app.encode()).hexdigest()[:12];ap=f'assets/app.r43.{ah}.js';(OUT/ap).write_text(app)
css=(BASE/'assets/style.4a5ca8ef8361.css').read_text()+'\n'+(W/'style_r43.css').read_text();ch=hashlib.sha256(css.encode()).hexdigest()[:12];cp=f'assets/style.r43.{ch}.css';(OUT/cp).write_text(css)
index=(BASE/'index.html').read_text().replace('assets/style.4a5ca8ef8361.css',cp).replace('assets/app.e6b3f5c187d0.js',ap)
index=index.replace(f'<script src="{ap}">',f'<script src="{dp}"></script><script src="{ap}">')
index=index.replace('Fubgun 冰射攻略 · R42','Fubgun 冰射攻略 · R43').replace('0.5.5 · R42 全站阶段路线','0.5.5 · R43 原页采集核对')
index=index.replace('<b>按阶段，顺着做</b>全身目标 → 技能 → 打造 → 下一步。<br>人物珠宝与技能宝石分开。','<b>装备一页看全</b>Build 用原名称。<br>天赋、异界、打造分别阅读。')
index=index.replace('Fubgun冰射攻略R42：剧情至异界同阶段整套目标、技能、逐步打造、材料预留与转换条件，原版过滤器保持。','Fubgun冰射攻略R43：六套原名build的一页式完整装备、珠宝与镶嵌；人物天赋、异界已选项和打造分开。原版过滤器未修改。')
(OUT/'index.html').write_text(index)
# Shortcuts resolve to the current site; no raw original is changed.
for name,url in [('全身装备_从这里打开.html','#/gear?stage=e01'),('原页核对与差异_从这里打开.html','#/tools/capture-audit'),('人物天赋与切换_从这里打开.html','#/character?stage=e01&tab=tree')]:
 (OUT/name).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fubgun R43</title><a href="index.html'+url+'">打开当前攻略</a><script>location.replace('+json.dumps('index.html'+url)+');</script></html>')
(W/'build_paths.json').write_text(json.dumps({'site':str(OUT),'app':ap,'data':dp,'css':cp},ensure_ascii=False,indent=2))
print(OUT,ap,cp,dp)
