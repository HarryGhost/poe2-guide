#!/usr/bin/env python3
from __future__ import annotations
import json,re,hashlib,collections,subprocess,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
W=Path('/mnt/data/r38_work');B=Path('/mnt/data/冰射攻略_接续资料_20261002/网站_R37_1');O=Path('/mnt/data/poe2_Fubgun_C_R38')
D=json.loads((W/'data_r38.json').read_text());old=json.loads((W/'data_baseline.json').read_text());checks=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'ok':bool(ok),**({'detail':detail} if detail is not None else {})})
 if not ok:print('FAIL:',name,detail,flush=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
for k in old:
 if k not in ['materials','executionViews','release']:ck('保留业务字段/'+k,D[k]==old[k])
for k,v in old['materials'].items():ck('保留原材料/'+k,D['materials'][k]==v)
for k,v in old['executionViews']['routes'].items():
 if k not in [g['route'] for g in D['essenceGuide']['slots'].values()]:ck('保留其他执行工艺/'+k,D['executionViews']['routes'][k]==v)
changed=[];missing=[];unchanged=[]
for p in B.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(B);q=O/rel
 if not q.exists():missing.append(str(rel))
 elif p.read_bytes()!=q.read_bytes():changed.append(str(rel))
 else:unchanged.append(str(rel))
ck('所有基线文件保留',not missing,missing)
ck('只有首页与两份当前说明变更',set(changed)=={'index.html','README_上线.md','00_先读我.md'},changed)
protected={}
for group in ['R28原站','filters']:
 ps=[p for p in (B/group).rglob('*') if p.is_file()];n=sum((O/p.relative_to(B)).read_bytes()==p.read_bytes() for p in ps)
 protected[group]={'total':len(ps),'same':n};ck('逐字节保护/'+group,n==len(ps),protected[group])
ck('R37.1金币修正哈希',sha((O/'filters/01_Fubgun_Early_Mapping_GoldFix_R37_1.filter').read_bytes())=='6064c1afe0ec9f548a6fbdf7164b802f378c3b322f6f4846d8012b7134123b95')
for slot,g in D['essenceGuide']['slots'].items():
 r=D['executionViews']['routes'][g['route']]['route'];steps={s['id']:s for s in r['steps']};ids=set(steps)
 ck('工艺无重复ID/'+slot,len(ids)==len(r['steps']))
 ck('工艺步骤可解析/'+slot,all((not s.get('next') or s['next'] in ids) and all(c['id'] in ids for c in s.get('choices',[])) for s in steps.values()))
 ck('蓝装升黄先分支/'+slot,steps['augment']['next']=='essence-choice' and steps['essence-choice'].get('next') is None)
 ck('精华富豪各自升黄后验收/'+slot,steps['regal']['next']=='rare-review' and steps['essence']['next']=='rare-review')
 ck('升黄后不自动接崇高/'+slot,steps['rare-review']['next'] is None)
 ck('每颗精华确有本部位效果/'+slot,all(slot in D['essenceGuide']['catalog'][x]['slots'] and slot in D['essenceGuide']['catalog'][x]['effect'] for x in g['options']))
 ck('材料引用可解析/'+slot,all(m in D['materials'] for st in r['steps'] for m in st.get('materials',[])))
ck('戒指普通身躯非强效', 'body-normal' in D['essenceGuide']['slots']['rings']['options'] and 'body-greater' not in D['essenceGuide']['slots']['rings']['options'])
ck('箭袋不套磨蚀急速寻觅',not set(['abrasion','haste','seeking'])&set(D['essenceGuide']['slots']['quiver']['options']))
ck('鞋子不套急速移速','haste' not in D['essenceGuide']['slots']['boots']['options'])
G=D['gemGuide'];ice=next(k for k,g in D['gems'].items() if g['en']=='Ice Shot');granted=next(k for k,g in G['info'].items() if g['kind']=='granted')
allids=set()
for branch,s in zip(old['branches'],G['stages'].values()):
 ids=[p['id'] for sk in branch['skills'] for p in [sk]+sk.get('support_skills',[])];allids.update(ids);n=collections.Counter(ids);sid=s['id'];actual={r['id']:r for r in s['rows']}
 ck('逐镶嵌记录核对数量/'+sid,n==s['counts'] and all(actual[k]['qty']==(0 if k==granted else v) for k,v in n.items()))
 ck('冰霜射击三份/'+sid,actual[ice]['qty']==3)
 ck('升华技能不采购/'+sid,actual[granted]['qty']==0)
 ck('清单总数/'+sid,s['gemTotal']==len(ids)-1 and s['types']==len(n)-1)
 ck('完整原连法未丢/'+sid,[[sk['id']]+[p['id'] for p in sk.get('support_skills',[])] for sk in branch['skills']]==[[sk['id']]+[p['id'] for p in sk['parts']] for sk in s['chains']])
 ck('血脉辅助分阶段/'+sid,sum(G['info'][r['id']]['kind']=='lineage' for r in s['rows'])==({'e05':5,'e06':6}.get(sid,0)))
ck('所有原件宝石均有说明',allids==set(G['info']),{'unique':len(allids)})
html=(O/'index.html').read_text();appref=re.search(r'<script src="(assets/app[^\"]+)"',html).group(1)
result=subprocess.run(['node','--check',str(O/appref)],capture_output=True,text=True);ck('JavaScript语法',result.returncode==0,result.stderr)
for m in re.finditer(r'(?:src|href)="([^"#]+)"',html):
 u=m[1]
 if not u.startswith(('http','data:')):ck('首页静态引用/'+u,(O/u).exists())
# Browser test actual generated scripts/styles in memory, after separate real-navigation probe failed.
html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(O/m[1]).read_text()+'</style>',html)
html=re.sub(r'<script src="([^"]+)"></script>',lambda m:'<script>'+(O/m[1]).read_text().replace('</script','<\\/script')+'</script>',html)
errors=[];screens=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 p=browser.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html,wait_until='load');p.add_style_tag(content='html{scroll-behavior:auto!important}')
 def go(route):
  h='#/'+route
  p.evaluate('(h)=>{location.hash=h;render()}',h)
  p.wait_for_function('(h)=>location.hash===h && document.querySelector("#main-content").dataset.page===h.slice(2).split(/[/?]/)[0]',arg=h)
  ck('页面成功渲染/'+route,not p.locator('h1').inner_text().startswith('页面暂时'))
 for sid,s in G['stages'].items():
  go('gems?stage='+sid)
  q=p.locator('[data-gem-id]').evaluate_all('(rs)=>rs.map(r=>[r.dataset.gemId,Number(r.dataset.gemQty)])')
  ck('浏览器宝石数量/'+sid,dict(q)=={r['id']:r['qty'] for r in s['rows']})
  ck('浏览器完整连法行/'+sid,p.locator('.gem-chain-table tbody tr').count()==len(s['chains']))
  ck('五个主分区/'+sid,p.locator('#main-nav>a.nav-item').count()==5)
  go('special-gems?stage='+sid)
  ck('特殊页保留六种/'+sid,p.locator('[data-special-id]').count()==6)
  ck('特殊页当前使用标识/'+sid,p.locator('.lineage-current').count()==({'e05':5,'e06':6}.get(sid,0)))
 # Stage selector navigation and submenu persistence.
 go('gems?stage=e01');p.locator('#stage-select').select_option('e05');p.wait_for_function("location.hash.includes('stage=e05') && document.querySelector('.gem-summary').innerText.startsWith('48')")
 ck('宝石阶段下拉联动',p.locator('.gem-summary').inner_text().split()[0]=='48')
 p.locator('#main-nav a',has_text='特殊宝石单独看').click();p.wait_for_function("location.hash.includes('special-gems') && document.getElementById('main-content').dataset.page==='special-gems' && document.querySelectorAll('[data-special-id]').length===6")
 ck('子导航保留阶段',p.locator('#stage-select').input_value()=='e05')
 # Nine workflows and selected material, then regal, including both rings.
 for slot,g in D['essenceGuide']['slots'].items():
  ui='ring1' if slot=='rings' else slot;go(f'item/{ui}?stage=e01&route={g["route"]}&step=essence-choice')
  ck('各部位展示精华表/'+slot,p.locator('#item-essences').count()==1)
  ck('目标先于精华、精华先于用料/'+slot,p.evaluate("document.getElementById('item-target').compareDocumentPosition(document.getElementById('item-essences'))&Node.DOCUMENT_POSITION_FOLLOWING")!=0 and p.evaluate("document.getElementById('item-essences').compareDocumentPosition(document.querySelector('.recipe-table'))&Node.DOCUMENT_POSITION_FOLLOWING")!=0)
  ck('全部本部位精华显示/'+slot,p.locator('[data-essence-option]').count()==len(g['options']))
  k=g['options'][0];p.locator(f'[data-essence-option="{k}"] a.btn').click();p.wait_for_function('(k)=>location.hash.includes("essence="+k) && document.getElementById("recipe-entry")?.value==="essence" && document.querySelector(".recipe-table [data-step]")?.dataset.step==="essence"',arg=k)
  visible=p.locator('.recipe-table').first.locator('[data-step]').evaluate_all('(rs)=>rs.map(r=>r.dataset.step)')
  ck('精华主路径不串富豪/'+slot,visible==['essence','rare-review'],visible)
  ck('选定精华名与效果显示/'+slot,D['essenceGuide']['catalog'][k]['zh'] in p.locator('.recipe-table').first.inner_text() and D['essenceGuide']['catalog'][k]['effect'][slot] in p.locator('.recipe-table').first.inner_text())
  go(f'item/{ui}?stage=e01&route={g["route"]}&step=regal')
  visible=p.locator('.recipe-table').first.locator('[data-step]').evaluate_all('(rs)=>rs.map(r=>r.dataset.step)')
  ck('富豪主路径不串精华/'+slot,visible==['regal','rare-review'],visible)
  go(f'item/{ui}?stage=e01&route={g["route"]}&step=essence')
  ck('缺选择停止不自动用料/'+slot,'尚未选择具体精华' in p.locator('.recipe-table').first.inner_text() and p.locator('.recipe-table').first.locator('[data-step]').count()==1)
 go('item/ring2?stage=e01&route=early-rings&step=essence&essence=body-normal');ck('第二枚戒指同样覆盖','身躯精华' in p.locator('.recipe-table').first.inner_text())
 # Explicit post-upgrade choice; no automatic exalting.
 go('item/bow?stage=e01&route=early-bow&step=essence&essence=abrasion')
 p.locator('.recipe-table').first.get_by_role('link',name='确认合法空位，再补第4条').click();p.wait_for_function("location.hash.includes('step=exalt') && document.querySelector('.recipe-table [data-step]')?.dataset.step==='exalt'")
 ck('升黄后可主动接黄装后续',p.locator('.recipe-table').first.locator('[data-step]').first.get_attribute('data-step')=='exalt')
 # Readonly and unique gating.
 go('item/bow?stage=e06');ck('06不给精华执行入口',p.locator('#item-essences').count()==0)
 go('item/belt?stage=e05');ck('暗金腰带不提供升黄',p.locator('#item-essences').count()==0)
 go('item/helmet?stage=e03');ck('护盾头仍默认作者工艺',p.locator('#recipe-select').input_value()=='helmet-stable')
 go('item/bow?stage=e04');ck('暴击弓仍默认作者工艺',p.locator('#recipe-select').input_value()=='bow-crit')
 # Search additions: calls test actual search function, UI search also clicked.
 for query,route in [('宝石','gems'),('卡哈塔','special-gems'),('身躯','item/ring1')]:
  result=p.evaluate('(q)=>searchData(q)',query);ck('全站搜索/'+query,any(x['route']==route for x in result),len(result))
 go('gems?stage=e01');p.locator('[data-search]').click();p.locator('#search-input').fill('格鲁坎');p.locator('#search-results button').first.click();p.wait_for_function("location.hash.includes('special-gems') && document.getElementById('main-content').dataset.page==='special-gems' && document.querySelectorAll('[data-special-id]').length===6");ck('搜索结果可进入特殊页',p.locator('[data-special-id]').count()==6)
 # Regression pages have unchanged business data; exercise rendering and actual navigation handlers.
 for route in ['gear?stage=e01','character?stage=e01','character?stage=e05','character?stage=e06','tools/filters','filter-guide','filter-check','learn/ascendancy','atlas-choose']:
  go(route);ck('原页面无错误/'+route,'页面暂时没有正确载入' not in p.locator('#main-content').inner_text())
 # Filter engine catalogue is byte-identical; exercise its UI without reinterpreting game drops.
 go('tools/filters');ck('金币修正版下载还在','GoldFix_R37_1' in p.locator('#main-content').inner_html())
 # Width / duplicate IDs and saved screenshots of actual DOM.
 routes=['gems?stage=e01','special-gems?stage=e05','item/ring1?stage=e01&route=early-rings&step=essence&essence=body-normal','item/bow?stage=e01&route=early-bow&step=essence&essence=abrasion']
 for width in [375,768,1440]:
  p.set_viewport_size({'width':width,'height':1000})
  for route in routes:
   go(route);w=p.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})');ck(f'整页无横向溢出/{width}/{route}',w['scroll']<=w['width']+1,w)
   duplicate=p.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(x=>x.id);return a.filter((x,i)=>a.indexOf(x)!==i)})()');ck(f'无重复ID/{width}/{route}',not duplicate,duplicate)
   if width in [375,1440]:
    title=('宝石准备' if route.startswith('gems') else '特殊宝石' if route.startswith('special') else '戒指精华' if 'ring1' in route else '弓精华')
    if title.endswith('精华'):p.locator('#item-essences').scroll_into_view_if_needed()
    filename=f'R38_{title}_{width}.png';p.screenshot(path=str(W/filename),full_page=False,animations='disabled');screens.append(filename)
 ck('浏览器无未捕获JS错误',not errors,errors)
 browser.close()
report={'release':'R38','date':'2026-10-02','checks':checks,'total':len(checks),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'baselineFiles':{'unchanged':len(unchanged),'changed':changed,'missing':missing},'protected':protected,'screenshots':screens,'browserErrors':errors,'navigationProbe':json.loads((W/'smoke.json').read_text()),'scope':'静态校验与Chromium内存文档交互。真实file和HTTP导航被环境策略阻止；无游戏客户端、掉落、工艺实战或用户域名部署验证。'}
(W/'qa_r38.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['total','passed','failed','baselineFiles','protected','screenshots']},ensure_ascii=False,indent=2),flush=True)
if report['failed']:sys.exit(1)
