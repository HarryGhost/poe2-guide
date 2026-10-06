#!/usr/bin/env python3
"""Apply R38 to a byte-verified R37.1 static website; no network or legacy rebuild.
Usage: python build_r38.py BASELINE_DIRECTORY OUTPUT_DIRECTORY
"""
from __future__ import annotations
import sys,json,re,hashlib,shutil
from pathlib import Path
from collections import Counter
from new_content import apply
HERE=Path(__file__).resolve().parent
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/冰射攻略_接续资料_20261002/网站_R37_1')
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/poe2_Fubgun_C_R38')
sha=lambda b:hashlib.sha256(b).hexdigest()
if OUT.resolve()==BASE.resolve() or OUT.resolve() in BASE.resolve().parents or BASE.resolve() in OUT.resolve().parents:raise SystemExit('Use distinct, non-nested baseline and output directories.')
index=(BASE/'index.html').read_text()
contentpath=re.search(r'src="(assets/content\.[^"]+\.js)"',index).group(1)
apppath=re.search(r'src="(assets/app\.[^"]+\.js)"',index).group(1)
csspath=re.search(r'href="(assets/site\.[^"]+\.css)"',index).group(1)
wrapped=(BASE/contentpath).read_text().strip()
D=json.loads(json.loads(wrapped.split('textContent=',1)[1].rstrip(';')))
assert D['release']['version']=='R37.1', 'R37.1 baseline required'
assert sha((BASE/'filters/01_Fubgun_Early_Mapping_GoldFix_R37_1.filter').read_bytes())=='6064c1afe0ec9f548a6fbdf7164b802f378c3b322f6f4846d8012b7134123b95'
D=apply(D)
app=(BASE/apppath).read_text();css=(BASE/csspath).read_text()
changes=[]
def patch(old,new,count=1):
 global app
 actual=app.count(old)
 if actual!=count:raise ValueError(f'Expected {count} patch matches, got {actual}: {old[:110]}')
 app=app.replace(old,new);changes.append(old[:100])
