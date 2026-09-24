#!/usr/bin/env python3
"""Run structural and Chromium UI regression tests. Browser rendering uses set_content.
Requires playwright, beautifulsoup4 and a Chromium executable. No network requests.
No claims about game-client import, live hosting or file:// permissions.
"""
from pathlib import Path
import json,hashlib,re,sys,copy,collections,os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'网站';D=json.loads((SITE/'_source/data.json').read_text());H=(SITE/'index.html').read_text();R=[];shots=ROOT/'检查与说明/页面截图';shots.mkdir(exist_ok=True)
def check(name,ok,detail=None):
 R.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok:print('FAIL:',name,detail,flush=True)
 if len(R)%50==0:print('CHECKPOINT',len(R),name,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check('Six original branches present',[b['number'] for b in D['branches']]==list(range(1,7)))
for b in D['branches']:
 raw=(SITE/b['download']).read_bytes();check('Original hash '+b['key'],hashlib.sha256(raw).hexdigest()==b['sha256']);check('Raw JSON preserved '+b['key'],json.loads(raw)==b['raw']);check('Node order preserved '+b['key'],[n['id'] for n in b['nodes']]==[n['id'] for n in b['raw']['passives']])
check('Raw totals',sum(len(b['raw']['skills']) for b in D['branches'])==60 and sum(len(b['nodes']) for b in D['branches'])==969 and sum(len(b['equipment']) for b in D['branches'])==91)
check('06 isolated readonly',D['branches'][5]['download'].endswith('.txt') and D['branches'][5]['ascendancyConflict'])
fixtures=[
 [('la','ra1 ea1'),('lr','con ea1'),('fb',''),('ht','con'),('bar',''),('ita',''),('pounce','')],
 [('la','ra1 ea1'),('lr','con ea1'),('fb',''),('ht','con ea1'),('bar',''),('ita','mag1'),('pounce','')],
 [('la','ra1 ea1'),('snipe','con win1 ea2'),('mark','dur1'),('ht','con ea1'),('bar',''),('ita','mag1 ea1'),('salvo','freeze con'),('fb','')],
 [('ice','ra1 ea2 bite1'),('snipe','con win1 ea2'),('mark','dur1 siphon eternal'),('hi','mag1 ea2 focus'),('bar','cdr1'),('ita','mag1 ea2'),('salvo','freeze con'),('cf','')],
 [('ice','ra1 ea2 bite2 fork'),('snipe','con win1 ea2 focus'),('mark','charged dur2 eternal'),('hi','mag1 ea2 focus'),('bar','cdr1 cast2'),('ita','short1 ea2 mag1'),('cf','prof1'),('wd','knock'),('tornado','dur2 over2 ra2')]]
for i,rows in enumerate(fixtures):
 actual=[(x['skill'],' '.join(x['supports'])) for x in D['leveling']['stages'][i]['skills']];check(f'Author stage{i+1} full connection fixture',actual==rows,actual)
check('60+ explicitly editorial',D['leveling']['stages'][5]['provenance']=='editorial_carry_forward')
check('60+ carry-forward matches42–59',D['leveling']['stages'][5]['skills']==D['leveling']['stages'][4]['skills'])
for s in D['leveling']['stages']:
 check(f'All campaign terms defined {s["number"]}',all(k in D['leveling']['terms'] for x in s['skills'] for k in [x['skill'],*x['supports']]))
check('Campaign priority differs from endgame',D['leveling']['priority']['sockets']==['狙击','冰霜射击','冰冻印记','寒冰之捷'])
check('No fabricated leveling build download',not list(SITE.glob('**/*leveling*.build')))
for path in [SITE/'index.html',SITE/'剧情练级速查.html',SITE/'六分支完整资料.html']:
 soup=BeautifulSoup(path.read_text(),'html.parser');ids=[x['id'] for x in soup.select('[id]')];check('Unique HTML ids '+path.name,len(ids)==len(set(ids)))
 check('No external scripts '+path.name,not soup.select('script[src]'))
 missing=[]
 for a in soup.select('a[href]'):
  href=a['href']
  if not href or href.startswith(('#','http:','https:','mailto:')):continue
  target=(path.parent/href.split('#')[0].split('?')[0])
  if not target.exists():missing.append(href)
 check('Local links exist '+path.name,not missing,missing)
static=BeautifulSoup((SITE/'剧情练级速查.html').read_text(),'html.parser');check('Static campaign has48 groups',len(static.select('[data-level-static]'))==48)
staticend=BeautifulSoup((SITE/'六分支完整资料.html').read_text(),'html.parser');check('Static endgame has60 groups',len(staticend.select('[data-static-skill]'))==60);check('Static endgame has969 nodes',len(staticend.select('[data-static-node]'))==969)
measure={};errors=[]
def go(pg,fragment):
 pg.evaluate('(s)=>{location.hash=s}',fragment);pg.wait_for_timeout(35)

def storage_fixture(seed=None):
 # Transparent unit fixture, not a claim that browser policy permitted real file storage.
 return '<script>window.__mockStore='+json.dumps(seed or {})+';Object.defineProperty(window,"localStorage",{value:{getItem:k=>window.__mockStore[k]??null,setItem:(k,v)=>window.__mockStore[k]=String(v),removeItem:k=>delete window.__mockStore[k]},configurable:true});</script>'

with sync_playwright() as w:
 browser=w.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 for width in [320,390,768,1440]:
  print('WIDTH',width,flush=True)
  pg=browser.new_page(viewport={'width':width,'height':900});pg.set_default_timeout(3500);pg.on('pageerror',lambda e:errors.append(str(e)));pg.set_content(H);check(f'Fresh default campaign {width}',pg.evaluate('window.__guideQA.getState().page')=='leveling')
  for b in D['branches']:
   for page in (['start','upgrade','skills','gear','tree','combat','craft','pitfalls','glossary','downloads','sources'] if b['number']==1 else ['skills','gear','tree','combat']):
    go(pg,f'{page}?bd={b["number"]}')
    ok=pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    check(f'No wholepage overflow {width}/b{b["number"]}/{page}',ok)
   go(pg,f'skills?bd={b["number"]}')
   check(f'All10 skill rows {width}/b{b["number"]}',pg.locator('#skill-cards [data-skill-id]').count()==len(b['raw']['skills']))
   count=sum(len(s['support_skills']) for s in b['raw']['skills'])
   check(f'All supports visible summaries {width}/b{b["number"]}',pg.locator('#skill-cards summary .gem-chip').count()==count)
   check(f'Summaries collapsed {width}/b{b["number"]}',pg.locator('#skill-cards details[open]').count()==0)
  for s in D['leveling']['stages']:
   for tab in (['skills','gear','combat','transition','tree','rewards'] if s['number']==4 else ['skills','transition']):
    go(pg,f'leveling?lv={s["number"]}&tab={tab}')
    check(f'Campaign tab display {width}/lv{s["number"]}/{tab}',pg.locator('#lv-pane-'+tab).is_visible())
    check(f'Campaign no overflow {width}/lv{s["number"]}/{tab}',pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
   go(pg,f'leveling?lv={s["number"]}&tab=skills')
   check(f'Campaign complete rows {width}/lv{s["number"]}',pg.locator('#level-skill-list [data-level-skill]').count()==len(s['skills']))
   check(f'Campaign complete supports {width}/lv{s["number"]}',pg.locator('#level-skill-list summary .gem-chip').count()==sum(len(x['supports']) for x in s['skills']))
  if width in [390,1440]:
   go(pg,'skills?bd=4');pg.evaluate('document.activeElement.blur()');pg.screenshot(path=str(shots/f'{width}_04技能_紧凑.png'),full_page=True)
   measure[str(width)]={'skills_list':pg.locator('#skill-cards').bounding_box(),'full_document_height':pg.evaluate('document.documentElement.scrollHeight')}
   go(pg,'leveling?lv=4&tab=skills');pg.evaluate('document.activeElement.blur()');pg.screenshot(path=str(shots/f'{width}_31级练级技能.png'),full_page=True)
   go(pg,'leveling?lv=3&tab=transition');pg.screenshot(path=str(shots/f'{width}_24到31差异.png'),full_page=True)
  pg.close()
 # Interaction regression tests.
 print('INTERACTIONS',flush=True)
 pg=browser.new_page(viewport={'width':1440,'height':900});pg.set_default_timeout(4500);pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.set_content(storage_fixture()+H);pg.evaluate('Object.defineProperty(navigator,"clipboard",{value:undefined,configurable:true})')
 go(pg,'skills?bd=5');go(pg,'leveling?lv=2&tab=skills')
 pg.locator('#level-character-level').fill('31');pg.locator('#level-character-level').dispatch_event('change')
 check('Level input selects31–41 without replacing endgame',pg.evaluate('window.__guideQA.getState().levelStage===4&&window.__guideQA.getState().current===5'))
 pg.locator('#level-filter').fill('虹吸');check('Campaign filter finds mark',pg.locator('#level-skill-list [data-level-skill]').count()==1 and pg.locator('#level-skill-list [data-level-skill]').get_attribute('data-level-skill')=='mark')
 pg.locator('#level-filter').fill('');pg.locator('[data-expand-list="level-skill-list"]').click();check('Expand all campaign rows',pg.locator('#level-skill-list details[open]').count()==8);pg.locator('[data-expand-list="level-skill-list"]').click();check('Collapse all campaign rows',pg.locator('#level-skill-list details[open]').count()==0)
 pg.locator('[data-copy-level-all]').click();check('Copy fallback complete stage',pg.locator('#copy-dialog').is_visible() and '虹吸印记' in pg.locator('#copy-text').input_value() and '31–41' in pg.locator('#copy-text').input_value());pg.locator('#copy-close').click()
 print('SPIRIT TEST',flush=True);pg.locator('#lv-tab-combat').click();pg.locator('#lv-pane-combat details').first.locator('summary').click()
 check('Empty spirit not silentlyzero',pg.locator('#level-spirit-result').get_attribute('data-status')=='incomplete')
 pg.locator('#level-spirit-total').fill('60');pg.locator('#level-spirit-other').fill('0');pg.locator('#lv-value-hi').fill('30');pg.locator('#lv-value-cf').fill('30')
 check('Campaign spirit exact balance',pg.locator('#level-spirit-result').get_attribute('data-status')=='enough' and '剩余 0' in pg.locator('#level-spirit-result').inner_text())
 pg.locator('#level-spirit-total').fill('40');check('Campaign spirit detects shortage','还缺 20' in pg.locator('#level-spirit-result').inner_text());pg.locator('#lv-on-cf').uncheck();check('Campaign inactive reserve excluded','剩余 10' in pg.locator('#level-spirit-result').inner_text())
 print('KEYBOARD TEST',flush=True);pg.locator('#lv-tab-skills').focus();pg.keyboard.press('ArrowRight');check('Tabs keyboard switches equipment',pg.locator('#lv-pane-gear').is_visible())
 go(pg,'leveling?lv=6&tab=transition');check('60 remainscampaign until explicit switch',pg.evaluate('window.__guideQA.getState().page')=='leveling');pg.locator('[data-enter-endgame]').click();pg.wait_for_timeout(60);check('Campaign toEarly explicit',pg.evaluate('window.__guideQA.getState().page==="start"&&window.__guideQA.getState().current===1'))
 print('ENDGAME INTERACTIONS',flush=True);go(pg,'skills?bd=4');pg.locator('#skill-filter').fill('冻结');check('Endgame skill filter',pg.locator('#skill-cards [data-skill-id]').count()>=1);pg.locator('#skill-filter').fill('');pg.locator('[data-copy-endgame-all]').click();check('Endgame allcopy includes10',pg.locator('#copy-text').input_value().count('\n')==10);pg.locator('#copy-close').click()
 before=pg.locator('#skill-cards').bounding_box()['height'];pg.locator('#density-toggle').click();after=pg.locator('#skill-cards').bounding_box()['height'];check('Density increases space without losingrows',after>before and pg.locator('#skill-cards [data-skill-id]').count()==10)
 pg.locator('#theme-toggle').click();check('Theme toggle works',pg.evaluate('document.documentElement.dataset.theme')=='dark')
 store=pg.evaluate('window.__mockStore');check('State serialization called','poe2-leveling-compact-v3' in store)
 pg2=browser.new_page();pg2.set_content(storage_fixture(store)+H);check('Persistence roundtrip viaexplicit fixture',pg2.evaluate('window.__guideQA.getState().current===4&&window.__guideQA.getState().density==="comfortable"'))
 pg2.close();pg.close()
 # Deep-link preservation on initial load.
 print('DEEP LINKS',flush=True)
 pg=browser.new_page();pg.evaluate("location.hash='leveling?lv=3&tab=gear'");pg.set_content(H);check('Initial campaign deep-link notoverwritten',pg.evaluate('window.__guideQA.getState().levelStage===3&&window.__guideQA.getState().levelTab==="gear"'));pg.close()
 pg=browser.new_page();pg.evaluate("location.hash='skills?bd=4'");pg.set_content(H);check('Initial endgame deep-link notoverwritten',pg.evaluate('window.__guideQA.getState().current===4&&window.__guideQA.getState().page==="skills"'));pg.close()
 check('No runtime JS errors',not errors,errors)
 # Old-version comparison if available in the review runtime; optional outside this runtime.
 old=Path('/mnt/data/leveling_compact_work/previous/poe2-guide_六分支进阶完整版/网站/index.html')
 if old.exists():
  pg=browser.new_page(viewport={'width':1440,'height':900});pg.set_content(old.read_text());go(pg,'skills?bd=4');ob=pg.locator('#skill-cards').bounding_box();measure['before_1440']={'skills_list':ob,'full_document_height':pg.evaluate('document.documentElement.scrollHeight')};nh=measure['1440']['skills_list']['height'];measure['list_reduction_fraction']=1-nh/ob['height'];pg.close()
 browser.close()
report={'date':'2026-09-24','tested_html_sha256':sha(SITE/'index.html'),'tested_data_sha256':sha(SITE/'_source/data.json'),'method':'Chromium set_content rendering of actual built HTML; external/file navigation blocked by runtime policy. Storage roundtrip uses an explicit in-memory fixture. No game-client or hosting test.','pass':all(x['pass'] for x in R),'checks':len(R),'failed':[x for x in R if not x['pass']],'measurements':measure,'results':R}
(ROOT/'检查与说明/程序检查结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['pass','checks','failed','measurements']},ensure_ascii=False,indent=2))
sys.exit(0 if report['pass'] else 1)
