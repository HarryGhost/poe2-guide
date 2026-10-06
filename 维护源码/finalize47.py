from pathlib import Path
import json,re,hashlib,zipfile,shutil,subprocess,sys
W=Path(__file__).resolve().parent;cfg=json.loads((W/'build_paths.json').read_text());S=Path(cfg['site']);B=W/'r45'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(file):
 t=file.read_text();x=json.loads(t[t.index('=')+1:].strip().rstrip(';'));return json.loads(x)if isinstance(x,str)else x
C=load(S/cfg['capture43']);D=load(S/cfg['content']);G=load(S/cfg['guide45']);P=load(S/cfg['personal47']);OC=json.loads((W/'capture.json').read_text())
checks=[]
def ck(name,value):
 checks.append({'check':name,'pass':bool(value)})
 if not value:raise AssertionError(name)
ck('3 active character builds',[b['stage']for b in C['builds']]==['e04','e05','e06'])
ck('3 stage selector sources',[s['id']for s in D['stages']]==['e04','e05','e06'])
ck('3 branch downloads',[s['number']for s in D['branches']]==[4,5,6])
ck('character campaign removed from active selector',D['guide42']['campaign']==[])
ck('all 7 Atlas configuration objects equal original',C['atlas']==OC['atlas'] and len(C['atlas'])==7)
ck('221 author selections',sum(len(v['keystone_selections'])for v in C['atlas'])==221)
for key in ['atlasStarter','atlasUnlock','atlasChoices41','variants','atlasRecords','masterNodes','atlas_setup','atlas_gems']:
 original=json.loads((W/'D.json').read_text())[key];ck('Atlas retained: '+key,D[key]==original)
for b in C['builds']:
 original=next(x for x in OC['builds']if x['stage']==b['stage'])
 for key in ['jewels','passive_tree','skill_gems','author_text','treePriorities','notes']:
  ck(b['stage']+' source field '+key,b[key]==original[key])
 for it in b['equipment']:
  oi=next(x for x in original['equipment']if x['uid']==it['uid'])
  for key in ['panel','socketed_items','quality','anointment','sourcePanelCaution']:
   ck(b['stage']+'/'+it['uid']+'/'+key,it.get(key)==oi.get(key))
for p in (S/'原版过滤器_从这里选').glob('*.filter'):
 ck('Original filter unchanged '+p.name,h(p)==h(B/'原版过滤器_从这里选'/p.name))
ck('Only 4 filter files',len(list(S.rglob('*.filter')))==4)
for b in D['branches']:
 dest=S/b['download'];ck('Original build '+b['key'],dest.exists() and h(dest)==b['sha256'])
ck('Only 3 original build downloads',len([p for p in S.rglob('*')if p.is_file()and '.build'in p.name])==3)
for p in (B/'采集证据_20261005').rglob('*'):
 if p.is_file():ck('Source preserved '+str(p.relative_to(B/'采集证据_20261005')),h(p)==h(S/p.relative_to(B)))
# Compare original player text, not the outdated R46 scope configuration.
op=json.loads((W/'r46/Ghostliness_当前使用版_R46/data/当前使用内容.json').read_text())
for it in P['items']:
 oi=next(x for x in op['items']if x['id']==it['id']);ck('Player preserved '+it['id'],it['player']['raw_tooltip']==oi['player']['raw_tooltip']and it['player']['lines']==oi['player']['lines'])
# Published JS syntax check.
subprocess.run(['node','--check',str(S/cfg['app'])],check=True)
logs=[]
for name in ['smoke','matrix-e04','matrix-e05','matrix-e06','matrix-atlas','tasks']:
 x=json.loads((W/'checks'/(name+'.json')).read_text());logs.append(x)
 ck(name+' no script errors',not x['errors'])
 for v in x['views']:
  ck(name+' view '+v['route'],not(v['error']or v['dupes']or v['dead']or v['object']or v['oldLinks']or v.get('missingLocal')or v['width']>v['view']+1))
 for t in x['tasks']:ck('Native '+t['task'],t['pass'])
# Deterministic independent generation, then restore current build configuration.
rawcfg=(W/'build_paths.json').read_bytes();repeat=W/'independent_repeat'
subprocess.run([sys.executable,str(W/'build47.py'),str(repeat)],check=True)
(W/'build_paths.json').write_bytes(rawcfg)
basefiles=[p for p in S.rglob('*')if p.is_file()]
for f in basefiles:
 other=repeat/f.relative_to(S);ck('Deterministic '+str(f.relative_to(S)),other.exists()and h(f)==h(other))