patch("function recipeTable(r,entry='ready'){", "function recipeTable(r,entry='ready'){\n r=r38PrepareRecipe(r);")
patch('${esc(s.bad)}</div><details class="row-detail">', '${esc(s.bad)}</div>${r38RecipeChoices(r,s)}<details class="row-detail">')
patch('let block=select+routeEndState(selected,slot,isUnique||independent);', 'let block=select+routeEndState(selected,slot,isUnique||independent)+r38EssencePanel(slot,selected,isUnique||independent);')
patch("else if(page==='character'){body=character();group='character';crumb='人物配置与技能'}", "else if(page==='character'){body=character();group='character';crumb='人物配置与技能'}else if(page==='gems'){body=gemsPage();group='character';crumb='本阶段宝石准备清单'}else if(page==='special-gems'){body=specialGemsPage();group='character';crumb='特殊宝石与血脉辅助'}")
patch("character:[['character','当前阶段配置'],", "character:[['character','当前阶段配置'],['gems','需要哪些宝石'],['special-gems','特殊宝石单独看'],")
patch("['character','gear','item/bow'].includes(r)","['character','gems','special-gems','gear','item/bow'].includes(r)")
patch("function searchData(q){let data=[", "function searchData(q){let data=[...r38SearchEntries(),")
patch("main+=sec('char-skills','02','技能与辅助组合',`", "main+=sec('char-skills','02','技能与辅助组合',`<div class=\"actions gem-shortcuts\">${routeLink('gems','需要哪些宝石 · 按数量准备','btn',{stage:state.stage})}${routeLink('special-gems','特殊宝石：获取与替代','btn',{stage:state.stage})}</div>")
patch("R37.1 金币显示修正与全量提示 · 攻略与工具", "R38 精华步骤与宝石准备 · 保留金币修正")
patch("document.title=crumb+' · Fubgun 冰射攻略 · R37.1'", "document.title=crumb+' · Fubgun 冰射攻略 · R38'")
patch("window.scrollTo(0,0);closeNav();", "window.scrollTo(0,0);closeNav();r38AfterRender();")
patch("step:e.target.value,...(p.get('alternate')", "step:e.target.value,...(p.get('essence')?{essence:p.get('essence')}:{}),...(p.get('alternate')")
app+='\n'+(HERE/'additions.js').read_text();css+='\n'+(HERE/'additions.css').read_text()
# Avoid a stale essence id disappearing from an explicitly selected state route.
# The per-row selection buttons always carry the essence id; the generic state selector
# deliberately returns to an unselected state when no concrete material has been chosen.
content='document.getElementById("site-data").textContent='+json.dumps(json.dumps(D,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';\n'
newpaths=[]
for prefix,ext,text,old in [('content','js',content,contentpath),('app','js',app,apppath),('site','css',css,csspath)]:
 p='assets/'+prefix+'.'+sha(text.encode())[:12]+'.'+ext;index=index.replace(old,p);newpaths.append((p,text))
index=index.replace('R37.1：01过滤器复核、完整提示色与声音图例；装备、升华、人物和异界攻略保留。','R38：九类装备精华选择与六阶段宝石准备、特殊宝石单列；完整人物、异界和金币修正保留。')
index=index.replace('R37.1 过滤器复核与全量图例','R38 精华步骤与宝石准备').replace('冰射攻略 · R37.1','冰射攻略 · R38')
index=index.replace('搜索装备、材料或玩法','搜索装备、材料或宝石').replace('搜索装备、材料或异界方案…','搜索装备、精华、宝石或异界方案…')
if OUT.exists():shutil.rmtree(OUT)
shutil.copytree(BASE,OUT)
(OUT/'index.html').write_text(index)
for p,text in newpaths:(OUT/p).write_text(text)
# Keep baseline assets and previous checksums as explicitly historical records.
for name,route in [('需要哪些宝石_从这里打开.html','gems'),('特殊宝石_从这里打开.html','special-gems')]:
 (OUT/name).write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html#/{route}"><title>冰射宝石准备 R38</title><a href="index.html#/{route}">打开宝石清单</a></html>')
# Checklist is generated from the same unmodified connections as the UI.
G=D['gemGuide'];md=['# R38｜六阶段宝石准备清单','',f'核对日期：{G["checked"]}。连接来自用户上传的六份Fubgun 0.5.5原件；本清单未重编BD。','',
 '**不是每个阶段重新买一整套。下方是该阶段完整镶嵌数量，已有宝石可继续使用；只在新位置需要额外副本。**','',
 '蜃影神射是升华授予的技能，数量记为“不购买”；它的内嵌冰霜射击及辅助仍要另备。原件中的31–100等是角色显示区间，不是宝石等级。普通辅助的II/III不是未切割材料等级。','',
 '本体等级和品质原件没有统一指定，不自动填成20级20品质。下表也不是刚进异界立即必须拥有的最低门槛。','']
for s in G['stages'].values():
 md += ['## '+s['label']+('【只读，不按此执行转型】' if s['readonly'] else ''),'',f'完整配置：{s["types"]}种、{s["gemTotal"]}颗宝石（不含升华授予技能本身）。','']
 for kind,label in G['kinds'].items():
  rows=[r for r in s['rows'] if G['info'][r['id']]['kind']==kind]
  if not rows:continue
  md += ['### '+label,'','| 宝石 | 数量 | 镶嵌位置 |','| --- | ---: | --- |']
  for r in rows:
   g=G['info'][r['id']];md += [f'| {g["zh"]} / {g["en"]} | '+('不购买' if kind=='granted' else str(r['qty']))+' | '+'；'.join(r['uses'])+' |']
  md += ['']
 md += ['### 完整连接（保留原顺序）','','| 技能 | 内嵌主动与辅助 |','| --- | --- |']
 for c in s['chains']:md += ['| '+c['zh']+' | '+' → '.join(('【内嵌主动】' if p['embedded'] else '')+p['zh']+('【血脉】' if p['special'] else '') for p in c['parts'])+' |']
 md += ['',f'未计品质、预留效率与特殊辅助的基础精魂合计：{s["baseSpirit"]}。这不是实际门槛；05/06风舞者的阿兹里辅助会改变预留种类，必须重算实际生命与精魂。','']
 if s['changes']:
  md+=['### 相比上阶段的数量变化','','| 宝石 | 上阶段→本阶段 | 说明 |','| --- | --- | --- |']
  for c in s['changes']:md+=['| '+G['info'][c['id']]['zh']+f' | {c["before"]}→{c["after"]} | '+('新增'+str(c['delta'])+'颗' if c['delta']>0 else '减少相应镶嵌，保留旧宝石')+' |']
  md+=['']
 md+=['原件：`'+s['sourceFile']+'`；SHA-256：`'+s['sha256']+'`。','']
md+=['## 特殊／血脉辅助：用途、获取与过渡','', '01–04原件没有血脉辅助；05用前五种，欧罗什只出现在06只读原件。掉落来源不是必掉承诺，价格不在此固化。','']
for id in G['specialIds']:
 g=G['info'][id];x=g['special'];md+=['### '+g['zh']+' / '+g['en'],'', '**作用：**'+x['effect'],'','**获取：**'+x['get'],'','**条件：**'+x['condition'],'','**缺少时：**'+x['fallback'],'','来源：'+x['source'],'']
md+=['## 普通技能、精魂宝石的刻印与启用','']
for g in G['info'].values():
 if g['kind'] not in ['skill','spirit','meta','granted']:continue
 md+=['### '+g['zh']+' / '+g['en'],'',g['get'],'',g['condition']+(' 基础精魂：'+str(g['spirit'])+'；实际预留再计效率。' if g['spirit'] is not None else ''),'','来源：'+g['url'],'']
md+=['## 不要自动升错辅助','', '本构筑的元素军械用II；III有不能施加元素异常状态的限制。按原件留II，不默认高阶就是更适合。','', '元素集中保持原件镶嵌位置，不随便放进需冻结的主冰霜射击。','', '来源：https://poe2db.tw/us/Elemental_Armament_II','来源：https://poe2db.tw/us/Elemental_Armament_III','来源：https://poe2db.tw/us/Elemental_Focus','', '## 来源与范围','', 'Fubgun正文：'+G['source'],'官方辅助系统：'+G['ruleSource'],'血脉辅助分类：'+G['lineageSource'],'', '六份连接和数量经程序交叉核对；普通辅助逐颗的刻印材料最低Tier未全部重新审定，未核实处只写按对应菜单要求，不猜数值。国服名称、实际获取与游戏生效仍以客户端为准；本次未进行游戏实测。']
(OUT/'R38_六阶段宝石准备清单.md').write_text('\n'.join(md)+'\n')
(OUT/'data/R38-gem-guide.json').write_text(json.dumps(G,ensure_ascii=False,indent=2))
(OUT/'data/R38-essence-guide.json').write_text(json.dumps(D['essenceGuide'],ensure_ascii=False,indent=2))
(HERE/'data_r38.json').write_text(json.dumps(D,ensure_ascii=False))
readme='''# R38｜精华步骤与宝石准备

基线：已取回的R37.1金币修正上线包。本包可独立解压使用，不需要拿R37旧源码覆盖生成。

打开 index.html。页面仍是原五分区、雪白深栏与装备目标优先。

- 装备养成 → 单件：完整成品属性后，先看该部位精华表，再选“精华升黄”或“富豪随机升黄”；两条路线升黄后先验收。九类普通装备均有直接入口。
- 人物与技能 → 需要哪些宝石：选阶段看全部名称、颗数、镶嵌位置、获取、原件连法和阶段增减。
- 人物与技能 → 特殊宝石单独看：血脉辅助单列；特殊条件、获取方式与缺少时处理分开写。

R38_六阶段宝石准备清单.md 可独立阅读。

原六份BD、原过滤器、R37.1金币补充版及R28档案未改。06保留只读，不作为已经验证的第六步转型。

发布到静态站点时，上传本目录完整内容，让 index.html 在发布目录根部，保留所有相对路径。没有后端或构建命令要求。R38新增资产已使用新内容哈希文件名，避免旧缓存混用。不要只传一个index.html。

包内R37/R37.1名称的说明、脚本和校验清单属于原交付历史资料。当前整包校验以 SHA256SUMS_R38.txt 为准；旧清单不用于断言R38的首页／文件全集仍等于旧版。

本次不是实际游戏或用户域名的验收，也未替用户部署。具体检查结果与限制见R38_更新与检查说明.md。
'''
(OUT/'README_上线.md').write_text(readme);(OUT/'00_先读我.md').write_text(readme)
(OUT/'data/R38-build-patch.json').write_text(json.dumps({'baselineVersion':'R37.1','release':'R38','patchPoints':changes,'generatedAssets':[x[0] for x in newpaths],'originalConnectionsUnchanged':True},ensure_ascii=False,indent=2))
print(json.dumps({'output':str(OUT),'assets':[x[0] for x in newpaths],'counts':{k:(v['types'],v['gemTotal'],v['baseSpirit']) for k,v in G['stages'].items()}},ensure_ascii=False,indent=2))
