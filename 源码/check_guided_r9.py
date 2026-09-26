"""Structural checks, local link validation and browser interaction QA for R9.
Browser uses actual generated HTML with local CSS/JS inlined via set_content.
This does not certify hosted deployment, file:// permissions, or game mechanics.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json, re, hashlib, sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from browser_memory import load, ROOT
REPORT=ROOT/'检查与预览';REPORT.mkdir(exist_ok=True)
D=json.loads((ROOT/'data/打造按步操作_R9.json').read_text())
checks=[];errors=[]
def ck(name,ok,detail=''):
 checks.append({'name':name,'passed':bool(ok),'detail':detail})
def is_dynamic(file,frag):
 if file=='craft.html':return frag in {r['id'] for r in D['routes']} or frag.startswith(('stage-','mat-')) or ('/' in frag and frag.split('/')[0] in {r['id'] for r in D['routes']})
 return False
pages={p.name:BeautifulSoup(p.read_text(),'html.parser') for p in ROOT.glob('*.html')}
for file,soup in pages.items():
 ck(file+' HTML language',soup.html.get('lang')=='zh-CN')
 ids=[x['id'] for x in soup.select('[id]')];ck(file+' duplicate IDs absent',len(ids)==len(set(ids)))
 missing=[]
 for el in soup.select('[href],[src]'):
  a=el.get('href') or el.get('src');u=urlsplit(a)
  if u.scheme or a.startswith('//'):continue
  rel=unquote(u.path);f=ROOT/rel if rel else ROOT/file
  if not f.exists():missing.append(a);continue
  frag=unquote(u.fragment)
  if frag and f.suffix=='.html' and f.name in pages:
   if not pages[f.name].find(id=frag) and not is_dynamic(f.name,frag):missing.append(a)
 ck(file+' local files and anchors',not missing,missing)
for r in D['routes']:
 ids={s['id'] for s in r['steps']}
 ck(r['id']+' unique steps',len(ids)==len(r['steps']))
 ck(r['id']+' valid state entry links',all(e['step'] in ids for e in r['entries']))
 for s in r['steps']:
  ck(r['id']+'/'+s['id']+' complete action fields',all(s.get(k) for k in ('before','action','expect','good','bad','refs')))
  ck(r['id']+'/'+s['id']+' material lookup',all(m in D['materials'] for m in s['materials']))
  ck(r['id']+'/'+s['id']+' valid next',s['next'] is None or s['next'] in ids)
  ck(r['id']+'/'+s['id']+' offline full-copy preserved',bool(pages['craft-steps-all.html'].find(id=r['id']+'--'+s['id'])))
for rid in ('early-flasks','early-charms'):
 r=next(r for r in D['routes'] if r['id']==rid)
 ck(rid+' no rare gear promotion',not any(m in ('normal-regal','normal-exalt') for s in r['steps'] for m in s['materials']))
ck('advanced 8 routes retained',set(r['id'] for r in D['routes'] if not r['id'].startswith('early-'))==set(r['id'] for r in json.loads((ROOT/'data/Fubgun_异界后期打造.json').read_text())['recipes']))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=b.new_context(viewport={'width':1366,'height':900},reduced_motion='reduce')
 def get(name):
  p=context.new_page();p.on('pageerror',lambda e:errors.append({'page':name,'error':str(e)}));load(p,name);return p
 p=get('craft.html')
 ck('fresh load defaults Early bow',p.evaluate('window.__GUIDED_CRAFT.route')=='early-bow')
 p.select_option('#g-phase','all');ck('all 20 routes selectable',p.locator('#g-route option').count()==20)
 for r in D['routes']:
  p.select_option('#g-route',r['id'])
  ck(r['id']+' navigation lists every step',p.locator('#g-step-nav button').count()==len(r['steps']))
  for s in r['steps']:
   p.locator('#g-step-nav [data-g-step="'+s['id']+'"]').click()
   ck(r['id']+'/'+s['id']+' displayed correct action',p.locator('#g-current-title').inner_text()==s['title'] and s['action'][0] in p.locator('.g-do').inner_text())
   ck(r['id']+'/'+s['id']+' visible stop instructions',s['bad'] in p.locator('.g-result.bad').inner_text())
   if s['kind']=='boundary':ck(r['id']+'/'+s['id']+' explicit non-executable notice',p.locator('#g-main .g-boundary').count()==1)
   if s['materials']:
    p.locator('#g-main [data-g-material="'+s['materials'][0]+'"]').first.click()
    ck(r['id']+'/'+s['id']+' material help',p.locator('#g-material-dialog').evaluate('(e)=>e.open') and p.locator('#g-material-title').inner_text()==D['materials'][s['materials'][0]]['zh'])
    p.locator('#g-material-close').click()
  ck(r['id']+' full selected route available',p.locator('#g-full-content .g-static-step').count()==len(r['steps']))
  ck(r['id']+' print selected route complete',p.locator('#g-print-content .g-static-step').count()==len(r['steps']))
 p.evaluate("window.__GUIDED_CRAFT.go('early-bow','augment')")
 p.locator('#g-stop').click();ck('unexpected result does not advance',p.evaluate('window.__GUIDED_CRAFT.step')=='augment' and p.locator('#g-stop-detail').is_visible())
 p.locator('#g-copy-step').click();ck('manual copy fallback displays selected step',p.locator('#g-copy-dialog').evaluate('(e)=>e.open') and '增幅石' in p.locator('#g-copy-text').input_value())
 p.locator('#g-copy-close').click();p.locator('#g-copy-route').click();ck('copy full route contains last step','不用凑满六条' in p.locator('#g-copy-text').input_value());p.locator('#g-copy-close').click()
 p.select_option('#g-entry','regal');ck('existing blue item skips white operation',p.evaluate('window.__GUIDED_CRAFT.step')=='regal')
 p.evaluate("location.hash='#amulet/resist'");p.wait_for_timeout(60);ck('URL route and step deep-link',p.evaluate('window.__GUIDED_CRAFT.route')=='amulet' and p.evaluate('window.__GUIDED_CRAFT.step')=='resist')
 p.evaluate("location.hash='#not-a-route'");p.wait_for_timeout(60);ck('invalid route safe fallback',p.evaluate('window.__GUIDED_CRAFT.route')=='early-bow')
 p.evaluate("location.hash='#%E0%A4%A'");p.wait_for_timeout(60);ck('invalid percent encoding handled',p.evaluate('window.__GUIDED_CRAFT.route')=='early-bow')
 p.evaluate("location.hash='#early-helmet'");p.wait_for_timeout(60);ck('legacy Early links supported',p.evaluate('window.__GUIDED_CRAFT.route')=='early-helmet')
 p.evaluate("location.hash='#stage-high'");p.wait_for_timeout(60);ck('stage bookmarks supported',p.evaluate('window.__GUIDED_CRAFT.phase')=='high')
 p.locator('#search-open').click();p.locator('#site-search').fill('富豪');ck('global search includes guided worksheets','打造照做' in p.locator('#search-results').inner_text());p.locator('[data-close="search-dialog"]').click()
 p.emulate_media(media='print');ck('print active route visible',p.locator('#g-print-content').is_visible() and not p.locator('#g-main').is_visible());p.emulate_media(media='screen')
 for width in (320,390,768,1024,1366,1920):
  p.set_viewport_size({'width':width,'height':900})
  for r in D['routes']:
   p.evaluate('([r,s])=>window.__GUIDED_CRAFT.go(r,s)',[r['id'],r['steps'][min(1,len(r['steps'])-1)]['id']])
   ck(str(width)+' '+r['id']+' no page overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
 p.set_viewport_size({'width':1366,'height':900})
 for rid,sid,name in [('early-bow','augment','01_Early蓝弓_一步怎么点.png'),('bow-noncrit','essence','02_非暴击弓_精华操作.png'),('amulet','resist','03_项链_每次催化收尾.png'),('emerald','capacity','04_未核实环节_明确只读.png')]:
  p.evaluate('([r,s])=>window.__GUIDED_CRAFT.go(r,s)',[rid,sid]);p.screenshot(path=str(REPORT/name),full_page=False)
 p.close()
 for file in pages:
  p=get(file);ck(file+' sidebar all12stages',p.locator('.sidebar a[href^="l0"]').count()==6 and p.locator('.sidebar a[href^="e0"]').count()==6);ck(file+' current footer', 'R9' in p.locator('.page-footer').inner_text());p.close()
 b.close()
ck('no JavaScript runtime errors',not errors,errors)
out={'version':'R9','date':'2026-09-26','method':'Generated local HTML, local scripts/styles inlined in Chromium; browser policy prevents direct file/hosted origin test. No game client test.','routes':len(D['routes']),'steps':sum(len(r['steps']) for r in D['routes']),'checks':checks,'total':len(checks),'failed':sum(not c['passed'] for c in checks),'runtime_errors':errors}
(REPORT/'R9逐项检查.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('checks',len(checks),'failed',out['failed'])
for c in checks:
 if not c['passed']:print('FAIL',c)
sys.exit(1 if out['failed'] else 0)
