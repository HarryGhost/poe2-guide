#!/usr/bin/env python3
"""Create the single-BD Ghostliness reading edition from verified local inputs.
Never edits the original site, character snapshot, .build or .filter files.
"""
from __future__ import annotations
import argparse, copy, hashlib, html, json, re, shutil
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--character',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    B,P,O=args.baseline.resolve(),args.character.resolve(),args.output.resolve()
    if O.exists() or O==B or B in O.parents or O in B.parents:
        raise SystemExit('Output must be a new directory separate from the baseline.')
    C=json.loads((B/'data/R43_capture_overlay.json').read_text())
    L=json.loads((B/'data/R44_localization.json').read_text())
    G=json.loads((B/'data/R45_selection_guide.json').read_text())
    player=json.loads((P/'character.json').read_text())
    author=next(x for x in C['builds'] if x['stage']=='e04')
    s=(B/'assets/content.e69d3567dd9c.js').read_text()
    D=json.loads(json.loads(s.split('.textContent=',1)[1].strip().rstrip(';')))
    O.mkdir(parents=True); (O/'assets').mkdir();(O/'evidence').mkdir();(O/'originals').mkdir()
    (O/'data').mkdir(); (O/'notes').mkdir()
    protected=[]
    def cp(src: Path, dst: str) -> str:
        t=O/dst;t.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,t)
        protected.append({'source_path':str(src.relative_to(B)) if src.is_relative_to(B) else str(src.relative_to(P)) if src.is_relative_to(P) else src.name,'output':dst,'sha256':sha(src)})
        assert sha(src)==sha(t)
        return dst
    names={k.lower():v for k,v in L['names'].items()}
    pat=re.compile(r'(?<![A-Za-z0-9_])(?:'+ '|'.join(map(re.escape,sorted(L['names'],key=len,reverse=True)))+r')(?![A-Za-z0-9_])', re.I)
    def cn(x: Any) -> str:
        st=str(x or '');st=L['sentences'].get(st,st).replace('’',"'").replace('‘',"'")
        for _ in range(2): st=pat.sub(lambda m:names.get(m[0].lower(),m[0]),st)
        for a,b in L['textAliases'].items():st=st.replace(a,b)
        for a,b in [('III','Ⅲ'),('II','Ⅱ'),('IV','Ⅳ'),('I','Ⅰ')]:st=re.sub(r'\b'+a+r'\b',b,st)
        return st.replace('Fubgun','作者').replace('03及后续','混合防御方向').replace('04/05','暴击方向')
    def mod(m):
        raw=m['text']; t=L['modifiers'].get(raw,m.get('zh',raw));return cn(t)
    def reqs(panel):
        trans={'Level':'等级','Dexterity':'敏捷','Intelligence':'智慧','Strength':'力量'}
        return '、'.join(trans.get(x['label'],cn(x['label']))+' '+str(x['value']) for x in panel.get('requirements',[])) or '面板未提供'
    def stats(panel):
        trans={'Critical Hit Chance':'物品暴击率','Physical Damage':'物理伤害','Cold Damage':'冰霜伤害','Fire Damage':'火焰伤害','Lightning Damage':'闪电伤害','Energy Shield':'能量护盾','Evasion':'闪避值','Evasion Rating':'闪避值','Armour':'护甲','Attacks per Second':'每秒攻击次数'}
        return [{'label':trans.get(v['label'],cn(v['label'])),'value':v['value']} for v in panel.get('top_stats',[])]
    def ev_author(src,kind):
        if not src:return None
        f=B/'采集证据_20261005'/src
        return cp(f,'evidence/author/'+kind+f.suffix) if f.is_file() else None
    def ev_player(src,kind):
        f=P/src
        return cp(f,'evidence/character/'+kind+f.suffix) if f.is_file() else None
    # Snapshot/status semantics are kept from the source; this is not a live scan.
    identity={k:player['identity'][k] for k in ['name','level','class']}
    meta={'edition':'R46','date':'2026-10-06','identity':identity,'selected_build':'Crit Hybrid','selected_name':'暴击混合防御','author':'Fubgun','player_captured':player['captured_at'],'author_captured':author['captured_at'],'reference_tree_level':94,'live_game_seen':False,'refresh_time':None}
    cp(args.plan,'notes/当前阶段与三步调整.md')
    cp(P/'README.md','evidence/character/原采集说明.md')
    # Only the one chosen build and the two relevant original mapping filters are delivered.
    cp(B/'R28原站/构筑文件/04_Crit_Hybrid.build','originals/暴击混合防御.build')
    filters=[]
    for name,title,desc in [('01_Fubgun_Early_Mapping.filter','异界起步原版','原作者保存的异界起步文件；仅供按原需求选用。'),('03_Fubgun_Endgame_Mapping.filter','异界终局原版','原作者保存的终局文件；不因本版精简就要求立即切换。')]:
        path=cp(B/'原版过滤器_从这里选'/name,'originals/'+name)
        filters.append({'name':title,'description':desc,'path':path,'sha256':sha(O/path)})
    pos={'主手武器':'bow','副手箭袋':'quiver','头盔':'helmet','胸甲':'body','手套':'gloves','鞋子':'boots','项链':'amulet','腰带':'belt','左戒指':'ring1','右戒指':'ring2','生命药剂':'life_flask','魔力药剂':'mana_flask','护符1':'charm1','护符2':'charm2','护符3':'charm3'}
    order=['bow','quiver','helmet','body','gloves','boots','amulet','belt','ring1','ring2','life_flask','mana_flask','charm1','charm2','charm3']
    labels={'bow':'主手弓','quiver':'箭袋','helmet':'头盔','body':'胸甲','gloves':'手套','boots':'鞋子','amulet':'项链','belt':'腰带','ring1':'左戒指','ring2':'右戒指','life_flask':'生命药剂','mana_flask':'魔力药剂','charm1':'咒符一','charm2':'咒符二','charm3':'咒符三'}
    actions={
      'bow':('先保留','已有暴击基础，当前先解决防御短板。已经腐化，不套普通蓝装精华流程。',''),
      'quiver':('先保留','与当前暴击方向相符，本轮不重做箭袋。',''),
      'helmet':('配套后换','没有显示能量护盾；先准备能穿的高护盾头，与恢复技能、智慧和天赋一起核对。','helmet'),
      'body':('先保留','胸甲与镶嵌承担大量抗性。没有补回整套净损失前，不为更高闪避直接换掉。',''),
      'gloves':('先保留','当前偏输出，后续可作为防御补位方向；本轮不同时换全身。',''),
      'boots':('先保留','保有精魂、火抗、闪电抗贡献，当前不是首要更换位。',''),
      'amulet':('先保留','先保住49精魂、力量与火抗，不先为额外伤害换掉。',''),
      'belt':('先保留','有生命、力量与药剂／咒符相关属性，先保留本轮配装基础。',''),
      'ring1':('优先替换','先找冷抗、闪电抗、生命合适的成品；右戒会复制得失，必须同时算火抗和魔力。','ring'),
      'ring2':('暂时保留','随左戒一起比较。作者的两枚普通戒指不是你本轮必须照搬的组合。','ring'),
      'life_flask':('优先替代','准备能手动应急的生命药剂。旧“机遇”有狙击窗口收益，保留，不卖掉。','flasks'),
      'mana_flask':('优先比较','优先比较不扣生命且恢复、充能能跟上的替代品，不先等指定暗金。','flasks'),
      'charm1':('先保留','暂不整套重买咒符，触发与效果按实际面板分别检查。',''),
      'charm2':('先保留','暂不整套重买咒符，触发与效果按实际面板分别检查。',''),
      'charm3':('先保留','暂不整套重买咒符，不能把条件性回复当任意时刻的应急回血。','')}
    items=[]
    for uid in order:
        p=next(x for x in player['equipment'] if pos[x['slot']]==uid)
        a=next(x for x in author['equipment'] if x['uid']==uid)
        photo=next((s for s in p['evidence'] if s.endswith('.jpg')),None)
        pc={'name':p['name'],'raw_tooltip':p['raw_tooltip'],'lines':p['raw_tooltip'].splitlines()[1:], 'image':ev_player(photo,uid) if photo else None,'quality_status':p['field_status'].get('quality'),'sockets':[]}
        for i,sock in enumerate(x for x in player['sockets'] if x['owner_equipment_display_index']==p['display_index']):
            pc['sockets'].append({'name':sock['name'],'index':sock['socket_display_index'],'text':sock['raw_tooltip'],'effect_context':sock['effect_context']})
        ac={'name':cn(a['name']),'modifiers':[mod(m) for m in a['panel']['modifiers']], 'stats':stats(a['panel']),'requirements':reqs(a['panel']),'quality':a['quality'],'sockets':[], 'image':ev_author(a.get('imageEvidence'),'equipment-'+uid), 'warnings':[cn(w) for w in a.get('sourcePanelCaution',[])], 'raw_tooltip':a['panel']['raw_text'],'capture_index':a['id']}
        for sock in a.get('socketed_items',[]):
            ac['sockets'].append({'name':cn(sock['name']),'index':sock['socket_index'],'effects':[mod(m) for m in sock['panel']['modifiers']]})
        g=copy.deepcopy(G['guides']['e04'].get(uid))
        if g:
            for bas in g['bases']:
                bas.pop('phases',None);bas.pop('en',None);bas['why']=cn(bas['why'])
                bas['stage_note']='本套可比较的底材，不是本轮全部采购目标'
            g={k:g[k] for k in ['title','brief','keep','when','acquire','stop','compare','sourceLabel','bases','supplement']}
            for k,v in g.items():
                if isinstance(v,str):g[k]=cn(v)
            if uid in ['ring1','ring2']:
                g.update(brief='你当前采用一枚左戒＋映射右戒。先比较左戒的整套净收益，不要求换成作者两枚普通戒指。',keep='本轮先补冷抗、闪电抗与生命；原左戒的火抗和魔力同时受映射影响。',when='保持现用品，只在新成品的抗性、生命与供蓝净得失核对后再换。',stop='冷、电缺口补上，同时火抗、魔力与技能没有因此失效。',compare='保持原全抗贡献的条件例子：左戒另有冷抗23%、闪电抗11%，映射后分别增加46、22个百分点。火抗溢出未知，不能保证只靠这三条就完成整套。')
        unique=G['unique'].get(a['name'])
        items.append({'id':uid,'label':labels[uid],'player':pc,'target':ac,'status':actions[uid][0],'advice':actions[uid][1],'work':actions[uid][2],'guide':g,'unique':unique,'is_main':uid in order[:10]})
    # Chinese skill names reuse the existing localization; source order and ACTIVE vs SUPPORT are retained.
    player_skills=[]
    for p in player['skills']:
        core=next((v for v in p['gems'] if v['role']=='displayed_core_gem'),p['gems'][0])
        player_skills.append({'name':cn(p['display_name']),'level':p['display_level'],'gems':[cn(g['name']) for g in p['gems'] if g['role']=='connected_gem'],'core_text':core['raw_tooltip'],'quality':'未取得实际品质','weapon_group':'未取得实际启用／武器组','order':p['display_index']})
    skills=[]
    for a in author['skill_gems']['groups']:
        print_name=cn(a['active_skill']['name'])
        pp=next((x for x in player_skills if x['name']==print_name),None)
        con=[{'name':cn(g['name']),'role':'内嵌主动' if g.get('gem_type')=='ACTIVE' else '辅助','level':g.get('level')} for g in a['connected_gems']]
        weapon=a.get('weapon_set');print( 'skill group',print_name,weapon )
        skills.append({'name':print_name,'player':pp,'gems':con,'weapon_group':{'set1':'武器组Ⅰ','set2':'武器组Ⅱ'}.get(weapon,'两组共同常驻／以实际设置为准'),'quality':a.get('configured_quality'),'player_present':pp is not None})
    extra_skills=[x for x in player_skills if x['name'] not in {a['name'] for a in skills}]
    tree=ev_author(author['treeImage'],'天赋参考原图')
    priorities=[{'name':cn(t['name']),'raw_name':t['name'],'id':t['slug']} for t in author['treePriorities']]
    own_tree=[]
    for src in player['passive_tree']['evidence']:
        if src.endswith('.jpg') and ('node_' not in src): own_tree.append(ev_player(src,Path(src).stem))
    jewels=[]
    for j in author['jewels']:
        photo=next((e['file'] for e in j['evidence'] if e['file'].endswith('.jpg')),None)
        jewels.append({'name':cn(j['name']),'modifiers':[mod(x) for x in j['panel']['modifiers']],'node':j['node_id'],'selected':j['node_in_explicit_selected_lists'],'image':ev_author(photo,'jewel-'+str(j['display_order'])) if photo else None})
    jewel_guidance=copy.deepcopy(G['jewels'])
    jewel_guidance['ordinary']['body']='暴击攻击路线比较攻击、投射物、有效元素伤害、弓攻速，以及攻击暴击率和攻击暴击伤害；法术限定词缀不作攻击收益。'
    jewel_guidance['ordinary']['fallback']='缺特殊珠宝时继续合适的普通输出／资源珠宝。当前不把特殊珠宝列入本轮三项优先采购。'
    # Keep the relevant spare helmet recipe, not costly alternate builds or unrelated recipe catalogues.
    er=D['executionViews']['routes'];hr=next(x for x in er if x['route']['id']=='helmet-stable')['route'] if isinstance(er,list) else er['helmet-stable']['route']
    # The optional two-add/high-risk quality branches are outside this personal edition; raw inputs remain in R45.
    retained_steps=[x for x in hr['steps'] if x['id'] not in ['suffix-double','quality']]
    recipe=[]
    for x in retained_steps:
        r={k:copy.deepcopy(x.get(k,'')) for k in ['id','title','before','action','expect','good','bad','note','kind','refs','next']}
        for k in ['title','before','expect','good','bad','note']:r[k]=cn(r[k])
        r['action']=[cn(t) for t in r['action']]
        if r['next'] in ['suffix-double','quality']:r['next']='finish'
        # No promise to continue spending: display the original conditional route, with a stop available at every step.
        recipe.append(r)
    ess=json.loads((B/'data/R40-essence-guide.json').read_text())
    ring_ess=[]
    for k,x in ess['catalog'].items():
        if 'rings' in x['slots'] and (k.startswith('body') or k.startswith('cold') or k.startswith('lightning')):
            ring_ess.append({'id':k,'name':cn(x['zh']),'tier':{'lesser':'次级','normal':'普通','greater':'强效'}[x['tier']],'effect':x['effect']['rings'],'side':x['side'],'limit':x['limit'],'url':x['url']})
    # Source section includes only current references. The full R45 and diagnostic ZIP remain unchanged outside the edition.
    cut={'kept_build':'Crit Hybrid','removed_builds':['Early','non-crit Midgame','non-crit Hybrid swap','Uber Endgame','Live Gear'],'removed_guides':['六段剧情练级','跨构筑升级路线','其他作者练级资料','七套收益刷法与独立大师配置','非暴击弓制作','高投入项链、破溃箭袋、毕业珠宝工艺','高风险双加与注能分支','历史补充过滤器','旧版本源码、报告和重复截图'],'not_deleted':'原R45完整包、角色诊断包和既有原文件未覆盖或删除；仅新当前使用版按白名单制作。','atlas_scope':'只保留当前刷图边界说明，不替未知的个人异界树分配节点。'}
    data={'meta':meta,'panels':player['panels'],'items':items,'skills':skills,'extra_skills':extra_skills,'jewels':jewels,'jewel_guidance':jewel_guidance,'tree':tree,'tree_priorities':priorities,'own_tree':own_tree,'helmet_recipe':recipe,'ring_essences':ring_ess,'filters':filters,'arrows':G['arrows'],'cut':cut}
    # Presentation is a source-derived view; raw target equipment and player strings for the one build are kept separately.
    (O/'data/当前使用内容.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    refs={'baseline':'R45','chosen_stage':'e04','chosen_name':'Crit Hybrid','plan':args.plan.name,'author':{'capture_sha256':author['source_configuration_sha256'],'source_url':author['source_url'],'equipment':[{k:x[k] for k in ['id','uid','name','panel','quality','item_level','socket_count','field_status']} for x in author['equipment']],'jewels':[{k:x[k] for k in ['id','name','panel','node_id','node_in_explicit_selected_lists']} for x in author['jewels']]},'player':{'captured_at':player['captured_at'],'identity':identity,'live_game_seen':False,'snapshot_refresh':None,'equipment':[{k:x[k] for k in ['name','slot','display_index','raw_tooltip','field_status']} for x in player['equipment']],'gaps':player['gaps']},'parent_files':[{'name':'角色诊断ZIP','sha256':'4006a797c927c0c7171c254b44eaa972cdf7caa6d4f1d84b36280ad756755a6e'},{'name':'R45 ZIP','sha256':'c2fc9616d8b9ee3eee251824473d817447606756d4e22d4869671c4e85e74194'}]}
    (O/'evidence/当前来源摘录.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2))
    (O/'evidence/字节保护清单.json').write_text(json.dumps(protected,ensure_ascii=False,indent=2))
    src=Path(__file__).parent
    env=Environment(loader=FileSystemLoader(src),autoescape=select_autoescape(['html']))
    env.filters['cn']=cn
    env.filters['tojson_safe']=lambda x:json.dumps(x,ensure_ascii=False).replace('<','\\u003c')
    env.globals.update(cn=cn)
    nav=[('index.html','当前只做三件事','行动'),('equipment.html','我的全身装备','装备'),('setup.html','技能与天赋','配置'),('crafting.html','本轮补装','补装'),('reference.html','必要资料','资料')]
    for filename,_,label in nav:
        page=filename.split('.')[0]
        out=env.get_template('page.html').render(page=page,nav=nav,current=filename,label=label,d=data)
        (O/filename).write_text(out)
    for f in ['style.css','app.js']:shutil.copyfile(src/f,O/'assets'/f)
    removed='\n'.join('- '+x for x in cut['removed_builds']+cut['removed_guides'])
    report=f'''# Ghostliness｜当前使用版 R46\n\n本次只整理使用范围，没有重新诊断、修改游戏或重做作者构筑。\n\n## 只保留一套\nFubgun「暴击混合防御」（Crit Hybrid），作为当前配装目标；没有认定84级角色已经配齐或应整树洗点。\n\n## 当前保留\n- 三步行动单：补抗与生命、药剂应急、防御配套。\n- 15件现装的完整快照文字、11条镶嵌关联，以及该套15件作者面板。\n- 对应底材需求、替代、词缀取舍；当前戒指映射的净得失说明优先于通用两戒模板。\n- 对应技能连接、天赋参考原图、人物珠宝用途和两颗作者示例。\n- 本轮左戒指、药剂、备用护盾头的补装内容；普通状态处理与有限的专用护盾头路线。\n- 当前刷图边界与两份保存的原版异界过滤器，文件字节不变。\n\n## 从新包、导航、搜索与下载入口剔除\n{removed}\n\n不是永久断言这些构筑永远没用；只是当前不需要读。未来换玩法再有针对性恢复。\n\n## 保留的边界\n角色资料来自2026-10-06采集的官方快照，刷新时间未知；不是游戏现场。作者示例来自2026-10-05采集。原始完整天赋、实际品质/预留、个人异界树仍未知。没有用作者参考树替代你的已点树。没有自动洗点、换装、花材料、修改过滤器或发布线上。\n\n原R45完整包及原始诊断包未覆盖或删除。本包不携带其他构筑的隐藏跳转、旧版本维护目录和历史派生过滤器。原始截图可能带有作者网站菜单，只作为证据，不是本版可选构筑。\n\n## 打开\n完整解压，打开 index.html。可直接离线使用；五个页面只围绕当前一套。不要叠加覆盖R45目录，避免旧文件残留。\n\n详细来源：evidence/当前来源摘录.json、notes/当前阶段与三步调整.md。\n'''
    (O/'00_只看这份.md').write_text(report)
    (O/'notes/保留与移除说明.md').write_text(report)
    (O/'.nojekyll').write_text('')
    print('created',O,'files',sum(x.is_file() for x in O.rglob('*')))

if __name__=='__main__':main()
