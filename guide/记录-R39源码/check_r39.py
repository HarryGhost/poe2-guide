#!/usr/bin/env python3
"""Check generated R39 files and UI. Supports explicit baseline/output arguments."""
from __future__ import annotations
import json,re,hashlib,subprocess,sys,threading,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/r38_baseline')
O=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/poe2_Fubgun_C_R39')
W=Path(sys.argv[3]) if len(sys.argv)>3 else Path('/mnt/data/r39_work')
W.mkdir(parents=True,exist_ok=True);checks=[]
def ck(n,ok,d=None):
 checks.append({'name':n,'ok':bool(ok),**({'detail':d} if d is not None else {})})
 if not ok: print('FAIL',n,str(d)[:200],flush=True)
def load(p):
 h=(p/'index.html').read_text();ref=re.search(r'src="(assets/content\.[^"]+\.js)"',h).group(1)
 return json.loads(json.loads((p/ref).read_text().strip().split('textContent=',1)[1].rstrip(';')))
old=load(B);D=load(O);G=D['jewelGuide'];sha=lambda b:hashlib.sha256(b).hexdigest()
for k in old:
 if k!='release':ck('原业务数据不变/'+k,D[k]==old[k])
allowed={'index.html','00_先读我.md','README_上线.md','需要哪些宝石_从这里打开.html','特殊宝石_从这里打开.html'}
changed=[];missing=[];same=0
for p in B.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(B);q=O/rel
 if not q.exists():missing.append(str(rel))
 elif q.read_bytes()!=p.read_bytes():changed.append(str(rel))
 else:same+=1
ck('没有丢弃R38文件',not missing,missing);ck('只改变已说明的当前入口与说明',set(changed)==allowed,changed)
protected={}
for dr in ['R28原站','filters']:
 fs=[p for p in (B/dr).rglob('*') if p.is_file()];n=sum(p.read_bytes()==(O/p.relative_to(B)).read_bytes() for p in fs);protected[dr]={'total':len(fs),'identical':n};ck('原文件字节保护/'+dr,len(fs)==n,protected[dr])
ck('金币修正不回退',sha((O/'filters/01_Fubgun_Early_Mapping_GoldFix_R37_1.filter').read_bytes())=='6064c1afe0ec9f548a6fbdf7164b802f378c3b322f6f4846d8012b7134123b95')
for sid,s in G['stages'].items():
 raw=json.loads((O/s['sourceFile']).read_text());rs=[(i,n) for i,n in enumerate(raw['passives'],1) if n['id'].startswith('jewel_slot')]
 ck('逐条槽位记录/'+sid,[(r['exportIndex'],r['id'],r['weaponSet']) for r in s['rows']]==[(i,n['id'],n.get('weapon_set')) for i,n in rs])
 ck('珠宝槽去重/'+sid,s['uniqueCount']==len({n['id'] for _,n in rs}))
 ck('原件哈希/'+sid,sha((O/s['sourceFile']).read_bytes())==s['sha256'])
 ck('不捏造原件实装/'+sid,s['installedJewels'] is None and s['fixedPositions'] is None and not s['inventoryJewels'])
 ck('阶段方案不超槽/'+sid,all(p['total']==sum(x['qty'] for x in p['items']) and p['total']<=s['uniqueCount'] for p in s['plans']))
 ck('限定数量与同名不重复/'+sid,all(len(p['items'])==len({x['id'] for x in p['items']}) and all(x['qty']<=1 for x in p['items'] if x['id'] in G['specialIds']) for p in s['plans']))
 ck('不混技能血脉辅助/'+sid,all(x['id'] in G['catalog'] for p in s['plans'] for x in p['items']))
 ck('保留06只读/'+sid,(not s['readonly']) or (not s['plans'] and sid=='e06'))
ck('两种特殊珠宝独立',G['specialIds']==['well','darkness'])
ck('06重复孔不当第六颗',G['stages']['e06']['recordCount']==6 and G['stages']['e06']['uniqueCount']==5)
h=(O/'index.html').read_text();a=re.search(r'src="(assets/app\.[^"]+\.js)"',h).group(1)
r=subprocess.run(['node','--check',str(O/a)],capture_output=True,text=True);ck('JavaScript语法',r.returncode==0,r.stderr)
for ref in re.findall(r'(?:src|href)="([^"#]+)"',h):
 if not ref.startswith(('http','data:')):ck('首页本地引用/'+ref,(O/ref).exists())