summary={'active_character_stages':['e04','e05','e06'],'author_equipment':sum(len(b['equipment'])for b in C['builds']),'player_equipment':len(P['items']),'atlas_variants':len(C['atlas']),'atlas_selected_bindings':sum(len(v['keystone_selections'])for v in C['atlas']),'view_instances':sum(len(x['views'])for x in logs),'native_and_layout_assertions':len(logs[-1]['tasks']),'width_instances':40,'independent_build_outputs':len(basefiles),'data_and_view_checks':len(checks),'http_and_file_navigation':logs[0]['navigation']}
(W/'checks/data-protection-and-build.json').write_text(json.dumps({'summary':summary,'checks':checks},ensure_ascii=False,indent=2))
notes=f'''# R47｜网站修改、保留范围与检查\n\n这次交付的是完整网站。基线是实际可访问的R45完整包和R46个人快照层；没有以单独过滤器替代网站。\n\n## 修改范围\n\n- 人物使用数据、选择、搜索和构筑下载仅保留暴击混合防御（当前目标）、高配冰射（后续）和作者实装（只读）。前三套人物构筑已从使用入口移出。\n- 个人快照15件装备与当前作者目标同页对照；保留逐件处理建议、底材、完整面板和制作入口。进入个人对照会固定当前目标，不继承此前浏览的未来阶段。\n- 后续配方、完整配装、技能、人物珠宝和升级条件保留。三件优先事项不是限制其他内容。\n- 异界与人物阶段分开：按用户自述从“刚开始”阅读。起步、解锁、任务、点数、大节点、地图循环、材料、七套后续刷法、大师与地图碑牌全部保留。\n- 过滤器用法写入首页、异界页和独立网站页面。当前显示01异界起步原版；03、04后续，02备用。四份均原字节，不改颜色、声音、规则，也不自动切换游戏。\n- 原始采集证据原样保存，其中可含旧阶段取证；它们不作为人物使用入口。旧R45/R46与角色诊断ZIP未覆盖或删除。\n\n## 实际核对\n\n- 保留3套作者配置，共{summary['author_equipment']}条装备；角色快照{summary['player_equipment']}件。作者面板、镶嵌与原文不因本轮范围调整而改写。\n- 七套异界数据与R45的采集对象逐字段相等，{summary['atlas_selected_bindings']}条已选绑定及所有具名大师配置保留。起步、解锁、材料等原数据独立比对相等。\n- 四份原版filter和三份构筑下载与源哈希一致。原始采集目录逐文件核对。\n- {summary['view_instances']}次页面视图检查（含重复任务路径）；{summary['native_and_layout_assertions']}项原生任务/布局断言全部通过。此数字不是游戏机制实测次数。检查包括旧人物链接转当前、未来人物与异界进度独立、个人对照进入当前制作、七套异界切换、过滤器网页选择和本地资源路径。\n- 390/768/1024/1440/1920五种宽度，8类页面共40视图。已目视检查桌面首页、个人装备、异界与手机主页。\n- {summary['independent_build_outputs']}个发布收尾前输出独立重建字节一致。\n\n## 首次失败与修正\n\n原生测试首次使用不正确文字“做”定位卡片，实际按钮是“打造”。改用实际href参数后重新跑完；不是修改网站文案迎合测试。同时修正个人对照必须锁定当前e04、不能继承后续e05的问题。资源检查发现旧六阶段宝石清单和异界建议文件链接缺失，前者换为只含当前及后续的清单，后者补回原有说明；全部相关页面重新检查通过。\n\n## 验证边界\n\n真实HTTP和file导航均实际尝试，返回ERR_BLOCKED_BY_ADMINISTRATOR。实际HTML/CSS/JS在Chromium内存文档运行；本地图片从输出包读取，仅用于展示检查。没有在用户域名上线，没有游戏实测、洗点、换装、消费材料或修改个人异界树。\n\n原资料中三张开荒外链图的网络依赖仍保留明确说明；七张作者异界原图和完整文字仍可读。本轮不把未知的完整个人天赋、品质启用、预算或作者实装数据冲突补造为事实。\n\n使用：完整解压到新目录，打开index.html；不要与R46零散混拼。\n'''
(S/'R47_网站修改与检查说明.md').write_text(notes)
(S/'维护源码').mkdir(exist_ok=True)
for f in ['build47.py','extension47.js','style47.css','test47.py','finalize47.py']:
 shutil.copy2(W/f,S/'维护源码'/f)
(S/'维护源码/README.md').write_text('''# 维护\n\n本次为R45和R46的独立网站范围重组。build47.py按自身目录中的r45/和r46/Ghostliness_当前使用版_R46/读取基线，接受全新输出目录参数，拒绝覆盖；test47.py读取build_paths.json进行检查。需要Python3；语法检查需Node，页面检查需Playwright和Chromium。用户正常阅读不需要这些工具。\n\nfinalize47.py中原始诊断资料从/mnt/data读取，换机器须调整路径。旧源文件不在本包重复打包；使用此前已交付的基线。\n''')
shutil.copytree(W/'checks',S/'网站检查',ignore=shutil.ignore_patterns('server.log','server.pid'),dirs_exist_ok=True)
for name,src in [('R47_网站首页_预览.png','home.png'),('R47_我的装备_预览.png','equipment.png'),('R47_异界入门_预览.png','atlas.png'),('R47_过滤器网页_预览.png','filters.png')]:
 shutil.copy2(W/'checks'/src,Path('/mnt/data')/name)
shutil.copy2(S/'R47_网站修改与检查说明.md','/mnt/data/R47_网站修改与检查说明.md')
# Current package manifest; old checksums are not included as a misleading current hash list.
paths=sorted([p for p in S.rglob('*')if p.is_file()])
manifest='\n'.join(h(p)+'  '+p.relative_to(S).as_posix()for p in paths)+'\n'
(S/'SHA256SUMS_R47.txt').write_text(manifest)
out=Path('/mnt/data/Ghostliness_R47_网站修正版_当前后续与完整异界.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for f in sorted(S.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(S).as_posix())
with zipfile.ZipFile(out)as z:
 assert z.testzip()is None
 for row in manifest.splitlines():
  sha,name=row.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==sha
 receipt={'zip':str(out),'bytes':out.stat().st_size,'sha256':h(out),'entries':len(z.namelist()),'manifest_verified':len(paths),'crc_verified':True,'checks':summary}
Path('/mnt/data/R47_网站交付核验.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt,ensure_ascii=False,indent=2))
