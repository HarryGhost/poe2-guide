from pathlib import Path
import json,re,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parent
B=ROOT/'r45'; P=ROOT/'r46/Ghostliness_当前使用版_R46'
O=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/mnt/data/Ghostliness_R47_当前与后续_异界完整网站')
if O.exists(): raise SystemExit('Output exists; choose a fresh directory.')
O.mkdir(parents=True)
def load_js(file):
 t=file.read_text();x=json.loads(t[t.index('=')+1:].strip().rstrip(';'));return json.loads(x) if isinstance(x,str) else x
idx=(B/'index.html').read_text()
paths=re.findall(r'<script src="([^"]+)"',idx)
by={}
for p in paths:
 k=Path(p).name.split('.')[0];by[k]=p
D=load_js(B/by['content']);C=load_js(B/by['capture43']);L=load_js(B/by['localization44']);G=load_js(B/by['guide45'])
keep={'e04','e05','e06'};removed={'e01','e02','e03'}
D['stages']=[s for s in D['stages'] if s['id'] in keep]
D['branches']=[s for s in D['branches'] if s['number']>=4]
for key in ['finish','equipmentTargets']:
 D[key]={k:v for k,v in D[key].items() if k in keep}
for key in ['gemGuide','jewelGuide']:
 D[key]['stages']={k:v for k,v in D[key]['stages'].items() if k in keep}
D['guide42']['campaign']=[];D['guide42']['milestones']={}
D['routes']=[r for r in D['routes'] if r['id']!='bow-noncrit']
for s in D['stages']:
 for it in s['items']:
  it['routes']=[r for r in it.get('routes',[]) if r['id']!='bow-noncrit']
D['filterGuide']['order']=['01','03','04','02']
D['filterGuide']['files']={k:v for k,v in D['filterGuide']['files'].items() if k in ['01','02','03','04']}
D['filters'].sort(key=lambda x:['01','03','04','02'].index(x['name'][:2]))
oldDoc=re.compile(r'^(?:e0[123]|l0[1-6]|all|index)\.html$')
D['documents']=[d for d in D['documents'] if not oldDoc.match(d['file'])]
for x in D['tools']:
 if x.get('route')=='builds':x.update(title='当前与后续人物构筑',desc='暴击混合防御、高配冰射与只读实装')
 if x.get('route')=='filters':x.update(desc='当前用01原版，后续按拾取需求选择；原规则不变')
C['builds']=[b for b in C['builds'] if b['stage'] in keep]
C['rawCompare']=[x for x in C['rawCompare'] if x['build'] in [b['name'] for b in C['builds']]]
# The first retained branch has no previous active branch; do not compare it with retired non-crit.
for it in C['builds'][0]['equipment']: it['diffFromPrevious']=None
G['guides']={k:v for k,v in G['guides'].items() if k in keep}
Pdata=json.loads((P/'data/当前使用内容.json').read_text())
Pdata.pop('cut',None);Pdata['meta']['edition']='R47';Pdata['meta']['atlas_progress']='刚开始异界（用户自述）'
# Keep all actual Atlas source material; remove superseded website code and retired build downloads.
for f in B.rglob('*'):
 if not f.is_file(): continue
 rel=f.relative_to(B); parts=rel.parts; name=f.name
 yes=False
 if parts[0]=='assets':
  yes=len(parts)>2 or not re.match(r'(?:content|capture43|guide45|localization44|app|style|references)\.',name)
 elif parts[0] in ['采集证据_20261005','来源记录','原版过滤器_从这里选']:yes=True
 elif parts[0]=='R28原站':
  yes=(len(parts)>2 and parts[1]=='assets') or (len(parts)==2 and f.suffix in ['.html','.json'] and not oldDoc.match(name))
 elif parts[0]=='pages':yes=not oldDoc.match(name)
 elif len(parts)==1 and name in ['.nojekyll','R43_比对与修订说明.md','R43_逐件差异清单.md','R44_中文名称与来源说明.md']:
  yes=True
 if f.suffix=='.filter' and parts[0]!='原版过滤器_从这里选':yes=False
 if '.build' in name:yes=False
 if yes:
  dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
