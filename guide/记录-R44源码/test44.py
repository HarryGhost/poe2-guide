from pathlib import Path
import json,re,hashlib,urllib.parse,base64,sys
from playwright.sync_api import sync_playwright
W=Path(__file__).parent;cfg=json.loads((W/'build_paths.json').read_text());S=Path(cfg['site']);B=W/'base';K=W/'checks';K.mkdir(exist_ok=True)
PART=int(sys.argv[1]) if len(sys.argv)>1 else 0
C=json.loads((S/'data/R43_capture_overlay.json').read_text());L=json.loads((S/'data/R44_localization.json').read_text())
r={'part':PART,'complete':False,'site':str(S),'app_sha256':hashlib.sha256((S/cfg['app']).read_bytes()).hexdigest(),'checks':[],'views':[],'english':{},'pageerrors':[],'navigation':[], 'method':'Actual generated HTML/CSS/JS in a Chromium memory document; not game or deployment verification.'}
def ck(name,ok,detail=None):
 r['checks'].append({'name':name,'ok':bool(ok),'detail':detail})
 if not ok:print('FAIL',name,detail,flush=True)
def save(): (K/('tests44_part'+str(PART)+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2))
sha=lambda b:hashlib.sha256(b).hexdigest()
allowed={'index.html','00_先读我.md','README_上线.md'}
basefiles=[p for p in B.rglob('*')if p.is_file()];changed=[]
for p in basefiles:
 q=S/p.relative_to(B)
 if not q.exists() or sha(q.read_bytes())!=sha(p.read_bytes()):changed.append(p.relative_to(B).as_posix())
ck('Only three current entry/readme files changed',set(changed)==allowed,changed)
ck('Capture overlay byte-preserved',(S/'data/R43_capture_overlay.json').read_bytes()==(B/'data/R43_capture_overlay.json').read_bytes())
ck('Every original filter is unchanged',all((S/p.relative_to(B)).read_bytes()==p.read_bytes() for p in B.rglob('*.filter')))
# Primary name coverage, entirely Chinese game names (Roman gem tier suffix is not English).
for group,names in [('Equipment',{i['name'] for b in C['builds']for i in b['equipment']}),('Jewels',{i['name']for b in C['builds']for i in b['jewels']}),('Augments',{i['name']for b in C['builds']for t in b['equipment']for i in t['socketed_items']}),('Passives',{i['name']for b in C['builds']for i in b['treePriorities']}),('Atlas nodes',{i['node_name']for v in C['atlas']for i in v['keystone_selections']}),('Master choices',{i['name']for v in C['atlas']for m in v['masters']for i in m['candidate_options']})]:
 for n in names:ck(group+': '+n,n in L['names'] and not re.search('[A-Za-z]',L['names'].get(n,'')),L['names'].get(n))
