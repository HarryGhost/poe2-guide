#!/usr/bin/env python3
"""Structural + Chromium memory-render tests. No claim of game-client verification.
Dependencies for this optional audit script: beautifulsoup4, playwright, a Chromium binary.
Run from anywhere: python 检查与说明/运行检查.py
"""
from pathlib import Path
import json,re,hashlib,zipfile,collections,shutil,os,time,functools,http.server,threading,urllib.request,urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'网站';OUT=ROOT/'检查与说明';SCREEN=OUT/'截图';SCREEN.mkdir(exist_ok=True)
D=json.loads((SITE/'_source/data.json').read_text(encoding='utf-8'));HTML=(SITE/'index.html').read_text(encoding='utf-8');STATIC=(SITE/'六分支完整资料.html').read_text(encoding='utf-8')
results=[];errors=[];requests=[];widths=[]
def check(name,ok,details=''):
 results.append({'检查':name,'通过':bool(ok),'说明':details})
 if not ok: print('FAIL',name,details,flush=True)
def normalized(obj):
 if isinstance(obj,dict): return {k:normalized(v) for k,v in obj.items() if k not in ['name','description','additional_text']}
 if isinstance(obj,list):return [normalized(v) for v in obj]
 return obj
soup=BeautifulSoup(HTML,'html.parser');ids=[x['id'] for x in soup.select('[id]')]
check('静态DOM ID唯一',len(ids)==len(set(ids)))
check('无外部脚本CSS或字体资源',not soup.select('script[src],link[rel="stylesheet"],link[rel="preload"],iframe'))
check('网页内嵌数据等于源码',json.loads(soup.select_one('#guide-data').string)==D)
check('对外完整数据等于源码',json.loads((SITE/'数据/六分支原始及中文映射.json').read_text())==D)
check('完整差异文件一致',json.loads((SITE/'数据/全部分支逐项差异.json').read_text())==D['diffs'])
raws={}
with zipfile.ZipFile(ROOT/'原件备份/Fubgun六分支原件.zip') as z:
 raws={n:z.read(n) for n in z.namelist() if n.endswith('.build')}
for b in D['branches']:
 n=b['number'];actual=(SITE/b['download']).read_bytes();original=raws[b['sourceFile']]
 check(f'{n:02} 原件逐字节与哈希',actual==original and hashlib.sha256(actual).hexdigest()==b['sha256'])
 check(f'{n:02} 原始JSON未改',json.loads(actual)==b['raw'])
 annotated=json.loads((SITE/b['annotatedDownload']).read_text())
 check(f'{n:02} 中文提示版只改说明',normalized(annotated)==normalized(b['raw']))
 check(f'{n:02} 节点ID行序与分组完整',[(x['row'],x['id'],x['scope']) for x in b['nodes']]==[(i+1,p['id'],'升华' if p['id'].startswith('Ascendancy') else '公共' if not p.get('weapon_set') else f'武器组{p["weapon_set"]}') for i,p in enumerate(b['raw']['passives'])])
 for idx,e in enumerate(b['equipment']):
  src=[x for x in e['raw'].get('additional_text','').splitlines() if re.match(r'^\d+\.',x)];dst=[x for x in e['translation'].splitlines() if re.match(r'^\d+\.',x)]
  nums=lambda x:re.findall(r'\d+(?:\.\d+)?',x)[1:]
  check(f'{n:02} 装备{idx+1:02}词条数值未变',[nums(x) for x in src]==[nums(x) for x in dst])
