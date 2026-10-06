from pathlib import Path
import json,asyncio,sys
sys.path.insert(0,str(Path(__file__).parent));from smoke import ROOT,CHECK,load
from playwright.async_api import async_playwright
async def main():
 result={'states':[],'layouts':[],'pageErrors':[]}
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:result['pageErrors'].append(str(e)));await load(p,True)
  async def check(r):
   return await p.evaluate('''r=>{history.replaceState(null,"",r);render();const m=document.querySelector('#main-content'),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return {error:m.dataset.error||null,dups:ids.filter((v,i,a)=>a.indexOf(v)<i),overflow:document.documentElement.scrollWidth>innerWidth+1,readonly:!document.querySelector('#c41-kind'),iframe:!!m.querySelector('iframe'),bad:/undefined|\\[object Object\\]/.test(m.innerText)}}''',r)
  for ctx in ['l02','l04','e01','e04','e06']:
   for slot in ['bow','quiver','helmet','body','gloves','boots','amulet','ring1','ring2','belt']:
    for kind in ['unknown','white','magic1','magic2','rare2','rare3','rare4','rare5','rare6','blocked']:
     q=('cp='if ctx[0]=='l'else'stage=')+ctx;r='#/item/'+slot+'?'+q+'&tab=craft&route=early-'+('rings'if slot.startswith('ring')else slot)+'&kind='+kind
     inf=await check(r);result['states'].append({'route':r,**inf,'ok':not(inf['error']or inf['dups']or inf['bad']or inf['iframe'])and(ctx!='e06'or inf['readonly'])})
   (CHECK/'states-partial.json').write_text(json.dumps(result,ensure_ascii=False));print('context',ctx,flush=True)
  for width in [390,768,1024,1440,1920]:
   await p.set_viewport_size({'width':width,'height':950})
   for r in ['#/gear?stage=e01','#/guide?cp=l03&tab=skills','#/guide?cp=l02&tab=next','#/item/boots?cp=l03&tab=craft&kind=magic1&goal=life','#/item/bow?stage=e05&tab=craft','#/learn/permanent?cp=l02&part=1','#/atlas/expedition?tab=masters','#/atlas-choices?group=biome','#/tools/filters','#/filter-check']:
    inf=await check(r);result['layouts'].append({'width':width,'route':r,**inf,'ok':not(inf['overflow']or inf['error']or inf['dups']or inf['bad'])})
   print('width',width,flush=True)
  result['summary']={'states':len(result['states']),'stateFailures':sum(not x['ok']for x in result['states']),'layouts':len(result['layouts']),'layoutFailures':sum(not x['ok']for x in result['layouts']),'pageErrors':len(result['pageErrors'])}
  (CHECK/'states-layout-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['summary']));print(json.dumps([x for x in result['states']+result['layouts']if not x['ok']],ensure_ascii=False)[:5000]);await b.close()
if __name__=='__main__':asyncio.run(main())
