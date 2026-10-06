"""R44 -> R45 incremental build; stdlib only, never writes input files."""
from pathlib import Path
import sys,re,hashlib,shutil,json
W=Path(__file__).resolve().parent
if len(sys.argv)!=3: raise SystemExit('用法：python build45.py 完整R44目录 全新输出目录')
B=Path(sys.argv[1]).resolve();O=Path(sys.argv[2]).resolve()
if O.exists() or O.is_relative_to(B) or B.is_relative_to(O): raise SystemExit('拒绝覆盖或嵌套输入输出。')
idx=(B/'index.html').read_text()
if 'localization44.' not in idx or 'guide45.' in idx:raise SystemExit('只接受独立的完整R44基线。')
app=re.search(r'<script src="(assets/app[^\"]+)"',idx)[1];style=re.search(r'<link[^>]+href="(assets/style[^\"]+)"',idx)[1]
s=(B/app).read_text();n="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';"
assert s.count(n)==1
s=s.replace(n,(W/'extension45.js').read_text()+'\n'+n)
css=(B/style).read_text()+'\n'+(W/'style45.css').read_text()
g=json.loads((W/'guide45.json').read_text());data='window.FUBGUN_GUIDE45='+json.dumps(g,ensure_ascii=False,separators=(',',':'))+';'
shutil.copytree(B,O)
assets={}
for k,v in [('app',s),('style',css),('guide45',data)]:
 path='assets/'+k+'.r45.'+hashlib.sha256(v.encode()).hexdigest()[:12]+('.css'if k=='style'else'.js')
 (O/path).write_text(v);assets[k]=path
idx=idx.replace(app,assets['app']).replace(style,assets['style']).replace('<script src="'+assets['app']+'"></script>','<script src="'+assets['guide45']+'"></script>\n<script src="'+assets['app']+'"></script>')
idx=idx.replace('R44 中文阅读','R45 配装指导修复').replace('攻略 · R44','攻略 · R45')
(O/'index.html').write_text(idx)
(O/'data/R45_selection_guide.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
(O/'00_先读我.md').write_text('# 冰霜射击攻略 · R45\n\n完整解压到新目录，打开 index.html。\n\n全身装备直接看面板、可用底材与替代；制作、天赋、异界独立。长篇指导在对应部位内，不再让读者拼材料表。\n\n只使用“原版过滤器_从这里选”或当前网页原版下载；原文件没有改动。历史派生文件只作追溯。\n\n见 R45_修改与检查说明.md。\n')
(O/'README_上线.md').write_text('# R45 静态网站\n\n上传完整目录，保留相对路径和新哈希资源。不要只换首页或混拼旧版。无后端，不需要安装运行依赖。\n\n本包没有自动部署；网页勾选是阅读记录，不是游戏角色存档。原版过滤器不自动切换。\n\n国服逐项名称和游戏实测边界见本版说明。\n')
(W/'build_paths.json').write_text(json.dumps({'site':str(O),'baseline':str(B),**assets},ensure_ascii=False,indent=2))
print(json.dumps({'site':str(O),**assets},ensure_ascii=False,indent=2))
