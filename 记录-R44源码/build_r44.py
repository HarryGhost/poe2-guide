from pathlib import Path
import json,hashlib,re,shutil,sys
W=Path(__file__).parent
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else W/'base'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/poe2_Fubgun_C_R44')
if OUT.exists():raise SystemExit('输出目录已存在；拒绝覆盖。')
if OUT.resolve().is_relative_to(BASE.resolve()):raise SystemExit('拒绝嵌套输出。')
index=(BASE/'index.html').read_text(); assert 'capture43.' in index and 'localization44.' not in index
shutil.copytree(BASE,OUT)
sha=lambda b:hashlib.sha256(b).hexdigest()
app_path=re.findall(r'<script src="(assets/app[^\"]+)"',index)[0]
css_path=re.findall(r'<link[^>]+href="(assets/style[^\"]+)"',index)[0]
app=(BASE/app_path).read_text();needle="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';";assert app.count(needle)==1
app=app.replace(needle,(W/'extension_r44.js').read_text()+'\n'+needle)
css=(BASE/css_path).read_text()+'\n'+(W/'style_r44.css').read_text()
L=json.loads((W/'localization44.json').read_text());lj='window.FUBGUN_LOCALIZATION44='+json.dumps(L,ensure_ascii=False,separators=(',',':'))+';'
assets={}
for k,s in [('app',app),('style',css),('localization44',lj)]:
 ext='css' if k=='style' else 'js';p=f'assets/{k}.r44.{sha(s.encode())[:12]}.{ext}';(OUT/p).write_text(s);assets[k]=p
index=index.replace(css_path,assets['style']).replace(app_path,assets['app'])
index=index.replace(f'<script src="{assets["app"]}"></script>',f'<script src="{assets["localization44"]}"></script>\n<script src="{assets["app"]}"></script>')
index=index.replace('Build 用原名称','全身装备 · 中文名称').replace('Fubgun 冰射攻略 · R43','冰霜射击攻略 · R44').replace('FUBGUN / POE 2','冰霜射击 · 中文攻略').replace('0.5.5 · R43 原页采集核对','0.5.5 · R44 中文阅读')
(OUT/'index.html').write_text(index)
(OUT/'data/R44_localization.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
notes='''# R44｜中文名称与来源说明

当前默认阅读界面使用中文：构筑阶段、装备、人物珠宝、技能及辅助、镶嵌物、人物天赋、异界节点与大师选项。原名只在折叠来源、截图与原始文件中保留。

## 名称口径
本轮直接对照流亡2编年史的 /cn 简体游戏数据条目，补齐原来英文优先或混用英文的专名；已有中文词典用于其他正文术语。每条名称来源和核对状态保存在 data/R44_localization.json。

公开国服页面未能逐项取得，不能据此声称所有条目都已在腾讯国服客户端逐字实测。未把英文自行意译后假称国服官方名。构筑阶段和刷法标题属于网站阅读标签，不是游戏物品名称。

## 不改变的内容
原始构筑、四份现行原版过滤器、七份历史过滤器、采集数据、原始截图和R28档案保持原字节。范围、数值、配方、已选节点绑定、珠宝绑定和只读限制未因翻译而改变。

## 怎样看
完整解压后打开 index.html。默认直接阅读中文，不需要逐个切换语言。英文出处折叠保留；中文搜索已覆盖名称、镶嵌物、人物天赋和异界节点。页面底部“中文名称与来源”可核查出处。

先前的弓面板与保存字段差异、需求冲突、部分珠宝孔生效未确认，以及机器连线／逐级点序等限制仍保留。
'''
(OUT/'R44_中文名称与来源说明.md').write_text(notes)
(OUT/'00_先读我.md').write_text('# 冰霜射击攻略 · R44\n\n完整解压新目录，打开 index.html。\n\n正文默认中文；原文与证据折叠。四份现行原版过滤器没有修改。\n\n见 R44_中文名称与来源说明.md。\n')
(OUT/'README_上线.md').write_text('# R44 静态网站\n\n上传完整目录，保留相对路径。当前首页引用全新哈希资产；不要与旧版零散混用。\n\n没有替用户部署，游戏实测与国服逐字名称核验边界见 R44_中文名称与来源说明.md。\n')
(W/'build_paths.json').write_text(json.dumps({'site':str(OUT),**assets},ensure_ascii=False,indent=2))
print(json.dumps({'site':str(OUT),**assets},ensure_ascii=False,indent=2))
