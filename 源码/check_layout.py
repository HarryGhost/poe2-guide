from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from browser_memory import ROOT,load
OUT=ROOT/'检查与预览';shots=OUT/'页面预览';shots.mkdir(exist_ok=True)
checks=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=b.new_context(viewport={'width':1366,'height':900},reduced_motion='reduce')
 for file in sorted(ROOT.glob('*.html')):
  page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));load(page,file.name)
  for width in [1366,1920,960,390]:
   page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(35)
   w=page.evaluate('({vw:innerWidth,body:document.body.scrollWidth,doc:document.documentElement.scrollWidth})')
   checks.append({'page':file.name,'width':width,'passed':max(w['body'],w['doc'])<=width+1,'observed':w})
  if file.name in ['index.html','e02.html','e03.html','e04.html','craft-examples.html']:
   page.set_viewport_size({'width':1366,'height':900})
   page.evaluate('scrollTo(0,0)');page.wait_for_timeout(80)
   page.screenshot(path=str(shots/(file.stem+'_首屏.png')))
   if file.name in ['index.html','e02.html','e03.html','e04.html']:
    page.locator('.transition-card').screenshot(path=str(shots/(file.stem+'_进阶清单.png')))
   if file.name=='index.html':
    page.select_option('#profile-select','1');page.wait_for_timeout(3650)
    page.locator('#gear').screenshot(path=str(shots/'Early_展示底材对应装备.png'))
    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(shots/'Early_切换后属性和技能.png'))
   if file.name=='craft-examples.html':
    page.locator('.case-nav a[href="#regal-or-essence"]').click();page.wait_for_timeout(100)
    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(shots/'打造_升黄分岔示例.png'))
    page.set_viewport_size({'width':390,'height':900});page.evaluate('scrollTo(0,0)');page.screenshot(path=str(shots/'打造_窄屏.png'))
  page.close()
 b.close()
report=dict(environment='original HTML and resource bytes in memory, Chromium rendering; no actual hosted navigation',total=len(checks),passed=sum(c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],js_errors=errors,checks=checks)
(OUT/'页面宽度与渲染检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
