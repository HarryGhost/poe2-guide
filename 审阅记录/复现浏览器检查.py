
from pathlib import Path
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
checks=[];errors=[]
def ck(name,val,detail=""):checks.append({"test":name,"passed":bool(val),"detail":detail})
def html_inline(name):
 s=BeautifulSoup((ROOT/name).read_text(),"html.parser")
 for tag in s.select('link[rel="stylesheet"]'):
  style=s.new_tag('style');style.string=(ROOT/tag['href']).read_text();tag.replace_with(style)
 for tag in s.select('script[src]'):
  tag.string=(ROOT/tag['src']).read_text();del tag['src']
 return str(s)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path="/usr/bin/chromium",headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
 for w,h in [(1366,900),(1920,1080),(1024,768),(390,844)]:
  p=b.new_page(viewport={"width":w,"height":h},device_scale_factor=1)
  p.on('pageerror',lambda e: errors.append(str(e)))
  p.set_content(html_inline("craft.html"),wait_until="load")
  ck(str(w)+" default Early/bow",p.evaluate("__EARLY_CRAFT.stage==='early'&&__EARLY_CRAFT.item==='bow'"))
  ck(str(w)+" no body horizontal overflow",p.evaluate("document.documentElement.scrollWidth<=innerWidth"))
  for sid in ['early','mid','hybrid','crit','uber']:
   p.locator('[data-craft-stage="'+sid+'"]').click()
   ck(str(w)+" stage "+sid,p.evaluate("__EARLY_CRAFT.stage")==sid and p.locator('[data-stage-panel]:visible').count()==1)
  p.locator('[data-craft-stage="early"]').click()
  for item in ['bow','quiver','body','helmet','gloves','boots','amulet','belt','rings','flasks','charms','jewels']:
   p.locator('[data-early-choice="'+item+'"]').click()
   ck(str(w)+" item "+item,p.evaluate("__EARLY_CRAFT.item")==item and p.locator('[data-early-item]:visible').count()==1)
   ck(str(w)+" fit "+item,p.evaluate("document.documentElement.scrollWidth<=innerWidth"))
  p.locator('[data-early-choice="bow"]').click()
  p.evaluate("window.scrollTo(0,0)");p.wait_for_timeout(160)
  if w==1366:p.screenshot(path=str(ROOT/"检查与预览/01_Early起步打造_1366.png"))
  if w==390:p.screenshot(path=str(ROOT/"检查与预览/02_Early起步打造_390.png"))
  p.locator('#density-toggle').click()
  ck(str(w)+" readable density",p.locator('body').get_attribute('data-density')=='comfortable')
  p.locator('#search-open').click()
  p.locator('#site-search').fill('Early起步打造')
  ck(str(w)+" search includes lessons",p.locator('.search-results a').count()>=12)
  p.locator('[data-close="search-dialog"]').click()
  p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
  ck(str(w)+" print exposes all lessons",p.locator('[data-early-item]:visible').count()==12)
  p.evaluate("window.dispatchEvent(new Event('afterprint'))")
  ck(str(w)+" print returns to selected",p.locator('[data-early-item]:visible').count()==1)
  p.close()
 for name in ['craft-advanced.html','craft-all.html','craft-early-all.html','e01.html']:
  p=b.new_page(viewport={"width":1366,"height":900})
  p.on('pageerror',lambda e:errors.append(str(e)))
  p.set_content(html_inline(name),wait_until='load')
  ck(name+" no body overflow",p.evaluate("document.documentElement.scrollWidth<=innerWidth"))
  if name=='craft-advanced.html':
   ck("8 advanced recipes remain",p.locator('[data-recipe]').count()==8)
   for rid in ['bow-noncrit','bow-crit','quiver-standard','quiver-advanced','amulet','helmet-stable','helmet-random','emerald']:
    p.locator('[data-craft-choice="'+rid+'"]').click()
    ck("advanced "+rid,p.evaluate("__CRAFT_TEST.current")==rid and p.locator('[data-recipe]:visible').count()==1)
   p.locator('#craft-material-filter').fill('寻觅')
   ck('material search',p.locator('.craft-material:visible').count()>=1)
  if name=='craft-all.html':ck('all advanced visible without gating',p.locator('[data-recipe]:visible').count()==8)
  if name=='craft-early-all.html':ck('all Early lessons visible',p.locator('[data-early-item]:visible').count()==12)
  if name=='e01.html':
   ck('Early direct beginner craft entry',p.locator('a[href="craft.html"]').count()>=1)
   ck('Early skills unchanged in rendered page',p.locator('.skill-row').count()>=10)
  p.close()
 # JS-disabled equivalent uses original static DOM with JS omitted in content.
 for name in ['craft.html','craft-early-all.html','craft-advanced.html','craft-all.html']:
  p=b.new_page(viewport={"width":1366,"height":900},java_script_enabled=False)
  p.set_content(html_inline(name),wait_until='load')
  expected=12 if name.startswith('craft-early') or name=='craft.html' else 8
  selector='[data-early-item]' if expected==12 else '[data-recipe]'
  ck(name+' without JS full content',p.locator(selector+':visible').count()==expected)
  p.close()
 b.close()
ck('no page JS errors',len(errors)==0,repr(errors))
result={"mode":"Chromium memory rendering of original HTML with same local CSS/JS inlined; file URL is blocked in this environment. Not deployment/game testing.","checks":checks,"errors":errors,"summary":{"checks":len(checks),"failures":sum(not c['passed'] for c in checks)}}
(ROOT/"检查与预览/02_浏览器交互检查.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result["summary"]))
