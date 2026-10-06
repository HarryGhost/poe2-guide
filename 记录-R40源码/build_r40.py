#!/usr/bin/env python3
"""Build R40 from an unpacked R39. Python standard library only. No source snapshot mutations."""
from __future__ import annotations
import argparse,hashlib,json,re,shutil
from pathlib import Path
from content_r40 import extend
HERE=Path(__file__).resolve().parent

def read_data(root):
    html=(root/'index.html').read_text()
    files={k:re.search(r'(assets/'+k+r'\.[^" ]+\.'+ext+r')',html).group(1) for k,ext in [('app','js'),('content','js'),('site','css')]}
    js=(root/files['content']).read_text().strip()
    return html,files,json.loads(json.loads(js.split('textContent=',1)[1].rstrip(';')))

def build(base:Path,out:Path):
    if base.resolve()==out.resolve():raise ValueError('Output must be a new directory, not the R39 source.')
    html,old,D=read_data(base)
    if D['release']['version']!='R39':raise ValueError('Expected verified R39 baseline.')
    out.mkdir(parents=True,exist_ok=True)
    shutil.copytree(base,out,dirs_exist_ok=True)
    D=extend(D)
    js=(base/old['app']).read_text()
    # Keep original implementations for deterministic partitioning, not a duplicate page underneath the new one.
    for f in ['gear','character','guide','itemPage','nav','footer','r38EssencePanel','r38CraftParams']:
        token='function '+f+'('
        assert js.count(token)==1,(f,js.count(token))
        js=js.replace(token,'function '+f+'R39(',1)
    start="window.addEventListener('hashchange',render);render();document.documentElement.dataset.releaseReady='true';"
    assert start in js;js=js.replace(start,'// Initial render follows R40 declarations below.')
    js=js.replace("try{if(page==='gear')body=gear();", "try{if(page==='craft-timing'){body=craftTiming();group='gear';crumb='什么时候值得打造'}else if(page==='early-craft'){body=earlyCraft();group='gear';crumb='剧情／低投入工作台'}else if(page==='supplies'){body=supplies();group='gear';crumb='底材与材料循环'}else if(page==='troubleshoot'){body=troubleshoot();group='guide';crumb='卡关与故障排查'}else if(page==='coverage'){body=coverage();group='tools';crumb='覆盖审阅与待核实'}else if(page==='gear')body=gear();")
    js=js.replace("const names={guide:'入门与成长路线',character:'人物与技能',gear:'装备养成',atlas:'异界与刷图',tools:'资料与工具'};", "const names={guide:'成长路线',character:'人物配置',gear:'装备与打造',atlas:'异界与产出',tools:'查询与下载'};")
    js=js.replace("document.title=crumb+' · Fubgun 冰射攻略 · R39'", "document.title=crumb+' · Fubgun 冰射攻略 · R40'")
    js=js.replace('closeNav();r38AfterRender();','closeNav();r40AfterRender();')
    js=js.replace("function searchData(q){let data=[", "function searchData(q){let data=[...r40SearchEntries(),")
    js=js.replace("params:{stage:state.stage,route:g.route,step:'essence-choice'}", "params:{stage:state.stage,route:g.route,tab:'plan',tier:'lesser'}")
    js=js.replace("if(e.target.id==='item-select'){navigate('item/'+e.target.value,{stage:state.stage});return;}", "if(e.target.id==='item-select'){navigate('item/'+e.target.value,{stage:state.stage,tab:current.params?.get('tab')||'target',tier:r40Tier()});return;}")
    js=js.replace("navigate(r,{stage:state.stage});}", "navigate(r,{stage:state.stage,...(current.section==='item'?{tab:current.params?.get('tab')||'target',tier:r40Tier()}:{} )});}")
    js=js.replace("route:e.target.value,...(p.get('alternate')", "route:e.target.value,tab:current.params?.get('tab')||'steps',tier:r40Tier(),...(p.get('alternate')")
    js=js.replace("step:e.target.value,...(p.get('essence')", "step:e.target.value,tab:'steps',tier:r40Tier(),...(p.get('essence')")
    js+='\n'+(HERE/'app_r40.js').read_text()+'\n'+start+'\n'
    css=(base/old['site']).read_text()+'\n'+(HERE/'style_r40.css').read_text()
    dat=json.dumps(D,ensure_ascii=False,separators=(',',':'))
    content='document.getElementById("site-data").textContent='+json.dumps(dat,ensure_ascii=False)+';\n'
    for k,txt,ext in [('app',js,'js'),('content',content,'js'),('site',css,'css')]:
        rel='assets/'+k+'.'+hashlib.sha256(txt.encode()).hexdigest()[:12]+'.'+ext
        (out/rel).write_text(txt);html=html.replace(old[k],rel)
    html=html.replace('Fubgun 冰射攻略 · R39','Fubgun 冰射攻略 · R40').replace('0.5.5 · R39 人物天赋珠宝','0.5.5 · R40 成长与打造')
    html=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Fubgun 冰射攻略 R40：剧情与低投入精华、打造时机、全身目标优先、分标签装备工作区、材料循环与卡关诊断。">',html)
    html=html.replace('先看目标，再看具体做法。<br>人物加点与异界加点分开。','目标 → 判断 → 操作 → 验收。<br>人物珠宝与技能宝石分开。')
    (out/'index.html').write_text(html)
    (out/'data/R40-progression-guide.json').write_text(json.dumps(D['progressionGuide'],ensure_ascii=False,indent=2)+'\n')
    (out/'data/R40-essence-guide.json').write_text(json.dumps(D['essenceGuide'],ensure_ascii=False,indent=2)+'\n')
    for name,route in [('剧情精华与低投入打造','early-craft'),('什么时候打造装备','craft-timing'),('成长路线','guide'),('全站覆盖与待核实','coverage'),('卡关与故障排查','troubleshoot')]:
        (out/(name+'_从这里打开.html')).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+name+'</title><script>location.replace("index.html#/'+route+'");</script><a href="index.html#/'+route+'">'+name+'</a></html>')
    (out/'00_先读我.md').write_text('''# R40｜成长路线与打造工作区\n\n完整解压，打开 index.html；默认仍是全身装备目标。\n\n- 剧情临时装备：装备与打造 → 剧情／低投入工作台。\n- 是否值得投入：装备与打造 → 什么时候值得打造。\n- 单件装备：完整目标／投入与材料／操作步骤／收尾与验收，四个标签。\n- 成长路线：剧情、初入异界、稳定刷图、转型分别阅读；不把01 Early当剧情快照。\n- 珠宝与技能宝石分别在人物配置中查看；升华、永久奖励、地图和材料有任务入口。\n\n原BD、原技能连接、原异界数据、7份过滤器与R37.1金币修正保留，06只读。\n\n数据是用户0.5.5快照和标注来源的补充，不保证与你当前游戏区服逐字一致。未完成项见全站覆盖页。\n''')
    (out/'README_上线.md').write_text('''# R40 静态网站使用\n\n上传此包解压后的全部内容，保证 index.html 位于站点入口，并保留所有相对路径。没有后端或构建依赖。不要只上传首页而漏掉新哈希资源。\n\n本包不包含自动发布行为。R40维护源码接受完整R39目录，输出到新的独立目录；不能用R37旧脚本覆盖当前版本。\n\n当前清单为 SHA256SUMS_R40.txt。旧清单只是历史记录。浏览器验证方式及未做的游戏实测见 R40_全站审阅与重排说明.md。\n''')
    sourceout=out/'R40维护源码';sourceout.mkdir(exist_ok=True)
    for f in ['content_r40.py','build_r40.py','app_r40.js','style_r40.css']:
        shutil.copy2(HERE/f,sourceout/f)
    (sourceout/'README.md').write_text('''# 重建 R40\n\nPython3标准库即可生成：\n\n```sh\npython build_r40.py --base /path/to/R39 --out /path/to/new_R40\n```\n\n必须输入完整R39，输出新目录。基础业务数据和旧资源保留，新界面以新的哈希文件名引用。\n浏览器检查另需 playwright、Chromium；检查脚本的路径按本机修改。原包历史检查不等于本轮重跑。\n''')
    return D
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=build(a.base,a.out);print(json.dumps({'output':str(a.out),'version':d['release']['version'],'essences':len(d['essenceGuide']['catalog']),'audit_topics':len(d['progressionGuide']['audit'])},ensure_ascii=False))
