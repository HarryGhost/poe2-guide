from pathlib import Path
import json,hashlib,re,urllib.parse
W=Path(__file__).parent;cfg=json.loads((W/'build_paths.json').read_text());B=Path(cfg['baseline']);S=Path(cfg['site']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'checks':[],'changed':[],'missing':[],'source_files':[]}
def check(name,ok,detail=None):r['checks'].append(dict(name=name,ok=bool(ok),detail=detail))
files=[p for p in B.rglob('*')if p.is_file()]
for p in files:
 rel=p.relative_to(B).as_posix();q=S/rel
 if not q.is_file():r['missing'].append(rel)
 elif sha(p)!=sha(q):r['changed'].append(rel)
check('Only three entry/readme files changed',set(r['changed'])=={'index.html','00_先读我.md','README_上线.md'},r['changed']);check('No original files missing',not r['missing'])
for label,arr in [('filters',list(B.rglob('*.filter'))),('builds',[p for p in B.rglob('*')if p.is_file()and('.build' in p.name)]),('R28archive',[p for p in (B/'R28原站').rglob('*')if p.is_file()]),('capture',[p for p in (B/'采集证据_20261005').rglob('*')if p.is_file()])]:
 check(label+' byte preservation',all(sha(p)==sha(S/p.relative_to(B))for p in arr),{'count':len(arr)});r[label+'_count']=len(arr)
for path in ['data/R43_capture_overlay.json','data/R44_localization.json','assets/content.e69d3567dd9c.js']:
 check(path+' source bytes untouched',sha(B/path)==sha(S/path))
idx=(S/'index.html').read_text();refs=re.findall(r'(?:src|href)="(assets/[^"]+)"',idx)
for ref in refs:check('index asset '+ref,(S/urllib.parse.unquote(ref)).is_file())
G=json.loads((S/'data/R45_selection_guide.json').read_text());C=json.loads((S/'data/R43_capture_overlay.json').read_text())
for b in C['builds']:
 for uid,g in G['guides'][b['stage']].items():
  check(b['stage']+'/'+uid+' separated from captures',all(k in g for k in ['brief','keep','when','stop','compare','source','bases'])and not any(k in g for k in ['raw','panel','oldRecord']))
  if b['stage']=='e06':check(b['stage']+'/'+uid+' read only',g['readonly']and not g['bases'])
  for x in g['bases']:
   check(b['stage']+'/'+uid+'/'+x['name']+' scope',x['current']==(b['stage']in x['phases'])and bool(x['url']))
   f=x.get('fact')
   if f:check('bare facts explicitly scoped '+x['en'],all(k in f for k in ['base','url','level','checked']) and f['level']>=1)
for q in ['Cadiro\'s Gambit','Lavianga\'s Spirits','Nascent Hope','The Fall of the Axe','Rite of Passage','Headhunter']:
 check('Unique guidance exists '+q,q in G['unique'])
check('Six arrow explanations distinct',len(G['arrows'])==len({a['name']for a in G['arrows']})==6)
check('All current captures remain distinct',sum(len(b['equipment'])for b in C['builds'])==91 and sum(len(b['jewels'])for b in C['builds'])==11 and sum(len(v['keystone_selections'])for v in C['atlas'])==221)
r['baseline_file_count']=len(files);r['new_file_count_before_release']=len([p for p in S.rglob('*')if p.is_file()]);r['all_passed']=all(x['ok']for x in r['checks']);(W/'checks/data-integrity.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('data',len(r['checks']),'pass',r['all_passed'],'baseline',len(files),'archive',r['R28archive_count'],'capture',r['capture_count'],'filters',r['filters_count'],'build',r['builds_count'])
