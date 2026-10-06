from pathlib import Path
import re,json,threading,http.server,functools
from playwright.sync_api import sync_playwright
OUT=Path('/mnt/data/poe2_Fubgun_C_R38'); W=Path('/mnt/data/r38_work')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(Quiet,directory=str(OUT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
logs=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:logs.append(str(e)))
 actual=[];mode=''
 for url in ['http://127.0.0.1:8765/index.html#/gems?stage=e01',OUT.as_uri()+'/index.html#/gems?stage=e01']:
  try:
   response=page.goto(url,wait_until='load',timeout=12000)
   page.wait_for_selector('h1',timeout=5000)
   assert page.locator('.gem-summary').count()==1
   actual.append({'url':url,'ok':True});mode='actual '+url.split(':')[0];break
  except Exception as e:actual.append({'url':url,'ok':False,'error':str(e)[:1000]})
 if not mode:
  html=(OUT/'index.html').read_text()
  html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(OUT/m[1]).read_text()+'</style>',html)
  html=re.sub(r'<script src="([^"]+)"></script>',lambda m:'<script>'+(OUT/m[1]).read_text().replace('</script','<\\/script')+'</script>',html)
  page.goto('about:blank');page.set_content(html,wait_until='load');page.evaluate("location.hash='#/gems?stage=e01'")
  page.wait_for_selector('.gem-summary');mode='about:blank with actual generated HTML/CSS/JS inlined'
 page.screenshot(path=str(W/'gems_e01_first.png'),full_page=False)
 data={'navigation':actual,'mode':mode,'errors':logs,'title':page.title(),'h1':page.locator('h1').inner_text(),'rows':page.locator('[data-gem-id]').count(),'navCount':page.locator('#main-nav>a.nav-item').count(),'overflow':page.evaluate('({window:innerWidth,body:document.documentElement.scrollWidth})')}
 (W/'smoke.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print(json.dumps(data,ensure_ascii=False,indent=2))
 browser.close()
server.shutdown()