# Copy the 3 original downloadable builds byte-for-byte.
originals=[]
for branch in D['branches']:
 fn=branch['download'].split('/')[-1]
 source=next((f for f in B.rglob(fn) if f.is_file()),None)
 if source is None:
  # .build records use alternate raw names in R28.
  source=next(f for f in (B/'R28原站/构筑文件').iterdir() if f.name.startswith(str(branch['number']).zfill(2)))
 dest=O/'原始构筑'/fn;dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
 originals.append({'stage':'e0'+str(branch['number']),'path':'原始构筑/'+fn,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 branch['download']='原始构筑/'+fn
# Player evidence, data and unchanged previous diagnosis, not a new gameplay assessment.
for f in (P/'evidence/character').rglob('*'):
 if f.is_file():dest=O/'角色证据'/f.relative_to(P/'evidence/character');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
for f in (P/'evidence/author').rglob('*'):
 if f.is_file():dest=O/'角色对照证据'/f.relative_to(P/'evidence/author');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
(O/'资料').mkdir(exist_ok=True)
for name in ['Ghostliness_当前阶段与三步调整_20261006.md','Ghostliness_原始装备与镶嵌记录.md']:
 shutil.copy2(Path('/mnt/data')/name,O/'资料'/name)
# Update personal evidence references, while preserving exact text and numeric fields.
def maprefs(v):
 if isinstance(v,str):return v.replace('evidence/character/','角色证据/').replace('evidence/author/','角色对照证据/')
 if isinstance(v,list):return [maprefs(x) for x in v]
 if isinstance(v,dict):return {k:maprefs(x) for k,x in v.items()}
 return v
Pdata=maprefs(Pdata)
# Native reference chapters retained for Atlas / practical learning, but retired character trees removed.
refs=load_js(B/D['guide42']['referenceAsset']);refs={k:v for k,v in refs.items() if not oldDoc.match(k)}
# No implicit instructions to revert to Early in the beginner Atlas chapter.
for key in ['after-quests.html']:
 if key in refs:
  st=json.dumps(refs[key],ensure_ascii=False).replace('先用Early','保持当前人物配装').replace('用Early','按当前人物配装').replace('Early建立','当前人物配装建立')
  refs[key]=json.loads(st)
assets={}
def asset(key,text,ext='js'):
 path=f'assets/{key}.r47.{hashlib.sha256(text.encode()).hexdigest()[:12]}.{ext}'
 (O/path).parent.mkdir(exist_ok=True,parents=True);(O/path).write_text(text);assets[key]=path;return path
D['guide42']['referenceAsset']=asset('references','window.R42references='+json.dumps(refs,ensure_ascii=False,separators=(',',':'))+';')
asset('content',"document.getElementById('site-data').textContent="+json.dumps(json.dumps(D,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';')
for key,var,obj in [('capture43','FUBGUN_CAPTURE43',C),('localization44','FUBGUN_LOCALIZATION44',L),('guide45','FUBGUN_GUIDE45',G),('personal47','GHOSTLINESS47',Pdata)]:
 asset(key,'window.'+var+'='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';')
s=(B/by['app']).read_text()
s=s.replace("state={stage:'e01'", "state={stage:'e04'").replace("getStore('stage','e01')","getStore('stage','e04')").replace("state.stage='e01'","state.stage='e04'").replace("state.context42='e01'","state.context42='e04'")
s=s.replace('D.finish.e01','D.finish.e04').replace('D.jewelGuide.stages.e01','D.jewelGuide.stages.e04')
s=s.replace("case 'gear':body=gear();break;","case 'home':body=home47();crumb='当前人物与异界起步';break;case 'my-gear':body=myGear47();crumb='我的现装与目标';break;case 'my-skills':body=mySkills47();group='character';crumb='我的技能与目标';break;case 'gear':body=gear();break;")
needle="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';"
assert s.count(needle)==1
s=s.replace(needle,(ROOT/'extension47.js').read_text()+'\n'+needle)
asset('app',s)
oldstyle=re.search(r'<link[^>]+href="([^"]+\.css)"',idx)[1]
asset('style',(B/oldstyle).read_text()+'\n'+(ROOT/'style47.css').read_text(),'css')
for k,p in by.items():idx=idx.replace(p,assets[k])
idx=idx.replace(oldstyle,assets['style'])
idx=idx.replace('<script src="'+assets['app']+'"></script>','<script src="'+assets['personal47']+'"></script>\n<script src="'+assets['app']+'"></script>')
idx=idx.replace('href="#/gear" aria-label="冰射攻略首页"','href="#/home" aria-label="冰射攻略首页"')
idx=idx.replace('<title>冰霜射击攻略 · R45</title>','<title>Ghostliness · 当前与后续攻略 R47</title>')
idx=re.sub(r'<meta name="description" content="[^"]+">','<meta name="description" content="Ghostliness当前与后续人物攻略；当前暴击混合防御，保留高配与只读实装。异界从入门到后续刷法完整保留。">',idx)
idx=idx.replace('0.5.5 · R45 配装指导修复','R47 · 当前与后续 · 异界完整')
idx=idx.replace('攻略目录','人物与异界分开推进').replace('<b>装备一页看全</b>全身装备 · 中文名称。<br>天赋、异界、打造分别阅读。','<b>人物：暴击混合防御</b>异界：刚开始，保留全流程。<br>后续人物配置仍可查看。')
(O/'index.html').write_text(idx)
# Human-friendly shortcuts to actual pages; not another filter-only deliverable.
for name,route in [('我的全身装备.html','my-gear'),('全身装备_从这里打开.html','gear?stage=e04'),('异界攻略_从这里打开.html','atlas-starter'),('新手异界开荒_从这里打开.html','atlas-starter'),('装备打造_一步步做.html','early-craft?stage=e04'),('过滤器_在这里选择.html','tools/filters')]:
 (O/name).write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html#/'+route+'"><a href="index.html#/'+route+'">进入当前网站</a>')
(O/'data').mkdir(exist_ok=True)
for name,obj in [('R47_当前与后续内容.json',{'stages':[b['stage']for b in C['builds']],'names':[b['name']for b in C['builds']],'atlas':[v['name']for v in C['atlas']],'originals':originals}),('R47_个人快照.json',Pdata),('R47_底材选择.json',G)]:
 (O/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
# Document scope separately from uncertain game mechanics.
(O/'00_打开网站.md').write_text('''# Ghostliness 网站修正版 · R47\n\n完整解压到新目录，打开 index.html。这是完整网站，不是过滤器文件。\n\n人物当前目标：暴击混合防御；后续保留高配冰射和作者实装（只读）。前三套人物阶段已从实际使用数据、选择、搜索和构筑下载中移出。\n\n异界是另一条进度：按用户自述从刚开始阅读。起步、解锁、加点、大节点、大师、地图碑牌、材料与七套后续刷法全部保留。\n\n过滤器选择在网页内：当前用保存的01异界起步原版；其余三份按用途留作后续或备用，全部原字节。网站不会替换游戏里的过滤器。\n\n网页展示角色快照，不读取当前游戏；完整个人天赋与实际启用状态仍未取得。不按网页操作自动洗点、换装或用料。\n\n旧R45、R46、作者采集包和角色诊断包没有覆盖或删除；证据档案可能含旧阶段，但不作为当前攻略入口。\n''')
shutil.copy2(B/'R41_异界大节点选择说明.md',O/'R41_异界大节点选择说明.md')
lines=['# 当前与后续技能宝石清单','', '按保留的原件连接统计副本。品质／等级未提供的，不自动填成满值；这份清单不要求现在一次买齐。','']
zhstage={'e04':'暴击混合防御 · 当前目标','e05':'高配冰射 · 后续','e06':'作者实装 · 只读'}
for sid in ['e04','e05','e06']:
    stage=D['gemGuide']['stages'][sid]; lines+=['## '+zhstage[sid],'','|名称|数量|','|---|---:|']
    for row in stage['rows']:
        info=D['gemGuide']['info'][row['id']]; name=L['names'].get(info['en'],info['zh']);lines.append('|'+name+'|'+str(row['qty'])+'|')
    lines+=['','### 完整连接','']
    for chain in stage['chains']:
        lines.append('**'+chain['zh']+'**：'+' ＋ '.join(('内嵌主动：'if x.get('embedded')else'')+x['zh']for x in chain['parts']))
    lines.append('')
(O/'资料/当前与后续技能宝石清单.md').write_text('\n'.join(lines))
(O/'README_上线.md').write_text('# R47 静态网站\n\n上传本目录全部内容，入口为 index.html，保留相对路径。无需数据库或构建服务。不要与R46混拼。\n\n本次未执行用户域名发布，游戏操作和原版过滤器不变。\n')
(ROOT/'build_paths.json').write_text(json.dumps({'site':str(O),**assets},ensure_ascii=False,indent=2))
print('Built',O,'files',sum(f.is_file()for f in O.rglob('*')))