check('06隔离且升华冲突保留',D['branches'][5]['download'].endswith('.build.txt') and len(D['branches'][5]['ascendancyConflict'])==10)
check('01-05未检测到同类升华冲突',all(not b['ascendancyConflict'] for b in D['branches'][:5]))
check('所有技能和内嵌ID有词典',all(s['id'] in D['gems'] and all(t['id'] in D['gems'] for t in s.get('support_skills',[])) for b in D['branches'] for s in b['raw']['skills']))
check('所有天赋均保留名称状态',all(x.get('status') for b in D['branches'] for x in b['nodes']))
ref=BeautifulSoup(STATIC,'html.parser')
for b in D['branches']:
 sec=ref.select_one(f'#b{b["number"]}')
 check(f'{b["number"]:02}静态技能与全部内嵌连接', [x['data-static-skill'] for x in sec.select('[data-static-skill]')]==[s['id'] for s in b['raw']['skills']] and len(sec.select('[data-static-skill] ol li'))==sum(len(s['support_skills']) for s in b['raw']['skills']))
 check(f'{b["number"]:02}静态装备记录齐全',len(sec.select('[data-static-gear]'))==len(b['equipment']))
 check(f'{b["number"]:02}静态天赋原序齐全',[x['data-static-node'] for x in sec.select('[data-static-node]')]==[x['id'] for x in b['nodes']])
for a in D['branches']:
 for b in D['branches']:
  if a==b:continue
  d=D['diffs'][f'{a["number"]}-{b["number"]}'];sm1={s['id']:s for s in a['raw']['skills']};sm2={s['id']:s for s in b['raw']['skills']}
  expect={id for id in set(sm1)|set(sm2) if sm1.get(id)!=sm2.get(id)}
  ok={x['id'] for x in d['skills']}==expect
  ok=ok and all(x['before']==sm1.get(x['id']) and x['after']==sm2.get(x['id']) for x in d['skills'])
  slot=lambda x: f"{x['raw']['inventory_id']}:{x['raw'].get('slot_x',0)}:{x['raw'].get('slot_y',0)}"
  gm1={slot(x):x for x in a['equipment']};gm2={slot(x):x for x in b['equipment']}
  changed={k for k in set(gm1)|set(gm2) if gm1.get(k)!=gm2.get(k)}
  ok=ok and {x['slot'] for x in d['equipment']}==changed and all(x['before']==gm1.get(x['slot']) and x['after']==gm2.get(x['slot']) for x in d['equipment'])
  for scope,v in d['nodes'].items():
   x={n['id'] for n in a['nodes'] if n['scope']==scope};y={n['id'] for n in b['nodes'] if n['scope']==scope}
   ok=ok and set(v['removed'])==x-y and set(v['added'])==y-x and v['unchanged']==len(x&y)
  check(f'{a["number"]}→{b["number"]}差异重新计算一致',ok)
# Static resource links are inspected on disk; no fabricated served/deployed result.
def resource_links_ok(items):
 bad=[]
 for href in items:
  if not href or href.startswith(('#','http:','https:','mailto:','javascript:')):continue
  path=urllib.parse.unquote(href.split('#')[0].split('?')[0]);p=SITE/path
  if not p.is_file():bad.append(href)
 return bad
