"""Independent R43 data, native-click, responsive and rendered-view checks.
Actual file/HTTP navigation results are separately logged in boot.json.
Memory-document tests retain native hash navigation; local pictures are inlined
only in the screenshot fixture, using the corresponding actual files.
"""
from pathlib import Path
import json,re,base64,urllib.parse,hashlib
from playwright.sync_api import sync_playwright
W=Path(__file__).parent;CFG=json.loads((W/'build_paths.json').read_text());S=Path(CFG['site']);O=json.loads((W/'overlay43.json').read_text());C=W/'capture/fubgun_capture_2026-10-05';CHECK=W/'checks';CHECK.mkdir(exist_ok=True)
results={'data':[],'click':[],'views':[],'layout':[],'pageerrors':[],'limits':'Actual HTML/CSS/JS in memory document. No game or real deployment acceptance.'}
def record(category,name,ok,detail=None):
 results[category].append({'name':name,'ok':bool(ok),'detail':detail})
 if category in ['click','layout'] or (category=='views' and len(results[category])%25==0):print(category,len(results[category]),name,ok,flush=True)
 if not ok:save()
def save():
 (CHECK/'r43_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
def check(category,name,ok,detail=None):
 record(category,name,ok,detail)
 if not ok:save();raise AssertionError(name+': '+str(detail))
# Resolve every concrete evidence file and JSON pointer, independent of capture manifest.
cache={};refs=set()
def traverse(x):
 if isinstance(x,dict):
  if 'file' in x and isinstance(x['file'],str) and x['file'].startswith('evidence/'):
   refs.add((x['file'],x.get('json_pointer')))
  for v in x.values():traverse(v)
 elif isinstance(x,list):
  for v in x:traverse(v)
for fn in ['builds.json','atlas.json']:traverse(json.loads((C/fn).read_text()))
for f,pointer in sorted(refs,key=str):
 path=C/f;ok=path.is_file();reason=None
 if ok and pointer:
  try:
   if f not in cache:cache[f]=json.loads(path.read_text())
   obj=cache[f]
   for key in pointer.lstrip('/').split('/') if pointer else []:
    key=key.replace('~1','/').replace('~0','~');obj=obj[int(key)] if isinstance(obj,list) else obj[key]
  except Exception as e:ok=False;reason=str(e)
 check('data','Evidence '+f+(pointer or ''),ok,reason)
for b in O['builds']:
 check('data',b['name']+' unique uids',len({x['uid'] for x in b['equipment']})==len(b['equipment']))
 for it in b['equipment']:
  check('data',b['name']+' panel '+it['uid'],it['panel']['name']==it['name'])
  check('data',b['name']+' translation '+it['uid'],all(m.get('zh') for m in it['panel']['modifiers']))
 for j in b['jewels']:check('data',b['name']+' jewel '+str(j['display_order']),j['panel']['name']==j['name'])
 for m in b['equipment']:
  for c in m['crosschecks']:
   if c['result']=='source_panel_difference':check('data',m['name']+' visible source conflict',any(str(c['source']) in t and str(c['panel']) in t for t in m['sourcePanelCaution']))
for v in O['atlas']:
 selected=set(n for al in v['atlas_tree']['allocations'].values() for n in (al.get('selected_node_ids') or []))
 for x in v['keystone_selections']:check('data',v['name']+' selected '+x['node_id'],x['node_id'] in selected and bool(x['zhChoice']))
 for m in v['masters']:check('data',v['name']+' master '+m['name'],m['selected_count']==sum(x['author_selected'] for x in m['candidate_options']) and all(x.get('zhEffects') for x in m['candidate_options']))
check('data','Original names match 91',sum(x['name_equal'] for x in O['rawCompare'])==91)
check('data','Stored descriptions 85 equal / 6 differ',sum(x['stored_desc_equal'] for x in O['rawCompare'])==85)
check('data','Live Emeralds differ',len({tuple(m['text'] for m in j['panel']['modifiers']) for j in O['builds'][-1]['jewels'] if j['name']=='Emerald'})==4)
expected=['(5-15)% increased Attack Damage','(25-29)% increased Critical Hit Chance for Attacks','(30-34)% increased Critical Damage Bonus for Attack Damage','(2-4)% increased Attack Speed with Bows']
check('data','Live first Emerald vs supplied screenshot',[m['text'] for m in O['builds'][-1]['jewels'][0]['panel']['modifiers']]==expected)
# Patch fixture only; production relative references stay unchanged.
def inline_images(page):
 imgs=page.locator('img')
 for i in range(imgs.count()):
  im=imgs.nth(i);src=im.get_attribute('src') or ''
  if not src or src.startswith(('http:','https:','data:','blob:')):continue
  fp=(S/urllib.parse.unquote(src.split('#')[0].split('?')[0])).resolve()
  if fp.is_file() and fp.is_relative_to(S):
   mime='image/'+('jpeg' if fp.suffix.lower() in ['.jpg','.jpeg'] else fp.suffix.lstrip('.'))
   im.evaluate('(el,s)=>el.src=s','data:'+mime+';base64,'+base64.b64encode(fp.read_bytes()).decode())
save()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
 page.on('pageerror',lambda e:results['pageerrors'].append(str(e)))
 html=(S/'index.html').read_text();html=re.sub(r'<script src="[^"]+"></script>','',html);html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',html)
 page.set_content(html);page.add_style_tag(path=str(S/CFG['css']))
 for f in ['assets/content.e69d3567dd9c.js',CFG['data'],'assets/references.4d695b29f980.js',CFG['app']]:page.add_script_tag(path=str(S/f))
 page.wait_for_selector('[data-ready="true"]')
 def goto(h):
  if not h.startswith('#'):h='#/'+h
  page.evaluate('(h)=>{location.hash=h}',h);page.wait_for_timeout(45)
  page.wait_for_selector('[data-ready="true"]')
 def view(name):
  r=page.evaluate('''()=>{let root=document.querySelector('#main-content'),els=[...root.querySelectorAll('[id]')],ids=els.map(x=>x.id);return {title:document.title,dupes:ids.filter((x,i)=>ids.indexOf(x)!==i),orphans:[...root.querySelectorAll('[data-scroll]')].filter(x=>!document.getElementById(x.dataset.scroll)).map(x=>x.dataset.scroll),objects:root.innerText.includes('[object Object]'),width:document.documentElement.scrollWidth,viewport:innerWidth};}''')
  ok=not r['dupes'] and not r['orphans'] and not r['objects'] and r['width']<=r['viewport']+1
  record('views',name,ok,r);return ok
 for b in O['builds']:
  goto('gear?stage='+b['stage']);check('click',b['name']+' all cards',page.locator('[data-capture-item]').count()==len(b['equipment']) and page.locator('[data-capture-jewel]').count()==len(b['jewels']))
  check('click',b['name']+' all main slots visible',page.locator('#r43-main > .r43-grid > article').count()==10)
  check('click',b['name']+' every modifier visible',page.locator('[data-capture-item] .r43-mods > li:visible').count()==sum(len(it['panel']['modifiers'])for it in b['equipment']))
  check('click',b['name']+' every rune visible',page.locator('.r43-rune:visible').count()==sum(len(it['socketed_items'])for it in b['equipment']))
  view('gear '+b['stage'])
  if b['stage']!='e06':
   page.locator('#r43-item-bow .r43-card-action a').click();page.wait_for_timeout(80)
   check('click',b['name']+' click craft keeps stage','stage='+b['stage'] in page.evaluate('location.hash') and 'tab=craft'in page.evaluate('location.hash'))
   check('click',b['name']+' craft current target',page.locator('.r43-craft-reference').count()==1)
  else:check('click','Live Gear no craft buttons',page.locator('.r43-card-action a').count()==0)
 check('click','Current captured Voices searchable',page.evaluate("R43.search('Voices').some(x=>x.route==='jewels'&&x.params.stage==='e06')"))
 check('click','Captured Atlas Omens searchable',page.evaluate("R43.search('Omens').some(x=>x.route.startsWith('atlas/')&&x.params.tab==='choices')"))
 # Native build switch and jump controls.
 goto('gear?stage=e01');page.locator('.r43-builds a').filter(has_text='non-crit Midgame').click();page.wait_for_timeout(80);check('click','Native build switch actual name',page.locator('.r43-context b').first.inner_text()=='non-crit Midgame')
 page.locator('[data-scroll="r43-jewels"]').click();page.wait_for_timeout(250);check('click','Section jump retains route','stage=e02' in page.evaluate('location.hash'))
 goto('gear?stage=e06');page.locator('#r43-item-mana_flask .r43-proof').first.locator('summary').first.click();page.wait_for_timeout(50)
 check('click','Proof expands original source',page.locator('#r43-item-mana_flask .r43-proof').first.get_attribute('open') is not None)
 page.locator('#r43-item-mana_flask [data-r43-image]').click();check('click','Evidence modal opens',page.locator('#image-dialog').get_attribute('open') is not None);inline_images(page);page.wait_for_function('document.querySelector("#modal-image").complete && document.querySelector("#modal-image").naturalWidth>0');check('click','Evidence modal actual picture',page.locator('#modal-image').evaluate('(e)=>e.complete && e.naturalWidth>0'));page.locator('[data-close="image-dialog"]').click()
 goto('gear?stage=e06');page.locator('#r43-item-bow > .r43-proof summary').first.click();check('click','Live conflicting source is retained',page.locator('#r43-item-bow').inner_text().find('255% increased Physical Damage')>=0)
 for v in O['atlas']:
  goto('atlas/'+v['id']+'?tab=choices');check('click',v['name']+' node count',page.locator('.r43-node').count()==len(v['keystone_selections']));view(v['name']+' choices')
  page.locator('#r43-node-query').fill('zz_unmatched_zz');check('click',v['name']+' filter excludes',page.locator('.r43-node:visible').count()==0);page.locator('#r43-node-query').fill('');check('click',v['name']+' filter restores',page.locator('.r43-node:visible').count()==len(v['keystone_selections']))
  page.locator('.c41-tab').filter(has_text='大师已选与候选').click();page.wait_for_timeout(70);check('click',v['name']+' master count',page.locator('.r43-section > .r43-grid > article').count()==sum(m['selected_count'] for m in v['masters']));view(v['name']+' masters')
 # Current target/steps/finish + all character tabs, jewels, Atlas tabs.
 for b in O['builds']:
  for it in b['equipment']:
   for tab in ['target','craft','finish']:
    goto('item/'+it['uid']+'?stage='+b['stage']+'&tab='+tab);view('item '+b['stage']+' '+it['uid']+' '+tab)
  for tab in ['skills','tree','play','check']:
   goto('character?stage='+b['stage']+'&tab='+tab);view('character '+b['stage']+' '+tab)
  for route in ['jewels','special-jewels','guide','gems','special-gems','early-craft']:
   goto(route+'?stage='+b['stage']);view(route+' '+b['stage'])
 for v in O['atlas']:
  for tab in ['tree','setup','play','source']:
   goto('atlas/'+v['id']+'?tab='+tab);view('atlas '+v['id']+' '+tab)
 for route in ['tools/filters','tools/capture-audit','coverage','atlas-choices','atlas-choose','atlas-starter','learn/ascendancy','learn/permanent','supplies']:
  goto(route+'?stage=e01');view(route)
 for cp in ['l01','l02','l03','l04','l05','l06']:
  for route in ['gear','guide','character','early-craft']:
   goto(route+'?stage='+cp);view('campaign '+cp+' '+route)
 # Screenshot and responsive checks of representative actual content.
 routes=['gear?stage=e01','gear?stage=e06','jewels?stage=e06','character?stage=e03&tab=skills','character?stage=e04&tab=tree','atlas/expedition?tab=choices','atlas/lineage-gems?tab=masters','item/bow?stage=e04&tab=craft','tools/capture-audit?stage=e01']
 for width in [390,768,1024,1440,1920]:
  page.set_viewport_size({'width':width,'height':1050});
  for route in routes:
   goto(route);inline_images(page);page.wait_for_timeout(80)
   ok=view('layout '+str(width)+' '+route);record('layout',str(width)+' '+route,ok)
 page.set_viewport_size({'width':1440,'height':1100})
 for filename,route in [('equipment','gear?stage=e01'),('jewels','jewels?stage=e06'),('atlas','atlas/expedition?tab=choices'),('craft','item/bow?stage=e04&tab=craft'),('master','atlas/lineage-gems?tab=masters'),('tree','character?stage=e04&tab=tree')]:
  goto(route);inline_images(page);page.wait_for_timeout(200);page.screenshot(path=str(CHECK/(filename+'.png')),full_page=False)
 page.set_viewport_size({'width':390,'height':900});goto('gear?stage=e06');page.wait_for_timeout(300);page.screenshot(path=str(CHECK/'mobile.png'),full_page=False)
 browser.close()
save();print({k:{'count':len(v),'fail':sum(not x.get('ok',False)for x in v)}for k,v in results.items()if isinstance(v,list)and k!='pageerrors'});print('ERRORS',results['pageerrors']);print('failed views',[(x['name'],x['detail'])for x in results['views']if not x['ok']][:20])
