from __future__ import annotations
from pathlib import Path
import argparse,functools,hashlib,http.server,json,re,subprocess,threading
from playwright.sync_api import sync_playwright
from build_r40 import read_data
P=argparse.ArgumentParser();P.add_argument('--base',type=Path,required=True);P.add_argument('--out',type=Path,required=True);P.add_argument('--results',type=Path,required=True);a=P.parse_args()
B,O,W=a.base,a.out,a.results;W.mkdir(parents=True,exist_ok=True)
_,_,D0=read_data(B);h,assets,D=read_data(O);checks=[];errors=[];nav=[]
def ck(name,ok,detail=''):
 checks.append({'name':name,'ok':bool(ok),'detail':detail})
 if not ok:print('FAIL',name,str(detail)[:400],flush=True)
def hash_(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=['branches','stages','slots','finish','routes','gems','gemGuide','jewelGuide','equipmentTargets','chineseAscendancy','variants','atlasSource','atlasUnlock','atlasRecords','atlasRecordAudit','atlasPrimaryAudit','atlasStarter','filterGuide','learningPages']
for k in protected:ck('原业务数据不变/'+k,D[k]==D0[k])
for sub in ['R28原站','filters']:
 fs=[p for p in (B/sub).rglob('*') if p.is_file()];ck('逐字节保护/'+sub,all((O/p.relative_to(B)).exists() and hash_(p)==hash_(O/p.relative_to(B)) for p in fs),{'files':len(fs)})
ck('金币修正',hash_(O/'filters/01_Fubgun_Early_Mapping_GoldFix_R37_1.filter')=='6064c1afe0ec9f548a6fbdf7164b802f378c3b322f6f4846d8012b7134123b95')
for id,m in D0['materials'].items():ck('原材料保留/'+id,D['materials'][id]==m)
for k,g in D['essenceGuide']['slots'].items():
 for t in ['lesser','normal','greater']:
  opts=[D['essenceGuide']['catalog'][v] for v in g['options'] if D['essenceGuide']['catalog'][v]['tier']==t]
  ck('部位档位都有明确参考/'+k+'/'+t,len(opts)>0)
  ck('条目效果与适用部位一致/'+k+'/'+t,all(k in m['slots'] and k in m['effect'] for m in opts))
  for m in opts:ck('用料记录/'+k+'/'+m['id'],'r38-'+m['id'] in D['materials'])
for s in ['quiver','gloves']:ck('低阶激战不套用/'+s,not any(x in D['essenceGuide']['slots'][s]['options'] for x in ['battle-lesser','battle-normal']))
for s in ['boots','gloves','quiver']:ck('急速不当鞋手箭袋攻速/'+s,not any('haste' in x for x in D['essenceGuide']['slots'][s]['options']))
ck('戒指普通身躯与强效差异','body-normal' in D['essenceGuide']['slots']['rings']['options'] and 'body-greater' not in D['essenceGuide']['slots']['rings']['options'])
ck('原九类执行只改增幅提示',all([(lambda old,new:old==new)(
 {k:v for k,v in x.items() if k not in ['title','note']},
 {k:v for k,v in D['executionViews']['routes'][rid]['route']['steps'][i].items() if k not in ['title','note']})
 for rid,rv in D0['executionViews']['routes'].items() for i,x in enumerate(rv.get('route',{}).get('steps',[]))]))
r=subprocess.run(['node','--check',str(O/assets['app'])],capture_output=True,text=True);ck('JavaScript语法',r.returncode==0,r.stderr)
for ref in re.findall(r'(?:src|href)="([^"#]+)"',h):
 if not ref.startswith(('http','data:')):ck('首页引用/'+ref,(O/ref).exists())
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(O)));threading.Thread(target=srv.serve_forever,daemon=True).start()
mode='';screens=[]
with sync_playwright() as pw:
 br=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=br.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
 for url in [f'http://127.0.0.1:{srv.server_address[1]}/index.html',O.as_uri()+'/index.html']:
  try:
   p.goto(url,wait_until='load',timeout=6000);p.wait_for_selector('.eq-table',timeout=2000);nav.append({'url':url,'ok':True});mode='real '+url.split(':')[0];break
  except Exception as e:nav.append({'url':url,'ok':False,'error':str(e)[:900]})
 if not mode:
  mem=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(O/m[1]).read_text()+'</style>',h)
  mem=re.sub(r'<script src="([^"]+)"></script>',lambda m:'<script>'+(O/m[1]).read_text().replace('</script','<\\/script')+'</script>',mem)
  p.goto('about:blank');p.set_content(mem,wait_until='load');mode='memory document: actual built HTML CSS JS'
 p.add_style_tag(content='html{scroll-behavior:auto!important}')
 def go(route):
  p.evaluate('(r)=>{location.hash="#/"+r;render()}',route)
  p.wait_for_function('(r)=>document.querySelector("#main-content").dataset.page===r.split(/[/?]/)[0]',arg=route)
  ck('页面加载/'+route,not p.locator('h1').inner_text().startswith('页面暂时'))
 def stable():p.wait_for_timeout(65)
 def content():return p.locator('#main-content').inner_text()
 # Source snapshot stages, all item tabs. No stage is locked by progress.
 for s in D['stages']:
  sid=s['id'];go('gear?stage='+sid);ck('首页先全身目标/'+sid,p.locator('#gear-main').count()==1)
  for slot in ['bow','quiver','body','helmet','gloves','boots','amulet','belt','ring1','ring2','jewels','life_flask','charm1','weapon2']:
   for tab in ['target','plan','steps','finish']:
    go('item/'+slot+'?stage='+sid+'&tab='+tab)
    ck('分区真实切换/'+sid+'/'+slot+'/'+tab,p.locator('[data-item-tab="'+tab+'"]').count()==1)
    if tab!='steps':ck('非操作区不塞操作表/'+sid+'/'+slot+'/'+tab,p.locator('#item-craft').count()==0)
    if sid=='e06':ck('06不出现普通精华执行/'+slot+'/'+tab,p.locator('[data-essence-option]').count()==0)
 # Stage-free campaign reference: each slot/tier uses its own effects, not all gems crammed onto one page.
 for slot,g in D['essenceGuide']['slots'].items():
  for tier in ['lesser','normal','greater']:
   go('early-craft?slot='+slot+'&tier='+tier)
   wanted=[v for v in g['options'] if D['essenceGuide']['catalog'][v]['tier']==tier]
   got=p.locator('[data-essence-option]').evaluate_all('(els)=>els.map(e=>e.dataset.essenceOption)')
   ck('工作台精华集合/'+slot+'/'+tier,got==wanted)
 # Real click, not a DOM-text-only assertion.
 go('early-craft?slot=bow&tier=lesser')
 p.locator('[data-essence-option="abrasion-lesser"] .btn').click();stable()
 ck('选择精华进入步骤',p.locator('#r40-kind').count()==1 and '次级磨蚀精华' in content())
 for kind in ['white','magic1','magic2','rare','blocked']:
  p.locator('#r40-kind').select_option(kind);stable();txt=content()
  ck('前期状态/'+kind,(('停止普通加工' in txt) if kind=='blocked' else ('不能继续用于这件黄装' in txt) if kind=='rare' else ('增幅不是精华的必需前置' in txt) if kind=='magic1' else ('新增1条' in txt) if kind=='magic2' else ('白装不能直接' in txt)))
 go('early-craft?slot=bow&tier=lesser&view=steps&kind=magic1');ck('未选精华停止默认用料','未选择精华：保持蓝装' in content())
 # Changing slot/tier discards incompatible selected material and returns to choose.
 go('early-craft?slot=bow&tier=lesser&essence=abrasion-lesser&view=steps')
 p.locator('#r40-slot').select_option('quiver');stable();ck('换部位清除不合用材料','abrasion-lesser' not in p.evaluate('location.hash'))
 p.locator('#r40-tier').select_option('normal');stable();ck('低阶箭袋无激战精华','激战精华' not in p.locator('.r40-ess-table').inner_text())
 # Item plan -> selected steps -> next decision preserves all required state.
 go('item/ring1?stage=e01&tab=plan&tier=normal');p.locator('[data-essence-option="body-normal"] .btn').click();stable()
 ck('单件材料切换步骤',p.locator('[data-item-tab="steps"]').count()==1 and '只使用一次：身躯精华' in content())
 ck('单件步骤不重复精华大表',p.locator('#item-essences').count()==0)
 p.locator('#stage-select').select_option('e02');stable();ck('切阶段保留分区',p.locator('[data-item-tab="steps"]').count()==1)
 p.locator('#item-select').select_option('boots');stable();ck('切部位保留分区清除材料',p.locator('[data-item-tab="steps"]').count()==1 and 'essence=' not in p.evaluate('location.hash'))
 go('item/bow?stage=e01&tab=plan&tier=lesser');p.locator('#r40-item-tier').select_option('normal');stable();ck('单件档位联动',p.locator('[data-essence-option="abrasion-normal"]').count()==1 and p.locator('[data-essence-option="abrasion-lesser"]').count()==0)
 # Explicit decision scenarios; not a fake recommendation based on player account.
 decisions=[({'type':'magic','wear':'unknown','need':'bottleneck','budget':'yes'},'先核对'),({'type':'blocked','wear':'yes','need':'bottleneck','budget':'yes'},'现在停止'),({'type':'magic','wear':'yes','need':'soon','budget':'yes'},'暂时不值得'),({'type':'magic','wear':'yes','need':'bottleneck','budget':'no'},'保留现用'),({'type':'rare','wear':'yes','need':'bottleneck','budget':'yes'},'先验收'),({'type':'magic','wear':'yes','need':'bottleneck','budget':'yes'},'可以比较一次')]
 go('craft-timing')
 for vals,result in decisions:
  for k,v in vals.items():p.locator(f'[name="{k}"]').select_option(v)
  p.locator('#r40-decision [type="submit"]').click();stable();ck('投入判断/'+result,result in p.locator('#r40-decision-result').inner_text())
 # New routes + every retained learning page and original specialist entry points.
 routes=['guide','craft-timing','early-craft','supplies','troubleshoot','coverage','character?stage=e01','jewels?stage=e05','special-jewels?stage=e05','gems?stage=e01','special-gems?stage=e05','atlas-starter','atlas-choose','atlas-unlock','tools','tools/filters','filter-guide','filter-check']+['learn/'+k for k in D['learningPages']]
 for route in routes:
  go(route);ck('五个主分区/'+route,p.locator('#main-nav>a.nav-item').count()==5)
  ck('重复ID/'+route,p.evaluate('(()=>{let a=[...document.querySelectorAll("[id]")].map(e=>e.id);return a.length===new Set(a).size})()'))
 ck('全站搜索前期精华',p.evaluate('searchData("前期").some(x=>x.route==="early-craft")'))
 ck('全站搜索投入时机',p.evaluate('searchData("什么时候").some(x=>x.route==="craft-timing")'))
 # Layout check and current actual output screenshots.
 layouts=[('gear?stage=e01','全身装备'),('guide?period=campaign','成长路线'),('craft-timing','打造时机'),('early-craft?slot=boots&tier=lesser','前期鞋子精华'),('early-craft?slot=bow&tier=lesser&view=steps&kind=magic1&essence=abrasion-lesser','一词蓝弓步骤'),('item/bow?stage=e01&tab=target','装备目标'),('item/bow?stage=e01&tab=plan&tier=lesser','精华材料分区'),('item/ring1?stage=e01&tab=finish','收尾验收'),('troubleshoot','故障排查'),('coverage?status=open','待核实项')]
 for width in [390,768,1024,1440,1920]:
  p.set_viewport_size({'width':width,'height':1000})
  for route,name in layouts:
   go(route);stable();ck('页面宽度/'+str(width)+'/'+name,p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
   if width==1440 and name in ['成长路线','打造时机','前期鞋子精华','精华材料分区','一词蓝弓步骤']:
    p.evaluate('scrollTo(0,0)');f='R40_'+name+'_1440.png';p.screenshot(path=str(W/f),full_page=False);screens.append(f)
   if width==390 and name=='前期鞋子精华':
    f='R40_前期精华_390.png';p.screenshot(path=str(W/f),full_page=False);screens.append(f)
 ck('无未捕获JS异常',not errors,errors)
 br.close()
srv.shutdown()
result={'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'mode':mode,'real_navigation_attempts':nav,'errors':errors,'screenshots':screens,'checks':checks}
(W/'R40_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2),flush=True)