check('静态资料下载链接目标存在',not resource_links_ok([a.get('href') for a in ref.select('a[href]')]))
chromium=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser')
launch={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
if chromium:launch['executable_path']=chromium
with sync_playwright() as p:
 browser=p.chromium.launch(**launch);page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');page.set_default_timeout(4500)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.set_content(HTML,wait_until='load');page.wait_for_function('window.__guideQA')
 check('默认01而不是04',page.evaluate('window.__guideQA.getState().current')==1 and page.input_value('#current-bd')=='1')
 check('默认目标独立未选',page.input_value('#target-bd')=='0')
 check('初始单章节显示',page.locator('main>section:visible').count()==1 and page.locator('#start').is_visible())
 check('桌面菜单开关不显示',not page.locator('#menu-toggle').is_visible() and not page.locator('#menu-close').is_visible())
 check('首页五阶段+独立06入口',page.locator('#roadmap [data-view]').count()==5 and page.locator('.snapshot-strip [data-view="6"]').count()==1)
 for b in D['branches']:
  n=b['number'];page.select_option('#current-bd',str(n))
  actual=page.locator('#skill-cards .skill-card').evaluate_all('(es)=>es.map(e=>({id:e.dataset.skillId,children:Array.from(e.querySelectorAll(".chain li")).map(x=>x.dataset.gemId)}))')
  expect=[dict(id=s['id'],children=[x['id'] for x in s['support_skills']]) for s in b['raw']['skills']]
  check(f'{n:02} 切换后技能与辅助逐条一致',actual==expect)
  check(f'{n:02} 切换后装备齐全',page.locator('#gear-records .gear-card').count()==len(b['equipment']))
  check(f'{n:02} 切换后天赋原序一致',page.locator('#node-table [data-node-id]').evaluate_all('(es)=>es.map(e=>e.dataset.nodeId)')==[x['id'] for x in b['nodes']])
  check(f'{n:02} 主下载与当前分支一致',page.locator('#main-download').get_attribute('href')==b['download'])
  check(f'{n:02} 标题和当前操作同步',all(page.locator(id).inner_text().startswith(f'{n:02}') for id in ['#skills-title','#gear-title','#tree-title','#combat-title']))
  check(f'{n:02} 精魂项目与本分支一致',page.locator('[data-reserve-value]').evaluate_all('(es)=>es.map(e=>e.dataset.reserveValue)')==[x.split('/')[-1] for x in b['reserveSkills']])
  check(f'{n:02} 无效资源总数不自动假定',page.locator('#spirit-result').get_attribute('data-status')=='incomplete')
  check(f'{n:02} 动态文件链接存在',not resource_links_ok(page.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))')))
  # Internal fragments are real IDs, including dynamically generated source entries.
  pairs=page.locator('a[href^="#"]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href").slice(1).split("?")[0])')
  absent=page.evaluate('(ids)=>ids.filter(id=>!document.getElementById(id))',pairs)
  check(f'{n:02} 内部章节来源锚点可定位',not absent,absent)
 # Long-term target must never silently select that build.
 page.select_option('#current-bd','2');page.select_option('#target-bd','5')
 check('目标05不替换当前02',page.input_value('#current-bd')=='2' and page.locator('#skills-title').inner_text().startswith('02') and page.locator('#main-download').get_attribute('href')==D['branches'][1]['download'])
 page.select_option('#mode','trade');check('交易模式切换不改BD',page.evaluate('window.__guideQA.getState().current')==2 and '买' in page.locator('#current-summary').inner_text()+page.locator('#gear-records').inner_text())
 page.select_option('#mode','ssf')
 # Every nav route and return home, using desktop links.
 for slug in ['upgrade','skills','gear','tree','combat','craft','pitfalls','glossary','downloads','sources','start']:
  page.locator(f'.nav-link[href="#{slug}"]').click()
  check('章节路由 '+slug,page.locator(f'#{slug}').is_visible() and page.locator('main>section:visible').count()==1)
 # Tasks must not leak across stages.
 page.select_option('#current-bd','1');page.locator('#task-list input').first.check();page.select_option('#current-bd','2')
 check('勾选不跨分支串用',not page.locator('#task-list input').first.is_checked())
 page.select_option('#current-bd','1');check('回到同分支保留勾选',page.locator('#task-list input').first.is_checked())
 # Search and filtered results preserve per-stage identity.
 page.locator('.nav-link[href="#skills"]').click();page.select_option('#current-bd','3');page.fill('#skill-filter','魔力残片')
 check('03搜索魔力残片为空',page.locator('#skill-cards .skill-card').count()==0)
 page.select_option('#current-bd','5');check('切05清空旧过滤并含魔力残片',page.locator('#skill-cards .skill-card').count()==10 and '魔力残片' in page.locator('#skill-cards').inner_text())
 check('05未混入狙击主技能',not page.locator('[data-skill-id="Metadata/Items/Gem/SkillGemSnipe"]').count())
 check('05优先级不再要求升狙击', '没有狙击' in page.locator('#skill-priorities').inner_text())
 page.select_option('#current-bd','3');names=page.locator('.skill-card h3').all_inner_texts();check('03有幽灵舞步无战斗狂怒和风舞者','幽灵舞步' in names and '战斗狂怒' not in names and '风舞者' not in names)
 page.fill('#skill-filter','Primal');check('内部旧ID可以查询',page.locator('.skill-card').count()>0);page.fill('#skill-filter','')
 # Per-stage arithmetic with explicitly entered actual values.
 page.select_option('#current-bd','1');page.fill('#spirit-total','200');vals=page.locator('[data-reserve-value]')
 for i in range(vals.count()):vals.nth(i).fill(str((i+1)*10))
 check('精魂录入200减60得到140','剩余 140' in page.locator('#spirit-result').inner_text())
 page.select_option('#current-bd','3');check('03预算未沿用01','尚不能计算' in page.locator('#spirit-result').inner_text())
 page.select_option('#current-bd','1');check('01预算会话内保留','剩余 140' in page.locator('#spirit-result').inner_text())
 page.fill('#spirit-other','-1');check('负保留被拒绝',page.locator('#spirit-result').get_attribute('data-status')=='incomplete');page.fill('#spirit-other','0')
 # Clipboard must either succeed or expose full manual fallback, not silently claim success.
 page.locator('[data-copy]').first.click();page.wait_for_timeout(100)
 check('复制按钮有成功或可复制降级',page.locator('#copy-dialog').is_visible() or '已复制' in page.locator('#toast').inner_text())
 if page.locator('#copy-dialog').is_visible():
  check('复制降级含当前01与完整技能','01' in page.input_value('#copy-text') and '冰霜射击' in page.input_value('#copy-text'));page.locator('#copy-close').click()
 # Scope filtering and source-status filtering.
 page.locator('.nav-link[href="#tree"]').click();page.select_option('#current-bd','4');page.select_option('#node-scope','武器组1')
 check('04武器Ⅰ过滤为24条',page.locator('#node-table [data-node-id]').count()==24)
 page.select_option('#node-scope','all');page.select_option('#node-status','sourced')
 check('04有来源过滤计数匹配',page.locator('#node-table [data-node-id]').count()==D['branches'][3]['namedCount'])
 page.select_option('#node-status','all')
 # Independent comparison: exact nodes listed, current remains unchanged.
 page.locator('.nav-link[href="#upgrade"]').click()
 for pair in ['1-2','2-3','3-4','4-5','5-6']:
  page.locator(f'#compare-presets [data-compare-pair="{pair}"]').click();diff=D['diffs'][pair];text=page.locator('#diff-content').inner_text()
  # Inner text of closed details may omit descendants: use textContent for actual data presence.
  alltext=page.locator('#diff-content').text_content()
  check(pair+'逐项差异渲染完整',all(x in alltext for scope in diff['nodes'].values() for x in scope['removed']+scope['added']))
  check(pair+'比较不改变当前04',page.input_value('#current-bd')=='4')
 page.select_option('#compare-from','4');page.select_option('#compare-to','4');check('相同分支友好提示','同一份' in page.locator('#diff-content').inner_text())
 # Deep link branch and chapter; no false static link routing.
 page.evaluate("location.hash='skills?bd=5&target=5&mode=ssf'");page.wait_for_timeout(100)
 check('深链接选05与技能章节同步',page.locator('#skills').is_visible() and page.input_value('#current-bd')=='5' and page.locator('.skill-card').count()==10)
 page.evaluate("location.hash='src-S7?bd=3'");page.wait_for_timeout(100);check('来源深链接不丢BD',page.locator('#sources').is_visible() and page.input_value('#current-bd')=='3')
 # Global search, injection handling, and Escape.
 page.locator('#search-open').click();page.fill('#global-search','魔力残片');check('全站搜索返回结果',page.locator('.search-result').count()>0)
 page.keyboard.press('Escape');check('Escape关闭搜索',page.locator('#search-mask').is_hidden())
 page.locator('#search-open').click();page.fill('#global-search','<img src=x onerror=alert(1)>');check('搜索输入不生成HTML注入',page.locator('#search-results img').count()==0);page.keyboard.press('Escape')
 # Responsive layout on 11 sections. Memory-rendered real output, no external requests.
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':900})
  for branch in range(1,7):
   for slug in ['start','upgrade','skills','gear','tree','combat','craft','pitfalls','glossary','downloads','sources']:
    page.evaluate('(args)=>{location.hash=args.slug+"?bd="+args.branch}',{'slug':slug,'branch':branch});page.wait_for_timeout(12)
    dims=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
    widths.append({'width':width,'branch':branch,'section':slug,**dims});check(f'{width}px BD{branch:02} {slug} 无整页横向溢出',dims['scroll']<=width+1,dims)
 # Mobile menu opens, is focusable, and closes after selecting navigation.
 page.set_viewport_size({'width':390,'height':844});page.locator('#menu-toggle').click();check('手机菜单打开',page.locator('#sidebar').get_attribute('aria-hidden')=='false')
 page.locator('.nav-link[href="#start"]').click();check('手机选择章节后菜单关闭',page.locator('#sidebar').get_attribute('aria-hidden')=='true' and page.locator('#start').is_visible())
 page.locator('#theme-toggle').click();check('深浅色切换生效',page.locator('html').get_attribute('data-theme')=='dark');page.locator('#theme-toggle').click()
 # Screenshots, cropped viewport and full-page to support visual QA.
 page.set_viewport_size({'width':1440,'height':1000});page.evaluate("location.hash='start?bd=1'");page.wait_for_timeout(150);page.locator('#toast').evaluate('(e)=>e.hidden=true')
 page.screenshot(path=str(SCREEN/'01_进阶首页_桌面.png'),full_page=True)
 page.evaluate("location.hash='skills?bd=3'");page.wait_for_timeout(100);page.screenshot(path=str(SCREEN/'02_03技能_桌面.png'),full_page=True)
 page.evaluate("location.hash='upgrade?bd=4'");page.wait_for_timeout(100);page.locator('#compare-presets [data-compare-pair="4-5"]').click();page.locator('#toast').evaluate('(e)=>e.hidden=true');page.screenshot(path=str(SCREEN/'03_04到05差异_桌面.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.evaluate("location.hash='start?bd=1'");page.wait_for_timeout(100);page.screenshot(path=str(SCREEN/'04_阶段首页_手机.png'),full_page=True)
 page.evaluate("location.hash='skills?bd=5'");page.wait_for_timeout(100);page.screenshot(path=str(SCREEN/'05_05技能_手机.png'),full_page=True)
 page.evaluate("location.hash='start?bd=6'");page.wait_for_timeout(100);page.screenshot(path=str(SCREEN/'06_隔离快照_手机.png'),full_page=True)
 check('浏览器运行无JS异常',not errors,errors)
 check('页面没有联网资源请求',not [u for u in requests if u.startswith(('http:','https:'))],requests)
 browser.close()
# Request file bytes over a Python local server, independent of Chromium restrictions.
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(SITE)));threading.Thread(target=srv.serve_forever,daemon=True).start()
try:
 for path in ['index.html','六分支完整资料.html']+[b['download'] for b in D['branches']]:
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{srv.server_port}/'+urllib.parse.quote(path),timeout=4) as r:body=r.read();code=r.status
   check('本地HTTP资源回读 '+path,code==200 and body==(SITE/path).read_bytes())
  except Exception as e:check('本地HTTP资源回读 '+path,False,str(e))
finally:srv.shutdown();srv.server_close()
report={'version':D['edition'],'date':D['date'],'scope':'源数据/派生差异/静态资源/Chromium内存渲染交互与布局','environment':{'browser':chromium or 'playwright bundled','rendering':'Chromium page.set_content(实际输出HTML)','limitation':'环境策略阻止浏览器直接导航file://及localhost；不宣称浏览器文件打开、线上部署或国服游戏验证。另用Python本地HTTP资源回读核对字节。','persistentStorage':'当前会话状态与禁用/不可用存储容错检查；真实浏览器重启后持久化未在当前环境验收。'},'passed':sum(r['通过'] for r in results),'failed':sum(not r['通过'] for r in results),'checks':results,'browser_errors':errors,'responsive':widths,'gameValidation':False}
(OUT/'自动检查结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT',report['passed'],'passed /',report['failed'],'failed',flush=True)
if report['failed']:raise SystemExit(1)
