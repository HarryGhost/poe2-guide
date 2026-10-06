"""Independent R45 task paths and scoped regression; not game validation."""
from pathlib import Path
import json,re,hashlib,base64,urllib.parse,sys
from playwright.sync_api import sync_playwright
W=Path(__file__).parent;cfg=json.loads((W/'build_paths.json').read_text());S=Path(cfg['site']);B=Path(cfg['baseline']);K=W/'checks';K.mkdir(exist_ok=True);PART=sys.argv[1] if len(sys.argv)>1 else 'tasks'
C=json.loads((S/'data/R43_capture_overlay.json').read_text());G=json.loads((S/'data/R45_selection_guide.json').read_text());L=json.loads((S/'data/R44_localization.json').read_text())
r={'part':PART,'complete':False,'checks':[],'views':[],'pageerrors':[],'english':{},'method':'Actual generated HTML/CSS/JS, native clicks/hash in Chromium memory document; real navigation attempts separately recorded in smoke.json.'}
def ck(name,ok,detail=None):
 r['checks'].append({'name':name,'ok':bool(ok),'detail':detail})
 if PART=='tasks':print('CHECK',name,bool(ok),flush=True)
 if not ok: print('FAIL',name,detail,flush=True)
def save(): (K/f'test45-{PART}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
idx=(S/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)"',idx);html=re.sub(r'<script src="[^"]+"></script>','',idx);html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',html)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 p=browser.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:r['pageerrors'].append(str(e)))
 p.set_content(html);p.add_style_tag(path=str(S/cfg['style']))
 for js in scripts:p.add_script_tag(path=str(S/js))
 for f in(S/'assets').glob('references.*.js'):p.add_script_tag(path=str(f));break
 p.wait_for_selector('[data-ready="true"]')
 def goto(h):
  r['in_progress_route']=h
  try:
   p.evaluate('(h)=>location.hash="#/"+h',h);p.wait_for_timeout(70);p.wait_for_selector('[data-ready="true"]',timeout=5000)
  except Exception as e:
   r['navigation_exception']=str(e);r['failure_text']=p.locator('body').inner_text();save();raise
 def scan(h):
  o=p.evaluate('''()=>{const c=document.querySelector('#main-content'),ids=[...c.querySelectorAll('[id]')].map(e=>e.id);return {dupes:ids.filter((x,i)=>ids.indexOf(x)!==i),dead:[...c.querySelectorAll('[data-scroll]')].filter(e=>!document.getElementById(e.dataset.scroll)).map(e=>e.dataset.scroll),width:document.documentElement.scrollWidth,viewport:innerWidth,objects:c.innerText.includes('[object Object]'),text:c.innerText};}''');text=o.pop('text');ok=not o['dupes']and not o['dead']and not o['objects']and o['width']<=o['viewport']+1;r['views'].append({'route':h,'ok':ok,**o})
  en=[x for x in text.splitlines()if re.search('[A-Za-z]{3,}',x)]
  if en:r['english'][h]=en
  if not ok:print('VIEWFAIL',h,o,flush=True)
  if len(r['views'])%40==0:save();print(PART,'views',len(r['views']),flush=True)
  return text
 def pic(name,h,full=False):
  goto(h)
  for img in p.locator('#main-content img').all():
   src=img.get_attribute('src');f=S/urllib.parse.unquote(src or '')
   if f.is_file():
    m='image/jpeg'if f.suffix.lower()in['.jpg','.jpeg']else'image/svg+xml'if f.suffix.lower()=='.svg'else'image/png';img.evaluate('(e,s)=>e.src=s','data:'+m+';base64,'+base64.b64encode(f.read_bytes()).decode())
  p.wait_for_timeout(150);p.screenshot(path=str(K/(name+'.png')),full_page=full)
  (K/(name+'.txt')).write_text(p.locator('#main-content').inner_text())
 if PART in ['stages1','stages2','stages3']:
  index=int(PART[-1])-1
  for b in C['builds'][index*2:index*2+2]:
   st=b['stage'];goto('gear?stage='+st);text=scan('gear?stage='+st)
   ck(st+' every captured equipment',p.locator('[data-capture-item]').count()==len(b['equipment']))
   ck(st+' all actual modifiers directly visible',p.locator('[data-capture-item] [data-r43-mod]:visible').count()==sum(len(it['panel']['modifiers'])for it in b['equipment']))
   ck(st+' socket associations visible',p.locator('.r43-rune:visible').count()==sum(len(it['socketed_items'])for it in b['equipment']))
   ck(st+' jewel count same',p.locator('[data-capture-jewel]').count()==len(b['jewels']))
   for it in b['equipment']:
    base=p.locator('[data-capture-item="'+it['id']+'"]')
    ck(st+' raw panel unchanged '+it['uid'],base.locator('.r43-proof pre').first.text_content()==it['panel']['raw_text'])
    if it['uid']in G['guides'][st]:
     g=G['guides'][st][it['uid']];ck(st+' immediate selection guidance '+it['uid'],base.locator('[data-r45-guide]').is_visible())
     if st!='e06':
      ck(st+' all phase-specific base candidates visible '+it['uid'],all(L['names'].get(x['en'],x['name']).replace('沙漠之帽','沙漠帽')in base.inner_text() or x['name'] in base.inner_text() for x in g['bases']if x['current']))
      ck(st+' actionable stop visible '+it['uid'],base.locator('.r45-card-stop').is_visible())
   if st=='e06':ck('Read-only never offers crafting from equipment',p.locator('.r43-card-action a').count()==0)
   for it in b['equipment']:
    for tab in ['target','craft','finish']:
     h='item/'+it['uid']+'?stage='+st+'&tab='+tab;goto(h);text=scan(h)
     if tab=='target'and it['uid']in G['guides'][st]and st!='e06':
      ck(h+' guidance open',p.locator('#r45-guide-'+it['uid']).get_attribute('open')is not None)
      ck(h+' guidance has action conditions',all(x in text for x in ['什么时候换','怎样取得','白底和成品','做到这里先停']))
      ck(h+' no old fixed result mislabeled', '约183–336'not in text)
   for tab in ['overview','skills','craft','next']:
    h='guide?stage='+st+'&tab='+tab;goto(h);text=scan(h)
    if tab=='overview':
     ck(h+' uses current-data scope', '与装备总览使用同一份当前采集数据' in text)
     ck(h+' actual mod count',p.locator('.r45-current-targets [data-r43-mod]').count()==sum(len(i['panel']['modifiers'])for i in b['equipment']if i['uid']in ['bow','quiver','helmet','body','gloves','boots','amulet','belt','ring1','ring2']))
     ck(h+' utility actual mods',p.locator('.r45-current-utility [data-r43-mod]').count()==sum(len(i['panel']['modifiers'])for i in b['equipment']if i['uid']not in ['bow','quiver','helmet','body','gloves','boots','amulet','belt','ring1','ring2']))
    if tab=='skills':ck(h+' current captured skill groups',p.locator('[data-skill-captured]').count()==len(b['skill_gems']['groups']))
   for tab in ['skills','tree','play','check']:
    h='character?stage='+st+'&tab='+tab;goto(h);scan(h)
    if tab=='tree':ck(h+' tree visible not hidden',p.locator('[data-r45-visible-tree]').is_visible())
   for path in ['jewels','special-jewels','gems','special-gems','early-craft','craft-timing']:
    h=path+'?stage='+st;goto(h);text=scan(h)
    if path in ['jewels','special-jewels']:ck(h+' preparation available even without capture', '怎么准备、怎么替换'in text and '取得：'in text)
 elif PART=='atlas':
  for v in C['atlas']:
   for tab in ['tree','choices','masters','setup','play','source']:
    h='atlas/'+v['id']+'?tab='+tab;goto(h);text=scan(h)
    if tab=='choices':
     ck(h+' captured selected bindings',p.locator('.r43-node').count()==len(v['keystone_selections']))
     p.locator('#r43-node-query').fill('不存在的节点xyz');ck(h+' search filters',p.locator('.r43-node:visible').count()==0);p.locator('#r43-node-query').fill('');ck(h+' clear restores all',p.locator('.r43-node:visible').count()==len(v['keystone_selections']))
    if tab=='masters':ck(h+' actual master selected count',p.locator('.r43-section>.r43-grid>article').count()==sum(m['selected_count']for m in v['masters']))
    if v['id']=='expedition'and tab=='play':
     ck('Expedition full operation remains visible',all(x in text for x in ['各取一种','重投','8–9','4–6','首领传闻①','独特地图传闻⑤','专名待核']))
     ck('Expedition no hidden whole-rule wrapper',p.locator('.r44-unverified-names').count()==0)
     ck('Expedition display not English names',not re.search(r'Opulent|Power|Death|Bond|Uthred',text))
  for cp in ['l01','l02','l03','l04','l05','l06']:
   for path in ['gear','guide','character','early-craft']:
    h=path+'?cp='+cp;goto(h);scan(h)
   for tab in ['skills','craft','next']:
    h='guide?cp='+cp+'&tab='+tab;goto(h);scan(h)
  for path in ['tools/filters','tools/capture-audit','tools/names','tools/selection-guide','tools/builds','atlas-starter','atlas-choose','atlas-choices','learn/ascendancy','learn/permanent','supplies','troubleshoot','filter-guide','filter-check']:
   goto(path+'?stage=e01');scan(path+'?stage=e01')
 elif PART=='tasks':
  goto('gear?stage=e01');scan('gear?stage=e01')
  for q,route,keyword in [('狂热弓','item/bow','裸底材'),('蛇鳞外套','item/body','基础闪避260'),('击杀回蓝','jewels','2%击杀回蓝'),('金刚箭','item/quiver','该箭的击中必定暴击')]:
   stage='e04'if q=='金刚箭'else'e01';goto('gear?stage='+stage)
   p.locator('[data-search]').first.click();p.locator('#search-input').fill(q);p.wait_for_timeout(130)
   ck('Native search has '+q,p.locator('.search-result').count()>0)
   p.locator('.search-result').first.click();p.wait_for_timeout(200);h=p.evaluate('location.hash');txt=p.locator('#main-content').inner_text()
   ck('Native search targets '+q,route in h and 'stage='+stage in h and keyword in txt,{'hash':h,'found':keyword in txt})
   ck('Search result has no dead scroll',not p.evaluate("[...document.querySelectorAll('[data-scroll]')].filter(e=>!document.getElementById(e.dataset.scroll)).length"))
  # Current phase stays on target -> native crafting -> target.
  goto('item/bow?stage=e02&tab=target');p.locator('a').filter(has_text='进入一步步做').first.click();p.wait_for_timeout(130)
  ck('Target to craft retains e02','stage=e02'in p.evaluate('location.hash')and'tab=craft'in p.evaluate('location.hash'))
  p.locator('a').filter(has_text='先选底材／替代').click();p.wait_for_timeout(130)
  ck('Craft returns to correct open bases','stage=e02'in p.evaluate('location.hash')and p.locator('#r45-guide-bow').is_visible())
  goto('item/quiver?stage=e04&tab=target');txt=scan('native unique quiver')
  ck('Six distinct arrow functions',p.locator('.r45-arrows tbody tr').count()==6 and all(t in txt for t in ['渐强箭','裂片箭','回转箭','金刚箭','贪婪箭','钝击箭']))
  goto('jewels?stage=e06');j=p.locator('[data-capture-jewel]').first;ck('Emerald captured ranges preserved',all(s in j.inner_text()for s in ['5-15','25-29','30-34','2-4']))
  j.locator('summary').first.click();ck('Raw source opens unchanged','increased Attack Damage'in j.inner_text())
  goto('item/bow?stage=e04&tab=craft');p.locator('#c41-route').select_option('bow-crit')if p.locator('#c41-route').count()else None
  p.locator('#c41-advanced-step').select_option('essence');p.wait_for_timeout(120);txt=p.locator('.c41-step').inner_text()
  ck('Crit recipe actual essence only Seeking','强效寻觅精华'in txt and '次级磨蚀'not in txt)
  # Path exposes exact next steps, not just rendered text assertions.
  goto('item/boots?cp=l03&tab=craft');p.locator('#c41-kind').select_option('magic1');p.wait_for_timeout(100)
  (K/'native-blue1.html').write_text(p.locator('#main-content').inner_html())
  controls=p.locator('select').evaluate_all('(xs)=>xs.map(x=>({id:x.id,value:x.value,options:[...x.options].map(o=>({value:o.value,label:o.text}))}))');(K/'native-controls.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2))
  links=p.locator('#main-content a').evaluate_all('(xs)=>xs.map(x=>({text:x.innerText,href:x.getAttribute("href")}))');(K/'native-links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2))
  # Manual selector presence controls next native step; guarded so diagnosis stays in evidence.
  for goalid in ['c41-goal','c41-need']:
   if p.locator('#'+goalid).count():p.locator('#'+goalid).select_option('life');p.wait_for_timeout(100);break
  links=p.locator('#main-content a').evaluate_all('(xs)=>xs.map(x=>({text:x.innerText,href:x.getAttribute("href")}))');(K/'native-links-life.json').write_text(json.dumps(links,ensure_ascii=False,indent=2))
  candidates=p.locator('#main-content a[href*="essence=body-lesser"]')
  if candidates.count():
   candidates.first.click();p.wait_for_timeout(140);txt=p.locator('#main-content').inner_text();ck('Native lesser body chosen','次级身躯'in txt and'cp=l03'in p.evaluate('location.hash'))
   nexts=p.locator('#main-content a').filter(has_text=re.compile('黄装.*2|2.*黄装|两词'))
   if nexts.count():nexts.first.click();p.wait_for_timeout(130)
   else:
    results=p.locator('#main-content a').filter(has_text=re.compile('结果.*符合|已.*升黄|实际.*结果'))
    if results.count():results.first.click();p.wait_for_timeout(130)
   txt=p.locator('#main-content').inner_text();ck('Blue1 to rare2 current context','cp=l03'in p.evaluate('location.hash') and p.locator('#c41-kind').input_value()=='rare2',p.evaluate('location.hash'))
   add=p.locator('#main-content a').filter(has_text=re.compile('第3|第三'))
   ck('Rare2 has conditional third affix native action',add.count()>0)
   if add.count():add.first.click();p.wait_for_timeout(130);ck('Third affix step uses exalt explicitly','崇高石'in p.locator('.c41-step').inner_text())
  else:ck('Native choose lesser body link available',False,p.locator('#main-content').inner_text())
  goto('tools/filters?stage=e01');txt=scan('tools/filters?stage=e01');download=p.locator('#main-content a[download]').evaluate_all('(xs)=>xs.map(x=>({href:x.getAttribute("href"),name:x.getAttribute("download")}))');ck('Only four original filter downloads',len(download)==4,download)
  for x in download:
   f=S/urllib.parse.unquote(x['href']);ck('Original filter download exists '+x['name'],f.exists())
  # Compare current growth panel to the equipment page using the same translated text, not fixed values.
  goto('gear?stage=e01');mods=p.locator('#r43-item-bow .r43-mods').inner_text();goto('guide?stage=e01&tab=overview');ck('Growth and gear exact bow mod texts',p.locator('.r45-current-targets .r43-mods').first.inner_text()==mods)
  for width in [390,768,1024,1440,1920]:
   p.set_viewport_size({'width':width,'height':1000})
   for h in ['gear?stage=e01','item/bow?stage=e01&tab=target','item/quiver?stage=e04&tab=target','jewels?stage=e01','guide?stage=e02&tab=overview','atlas/expedition?tab=play','character?stage=e03&tab=tree','item/bow?stage=e04&tab=craft']:
    goto(h);scan('width='+str(width)+' '+h)
  p.set_viewport_size({'width':1440,'height':1100})
  for name,h in [('gear','gear?stage=e01'),('bases','item/bow?stage=e01&tab=target&focus=r45-guide-bow'),('jewels','jewels?stage=e01'),('arrows','item/quiver?stage=e04&tab=target'),('atlas','atlas/expedition?tab=play'),('tree','character?stage=e03&tab=tree'),('craft','item/bow?stage=e04&tab=craft')]:pic(name,h)
  p.set_viewport_size({'width':390,'height':1000});pic('mobile','gear?stage=e01')
 ck('No JavaScript exceptions',not r['pageerrors'],r['pageerrors']);r['complete']=True;save();browser.close()
print(PART,'assertions',len(r['checks']),'failed',sum(not x['ok']for x in r['checks']),'views',len(r['views']),'failed',sum(not x['ok']for x in r['views']),'english',len(r['english']),flush=True)
