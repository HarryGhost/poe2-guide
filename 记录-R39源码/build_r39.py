#!/usr/bin/env python3
"""Apply passive-tree jewel guide to a complete R38 site without a legacy rebuild.
Usage: python build_r39.py BASELINE_R38 OUTPUT_R39
"""
from __future__ import annotations
import sys,json,re,hashlib,shutil
from pathlib import Path
from jewel_content import make_guide,markdown
HERE=Path(__file__).resolve().parent
B=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/r38_baseline')
O=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/poe2_Fubgun_C_R39')
if B.resolve()==O.resolve() or B.resolve() in O.resolve().parents or O.resolve() in B.resolve().parents:raise SystemExit('Baseline and output must be separate non-nested directories')
sha=lambda b:hashlib.sha256(b).hexdigest()
index=(B/'index.html').read_text();paths={k:re.search(p,index).group(1) for k,p in {'content':r'src="(assets/content\.[^"]+\.js)"','app':r'src="(assets/app\.[^"]+\.js)"','site':r'href="(assets/site\.[^"]+\.css)"'}.items()}
wrapped=(B/paths['content']).read_text().strip();D=json.loads(json.loads(wrapped.split('textContent=',1)[1].rstrip(';')))
assert D['release']['version']=='R38','Use the complete delivered R38 baseline.'
assert sha((B/'filters/01_Fubgun_Early_Mapping_GoldFix_R37_1.filter').read_bytes())=='6064c1afe0ec9f548a6fbdf7164b802f378c3b322f6f4846d8012b7134123b95'
D['jewelGuide']=make_guide(B,D)
D['release']={'version':'R39','date':'2026-10-02','basis':'R38；纠正人物天赋珠宝与技能宝石的混淆，增加人物珠宝与特殊人物珠宝清单','type':'保留原BD、技能连接、精华执行分支、异界和R37.1金币修正；不是游戏实测或用户域名部署'}
app=(B/paths['app']).read_text();css=(B/paths['site']).read_text();patches=[]
def patch(old,new,count=1):
 global app
 n=app.count(old)
 if n!=count:raise AssertionError(f'Expected {count} occurrences, found {n}: {old[:100]}')
 app=app.replace(old,new);patches.append({'old':old,'new':new,'count':count})
patch("else if(page==='gems'){", "else if(page==='jewels'){body=jewelsPage();group='character';crumb='人物天赋珠宝清单'}else if(page==='special-jewels'){body=specialJewelsPage();group='character';crumb='特殊人物珠宝'}else if(page==='gems'){")
patch("character:[['character','当前阶段配置'],['gems','需要哪些宝石'],['special-gems','特殊宝石单独看'],", "character:[['character','当前阶段配置'],['jewels','人物天赋珠宝'],['special-jewels','特殊人物珠宝'],['gems','技能／辅助宝石清单'],['special-gems','血脉辅助（非天赋珠宝）'],")
patch("['character','gems','special-gems','gear','item/bow'].includes(r)","['character','jewels','special-jewels','gems','special-gems','gear','item/bow'].includes(r)")
patch("function searchData(q){let data=[...r38SearchEntries(),", "function searchData(q){let data=[...j39SearchEntries(),...r38SearchEntries(),")
patch("+treeNote,'',true);", "+treeNote+j39Bridge(),'',true);")
patch("let main=sec('item-target','01','成品应具备哪些属性'", "let main=(slot==='jewels'?j39Bridge():'')+sec('item-target','01','成品应具备哪些属性'")
patch("R38 精华步骤与宝石准备 · 保留金币修正", "R39 人物天赋珠宝 · 保留精华与金币修正")
patch("document.title=crumb+' · Fubgun 冰射攻略 · R38'", "document.title=crumb+' · Fubgun 冰射攻略 · R39'")
patch("crumb='本阶段宝石准备清单'", "crumb='技能／辅助宝石清单'")
patch("crumb='特殊宝石与血脉辅助'", "crumb='血脉辅助（非人物天赋珠宝）'")
# Specific presentation labels, not build data, are corrected. Routes remain compatible.
for old,new in [
 ("'需要哪些宝石 · 按数量准备'","'技能／辅助宝石 · 按数量准备'"),
 ("'特殊宝石：获取与替代'","'血脉辅助：获取与替代'"),
 ("'本阶段需要哪些宝石'","'本阶段技能／辅助宝石'"),
 ("'特殊宝石单独看'","'血脉辅助单独看'"),
 ("'人物与技能 / 宝石准备','这一阶段，需要哪些宝石？'","'人物与技能 / 技能宝石准备','这一阶段，需要哪些技能／辅助宝石？'"),
 ("'人物与技能 / 特殊宝石','特殊宝石，单独列清楚'","'人物与技能 / 血脉辅助','血脉辅助，单独列清楚'"),
 ("title:'这一阶段需要哪些宝石：完整准备清单'","title:'技能／辅助宝石：完整准备清单'"),
 ("title:'特殊宝石与血脉辅助单独列表'","title:'血脉辅助单独列表（非人物天赋珠宝）'"),
 ]:patch(old,new)
