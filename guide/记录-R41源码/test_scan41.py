from pathlib import Path
import json,re,hashlib
from playwright.sync_api import sync_playwright
W=Path('/mnt/data/work_R41');R=json.loads((W/'build_result.json').read_text());S=Path(R['output']);B=W/'baseline';out=W/'checks';out.mkdir(exist_ok=True)
H=(S/'index.html').read_text();M=re.sub(r'<link[^>]*href="[^"]+\.css"[^>]*>',lambda m:'<style>'+(S/R['css']).read_text()+'</style>',H)
for pre,key in [('content','content'),('app','app')]:M=re.sub('<script src="[^"]*'+pre+r'\.[^"]+\.js"></script>',lambda m:'<script>'+(S/R[key]).read_text().replace('</script','<\\/script')+'</script>',M)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':1440,'height':1000});p.set_content(M,wait_until='domcontentloaded')
 rows=p.evaluate('''()=>{let result=[];let errors=[];const old=console.error;console.error=(...args)=>errors.push(args.map(String).join(' '));function one(h){history.replaceState(null,'','#/'+h);render();const root=document.querySelector('#main-content');let ids=[...document.querySelectorAll('[id]')].map(x=>x.id),text=root.innerText;let dead=[...root.querySelectorAll('[data-scroll]')].filter(x=>!document.getElementById(x.dataset.scroll)).map(x=>x.dataset.scroll);result.push({route:h,error:text.includes('页面暂时没有正确载入'),dupes:ids.filter((x,i)=>ids.indexOf(x)!==i),dead,overflow:document.documentElement.scrollWidth>innerWidth});}
 for(const stage of D.stages)for(const slot of D.slots)for(const tab of ['target','craft','finish'])one('item/'+slot.id+'?stage='+stage.id+'&tab='+tab);
 for(const v of D.variants)for(const tab of ['tree','choices','masters','setup','play','source'])one('atlas/'+v.id+'?tab='+tab);
 for(const group of A41.groups)one('atlas-choices?group='+group.id);
 for(const tab of ['route','tree','choices','rules'])one('atlas-starter?tab='+tab);
 for(const r of ['guide','supplies','craft-timing','character','jewels','gems','special-jewels','special-gems','tools/filters','coverage'])one(r);
 console.error=old;return {views:result,errors};}''')
 rows['failures']=[x for x in rows['views'] if x['error'] or x['dupes'] or x['dead'] or x['overflow']]
 (out/'view-scan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('views',len(rows['views']),'failures',len(rows['failures']));print(json.dumps(rows['failures'][:8],ensure_ascii=False,indent=2));print('errors',rows['errors'][:3]);b.close()
# Independent input/output raw data and physical file protection.
base=json.loads((W/'content.json').read_text());current=json.loads(json.loads((S/R['content']).read_text().split('=',1)[1].strip().rstrip(';')))
changed=[k for k in base if base[k]!=current.get(k)];assert changed==['release'],changed
same=[];modified=[]
for f in B.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(B);g=S/rel
 (same if g.is_file() and f.read_bytes()==g.read_bytes() else modified).append(str(rel))
orig=[]
for k in ['01','02','03','04']:
 f=base['filterGuide']['files'][k];a=(B/f['url']).read_bytes();c=(S/'原版过滤器_从这里选'/f['name']).read_bytes();assert a==c
 orig.append({'key':k,'name':f['name'],'sha256':hashlib.sha256(c).hexdigest(),'metadata_match':hashlib.sha256(c).hexdigest()==f['sha256']})
rep={'same_baseline_files':len(same),'modified_baseline_files':modified,'changed_existing_data_keys':changed,'original_filters':orig,'all_legacy_filters_unchanged':all((S/f.relative_to(B)).read_bytes()==f.read_bytes() for f in (B/'filters').glob('*.filter'))}
(out/'integrity.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2));print(json.dumps(rep,ensure_ascii=False,indent=2))
