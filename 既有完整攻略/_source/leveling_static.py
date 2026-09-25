"""Create complete readable campaign reference; stdlib, invoked by build.py."""
import html

def write_leveling_reference(site,data,css):
 esc=lambda s:html.escape(str(s),quote=True)
 L=data['leveling'];terms=L['terms']
 blocks=['<header><div class="eyebrow">CAMPAIGN / 无脚本阅读版</div><h1>剧情练级速查</h1><p>技能配置与逐段变化、装备方向、操作、资源及永久奖励。不是假造的游戏构筑导出或完整天赋坐标图。</p><p><a href="index.html#leveling">返回紧凑交互版</a> · <a href="六分支完整资料.html">异界六分支完整资料</a></p><p>'+esc(L['coverage'])+'</p><nav>'+' · '.join(f'<a href="#lv{s["number"]}">{esc(s["label"])}</a>' for s in L['stages'])+'</nav></header>']
 for s in L['stages']:
  n=s['number'];blocks.append(f'<section id="lv{n}"><h2>{esc(s["label"])} · {esc(s["title"])}</h2><p>{esc(s["intro"])}</p><p class="notice {"warn" if n==6 else ""}">{esc(s["sourceNote"])}</p><p><a href="{esc(s["source"])}">作者对应来源 / 天赋入口（国际服）</a></p><h3>完整技能连接</h3><div class="table-wrap"><table class="wide-table"><thead><tr><th>技能 / 组别</th><th>辅助顺序</th><th>使用说明</th></tr></thead><tbody>')
  for r in s['skills']:
   t=terms[r['skill']];sup='<br>'.join(f'{j+1}. <a href="{esc(terms[k]["url"])}">{esc(terms[k]["zh"])}</a> <small>{esc(terms[k]["en"])}</small>' for j,k in enumerate(r['supports'])) or '原页面未配辅助'
   blocks.append(f'<tr data-level-static="{n}:{r["skill"]}"><td><b>{esc(t["zh"])}</b><br><small>{esc(t["en"])} {"武器组"+str(r["weaponSet"]) if r["weaponSet"] else ""} {"可选" if r["optional"] else ""}</small></td><td>{sup}</td><td>{esc(r["note"])}</td></tr>')
  blocks.append('</tbody></table></div><h3>当前任务</h3><ol>'+''.join('<li>'+esc(t)+'</li>' for t in s['tasks'])+'</ol><h3>装备与材料</h3><div class="table-wrap"><table><thead><tr><th>部位</th><th>目标</th><th>边界</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in r)+'</tr>' for r in s['gear'])+'</tbody></table></div><h3>操作</h3><ol>'+''.join(f'<li><b>{esc(t)}</b>：{esc(v)}</li>' for t,v in s['combat'])+'</ol><p><b>常驻预算：</b>'+esc('、'.join(terms[k]['zh'] for k in s['reserve']))+'；按装好辅助后的实际保留录入。未开启的不要计算。</p><h3>天赋</h3><p>'+esc(s['tree'])+'</p></section>')
 # Adjacent skill/support changes, preserving original order. No invented tree differences.
 blocks.append('<h2>逐段技能差异</h2><p>只比较已收录技能与辅助；不是天赋洗点费用或全部装备变更。最后一组是60+本地衔接与上传Early原件。</p>')
 for i,stage in enumerate(L['stages']):
  a={terms[r['skill']]['zh']:[terms[k]['zh'] for k in r['supports']] for r in stage['skills']}
  if i<5:
   target=L['stages'][i+1]; title=stage['label']+' → '+target['label']
   b={terms[r['skill']]['zh']:[terms[k]['zh'] for k in r['supports']] for r in target['skills']}
  else:
   title=stage['label']+' → 剧情通关后的01 Early'
   b={data['gems'][r['id']]['zh']:[('〔内嵌主动〕' if k['id'].split('/')[-1].startswith('SkillGem') else '')+data['gems'][k['id']]['zh'] for k in r['support_skills']] for r in data['branches'][0]['raw']['skills']}
  rows=[]
  for name in dict.fromkeys([*a,*b]):
   if name in a and name in b and a[name]==b[name]:continue
   status='新增' if name not in a else '移除' if name not in b else '辅助改变'
   before=' / '.join(a[name]) or '未配辅助' if name in a else '—'
   after=' / '.join(b[name]) or '未配辅助' if name in b else '—'
   rows.append('<tr><td>'+esc(name)+'<br>'+status+'</td><td>'+esc(before)+'</td><td>'+esc(after)+'</td></tr>')
  blocks.append('<h3>'+esc(title)+'</h3>')
  if rows:blocks.append('<div class="table-wrap"><table><thead><tr><th>技能</th><th>当前</th><th>下一步</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>')
  else:blocks.append('<p>本地衔接保持已有连接，不因人物达到60级强制换技能。继续完成剧情和任务。</p>')
 blocks.append('<h2>开孔与品质</h2><p>剧情开孔：'+esc(' → '.join(L['priority']['sockets']))+'。剧情品质：'+esc(' → '.join(L['priority']['quality']))+'。</p><p>第一颗低等工匠石先狙击，再冰射；24级转型预留6/7级未切割技能宝石。这里不是逐级固定资源掉落保证。</p>')
 blocks.append('<h2>永久奖励核对</h2><p>只收录作者所列奖励。地图和目标英文保留，不杜撰国服名字；选择项不全部相加。</p><div class="table-wrap"><table><thead><tr><th>章节</th><th>目标</th><th>奖励/备注</th></tr></thead><tbody>'+''.join('<tr><td>'+esc(r['chapter'])+'</td><td>'+esc(r['location'])+'</td><td>'+esc(r['reward'])+'</td></tr>' for r in L['rewards'])+'</tbody></table></div>')
 blocks.append('<h2>名称索引与来源</h2><div class="table-wrap"><table><thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead><tbody>'+''.join(f'<tr><td><a href="{esc(t["url"])}">{esc(t["zh"])}</a></td><td>{esc(t["en"])}</td><td>{esc(t["note"] or t["status"])}</td></tr>' for t in terms.values())+'</tbody></table></div>')
 page='<!doctype html><html lang="zh-CN" data-theme="light" data-density="compact"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>剧情练级速查 · 锐眼冰射</title><style>'+css+'</style></head><body><main class="main">'+''.join(blocks)+'</main></body></html>'
 (site/'剧情练级速查.html').write_text(page,encoding='utf-8')
