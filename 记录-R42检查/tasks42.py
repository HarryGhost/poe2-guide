from pathlib import Path
import json,asyncio,sys,hashlib,re,zipfile,base64
sys.path.insert(0,str(Path(__file__).parent));from smoke import ROOT,CHECK,load,go
from visual import images
from playwright.async_api import async_playwright
D=json.loads(Path('/mnt/data/r42_work/data41.json').read_text());G=json.loads(Path('/mnt/data/r42_work/src/guide42.json').read_text())
async def main():
 result={'flows':[],'views':[],'errors':[],'anchorRepairs':[],'layouts':[]}
 def record(name,ok,details=None):result['flows'].append({'name':name,'ok':bool(ok),'details':details})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  p=await b.new_page(viewport={'width':1440,'height':1000},accept_downloads=True);p.on('pageerror',lambda e:result['errors'].append(str(e)));await load(p,True)
  # Native user paths, not string-existence checks.
  await go(p,'#/guide?cp=l02&tab=next');txt=await p.locator('#main-content').inner_text();record('24级预留数量与等级直接可见',all(v in txt for v in ['3颗','7级','4–5']))
  await p.get_by_role('link',name=re.compile('查看下一阶段：24')).click();await p.wait_for_timeout(100);record('15–23→24–30保留剧情上下文','cp=l03' in p.url)
  await p.get_by_role('link',name='技能与操作',exact=True).click();await p.wait_for_timeout(100);record('24级技能表在主页面，没有iframe',await p.locator('iframe').count()==0 and '闪电箭矢' in await p.locator('main').inner_text())
  await go(p,'#/guide?cp=l06&tab=next');await p.get_by_role('link',name=re.compile('查看下一阶段：01')).click();await p.wait_for_timeout(100);record('通关衔接→01不继承旧剧情参数','stage=e01' in p.url and 'cp=' not in p.url)
  await go(p,'#/gear?stage=e05');await p.locator('#r42-stage').select_option('l03');await p.wait_for_timeout(100);record('从05主动切剧情：全身目标与阶段同步','cp=l03' in p.url and await p.locator('#r42-stage').input_value()=='l03')
  await go(p,'#/item/boots?cp=l03&tab=target');await p.get_by_role('link',name='目标确认，看怎么做 →',exact=True).click();await p.wait_for_timeout(100);record('目标→制作保留鞋子与24–30',all(v in p.url for v in ['item/boots','cp=l03','tab=craft']))
  await p.locator('#c41-kind').select_option('magic1');await p.wait_for_timeout(80);record('一词蓝装不强迫增幅',await p.locator('#c41-goal').input_value()=='')
  await p.locator('#c41-goal').select_option('life');await p.wait_for_timeout(80)
  card=p.locator('.q42-essences article').filter(has=p.get_by_role('heading',name='次级身躯精华',exact=True));await card.get_by_role('link',name='我有这颗，核对使用步骤').click();await p.wait_for_timeout(80)
  record('明确选择后才给当前一颗材料',await p.locator('.c41-step .c41-tool').inner_text()=='次级身躯精华 ×1')
  await p.get_by_role('link',name='用完：黄装2条，先验收').click();await p.wait_for_timeout(80);record('蓝1→黄2已接上','kind=rare2' in p.url)
  await p.get_by_role('link',name='确认空位与预算，再看补第3条').click();await p.wait_for_timeout(80);record('黄2补第3条实际材料是普通崇高',await p.locator('.c41-step .c41-tool').inner_text()=='普通崇高石 ×1')
  await p.get_by_role('link',name='点完：重新检查3条黄装').click();await p.wait_for_timeout(80);await p.get_by_role('link',name='够用了，查看换上前检查').click();await p.wait_for_timeout(80);await p.get_by_role('link',name='查看本部位品质与镶嵌').click();await p.wait_for_timeout(80);record('加工完回当前剧情部位收尾，没有跳e01',all(v in p.url for v in ['cp=l03','item/boots','tab=finish']) and 'stage=e01' not in p.url)
  await p.get_by_role('link',name='回本阶段，检查下一步').click();await p.wait_for_timeout(80);record('收尾→阶段下一步仍是24–30',all(v in p.url for v in ['guide','cp=l03','tab=next']))
  await go(p,'#/item/bow?stage=e05&tab=craft');record('05弓默认专用暴击路线',await p.locator('#c41-route').input_value()=='bow-crit')
  opts=await p.locator('#c41-advanced-step option').evaluate_all('es=>es.map(e=>({v:e.value,t:e.textContent}))');es=next(x for x in opts if x['v']=='essence');await p.locator('#c41-advanced-step').select_option(es['v']);await p.wait_for_timeout(80);record('暴击弓步骤不混入磨蚀','强效寻觅' in await p.locator('.c41-step').inner_text() and '次级磨蚀' not in await p.locator('.c41-step').inner_text())
  await p.locator('#q42-slot').select_option('helmet');await p.wait_for_timeout(80);record('换部位清除旧配方和材料','bow-crit' not in p.url and 'essence=' not in p.url)
  await go(p,'#/early-craft?stage=e06');record('06不能经普通工作台绕开只读',await p.locator('#c41-kind').count()==0 and '只读' in await p.locator('main').inner_text())
  await go(p,'#/item/boots?cp=l03&tab=craft&kind=magic1');record('看过06再回剧情仍可正常制作',await p.locator('#c41-kind').count()==1)
  await go(p,'#/character?cp=l03&tab=check');await p.locator('[name=total]').fill('60');await p.locator('[name=used]').fill('90');await p.get_by_role('button',name='核对余量').click();record('实际精魂不足30的结果','不足 30' in await p.locator('#q42-resource-result').inner_text())
  # Stage checkbox remains keyed to current stage, not globally shared.
  await go(p,'#/guide?cp=l02&tab=next');cb=p.locator('[data-check]').first;key=await cb.get_attribute('data-check');await cb.check();await go(p,'#/guide?cp=l03&tab=next');record('换阶段不继承上一阶段完成勾选',not await p.locator('[data-check]').first.is_checked());await go(p,'#/guide?cp=l02&tab=next');record('返回原阶段保留手动勾选',await p.locator('[data-check]').first.is_checked())
  await go(p,'#/tools');await p.get_by_text('导出／恢复网页中的手动勾选记录',exact=True).click()
  async with p.expect_download() as dd:await p.get_by_role('button',name='导出记录 JSON').click()
  download=await dd.value;await download.save_as(str(CHECK/'records-export.json'));ex=json.loads((CHECK/'records-export.json').read_text());record('导出是R42且含网页勾选，不冒充游戏存档',ex['version']=='R42' and ex['entries'].get('fubgun-layout-check-'+key)=='1')
  await p.locator('[data-search]').first.click();await p.locator('#search-input').fill('24');await p.wait_for_timeout(80);record('全站搜索可找到剧情24级入口',await p.locator('#search-results').inner_text()!='');await p.keyboard.press('Escape')
  await go(p,'#/tools/filters');downloads=await p.locator('main a[download]').evaluate_all('es=>es.map(e=>({h:e.getAttribute("href"),n:e.textContent}))');record('当前下载只露出四份原版',len(downloads)==4 and all('原版过滤器_从这里选' in x['h'] for x in downloads),downloads)
  (CHECK/'native-flows.json').write_text(json.dumps(result['flows'],ensure_ascii=False,indent=2))
  # All ordinary item states, including malformed direct links and gating, separate from UI page count.
  for ctx in ['l02','l04','e01','e04','e06']:
   for slot in ['bow','quiver','helmet','body','gloves','boots','amulet','ring1','ring2','belt']:
    for kind in ['unknown','white','magic1','magic2','rare2','rare3','rare4','rare5','rare6','blocked']:
     q=('cp=' if ctx[0]=='l' else 'stage=')+ctx;r='#/item/'+slot+'?'+q+'&tab=craft&route=early-'+('rings' if slot.startswith('ring') else slot)+'&kind='+kind
     info=await go(p,r);record('状态覆盖 '+ctx+'/'+slot+'/'+kind,not info['error'] and not info['dups'])
  for width in [390,768,1024,1440,1920]:
   await p.set_viewport_size({'width':width,'height':950})
   for r in ['#/gear?stage=e01','#/guide?cp=l03&tab=skills','#/guide?cp=l02&tab=next','#/item/boots?cp=l03&tab=craft&kind=magic1&goal=life','#/item/bow?stage=e05&tab=craft','#/learn/permanent?cp=l02&part=1','#/atlas/expedition?tab=masters','#/atlas-choices?group=biome','#/tools/filters','#/filter-check']:
    info=await go(p,r);result['layouts'].append({'width':width,'route':r,'ok':not info['overflow'] and not info['error']})
  result['summary']={'flows':len(result['flows']),'flowFailures':sum(not x['ok'] for x in result['flows']),'views':len(result['views']),'viewFailures':sum(not x['ok'] for x in result['views']),'layouts':len(result['layouts']),'layoutFailures':sum(not x['ok'] for x in result['layouts']),'pageErrors':len(result['errors'])}
  (CHECK/'tasks-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['summary']));print('fails',json.dumps([x for x in result['flows']if not x['ok']]+[x for x in result['views']if not x['ok']]+[x for x in result['layouts']if not x['ok']],ensure_ascii=False)[:15000]);print('anchor repairs',result['anchorRepairs'][:20]);await b.close()
if __name__=='__main__':asyncio.run(main())
