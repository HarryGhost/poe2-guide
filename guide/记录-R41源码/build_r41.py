from pathlib import Path
import json, re, shutil, hashlib, argparse
W=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Build R41 from an intact R40 directory; never overwrite the input.')
parser.add_argument('--baseline',type=Path,default=W/'baseline');parser.add_argument('--output',type=Path,default=Path('/mnt/data/poe2_Fubgun_C_R41'))
args=parser.parse_args();B=args.baseline.resolve();O=args.output.resolve()
if B==O or B.is_relative_to(O) or O.is_relative_to(B):raise ValueError('Output must be separate from the baseline, not its parent.')
source_html=(B/'index.html').read_text()
source_js=re.search(r'<script src="([^"]*content\.[^"]+\.js)"',source_html).group(1)
source_app=re.search(r'<script src="([^"]*app\.[^"]+\.js)"',source_html).group(1)
source_literal=(B/source_js).read_text().split('=',1)[1].strip().rstrip(';')
source_data=json.loads(json.loads(source_literal))
if source_data.get('release',{}).get('version')!='R40':raise ValueError('Expected exact R40 release input; do not stack this patch on R41.')
if O.exists():shutil.rmtree(O)
shutil.copytree(B,O)
D=source_data;D['craftGuide41']=json.loads((W/'craft41.json').read_text());D['atlasChoices41']=json.loads((W/'atlas41.json').read_text())
D['release']={**D['release'],'version':'R41','date':'2026-10-03','type':'逐步打造与异界大节点选择'}
app=(B/source_app).read_text()
# Alias only the definitions needed by wrappers. Others override later by declaration.
for n in ['fullTargetPanel','atlasPage','atlasStarter','filterGuidePage','filterCheckPage']:
 new=n+('Old41' if n=='fullTargetPanel' else 'R40')
 old='function '+n+'('
 assert app.count(old)==1,(n,app.count(old))
 app=app.replace(old,'function '+new+'(',1)
# New atlas route. Existing current-section parsing still controls navigation and other features.
old="else if(page==='atlas-starter')"
assert old in app
app=app.replace(old,"else if(page==='atlas-choices'){body=atlasChoices();group='atlas';crumb='大节点选什么';}\n "+old)
# Important: load new constants before the final initial render.
needle="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';"
assert app.count(needle)==1
newjs=(W/'additions41.js').read_text().replace("({ring1:'rings',ring2:'rings'})","({ring1:'rings',ring2:'rings',weapon2:'bow',quiver2:'quiver'})")
app=app.replace(needle,newjs+'\n'+needle)
# Current UI build label only. Historical source text/date is untouched.
app=app.replace(' · R40',' · R41')
app=app.replace("crumb='剧情／低投入工作台'","crumb='一步步做装备'")
app=app.replace("crumb='什么时候值得打造'","crumb='值得做吗：比较例子'")
app=app.replace("'atlas-starter':'新手异界开荒'","'atlas-starter':'新手异界开荒','atlas-choices':'大节点选什么'")
app=app.replace("'early-craft':'剧情／低投入工作台'","'early-craft':'一步步做装备'")
app=app.replace("{title:'过滤器：选择、下载与01补底材碎片',text:'01/02/03/04 · 原版与补充版分清'","{title:'过滤器：四份原版快照',text:'01/02/03/04 · 不修改原文件'")
# Guard old direct item state handler from dragging stale material tier to new workspace.
app=app.replace(",tier:r40Tier()","")
# Function bodies now override old removed flow; all old raw reference pages remain preserved.
html=(O/'index.html').read_text();old_app=re.search(r'<script src="([^"]*app\.[^"]+\.js)"',html).group(1);old_data=re.search(r'<script src="([^"]*content\.[^"]+\.js)"',html).group(1)
old_css=re.search(r'<link[^>]*href="([^"]+\.css)"',html).group(1)
css=(O/old_css).read_text()+'\n'+(W/'additions41.css').read_text()
# Match the content bootstrap contract.
old_boot=(O/old_data).read_text();print('bootstrap prefix',old_boot[:90])
serialized=json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
boot="document.getElementById('site-data').textContent="+json.dumps(serialized,ensure_ascii=False)+";\n"
def hashed(prefix,text,ext):
 h=hashlib.sha256(text.encode()).hexdigest()[:12];rel=f'assets/{prefix}.{h}.{ext}';(O/rel).write_text(text);return rel
ap=hashed('app',app,'js');cp=hashed('content',boot,'js');cs=hashed('style',css,'css')
html=html.replace(old_app,ap).replace(old_data,cp).replace(old_css,cs)
html=html.replace('R40','R41')
(O/'index.html').write_text(html)
(O/'data/R41-crafting.json').write_text(json.dumps(D['craftGuide41'],ensure_ascii=False,indent=2));(O/'data/R41-atlas-choices.json').write_text(json.dumps(D['atlasChoices41'],ensure_ascii=False,indent=2))
for name,route in [('装备打造_一步步做.html','early-craft'),('异界大节点_选什么.html','atlas-choices')]:
 (O/name).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>冰射攻略 R41</title><meta http-equiv="refresh" content="0;url=index.html#/'+route+'"><a href="index.html#/'+route+'">进入攻略</a></html>')
(O/'原版过滤器_从这里选').mkdir(exist_ok=True)
for k in ['01','02','03','04']:
 f=D['filterGuide']['files'][k];shutil.copyfile(B/f['url'],O/'原版过滤器_从这里选'/f['name'])
(W/'build_result.json').write_text(json.dumps(dict(output=str(O),app=ap,content=cp,css=cs),ensure_ascii=False,indent=2));print('created',O,ap)
