from pathlib import Path
import json,asyncio,sys,textwrap
from urllib.parse import unquote,urlsplit
sys.path.insert(0,str(Path(__file__).parent));from smoke import ROOT,CHECK,load
from playwright.async_api import async_playwright
D=json.loads(Path('/mnt/data/r42_work/data41.json').read_text());G=json.loads(Path('/mnt/data/r42_work/src/guide42.json').read_text())
code=(CHECK/'audit.py').read_text();exec(textwrap.dedent(code[code.index('  routes=[]'):code.index('  for ix,r in enumerate(routes):')]))
(CHECK/'route-matrix.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2))
start=int(sys.argv[1]);end=int(sys.argv[2]);result=[]
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1440,'height':1000});await load(p,True)
  for idx,r in enumerate(routes[start:end],start):
   await p.evaluate('(r)=>{history.replaceState(null,"",r);render();}',r)
   info=await p.evaluate('''()=>{const m=document.querySelector('#main-content'),ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return {error:m.dataset.error||null,duplicates:ids.filter((v,i,a)=>a.indexOf(v)<i),iframe:m.querySelectorAll('iframe').length,repairs:window.q42AnchorRepairs||[],undefined:/undefined|\\[object Object\\]/.test(m.innerText),overflow:document.documentElement.scrollWidth>innerWidth+1,local:[...m.querySelectorAll('a[href],img[src]')].map(e=>e.getAttribute(e.tagName==='IMG'?'src':'href')).filter(h=>h&&!h.startsWith('#')&&!/^(https?:|data:|blob:|mailto:)/.test(h))}}''')
   missing=[]
   for v in info.pop('local'):
    f=unquote(urlsplit(v).path)
    if f and not(ROOT/f).is_file()and not f.startswith('R42_'):missing.append(v)
   info['missingFiles']=missing;info['route']=r;info['ok']=not(info['error']or info['duplicates']or info['iframe']or info['undefined']or info['overflow']or missing);result.append(info)
   if idx%100==0:(CHECK/f'scan-{start:04}-{end:04}-partial.json').write_text(json.dumps(result,ensure_ascii=False))
  (CHECK/f'scan-{start:04}-{end:04}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('views',len(result),'failed',len([x for x in result if not x['ok']]));print(json.dumps([x for x in result if not x['ok']],ensure_ascii=False)[:3000]);await b.close()
if __name__=='__main__':asyncio.run(main())