idx=(S/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)"',idx);html=re.sub(r'<script src="[^"]+"></script>','',idx);html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',html)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for uri in ['http://127.0.0.1:8744/index.html',(S/'index.html').as_uri()]:
  p=browser.new_page()
  try:p.goto(uri,timeout=5000);r['navigation'].append({'url':uri,'result':'loaded','note':'A loaded document alone is not end-to-end deployment acceptance.'})
  except Exception as e:r['navigation'].append({'url':uri,'result':str(e).splitlines()[0]})
  p.close()
 p=browser.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:r['pageerrors'].append(str(e)))
 p.set_content(html);p.add_style_tag(path=str(S/cfg['style']))
 for js in scripts:p.add_script_tag(path=str(S/js))
 # Historic reference catalog is loaded locally in this fixture to test chapter routes.
 for f in (S/'assets').glob('references.*.js'):p.add_script_tag(path=str(f));break
 p.wait_for_selector('[data-ready="true"]')
 def goto(h):
  p.evaluate('(h)=>location.hash="#/"+h',h);p.wait_for_timeout(40);p.wait_for_selector('[data-ready="true"]')
 def scan(h):
  o=p.evaluate('''()=>{const c=document.querySelector('#main-content'),ids=[...c.querySelectorAll('[id]')].map(e=>e.id);return {dupes:ids.filter((x,i)=>ids.indexOf(x)!==i),dead:[...c.querySelectorAll('[data-scroll]')].filter(e=>!document.getElementById(e.dataset.scroll)).map(e=>e.dataset.scroll),width:document.documentElement.scrollWidth,viewport:innerWidth,objects:c.innerText.includes('[object Object]'),text:c.innerText};}''')
  text=o.pop('text');ok=not o['dupes']and not o['dead'] and not o['objects'] and o['width']<=o['viewport']+1
  r['views'].append({'route':h,'ok':ok,**o})
  en=[x for x in text.splitlines()if re.search('[A-Za-z]{3,}',x)]
  if en:r['english'][h]=en
  if len(r['views'])%60==0:print('views',len(r['views']),flush=True);save()
  return text
 for b in (C['builds'] if PART==0 else C['builds'][(PART-1)*2:PART*2] if PART in [1,2,3] else []):
  goto('gear?stage='+b['stage']);text=scan('gear?stage='+b['stage'])
  ck(b['name']+' equipment count',p.locator('[data-capture-item]').count()==len(b['equipment']))
  ck(b['name']+' jewel count',p.locator('[data-capture-jewel]').count()==len(b['jewels']))
  ck(b['name']+' all headings Chinese',all(not re.search('[A-Za-z]',t) for t in p.locator('.r43-equip header h2').all_inner_texts()))
  ck(b['name']+' all mods directly visible',p.locator('[data-capture-item] .r43-mods > li:visible').count()==sum(len(i['panel']['modifiers'])for i in b['equipment']))
  ck(b['name']+' all augments visible',p.locator('.r43-rune:visible').count()==sum(len(i['socketed_items'])for i in b['equipment']))
  for it in b['equipment']:
   first=p.locator(f'[data-capture-item="{it["id"]}"] .r43-proof pre').first.text_content()
   ck(b['name']+' raw panel kept '+it['uid'],first==it['panel']['raw_text'])
  if b['stage']!='e06':
   p.locator('#r43-item-bow .r43-card-action a').click();p.wait_for_timeout(70)
   ck(b['name']+' native craft kept stage','stage='+b['stage'] in p.evaluate('location.hash') and 'tab=craft'in p.evaluate('location.hash'))
  else:ck('Live read-only no craft buttons',p.locator('.r43-card-action a').count()==0)
  for tab in ['skills','tree','play','check']:
   h='character?stage='+b['stage']+'&tab='+tab;goto(h);scan(h)
  for path in ['jewels','special-jewels','gems','special-gems','guide','early-craft']:
   h=path+'?stage='+b['stage'];goto(h);scan(h)
  for it in b['equipment']:
   for tab in ['target','craft','finish']:
    h='item/'+it['uid']+'?stage='+b['stage']+'&tab='+tab;goto(h);scan(h)
 for v in (C['atlas'] if PART in [0,4] else []):
  for tab in ['tree','choices','masters','setup','play','source']:
   h='atlas/'+v['id']+'?tab='+tab;goto(h);scan(h)
   if tab=='choices':
    ck(v['name']+' all selected nodes',p.locator('.r43-node').count()==len(v['keystone_selections']))
    p.locator('#r43-node-query').fill('不存在的节点xyz');ck(v['name']+' filter works',p.locator('.r43-node:visible').count()==0)
    p.locator('#r43-node-query').fill('');ck(v['name']+' filter restores',p.locator('.r43-node:visible').count()==len(v['keystone_selections']))
   if tab=='masters':ck(v['name']+' selected count unchanged',p.locator('.r43-section>.r43-grid>article').count()==sum(m['selected_count']for m in v['masters']))
 for path in (['tools/filters','tools/capture-audit','tools/names','tools/dictionary','tools/builds','tools/sources','atlas-choices','atlas-choose','atlas-starter','learn/ascendancy','learn/permanent','supplies','filter-guide','filter-check','craft-timing','troubleshoot'] if PART in [0,4] else []):
  goto(path+'?stage=e01');scan(path)
 for stage in (['l01','l02','l03','l04','l05','l06'] if PART in [0,4] else []):
  for path in ['gear','guide','character','early-craft']:
   h=path+'?stage='+stage;goto(h);scan(h)
 if PART in [0,4]:
  for q,route in [('天神之音','jewels'),('渡鸦之触碎片','item/helmet'),('阿曼娜姆','atlas/'),('未卜之患','atlas/'),('破雪者','character')]:
   ck('Chinese search '+q,p.evaluate('([q,r])=>R44.search(q).some(x=>x.route.startsWith(r))',[q,route]))
  # Native tab, source folding, and actual numeric ranges are not lost.
  goto('gear?stage=e01');p.locator('.r43-builds a').filter(has_text='非暴击中期').click();p.wait_for_timeout(100)
  ck('Native Chinese build switch',p.locator('.r43-context b').first.inner_text()=='非暴击中期')
  goto('jewels?stage=e06');j=p.locator('[data-capture-jewel]').first
  ck('Four Emerald ranges unchanged',all(t in j.inner_text()for t in ['5-15','25-29','30-34','2-4']))
  j.locator('summary').first.click();ck('Original English exact panel can open','increased Attack Damage' in j.inner_text())
  routes=[('gear','gear?stage=e01'),('live','gear?stage=e06'),('jewels','jewels?stage=e06'),('atlas','atlas/expedition?tab=choices'),('masters','atlas/lineage-gems?tab=masters'),('craft','item/bow?stage=e04&tab=craft'),('skills','character?stage=e04&tab=skills'),('tree','character?stage=e04&tab=tree')]
  for width in [390,768,1024,1440,1920]:
   p.set_viewport_size({'width':width,'height':1000})
   for name,h in routes:goto(h);scan('width:'+str(width)+' '+h)
  p.set_viewport_size({'width':1440,'height':1100})
  for name,h in routes:
   goto(h);p.wait_for_timeout(150);p.screenshot(path=str(K/(name+'-final.png')),full_page=False)
  p.set_viewport_size({'width':390,'height':1000});goto('gear?stage=e06');p.wait_for_timeout(250);p.screenshot(path=str(K/'mobile-final.png'),full_page=False)
 browser.close()
ck('No page exceptions',not r['pageerrors'],r['pageerrors']);r['complete']=True;save()
print('checks',len(r['checks']),'failed',sum(not x['ok']for x in r['checks']),'views',len(r['views']),'failed',sum(not x['ok']for x in r['views']),'englishviews',len(r['english']),flush=True)
