from pathlib import Path
import json,re,hashlib
W=Path(__file__).parent; C=W/'capture/fubgun_capture_2026-10-05'; B=W/'baseline'
d=json.loads((C/'builds.json').read_text()); a=json.loads((C/'atlas.json').read_text()); old=json.loads((W/'old_data.json').read_text())
manifest=json.loads((C/'manifest.json').read_text())
checks=[]
for f in manifest['files']:
 p=C/f['path']; checks.append({'path':f['path'],'ok':p.is_file() and len(p.read_bytes())==f['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']})
oldchecks=[]
for l in (B/'SHA256SUMS_R42.txt').read_text().splitlines():
 if not l.strip():continue
 h,n=l.split(None,1);p=B/n.strip().lstrip('*'); oldchecks.append({'path':n.strip(),'ok':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h})
print('capture hashes',len(checks),sum(x['ok'] for x in checks)); print('base hashes',len(oldchecks),sum(x['ok'] for x in oldchecks))
# standalone translation vocab
items=[i for b in d['builds'] for i in b['equipment']+b['jewels']]
runes={s['slug']:s for i in items for s in i.get('socketed_items',[])}
mods=sorted(set(m['text'] for i in items+list(runes.values()) for m in i['panel']['modifiers']))
(W/'modifiers.txt').write_text('\n'.join(f'{n}\t{s}' for n,s in enumerate(mods)))
(W/'modifiers.json').write_text(json.dumps(mods,ensure_ascii=False,indent=2))
choices={s['author_selected']['slug']:s for v in a['variants'] for s in v['keystone_selections']}
(W/'atlas_choices.txt').write_text('\n'.join(f"{s['node_name']} | {s['author_selected']['name']} | {s['author_selected']['selection_description']} | {s['node_id']}" for s in choices.values()))
(W/'runes.txt').write_text('\n\n'.join(x['name']+'\n'+x['panel']['raw_text'] for x in runes.values()))
# Old build compared to captured stored descriptions, not panel ranges
SLOT={'mainHand':'Weapon1','offHand':'Offhand1','helmet':'Helm1','body':'BodyArmour1','gloves':'Gloves1','boots':'Boots1','amulet':'Amulet1','belt':'Belt1','leftRing':'Ring1','rightRing':'Ring2','flask1':'Flask1','flask2':'Flask1','charm1':'Charm1','charm2':'Charm1','charm3':'Charm1'}
compare=[]
for bi,b in enumerate(d['builds']):
 st=old['stages'][bi]; p=B/'R28原站'/st['items'][0]['sourceFile']; raw=json.loads(p.read_text()); assert hashlib.sha256(p.read_bytes()).hexdigest()==st['items'][0]['sourceHash']
 for it in b['equipment']:
  iid='Weapon2' if it['weapon_group']=='Set 2' and it['slot']=='mainHand' else SLOT[it['slot']]
  x=1 if it['slot']=='flask2' else int(it['slot'][-1])-1 if it['slot'].startswith('charm') else 0
  oi=[z for z in raw['inventory_slots'] if z['inventory_id']==iid and z.get('slot_x',0)==x]
  src=it['source_configuration']['commonItem']; newdesc=[q['description'] for q in (src.get('explicitDescriptions') or []) if q.get('description')]
  o=oi[0] if len(oi)==1 else {}
  olddesc=[re.sub(r'^\d+\.\s*','',l) for l in o.get('additional_text','').splitlines()[1:]]
  oldname=o.get('unique_name') or o.get('additional_text','').split('\n')[0]
  compare.append({'build':b['name'],'item':it['name'],'slot':it['slot'],'set':it['weapon_group'],'old_name':oldname,'name_equal':oldname==it['name'],'old_descriptions':olddesc,'captured_saved_descriptions':newdesc,'stored_desc_equal':olddesc==newdesc,'captured_panel_modifiers':[m['text'] for m in it['panel']['modifiers']],'runes':[s['name'] for s in it.get('socketed_items',[])],'panel_top':it['panel']['top_stats']})
print('items',len(compare),'same_name',sum(x['name_equal'] for x in compare),'stored_desc_same',sum(x['stored_desc_equal'] for x in compare),'unique mods',len(mods),'choice defs',len(choices),'runes',len(runes))
for x in compare:
 if not x['name_equal'] or not x['stored_desc_equal']: print('DIFF',json.dumps(x,ensure_ascii=False))
(W/'raw_compare.json').write_text(json.dumps(compare,ensure_ascii=False,indent=2))
(W/'integrity.json').write_text(json.dumps({'capture':checks,'baseline':oldchecks},ensure_ascii=False,indent=2))
