import asyncio,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));from smoke import ROOT,CHECK,load,go
from visual import images
from playwright.async_api import async_playwright
async def main():
 out=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1440,'height':1050});await load(p,True)
  for name,r in [('R42_剧情与转型_预览','#/guide?cp=l03&tab=skills'),('R42_阶段准备_预览','#/guide?cp=l02&tab=next'),('R42_全身目标_预览','#/gear?stage=e01'),('R42_异界方案_预览','#/atlas/expedition?tab=choices')]:
   await go(p,r);await images(p);await p.wait_for_timeout(250);await p.screenshot(path='/mnt/data/'+name+'.png',full_page=False)
  await go(p,'#/item/boots?cp=l03&tab=craft&kind=magic1&goal=life');card=p.locator('.q42-essences article').filter(has=p.get_by_role('heading',name='次级身躯精华',exact=True));await card.get_by_role('link',name='我有这颗，核对使用步骤').click();await p.wait_for_timeout(250);await p.evaluate('scrollTo(0,0)');await p.screenshot(path='/mnt/data/R42_逐步打造_预览.png',full_page=False)
  await p.set_viewport_size({'width':390,'height':844});await go(p,'#/guide?cp=l03&tab=skills');await p.wait_for_timeout(300);await p.screenshot(path='/mnt/data/R42_手机阅读_预览.png',full_page=False)
  rect=await p.locator('#sidebar').bounding_box();out.append({'name':'移动端默认菜单完全收起','ok':rect['x']+rect['width']<=1,'rect':rect})
  await p.locator('#menu-button').click();await p.wait_for_timeout(250);rect=await p.locator('#sidebar').bounding_box();out.append({'name':'点击菜单后完整展开','ok':abs(rect['x'])<=1,'rect':rect})
  await p.locator('#main-nav a').filter(has_text='人物配置').first.click();await p.wait_for_timeout(250);rect=await p.locator('#sidebar').bounding_box();out.append({'name':'点击分区后菜单收起且保留剧情','ok':rect['x']+rect['width']<=1 and 'cp=l03' in p.url,'url':p.url})
  (CHECK/'mobile-menu-final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False));await b.close()
asyncio.run(main())
