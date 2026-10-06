from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import re,json
W=Path('/mnt/data/work_R41');R=json.loads((W/'build_result.json').read_text());S=Path(R['output']);OUT=W/'checks';OUT.mkdir(exist_ok=True)
html=(S/'index.html').read_text();css=(S/R['css']).read_text();data=(S/R['content']).read_text();app=(S/R['app']).read_text()
mem=re.sub(r'<link[^>]*href="[^"]+\.css"[^>]*>',lambda m:'<style>'+css+'</style>',html)
mem=re.sub(r'<script src="[^"]*content\.[^"]+\.js"></script>',lambda m:'<script>'+data.replace('</script','<\\/script')+'</script>',mem)
mem=re.sub(r'<script src="[^"]*app\.[^"]+\.js"></script>',lambda m:'<script>'+app.replace('</script','<\\/script')+'</script>',mem)
checks=[];errors=[];console=[]
def check(name,condition,detail=None):
 checks.append({'name':name,'passed':bool(condition),'detail':detail})
 if not condition:print('FAIL',name,detail)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':1440,'height':1000});p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:console.append(e.text) if e.type=='error' else None)
 def asset(route):
  from urllib.parse import urlparse,unquote
  f=S/unquote(urlparse(route.request.url).path).lstrip('/')
  route.fulfill(path=str(f)) if f.is_file() else route.abort()
 p.route('https://r41.test/**',asset);p.goto('about:blank');p.set_content(mem,wait_until='domcontentloaded');p.wait_for_timeout(300)
 def go(h):p.evaluate('(h)=>location.hash=h','#/'+h);p.wait_for_timeout(90)
 def text():return p.locator('#main-content').inner_text()
 def click(selector,word=None):
  l=p.locator(selector) if word is None else p.locator(selector).get_by_role('link',name=word,exact=True)
  l.click();p.wait_for_timeout(110)
 # Literal user task 1: target -> real craft, same stage and slot.
 for st in ['e01','e02','e03','e04','e05','e06']:
  go(f'item/bow?stage={st}&tab=target');button=p.get_by_role('link',name='查看只读限制' if st=='e06' else '这件怎么做 →',exact=True)
  check(st+' target action is link',button.count()==1)
  button.click();p.wait_for_timeout(100)
  check(st+' target opens craft preserving context','tab=craft' in p.url and 'stage='+st in p.url and 'item/bow' in p.url)
  check(st+' craft no old materials tab','投入与材料' not in text())
  if st=='e06':check('e06 no consumable controls',p.locator('#c41-route,#c41-kind').count()==0 and '不生成耗材操作' in text())
 # Named01 entrance after e05 history.
 go('gear?stage=e05');go('guide?period=entry')
 a=p.get_by_role('link',name='01整套装备目标',exact=True)
 if not a.count():
  print('guide link missing text excerpt',text()[:2000])
 check('01 explicit link exists',a.count()>0)
 if a.count():
  check('01 explicit href not history', 'stage=e01' in a.first.get_attribute('href'));a.first.click();p.wait_for_timeout(80);check('01 click stage is e01',p.locator('#stage-select').input_value()=='e01')
 # Boots full once: blue1 + selected essence -> rare2 -> third -> stop.
 go('early-craft?slot=boots&period=pre31&kind=magic1');row=p.locator('.c41-essences article').filter(has_text='次级身躯精华')
 check('boots lower tier present',row.count()==1);row.get_by_role('link',name='用这颗：看本次操作').click();p.wait_for_timeout(90)
 check('boots uses selected tool only',p.locator('.c41-tool').inner_text()=='次级身躯精华 ×1');check('blue1 yields explicit rare2','1条蓝装变为2条' in text())
 p.screenshot(path=str(OUT/'R41_过渡鞋子_具体操作_1440.png'),full_page=True)
 p.get_by_role('link',name='用完：黄装2条，先验收',exact=True).click();p.wait_for_timeout(100);check('rare2 readable','黄装2条：先比较' in text())
 p.get_by_role('link',name='确认空位与预算，再看补第3条',exact=True).click();p.wait_for_timeout(100);check('third affix explicit','只补第3条，不连点' in text() and p.locator('.c41-tool').inner_text()=='普通崇高石 ×1')
 p.get_by_role('link',name='点完：重新检查3条黄装',exact=True).click();p.wait_for_timeout(100);check('rare3 context preserved','slot=boots' in p.url and 'period=pre31' in p.url and '黄装3条' in text())
 p.get_by_role('link',name='够用了，查看换上前检查',exact=True).click();p.wait_for_timeout(100);check('stop no hidden followup','这轮先结束' in text() and p.locator('.c41-tool').inner_text()=='不再使用加词缀材料')
 # White and augmentation optional branches.
 go('early-craft?slot=boots&kind=white');check('white only transmute','普通蜕变石 ×1' in text() and '白装不能直接' in text())
 go('early-craft?slot=boots&kind=magic1');p.get_by_role('link',name='可选：先用增幅补第2条',exact=True).click();p.wait_for_timeout(90);check('aug optional branch','普通增幅石 ×1' in text() and '不是精华的必要前置' in text())
 # Crit route never gets a general material matrix, proper exact advanced essence.
 go('item/bow?stage=e05&tab=craft');check('crit default route',p.locator('#c41-route').input_value()=='bow-crit');check('crit no generic essence chooser',p.locator('.c41-essences').count()==0)
 check('ready names optional augmentation','普通增幅石 ×1' in p.locator('.c41-tool').inner_text())
 p.locator('#c41-advanced-step').select_option('essence');p.wait_for_timeout(100);check('crit exact essence',p.locator('.c41-tool').inner_text()=='强效寻觅精华')
 check('crit persists route and stage',p.locator('#c41-route').input_value()=='bow-crit' and p.locator('#stage-select').input_value()=='e05')
 p.screenshot(path=str(OUT/'R41_暴击弓_专用步骤_1440.png'),full_page=True)
 p.locator('#c41-route').select_option('early-bow');p.wait_for_timeout(100);check('explicit alternative changes recipe without stage',p.locator('#c41-route').input_value()=='early-bow' and p.locator('#stage-select').input_value()=='e05' and '不是上方高配目标' in text())
 p.locator('#c41-kind').select_option('magic2');p.wait_for_timeout(90);check('explicit generic now has matching options',p.locator('.c41-essences').count()==1)
 # Switching parts resets invalid material/recipe; two ring limitation.
 go('item/bow?stage=e01&tab=craft&kind=magic1&action=essence&essence=abrasion-lesser');p.locator('#item-select').select_option('boots');p.wait_for_timeout(100);check('part change clears selected essence','essence=' not in p.url and '次级磨蚀精华' not in text())
 for s in ['ring1','ring2']:
  go(f'item/{s}?stage=e01&tab=craft&kind=magic1&goal=life');card=p.locator('.c41-essences');check(s+' only lesser/normal body',card.locator('article').count()==2 and card.get_by_role('heading',name='强效身躯精华',exact=True).count()==0)
 go('early-craft?slot=bow&kind=magic1&goal=damage-cold');check('early elemental candidate','次级冰霜精华' in text() and '掉落等级25' in text())
 go('early-craft?slot=boots&kind=rare6');check('rare6 no add seventh',p.get_by_role('link',name=re.compile('补第7')).count()==0 and '不再用普通崇高' in text())
 # Special slot protection and current unique.
 go('item/belt?stage=e05&tab=craft');check('unique no ordinary craft default','目标是暗金' in text() and p.locator('#c41-kind').count()==0)
 go('item/weapon2?stage=e01&tab=craft');check('secondary no automatic duplication','先确认该武器组是否共享主手' in text())
 # Atlas across all seven default and starter; actual profile/group changes.
 go('atlas-starter');p.get_by_role('link',name='大节点选哪项',exact=True).click();p.wait_for_timeout(100);check('starter opens true selection section',p.locator('[data-atlas-node]').count()>0 and '主树常用' in text())
 go('atlas/expedition');p.get_by_role('link',name='大节点选哪项',exact=True).click();p.wait_for_timeout(100);check('Fubgun view selection integrated','战略优势' in text() and '不是作者逐项实装' in text())
 p.locator('#a41-profile').select_option('crit');p.wait_for_timeout(100);check('crit selected seeking profile',p.locator('[data-atlas-node="crystal"] .a41-pick b').inner_text()=='寻觅精华组')
 check('crit dowsing not mislabeled noncrit','寻觅不在这个节点里' in p.locator('[data-atlas-node="essence"]').inner_text())
 p.get_by_role('link',name='地貌与城市',exact=True).click();p.wait_for_timeout(100);check('biome main six present',all(x in text() for x in ['草原专精','沙漠专精','山地专精','水域专精','沼泽专精','森林专精']))
 p.screenshot(path=str(OUT/'R41_异界大节点_地貌选择_1440.png'),full_page=True)
 go('atlas-choices?profile=ritual-belts&group=ritual');check('ritual belts specific correct',p.locator('[data-atlas-node="ritual-type"] .a41-pick b').inner_text()=='污秽的' and '弥漫黑暗' in text())
 go('atlas-choices?profile=lineage-gems&group=abyss');check('lineage not jewel',p.locator('[data-atlas-node="abyss-treasure"] .a41-pick b').inner_text()=='血脉辅助掉落几率提高50%')
 # Tabs moved source sections: make sure all seven source links really switch, not dead scroll.
 for variant in ['expedition','ritual-belts','currency-abyss','breach-rares','abyss-rares','lineage-gems','deli-rush']:
  go('atlas/'+variant+'?tab=masters');lnk=p.get_by_role('link',name=re.compile('原页核对.*来源与原记录')).first
  check('source link route '+variant,lnk.count()==1 and 'tab=source' in lnk.get_attribute('href'))
  lnk.click();p.wait_for_timeout(90);check('source click preserves '+variant,'atlas/'+variant in p.url and 'tab=source' in p.url and p.locator('#atlas-source').count()==1)
 # Original filters only active download and select.
 go('tools/filters');downloads=p.locator('#main-content a[download]').evaluate_all('(es)=>es.map(x=>({name:x.download,href:x.getAttribute("href")}))');check('four original downloads only',len(downloads)==4 and all(not any(w in x['name'] for w in ['GoldFix','Materials','Bases_Shards']) for x in downloads),downloads)
 go('filter-guide?f=01b');check('old derivative deep link clearly original','当前明确' in text() or '明确切到01' in text());check('selector only original IDs',p.locator('#fg-file option').evaluate_all('(es)=>es.map(x=>x.value)')==['02','01','03','04'])
 # Width checks current three functional screens, not keywords only.
 for width in [390,768,1024,1440,1920]:
  p.set_viewport_size({'width':width,'height':950})
  for route in ['early-craft?slot=boots&kind=magic1','item/bow?stage=e05&tab=craft&route=bow-crit&step=essence','atlas-choices?profile=starter&group=biome']:
   go(route);metrics=p.evaluate('()=>({overflow:document.documentElement.scrollWidth>innerWidth,dupes:[...document.querySelectorAll("[id]")].map(x=>x.id).filter((x,i,a)=>a.indexOf(x)!==i)})');check(f'layout {width} {route}',not metrics['overflow'] and not metrics['dupes'],metrics)
   if width==390 and route.startswith('early'):p.screenshot(path=str(OUT/'R41_打造_手机390.png'),full_page=True)
 check('no uncaught JS errors',not errors,errors);check('no swallowed render errors',not [x for x in console if 'Error' in x and 'resource' not in x],[x for x in console if 'Error' in x])
 b.close()
(OUT/'flows.json').write_text(json.dumps({'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'pageerrors':errors,'console':console},ensure_ascii=False,indent=2));print(json.dumps({'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'errors':errors},ensure_ascii=False))
