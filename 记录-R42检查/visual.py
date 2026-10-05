import asyncio,json,re,base64,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));from smoke import ROOT,CHECK,load,go
from playwright.async_api import async_playwright
async def images(page):
 for r in await page.locator('#main-content img').evaluate_all("els=>els.map((e,i)=>({i,src:e.getAttribute('src')}))"):
  if not r['src'] or r['src'].startswith(('data:','http:','https:','blob:')):continue
  p=ROOT/r['src']
  if p.is_file():
   mime='image/png' if p.suffix.lower()=='.png' else 'image/jpeg' if p.suffix.lower() in ['.jpg','.jpeg'] else 'image/webp' if p.suffix=='.webp' else 'image/svg+xml'
   await page.locator('#main-content img').nth(r['i']).evaluate('(e,s)=>e.src=s','data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode())
 await page.wait_for_timeout(100)
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  p=await b.new_page(viewport={'width':1440,'height':1000});await load(p,True)
  for name,r in [('route24','#/guide?cp=l03&tab=skills'),('reserve16','#/guide?cp=l02&tab=next'),('gear01','#/gear?stage=e01'),('craft','#/item/boots?cp=l03&tab=craft&kind=magic1&goal=life'),('crit','#/item/bow?stage=e05&tab=craft'),('atlas','#/atlas/expedition?tab=choices'),('learning','#/learn/permanent?cp=l03'),('native','#/reference?doc=runes-all.html'),('library','#/tools')]:
   d=await go(p,r);await images(p);await p.screenshot(path=str(CHECK/(name+'.png')),full_page=False);print(name,d['error'],await p.locator('#main-content').evaluate("e=>({obj:e.innerText.includes('[object Object]'),undef:e.innerText.includes('undefined'),height:e.scrollHeight})"))
  await p.set_viewport_size({'width':390,'height':844});await go(p,'#/guide?cp=l03&tab=skills');await p.screenshot(path=str(CHECK/'mobile.png'),full_page=False)
  await b.close()
if __name__=='__main__':asyncio.run(main())
