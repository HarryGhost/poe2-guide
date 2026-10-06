from pathlib import Path
import json,hashlib,re,subprocess,shutil,sys,os
SRC=Path(__file__).resolve().parent
BASE=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/r42_work/base')
OUT=Path(sys.argv[2] if len(sys.argv)>2 else '/mnt/data/poe2_Fubgun_C_R42')
if BASE.resolve()==OUT.resolve() or BASE.resolve() in OUT.resolve().parents or OUT.resolve() in BASE.resolve().parents:raise ValueError('Use separate input and output directories; neither may contain the other')
if not (BASE/'SHA256SUMS_R41.txt').exists():raise ValueError('Use an R41 base only')
if OUT.exists():raise ValueError('Output already exists. Choose a new, empty output path; this builder never overwrites a previous delivery.')
html=(BASE/'index.html').read_text()
oldcontent=re.search(r'<script src="([^"]*content\.[^"]+)"',html).group(1)
oldapp=re.search(r'<script src="([^"]*app\.[^"]+)"',html).group(1)
oldcss=re.search(r'<link rel="stylesheet" href="([^"]+)"',html).group(1)
D=json.loads(json.loads((BASE/oldcontent).read_text().split('=',1)[1].rstrip(';\n')))
if D.get('release',{}).get('version')!='R41':raise ValueError('Input release must be R41, not a later incremental output')
shutil.copytree(BASE,OUT)
G=json.loads((SRC/'guide42.json').read_text())
def hashed(kind,text,ext):
 b=text.encode();rel='assets/'+kind+'.'+hashlib.sha256(b).hexdigest()[:12]+'.'+ext;(OUT/rel).write_bytes(b);return rel
reftext='window.R42references='+json.dumps(json.loads((SRC/'references42.json').read_text()),ensure_ascii=False,separators=(',',':'))+';\n'
refrel=hashed('references',reftext,'js');G['referenceAsset']=refrel
D['guide42']=G
D['release']={'version':'R42','date':'2026-10-03','title':'全站阶段路线与统一阅读','baseline':'R41','scope':'全站结构重整，原构筑与四份原版过滤器不变'}
content='document.getElementById(\'site-data\').textContent='+json.dumps(json.dumps(D,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';\n'
newcontent=hashed('content',content,'js')
tmp=OUT/'app42.tmp.js';subprocess.run(['node',str(SRC/'merge42.cjs'),str(BASE/oldapp),str(SRC/'app42.js'),str(tmp)],check=True)
newapp=hashed('app',tmp.read_text(),'js');tmp.unlink();(OUT/'app42.tmp.js.merge.json').unlink()
css=(BASE/oldcss).read_text()+'\n'+(SRC/'style42.css').read_text();newcss=hashed('style',css,'css')
html=html.replace(oldcontent,newcontent).replace(oldapp,newapp).replace(oldcss,newcss)
html=html.replace('R41','R42').replace('R42 成长与打造','R42 全站阶段路线').replace('一个角色，一套完整路线','按阶段，顺着做').replace('目标 → 判断 → 操作 → 验收。','全身目标 → 技能 → 打造 → 下一步。')
html=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Fubgun冰射攻略R42：剧情至异界同阶段整套目标、技能、逐步打造、材料预留与转换条件，原版过滤器保持。">',html)
(OUT/'index.html').write_text(html)
for name,route in [('开始阅读_从这里打开.html','#/guide?stage=e01'),('剧情攻略_从这里打开.html','#/guide?cp=l01'),('装备打造_从这里打开.html','#/gear?stage=e01'),('异界攻略_从这里打开.html','#/atlas-starter')]:
 (OUT/name).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html'+route+'"><title>打开R42攻略</title><a href="index.html'+route+'">打开攻略</a></html>')
(OUT/'data/R42-guide.json').write_text(json.dumps(G,ensure_ascii=False,indent=2))
print(json.dumps({'output':str(OUT),'assets':[newcontent,newapp,newcss,refrel],'files':len(list(OUT.rglob('*')))},ensure_ascii=False))
