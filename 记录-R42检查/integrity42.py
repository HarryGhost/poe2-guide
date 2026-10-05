from pathlib import Path
import json,re,hashlib,subprocess
BASE=Path('/mnt/data/r42_work/base');OUT=Path('/mnt/data/poe2_Fubgun_C_R42');RE=Path('/mnt/data/r42_work/rebuilt42');CHECK=Path('/mnt/data/r42_work/checks')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def data(p):
 h=(p/'index.html').read_text();r=re.search(r'<script src="([^"]*content\.[^"]+)"',h).group(1);return json.loads(json.loads((p/r).read_text().split('=',1)[1].rstrip(';\n')))
B,D=data(BASE),data(OUT);result={}
result['businessFields']={'compared':[k for k in B if k!='release'],'different':[k for k in B if k!='release'and B[k]!=D.get(k)],'added':[k for k in D if k not in B]}
assert not result['businessFields']['different'];assert result['businessFields']['added']==['guide42']
for name,sub in [('archive','R28原站'),('historicalFilters','filters'),('originalFilters','原版过滤器_从这里选')]:
 f=[x for x in (BASE/sub).rglob('*')if x.is_file()];diff=[str(x.relative_to(BASE))for x in f if not (OUT/x.relative_to(BASE)).is_file()or sha(x)!=sha(OUT/x.relative_to(BASE))];result[name]={'files':len(f),'different':diff};assert not diff
result['originalFilterHashes']={str(p.relative_to(OUT)):sha(p)for p in (OUT/'原版过滤器_从这里选').glob('*.filter')}
bfiles=[p for p in BASE.rglob('*')if p.is_file()];result['baselinePreservation']={'files':len(bfiles),'different':[str(p.relative_to(BASE))for p in bfiles if not(OUT/p.relative_to(BASE)).is_file()or sha(p)!=sha(OUT/p.relative_to(BASE))]}
outfiles=[p for p in OUT.rglob('*')if p.is_file()];diff=[str(p.relative_to(OUT))for p in outfiles if not(RE/p.relative_to(OUT)).is_file()or sha(p)!=sha(RE/p.relative_to(OUT))];extras=[str(p.relative_to(RE))for p in RE.rglob('*')if p.is_file()and not(OUT/p.relative_to(RE)).is_file()];result['repeatBuild']={'comparedFiles':len(outfiles),'different':diff,'extra':extras};assert not diff and not extras
html=(OUT/'index.html').read_text();refs=re.findall(r'(?:src|href)="(assets/[^\"]+)"',html);result['entryAssets']={r:{'exists':(OUT/r).is_file(),'sha256':sha(OUT/r)}for r in refs};result['referenceAsset']={D['guide42']['referenceAsset']:sha(OUT/D['guide42']['referenceAsset'])};assert all((OUT/r).is_file()for r in refs)
result['javascriptSyntax']=[]
for r in refs+[D['guide42']['referenceAsset']]:
 if r.endswith('.js'):
  x=subprocess.run(['node','--check',str(OUT/r)],text=True,capture_output=True);result['javascriptSyntax'].append({'file':r,'exit':x.returncode,'error':x.stderr});assert x.returncode==0
result['campaignSource']={'records':len(D['guide42']['campaign']),'keys':list(D['guide42']['campaign'])if isinstance(D['guide42']['campaign'],dict)else[],'sourceFilesKept':all((OUT/'pages/reference'/f'l0{i}.html').read_bytes()==(BASE/'pages/reference'/f'l0{i}.html').read_bytes()for i in range(1,7))}
(CHECK/'integrity-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items()if k not in ['entryAssets','originalFilterHashes','businessFields','javascriptSyntax']},ensure_ascii=False,indent=2))