patch("+phaseNote(true)+r38GemTabs();", "+phaseNote(true)+note('本页是技能／辅助宝石，不是人物天赋树镶嵌的珠宝。 '+routeLink('jewels','查看人物天赋珠宝清单','text-link',{stage:state.stage}))+r38GemTabs();")
patch("+phaseNote(true)+r38GemTabs(true);", "+phaseNote(true)+note('血脉辅助装在技能连接中，不装进人物天赋珠宝槽。 '+routeLink('special-jewels','查看特殊人物珠宝','text-link',{stage:state.stage}))+r38GemTabs(true);")
patch("if(kind==='sources')return note(","if(kind==='sources')return note('<strong>R39 人物天赋珠宝：</strong>'+routeLink('jewels','清单、原件节点与来源','text-link',{stage:state.stage})+'；作者建议与实际插装分开。')+note(")
app+='\n'+(HERE/'additions.js').read_text();css+='\n'+(HERE/'additions.css').read_text()
wrapped='document.getElementById("site-data").textContent='+json.dumps(json.dumps(D,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';\n'
assets=[]
for k,ext,text in [('content','js',wrapped),('app','js',app),('site','css',css)]:
 path=f'assets/{k}.{sha(text.encode())[:12]}.{ext}';index=index.replace(paths[k],path);assets.append((path,text))
index=index.replace('R38：九类装备精华选择与六阶段宝石准备、特殊宝石单列；完整人物、异界和金币修正保留。','R39：人物天赋珠宝、特殊人物珠宝、六阶段孔位与目标词缀；保留精华、技能、异界及金币修正。')
index=index.replace('冰射攻略 · R38','冰射攻略 · R39').replace('R38 精华步骤与宝石准备','R39 人物天赋珠宝')
index=index.replace('搜索装备、材料或宝石','搜索装备、材料或珠宝').replace('搜索装备、精华、宝石或异界方案…','搜索人物珠宝、装备、精华或技能…')
if O.exists():shutil.rmtree(O)
shutil.copytree(B,O);(O/'index.html').write_text(index)
for p,t in assets:(O/p).write_text(t)
for name,route,title in [('人物天赋珠宝_从这里打开.html','jewels','人物天赋珠宝'),('特殊人物珠宝_从这里打开.html','special-jewels','特殊人物珠宝'),('需要哪些宝石_从这里打开.html','jewels','人物天赋珠宝'),('特殊宝石_从这里打开.html','special-jewels','特殊人物珠宝'),('技能辅助宝石_从这里打开.html','gems','技能／辅助宝石'),('血脉辅助_从这里打开.html','special-gems','血脉辅助')]:
 (O/name).write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html#/{route}"><title>{title} · R39</title><a href="index.html#/{route}">打开{title}</a></html>')
(O/'data/R39-jewel-guide.json').write_text(json.dumps(D['jewelGuide'],ensure_ascii=False,indent=2))
(O/'data/R39-build-patch.json').write_text(json.dumps({'version':'R39','baseline':'R38','generatedAssets':[p for p,_ in assets],'patches':patches,'immutableBusinessKeys':[k for k in D if k not in ['release','jewelGuide']]},ensure_ascii=False,indent=2))
(O/'R39_人物天赋珠宝清单.md').write_text(markdown(D['jewelGuide']))
readme='''# R39｜人物天赋珠宝与特殊珠宝

从已交付R38增量生成；不是用R37旧源码回退重建。本包完整解压即可用。

打开 index.html，保持原有全身装备目标首页、雪白深栏、五个主分区。

人物与技能 → 人物天赋珠宝：回蓝蓝玉、普通输出珠宝、六阶段孔位、按槽容量准备与镶嵌检查。
人物与技能 → 特殊人物珠宝：泉井之心与抗衡黑暗分别列词缀、限定数量、获取、半径与替代。
人物配置页的天赋段、旧的装备养成/天赋珠宝页均有直达入口。

R38误把“人物天赋的宝石”理解成了技能宝石。技能清单保留并明确改名，血脉辅助不再冒充特殊人物珠宝。
原“需要哪些宝石_从这里打开.html”和“特殊宝石_从这里打开.html”现指向用户真正所指的人物珠宝；技能页仍可从侧栏或新增的技能辅助/血脉辅助快捷文件进入。

六份原件只有珠宝槽记录，没有逐孔珠宝物品。01/02各2个不同槽；03/04/05各3个；06只读5个不同ID、6条记录，其中一个为武器组重复记录。节点数不是实装采购数，也不是已验证同时生效数量。页面里的阶段组合明确标为本站准备示例，不覆盖原构筑。

原始BD、技能连接、全部过滤器、R28档案492文件、R38九类精华执行分支和R37.1金币修正全部保留。

部署静态站点需上传完整目录，保留相对路径；没有后端或数据库要求。当前资产使用新哈希文件名，不只上传index.html。

当前清单：SHA256SUMS_R39.txt。R37/R37.1/R38说明、脚本与清单均保留为历史记录，不能用历史清单验证当前首页。
增量构建与检查源码见 R39维护源码。本轮未部署用户站点，也不代表游戏实测。具体结果见 R39_更新与检查说明.md。
'''
for name in ['00_先读我.md','README_上线.md']:(O/name).write_text(readme)
print(json.dumps({'output':str(O),'assets':[p for p,_ in assets],'counts':{k:[v['uniqueCount'],v['recordCount']] for k,v in D['jewelGuide']['stages'].items()}},ensure_ascii=False,indent=2))
