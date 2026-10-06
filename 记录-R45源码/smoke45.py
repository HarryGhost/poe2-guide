from pathlib import Path
import json,re,base64,urllib.parse
from playwright.sync_api import sync_playwright
W=Path(__file__).parent;cfg=json.loads((W/'build_paths.json').read_text());S=Path(cfg['site']);K=W/'checks';K.mkdir(exist_ok=True)
idx=(S/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)"',idx);html=re.sub(r'<script src="[^"]+"></script>','',idx);html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',html)
log={'navigation':[],'errors':[],'routes':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for uri in ['http://127.0.0.1:8745/index.html',(S/'index.html').as_uri()]:
  p=b.new_page()
  try:p.goto(uri,timeout=6000);log['navigation'].append([uri,'loaded',p.title()])
  except Exception as e:log['navigation'].append([uri,str(e).splitlines()[0]])
  p.close()
 p=b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:log['errors'].append(str(e)))
 p.set_content(html);p.add_style_tag(path=str(S/cfg['style']))
 for js in scripts:p.add_script_tag(path=str(S/js))
 for f in(S/'assets').glob('references.*.js'):p.add_script_tag(path=str(f));break
 p.wait_for_selector('[data-ready="true"]')
 routes=['gear?stage=e01','item/bow?stage=e01&tab=target','guide?stage=e01&tab=overview','jewels?stage=e01','special-jewels?stage=e04','item/quiver?stage=e04&tab=target','atlas/expedition?tab=play','character?stage=e01&tab=tree','item/boots?cp=l03&tab=craft','item/bow?stage=e04&tab=craft','gear?stage=e06','tools/selection-guide']
 for i,h in enumerate(routes):
  p.evaluate('(h)=>location.hash="#/"+h',h);p.wait_for_timeout(160)
  for img in p.locator('#main-content img').all():
   src=img.get_attribute('src');f=S/urllib.parse.unquote(src or '')
   if f.is_file():
    ext=f.suffix.lower();m='image/jpeg'if ext in ['.jpg','.jpeg']else'image/png'if ext=='.png'else'image/svg+xml'
    img.evaluate('(e,s)=>e.src=s','data:'+m+';base64,'+base64.b64encode(f.read_bytes()).decode())
  p.wait_for_timeout(100)
  txt=p.locator('#main-content').inner_text();(K/f'smoke-{i}.txt').write_text(txt)
  scan=p.evaluate('''()=>{let c=document.querySelector('#main-content'),ids=[...c.querySelectorAll('[id]')].map(x=>x.id);return {dupes:ids.filter((v,i)=>ids.indexOf(v)!==i),dead:[...c.querySelectorAll('[data-scroll]')].filter(e=>!document.getElementById(e.dataset.scroll)).map(e=>e.dataset.scroll),width:document.documentElement.scrollWidth,view:innerWidth,objects:c.innerText.includes('[object Object]'),cards:c.querySelectorAll('[data-capture-item]').length,bases:c.querySelectorAll('.r45-base-detail').length}}''')
  log['routes'].append({'route':h,**scan,'length':len(txt)})
  p.screenshot(path=str(K/f'smoke-{i}.png'),full_page=False)
 (K/'smoke.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
 print(json.dumps(log,ensure_ascii=False,indent=2))
 b.close()
