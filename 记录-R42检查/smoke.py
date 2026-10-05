from pathlib import Path
import re,json,asyncio,threading,http.server,functools,base64
from playwright.async_api import async_playwright
ROOT=Path('/mnt/data/poe2_Fubgun_C_R42'); CHECK=Path('/mnt/data/r42_work/checks')
html=(ROOT/'index.html').read_text()
async def load(page, full=False):
 css=re.findall(r'<link rel="stylesheet" href="([^"]+)"[^>]*>',html)
 h=html
 for p in css:h=h.replace(next(x.group() for x in re.finditer(r'<link[^>]+>',h) if p in x.group()),'<style>'+ (ROOT/p).read_text()+'</style>')
 for m in list(re.finditer(r'<script src="([^"]+)"[^>]*></script>',h)):
  text=(ROOT/m.group(1)).read_text();h=h.replace(m.group(),'<script>'+text.replace('</script','<\\/script')+'</script>')
 if full:
  ref=next(ROOT.glob('assets/references.*.js'));h=h.replace('</body>','<script>'+ref.read_text().replace('</script','<\\/script')+'</script></body>')
 await page.set_content(h,wait_until='load',timeout=30000)
 await page.wait_for_function("document.documentElement.dataset.releaseReady==='true'")
async def go(page,r):
 await page.evaluate('(r)=>location.hash=r',r)
 await page.wait_for_timeout(70)
 return await page.evaluate("({h:location.hash,title:document.title,error:document.querySelector('#main-content').dataset.error||null,text:document.querySelector('#main-content').innerText.slice(0,300),overflow:document.documentElement.scrollWidth>innerWidth+1,iframes:document.querySelectorAll('#main-content iframe').length,dups:[...document.querySelectorAll('[id]')].map(x=>x.id).filter((v,i,a)=>a.indexOf(v)<i)})")
async def main():
 errors=[];report={'navigation':[],'pages':[]}
 class Quiet(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',8764),functools.partial(Quiet,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  p=await b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
  for url in ['http://127.0.0.1:8764/index.html','file://'+str(ROOT/'index.html')]:
   try:await p.goto(url,wait_until='load',timeout=15000);report['navigation'].append({'url':url,'ok':True})
   except Exception as e:report['navigation'].append({'url':url,'ok':False,'error':str(e)})
  (CHECK/'navigation.json').write_text(json.dumps(report['navigation'],ensure_ascii=False,indent=2))
  await p.close();p=await b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
  await load(p,True)
  for r in ['#/gear?stage=e01','#/guide?cp=l01','#/guide?cp=l02&tab=next','#/guide?cp=l03&tab=skills','#/guide?cp=l04&tab=craft','#/gear?cp=l05','#/guide?cp=l06&tab=next','#/item/boots?cp=l03&tab=craft&kind=magic1','#/item/bow?stage=e05&tab=craft','#/character?stage=e01','#/character?cp=l03&tab=check','#/gems?cp=l03','#/jewels?cp=l01','#/special-jewels?cp=l03','#/atlas-starter','#/atlas/expedition','#/atlas-choices','#/learn/permanent?cp=l01','#/supplies?cp=l04','#/tools','#/tools/filters','#/coverage','#/reference?doc=runes-all.html']:
   report['pages'].append(await go(p,r))
  report['errors']=errors
  (CHECK/'smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps(report,ensure_ascii=False,indent=2))
  await b.close()
 server.shutdown()
if __name__=='__main__':asyncio.run(main())
