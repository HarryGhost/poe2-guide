from pathlib import Path
import json,traceback
from playwright.sync_api import sync_playwright
from browser_memory import load,ROOT
OUT=ROOT/'检查与预览';S=json.loads((ROOT/'data/全站阶段与核算.json').read_text());result=[]
def chk(name,ok,detail=None):result.append(dict(name=name,passed=bool(ok),detail=detail))
errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1366,'height':900},reduced_motion='reduce')
 def get(name):
  p=ctx.new_page();p.on('pageerror',lambda err:errors.append({'page':name,'error':str(err)}));load(p,name);return p
 # Every selectable profile. Real in-memory browser, no fake storage.
 for st in S:
  page=get(st['file'])
  for i,p in enumerate(st['profiles']):
   page.select_option('#profile-select',str(i))
   vals={k:max(r[k] for r in p['rows'] if r.get('skillKey') not in st['defaultDisabled']) for k in ['str','dex','int']}
   for k,v in vals.items():chk(st['id']+'/'+p['id']+' displayed '+k,page.locator('#total-'+k).inner_text()==str(v))
   chk(p['id']+' two selectors synchronized',page.locator('#gear-profile-select').input_value()==str(i))
   chk(p['id']+' one matching gear visible',page.locator('[data-profile-gear]:visible').count()==1 and page.locator('[data-profile-gear]:visible').get_attribute('data-reference-id')==p['referenceId'])
   chk(p['id']+' gem summary follows profile',str(p['gemlevel'])+' 级' in page.locator('#profile-gem-summary').inner_text())
   for r in p['rows']:
    if r['category'].startswith('装备'):
     chk(p['id']+' visible gear '+r['label'],r['label'].replace('：不另带三维需求的普通底材黄装','：无额外三维需求的常规黄装') in page.locator('[data-profile-gear]:visible').inner_text())
   chk(p['id']+' original samples initially collapsed',not page.locator('#author-gear-records').evaluate('(x)=>x.open'))
  if st['profiles']:
   # Select via gear control, then empty requirement should invalidate totals and be mirrored.
   page.select_option('#gear-profile-select','0')
   chk(st['id']+' gear selector drives hero',page.locator('#profile-select').input_value()=='0')
   page.locator('#attribute-ledger').evaluate('(e)=>e.open=true')
   inp=page.locator('[data-attr-index="0"][data-attr-kind="dex"]');inp.fill('')
   chk(st['id']+' blank invalid, never zero',page.locator('#total-dex').inner_text()=='待核对')
   chk(st['id']+' edits visibly marked',page.locator('#profile-edited-note').is_visible())
   chk(st['id']+' blank reflected in gear',page.locator('[data-bound-req="0:0:dex"]').inner_text()=='待核对')
   inp.fill('222');chk(st['id']+' edited requirement applied',page.locator('#total-dex').inner_text()=='222')
   chk(st['id']+' edited gear sync',page.locator('[data-bound-req="0:0:dex"]').inner_text()=='222')
   page.locator('#attr-reset').click();chk(st['id']+' reset edit marker',not page.locator('#profile-edited-note').is_visible())
  chk(st['id']+' all 12 stages linked',page.locator('.sidebar a[href^="l0"]').count()==6 and page.locator('.sidebar a[href^="e0"]').count()==6)
  page.close()
 # Targeted novice safety regression.
 page=get('e01.html')
 checktext=page.locator('.transition-card .checklist').inner_text()
 chk('Early edge keeps noncrit, does not require ES','不要求先做暴击弓或护盾头' in checktext)
 page.locator('#verified-node-help').evaluate('(e)=>e.open=true')
 page.locator('[data-node-jump="shock6"]').click()
 chk('verified node jump opens records',page.locator('#node-records').evaluate('(e)=>e.open'))
 chk('verified node jump filters exact id',page.locator('#node-search').input_value()=='shock6' and page.locator('#node-records tbody tr:visible').count()==1)
 page.locator('#keys-open').click();page.locator('[data-key-edit="snipe"]').fill('F9');page.locator('#key-save').click()
 chk('remap key in skills and rotation',all(t=='F9' for t in page.locator('[data-key-label="snipe"]').all_text_contents()))
 page.locator('[data-copy="combat"]').click()
 chk('clipboard unavailable has manual copy fallback',page.locator('#copy-dialog').evaluate('(d)=>d.open'))
 chk('manual copy contains actual remapped key','F9' in page.locator('#copy-text').input_value())
 page.locator('[data-close="copy-dialog"]').click()
 page.locator('#search-open').click();page.locator('#site-search').fill('富豪')
 chk('search includes worked examples',page.locator('#search-results').inner_text().find('打造实例')>=0)
 page.locator('[data-close="search-dialog"]').click()
 page.locator('#spirit-total').fill('1');chk('budget marks insufficient','缺少' in page.locator('#budget-result').inner_text())
 page.locator('#spirit-total').fill('1000');page.locator('#budget-confirmed').check();chk('final-value confirmation required','已录入最终值' in page.locator('#budget-result').inner_text())
 chk('no storage permissions handled without crashing','不能保存' in page.locator('#toast').inner_text())
 page.close()
 page=get('l03.html');chk('optional FrostBomb off by default',page.locator('#total-int').inner_text()=='25')
 page.locator('[data-skill-enable="fb"]').check();chk('optional FrostBomb raises full int to41',page.locator('#total-int').inner_text()=='41');page.close()
 page=get('e05.html');page.locator('#spirit-total').fill('300');chk('blank life reservation not counted as0','尚未填全' in page.locator('#budget-result').inner_text());page.close()
 page=get('craft-examples.html')
 for c in json.loads((ROOT/'data/打造教学实例.json').read_text())['cases']:
  page.locator('.case-nav a[href="#'+c['id']+'"]').click()
  page.wait_for_function("id => document.querySelector('[data-case]:not([hidden])')?.id===id",arg=c['id'],timeout=4000)
  chk(c['id']+' selected without gate',page.locator('[data-case]:visible').count()==1 and page.locator('[data-case]:visible').get_attribute('id')==c['id'])
 page.locator('#bow-math-demo').click();ar=page.locator('#bow-a-result').inner_text();br=page.locator('#bow-b-result').inner_text()
 chk('physical arithmetic example 180 and196','180' in ar and '196' in br)
 chk('rate comparison does not assert winner','不构成完整输出或换装结论' in page.locator('#bow-math-result').inner_text())
 page.locator('[data-bow="b"][data-field="max"]').fill('1');chk('inverted range blocked','最大伤害不能小于' in page.locator('#bow-b-result').inner_text())
 page.locator('#bow-math-clear').click();chk('empty arithmetic stays incomplete','未填完整' in page.locator('#bow-a-result').inner_text())
 page.evaluate("window.dispatchEvent(new Event('beforeprint'))");chk('printing shows all cases',page.locator('[data-case]:visible').count()==6)
 page.evaluate("window.dispatchEvent(new Event('afterprint'))");chk('printing restores current case',page.locator('[data-case]:visible').count()==1)
 page.close()
 # Existing crafting navigation and comparison kept.
 page=get('craft.html');page.locator('[data-craft-stage="crit"]').click();chk('later crafting always accessible',page.locator('[data-stage-panel="crit"]').is_visible());page.locator('[data-craft-stage="early"]').click();page.locator('[data-early-choice="bow"]').click();chk('Early example entry exists',page.locator('#early-bow a[href="craft-examples.html#blue-bow"]').count()==1);page.close()
 page=get('compare.html');page.select_option('#compare-from','e03');page.select_option('#compare-to','e04');page.locator('#compare-run').click();chk('comparison works','风舞者' in page.locator('#compare-result').inner_text());page.close()
 chk('no JavaScript page errors',not errors,errors)
 browser.close()
report={'environment':'Chromium; original HTML and unchanged local CSS/JS bytes inlined in memory. Browser policy blocks localhost network. Real file/HTTP deployment and genuine localStorage persistence NOT tested. Unavailable-storage and clipboard fallbacks tested.','total':len(result),'passed':sum(r['passed'] for r in result),'failed':[r for r in result if not r['passed']],'checks':result}
(OUT/'浏览器交互回归检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