# Try true navigation first, then document the actual fallback if the environment blocks it.
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(O)))
threading.Thread(target=srv.serve_forever,daemon=True).start();port=srv.server_address[1]
errors=[];attempts=[];mode='';screens=[]
with sync_playwright() as pw:
 br=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 p=br.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
 for url in [f'http://127.0.0.1:{port}/index.html#/jewels?stage=e01',O.as_uri()+'/index.html#/jewels?stage=e01']:
  try:
   p.goto(url,wait_until='load',timeout=7000);p.wait_for_selector('.jewel-summary',timeout=3000)
   attempts.append({'url':url,'ok':True});mode='actual '+url.split(':')[0];break
  except Exception as e:attempts.append({'url':url,'ok':False,'error':str(e)[:900]})
 if not mode:
  mem=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(O/m[1]).read_text()+'</style>',h)
  mem=re.sub(r'<script src="([^"]+)"></script>',lambda m:'<script>'+(O/m[1]).read_text().replace('</script','<\\/script')+'</script>',mem)
  p.goto('about:blank');p.set_content(mem,wait_until='load');mode='in-memory document with actual generated HTML/CSS/JS inlined'
 p.add_style_tag(content='html{scroll-behavior:auto!important}')
 def go(route):
  p.evaluate('(r)=>{location.hash="#/"+r;render()}',route)
  p.wait_for_function('(r)=>document.querySelector("#main-content").dataset.page===r.split(/[/?]/)[0]',arg=route)
  ck('页面渲染/'+route,not p.locator('h1').inner_text().startswith('页面暂时'))
 for sid,s in G['stages'].items():
  go('jewels?stage='+sid)
  ck('页面四类珠宝/'+sid,p.locator('[data-jewel-id]').count()==4)
  ck('页面逐条孔位/'+sid,p.locator('[data-jewel-socket]').count()==s['recordCount'])
  ck('页面方案容量/'+sid,p.locator('[data-jewel-plan-total]').evaluate_all('(es)=>es.map(e=>Number(e.dataset.jewelPlanTotal))')==[x['total'] for x in s['plans']])
  ck('保留五主分区/'+sid,p.locator('#main-nav>a.nav-item').count()==5)
  if sid=='e01':
   p.screenshot(path=str(W/'R39_人物天赋珠宝_1440.png'),full_page=False);screens.append('R39_人物天赋珠宝_1440.png')
  go('special-jewels?stage='+sid)
  ck('特殊珠宝恰好两类/'+sid,p.locator('[data-jewel-detail]').evaluate_all('(es)=>es.map(e=>e.dataset.jewelDetail)')==['well','darkness'])
  ck('不把技能表用作特殊珠宝/'+sid,p.locator('[data-special-id]').count()==0)
  if sid=='e05':
   p.screenshot(path=str(W/'R39_特殊人物珠宝_1440.png'),full_page=False);screens.append('R39_特殊人物珠宝_1440.png')
 for sid in G['stages']:
  go('character?stage='+sid);ck('天赋旁有珠宝入口/'+sid,p.locator('#char-tree [data-jewel-bridge]').count()==1)
  go('item/jewels?stage='+sid);ck('旧珠宝部位直达新页/'+sid,p.locator('[data-jewel-bridge]').count()==1)
  go('gems?stage='+sid);ck('原技能清单保留/'+sid,p.locator('[data-gem-id]').count()==len(D['gemGuide']['stages'][sid]['rows']))
  ck('技能页面消除歧义/'+sid,'技能／辅助宝石' in p.locator('h1').inner_text())
  go('special-gems?stage='+sid);ck('血脉内容保留/'+sid,p.locator('[data-special-id]').count()==6)
  ck('血脉页面消除歧义/'+sid,'血脉辅助' in p.locator('h1').inner_text())
 for q,expected in [('人物天赋','jewels'),('泉井之心','special-jewels'),('抗衡黑暗','special-jewels'),('jewel_slot1960','jewels')]:
  found=p.evaluate('(q)=>searchData(q)',q);ck('搜索直达/'+q,any(v['route']==expected for v in found))
 # Targeted regression of essence branches, gold and major existing pages.
 for slot in ['bow','quiver','body','helmet','gloves','boots','amulet','belt','ring1','ring2']:
  go('item/'+slot+'?stage=e01');ck('精华选择保留/'+slot,p.locator('[data-essence-option]').count()>0 or '本部位精华' in p.locator('#main-content').inner_text() or '精华怎么选' in p.locator('#main-content').inner_text())
 for route in ['gear?stage=e01','learn/ascendancy','atlas-choose','tools/filters','filter-guide?f=01b','filter-check?f=01b&sample=gold_79_1000','tools/sources']:
  go(route)
 go('jewels?stage=e01')
 # Exercise a real navigation click and the inherited stage selector.
 p.locator('.jewel-tabs a').filter(has_text='特殊人物珠宝').click();p.wait_for_function('current.section==="special-jewels"');ck('特殊页链接可点击',p.locator('[data-jewel-detail]').count()==2)
 select=p.locator('select').filter(has=p.locator('option[value="e05"]'))
 if select.count()==1:
  select.select_option('e05');p.wait_for_function('state.stage==="e05"');ck('全局阶段切换可用',p.locator('[data-jewel-plan-total]').count()==3)
 else:
  # Recognize the original stage buttons when no dropdown is present.
  btn=p.locator('[data-stage="e05"]');
  if btn.count():btn.first.click();p.wait_for_function('state.stage==="e05"');ck('全局阶段切换可用',True)
  else:ck('全局阶段切换可用',False,'stage control not found')
 for width in [1920,1440,1024,390]:
  p.set_viewport_size({'width':width,'height':950})
  for route in ['jewels?stage=e01','special-jewels?stage=e05','jewels?stage=e06']:
   go(route)
   dims=p.evaluate('({w:innerWidth,s:document.documentElement.scrollWidth})');ck(f'无整页横向溢出/{width}/{route}',dims['s']<=dims['w']+1,dims)
   dup=p.evaluate('(()=>{let a=[...document.querySelectorAll("[id]")].map(e=>e.id);return a.filter((x,i)=>a.indexOf(x)!==i)})()');ck(f'无重复ID/{width}/{route}',not dup,dup)
  if width==390:
   go('jewels?stage=e01');p.screenshot(path=str(W/'R39_人物天赋珠宝_390.png'),full_page=False);screens.append('R39_人物天赋珠宝_390.png')
 ck('无未捕获JS异常',not errors,errors)
 br.close()
srv.shutdown()
summary={'release':'R39','passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'navigationMode':mode,'navigationAttempts':attempts,'protected':protected,'baselineFilesUnchanged':same,'changedBaselineFiles':changed,'screenshots':screens,'checks':checks}
(W/'R39_检查结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='checks'},ensure_ascii=False,indent=2))
if summary['failed']:sys.exit(1)
