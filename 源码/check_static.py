from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,hashlib,re
R=Path(__file__).resolve().parent.parent;B=Path(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else R;OUT=R/'检查与预览';OUT.mkdir(exist_ok=True)
results=[]
def check(name,ok,detail=None):results.append(dict(name=name,passed=bool(ok),detail=detail))
stages=json.loads((R/'data/全站阶段与核算.json').read_text()); old=json.loads((B/'data/全站阶段与核算.json').read_text())
trans=json.loads((R/'data/转换检查清单.json').read_text()); parsed={p.name:BeautifulSoup(p.read_text(),'html.parser') for p in R.glob('*.html')}
check('26 standalone HTML pages',len(parsed)==26,len(parsed))
for p in R.glob('data/*.json'):
 try:json.loads(p.read_text());ok=True
 except Exception:ok=False
 check('JSON valid: '+p.name,ok)
for name,soup in parsed.items():
 ids=[x['id'] for x in soup.select('[id]')];dup=[k for k,v in Counter(ids).items() if v>1]
 check(name+' unique DOM ids',not dup,dup)
 check(name+' C palette common shell',soup.html.get('data-look')=='c' and soup.body.get('data-layout')=='stage-workbook-r8')
 bad=[]
 for el in soup.select('a[href],script[src],link[href]'):
  url=el.get('href',el.get('src',''));q=urlsplit(url)
  if q.scheme or q.netloc:continue
  f=R/unquote(q.path) if q.path else R/name
  if not f.exists():bad.append(url);continue
  if q.fragment and f.suffix=='.html':
   other=parsed.get(f.name)
   if other and not other.find(id=unquote(q.fragment)):bad.append(url+' [missing fragment]')
 check(name+' local references and anchors',not bad,bad)
 if name!='index.html':check(name+' sources/footer exposes scope','国服实测毕业' in soup.get_text())
# Exact semantics and original byte invariants.
for a,b in zip(stages,old):
 check(a['id']+' raw original immutable',a['original']==b['original'])
 check(a['id']+' skills links immutable',a['skills']==b['skills'])
 check(a['id']+' node record scope+id+order retained',[(x['id'],x['scope'],x['row']) for x in a['nodes']]==[(x['id'],x['scope'],x['row']) for x in b['nodes']])
 check(a['id']+' all original skill rows',len(parsed[a['file']].select('.skill-row'))==len(a['skills']))
 if a['profiles']:
  for p,o in zip(a['profiles'],b['profiles']):
   nums=lambda pr:[(x['label'],x['str'],x['dex'],x['int'],x.get('level')) for x in pr['rows']]
   check(p['id']+' reference values unchanged',nums(p)==nums(o))
  soup=parsed[a['file']]
  check(a['id']+' visible default gear one panel',len(soup.select('[data-profile-gear]:not([hidden])'))==1)
  check(a['id']+' author gear separated',bool(soup.select_one('#author-gear-records')))
for p in (B/'构筑文件').glob('*'):
 if p.is_file():check('raw/annotated file bytes: '+p.name,(R/'构筑文件'/p.name).read_bytes()==p.read_bytes())
check('all eight advanced recipes unchanged',(R/'data/Fubgun_异界后期打造.json').read_bytes()==(B/'data/Fubgun_异界后期打造.json').read_bytes())
for t in trans:
 soup=parsed[t['fromStage']+'.html'];el=soup.select_one('[data-transition]')
 check(t['id']+' correct explicit edge',bool(el) and el.get('data-from-stage')==t['fromStage'] and el.get('data-to-stage')==t['toStage'])
 if el:
  check(t['id']+' exact intended checks',[x.get_text(strip=True) for x in el.select('.checklist label span')]==t['checks'])
  check(t['id']+' corrected check keys versioned',all('-r8-' in x.get('data-check','') for x in el.select('input[data-check]')))
for e in ('e05','e06'):check(e+' not forced to next stage',not parsed[e+'.html'].select('[data-transition]'))
check('index exactly aliases e01',(R/'index.html').read_bytes()==(R/'e01.html').read_bytes())
check('all profile tables readable without script',sum(1 for t in parsed['all.html'].select('h2') if t.get_text().startswith('完整属性参考：'))==13)
cases=json.loads((R/'data/打造教学实例.json').read_text())['cases'];check('six complete case articles',len(parsed['craft-examples.html'].select('[data-case]'))==6)
for c in cases:
 text=parsed['craft-examples.html'].find(id=c['id']).get_text()
 check(c['id']+' state/action/outcome/stop present',all(str(x) in text for x in [c['state'],c['action'],c['stop'],c['avoid']]))
report=dict(test='static source; pass prior unpacked package path to verify historical byte equality',environment='local bytes, no game client',total=len(results),passed=sum(x['passed'] for x in results),failed=[x for x in results if not x['passed']],checks=results)
(OUT/'静态与原件回归检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
