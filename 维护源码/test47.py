from pathlib import Path
import json,re,base64,urllib.parse,sys,traceback,subprocess,time
from playwright.sync_api import sync_playwright
W=Path(__file__).resolve().parent;cfg=json.loads((W/'build_paths.json').read_text());S=Path(cfg['site']);K=W/'checks';K.mkdir(exist_ok=True)
mode=sys.argv[1] if len(sys.argv)>1 else 'smoke'
html=(S/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)"',html)
stripped=re.sub(r'<script src="[^"]+"></script>','',html);stripped=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',stripped)
log={'mode':mode,'navigation':[],'errors':[],'views':[],'tasks':[]}
def paint_images(p):
 for img in p.locator('#main-content img').all():
  src=img.get_attribute('src')or''
  if src.startswith(('data:','http:','https:')):continue
  f=S/urllib.parse.unquote(src.split('?')[0]);
  if f.is_file():
   m='image/jpeg'if f.suffix.lower()in['.jpg','.jpeg']else'image/svg+xml'if f.suffix=='.svg'else'image/png'
   img.evaluate('(e,s)=>e.src=s','data:'+m+';base64,'+base64.b64encode(f.read_bytes()).decode())
def scan(p,route):
 p.evaluate('(h)=>{location.hash="#/"+h}',route);p.wait_for_timeout(130)
 out=p.evaluate('''()=>{const c=document.querySelector('#main-content'); const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return {page:c.dataset.page,error:c.dataset.error||null,length:c.innerText.length,dupes:ids.filter((x,i)=>ids.indexOf(x)!==i),dead:[...c.querySelectorAll('[data-scroll]')].filter(x=>!document.getElementById(x.dataset.scroll)).map(x=>x.dataset.scroll),view:innerWidth,width:document.documentElement.scrollWidth,stage:window.R47.state.stage,options:[...document.querySelectorAll('#r42-stage option')].map(x=>x.value),cards:c.querySelectorAll('.r43-equip').length,oldLinks:[...document.querySelectorAll('a[href]')].map(x=>x.getAttribute('href')).filter(x=>x.startsWith('#/')&&/(?:stage=e0[123]|cp=l0[1-6])/.test(x)),object:c.innerText.includes('[object Object]')}}''')
 urls=p.evaluate('''()=>[...document.querySelectorAll('#main-content a[href],#main-content img[src]')].map(e=>e.getAttribute(e.tagName==='A'?'href':'src'))''')
 out['missingLocal']=[]
 for url in urls:
  if not url or url.startswith(('#','https:','http:','data:','blob:','javascript:','mailto:','about:')):continue
  f=S/urllib.parse.unquote(url.split('#')[0].split('?')[0])
  if not f.exists():out['missingLocal'].append(url)
 out['route']=route;log['views'].append(out)
 return out
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 if mode=='smoke':
  f=open(K/'server.log','w');sv=subprocess.Popen([sys.executable,'-m','http.server','8747','--bind','127.0.0.1','--directory',str(S)],stdout=f,stderr=f);(K/'server.pid').write_text(str(sv.pid));time.sleep(.5)
  for url in ['http://127.0.0.1:8747/index.html',(S/'index.html').as_uri()]:
   p=b.new_page()
   try:p.goto(url,timeout=6500);p.wait_for_timeout(200);log['navigation'].append({'url':url,'status':'loaded','title':p.title()})
   except Exception as e:log['navigation'].append({'url':url,'status':str(e).splitlines()[0]})
   p.close()
 p=b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:log['errors'].append(str(e)))
 p.set_content(stripped);p.add_style_tag(path=str(S/cfg['style']))
 for s in scripts:p.add_script_tag(path=str(S/s))
 p.add_script_tag(path=str(S/cfg['references']))
 p.wait_for_selector('[data-ready="true"]',timeout=10000)
 if mode=='smoke':
  routes=['home','my-gear','my-skills','gear?stage=e04','item/bow?stage=e04&tab=target','item/helmet?stage=e04&tab=craft','gear?stage=e05','gear?stage=e06','atlas-starter','atlas-unlock','atlas-choose','atlas/expedition?tab=choices','atlas/expedition?tab=play','atlas/lineage-gems?tab=masters','tools/filters','filter-guide?file=01','tools/builds','guide?stage=e04&tab=next']
  shots={'home':'home','my-gear':'equipment','atlas-starter':'atlas','tools/filters':'filters','gear?stage=e05':'future'}
  for r in routes:
   sc=scan(p,r)
   if r in shots:paint_images(p);p.wait_for_timeout(120);p.screenshot(path=str(K/(shots[r]+'.png')),full_page=False)
   if sc['error']:(K/('error-'+str(len(log['views']))+'.txt')).write_text(p.locator('#main-content').inner_text())
  p.set_viewport_size({'width':390,'height':844});scan(p,'home');p.screenshot(path=str(K/'mobile.png'),full_page=False)
 elif mode=='matrix':
  a=sys.argv[2] if len(sys.argv)>2 else 'e04'
  if a.startswith('e'):
   for slot in ['bow','quiver','helmet','body','gloves','boots','amulet','belt','ring1','ring2','weapon2','quiver2','life_flask','mana_flask','charm1','charm2','charm3','jewels']:
    for tab in ['target','craft','finish']:scan(p,f'item/{slot}?stage={a}&tab={tab}')
   for r in ['gear','character?tab=skills','character?tab=tree','character?tab=play','character?tab=check','gems','special-gems','jewels','special-jewels','guide?tab=overview','guide?tab=skills','guide?tab=craft','guide?tab=next','early-craft','craft-timing','supplies']:
    scan(p,r+('&'if'?'in r else'?')+'stage='+a)
  elif a=='atlas':
   for ident in ['expedition','ritual-belts','currency-abyss','breach-rares','abyss-rares','lineage-gems','deli-rush']:
    for tab in ['tree','choices','masters','setup','play','source']:scan(p,f'atlas/{ident}?tab={tab}')
   for r in ['atlas-starter','atlas-starter?tab=tree','atlas-starter?tab=choices','atlas-starter?tab=rules','atlas-unlock','atlas-choose','atlas-choices','atlas-choices?profile=crit','learn/map-run','learn/readiness','learn/ascendancy','learn/permanent','learn/activities','tools/dictionary','tools/library','tools/selection-guide','tools/capture-audit','tools/names','filter-check?file=01']:
    scan(p,r)
  log['batch']=a
 elif mode=='tasks':
  def ck(name,ok,details=None):log['tasks'].append({'task':name,'pass':bool(ok),'detail':details})
  scan(p,'gear?stage=e04');p.select_option('#r42-stage','e05');p.wait_for_timeout(150);ck('选择后续高配',p.evaluate('R47.state.stage')=='e05')
  p.locator('#main-nav a').filter(has_text='异界：从入门继续').click();p.wait_for_timeout(150);ck('后续人物查看后仍能进异界入门',p.locator('#main-content').get_attribute('data-page')=='atlas-starter')
  ck('异界不切人物',p.evaluate('R47.state.stage')=='e05')
  p.locator('#main-content a').filter(has_text='七套后续方案').first.click();p.wait_for_timeout(150);ck('七套异界入口保留',p.locator('.r47-atlas-grid>article').count()==7)
  p.locator('.r47-atlas-grid>article').nth(5).locator('a').filter(has_text='大节点选什么').click();p.wait_for_timeout(150);ck('血脉方案作者已选13条',p.locator('.r43-node').count()==13)
  scan(p,'tools/filters');a=p.locator('a[download]').first;ck('当前原版01网页下载入口',a.get_attribute('href')=='原版过滤器_从这里选/01_Fubgun_Early_Mapping.filter');ck('四原版仍在',p.locator('a[download]').count()==4)
  scan(p,'tools/builds');ck('只剩3个构筑下载',p.locator('#main-content a[download]').count()==3)
  for q in ['暴击混合防御','高配冰射','非暴击中期','初入异界','底材','蛇鳞外套','击杀回蓝','森林','我的左戒','过滤器']:
   xs=p.evaluate('(q)=>R47.search(q)',q);ck('搜索不返回前三人物：'+q,all(x.get('params',{}).get('stage')not in['e01','e02','e03']and not x.get('params',{}).get('cp')for x in xs),len(xs))
  scan(p,'my-gear');p.locator('a[data-scroll="r47-own-ring1"]').click();ck('我的戒指定位',p.locator('#r47-own-ring1').count()==1)
  p.locator('#r47-own-ring1 .r43-equip a[href*="tab=craft"]').first.click();p.wait_for_timeout(120);ck('我的戒指进入同阶段制作',p.evaluate('R47.state.stage')=='e04'and p.locator('#main-content').get_attribute('data-page')=='item')
  for r in ['gear?stage=e01','gear?stage=e02','character?stage=e03','gear?cp=l03']:
   out=scan(p,r);ck('旧人物链接不会返回过时BD：'+r,out['stage']=='e04'and out['options']in[[],['e04','e05','e06']])
  scan(p,'gear?stage=e06');ck('实装只读提示',('只读'in p.locator('#main-content').inner_text()))
  for width in [390,768,1024,1440,1920]:
   p.set_viewport_size({'width':width,'height':900})
   for r in ['home','my-gear','gear?stage=e04','gear?stage=e05','atlas-choose','atlas/lineage-gems?tab=choices','tools/filters','item/helmet?stage=e04&tab=craft']:
    out=scan(p,r);ck('页面宽度 '+str(width)+' '+r,out['width']<=out['view']+1,{'width':out['width'],'view':out['view']})
 p.close();b.close()
name=mode+('-'+log.get('batch','')if mode=='matrix'else'')
(K/(name+'.json')).write_text(json.dumps(log,ensure_ascii=False,indent=2))
bad=[x for x in log['views']if x['error']or x['dupes']or x['dead']or x['object']or x['oldLinks']or x.get('missingLocal')or x['width']>x['view']+1]
print(json.dumps({'mode':name,'navigation':log['navigation'],'errors':log['errors'],'views':len(log['views']),'bad':bad,'tasks':len(log['tasks']),'taskFails':[x for x in log['tasks']if not x['pass']]},ensure_ascii=False,indent=2))
