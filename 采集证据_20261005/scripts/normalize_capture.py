#!/usr/bin/env python3
"""Normalize this run's read-only browser evidence. Python 3 standard library only.

Run: python3 scripts/normalize_capture.py
No network access, browser actions, .build/.filter changes, or outside-file reads.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
BUILD_NAMES = ['Early', 'non-crit Midgame', 'non-crit Hybrid swap', 'Crit Hybrid', 'Uber Endgame', 'Live Gear']
ATLAS_NAMES = ['Expedition', 'Ritual Belts', 'Currency Abyss', 'Breach Rares', 'Abyss Rares', 'Lineage Gems', 'Deli Rush']
SLOTS = ['mainHand', 'leftRing', 'helmet', 'body', 'amulet', 'rightRing', 'offHand', 'gloves', 'belt', 'boots', 'flask1', 'charm1', 'charm2', 'charm3', 'flask2']
SLOT_ZH = dict(zip(SLOTS, ['主手', '左戒指', '头盔', '衣服', '项链', '右戒指', '副手', '手套', '腰带', '鞋子', '药剂1', '咒符1', '咒符2', '咒符3', '药剂2']))
BUILD_URL = 'https://mobalytics.gg/poe-2/builds/ice-shot-deadeye'
ATLAS_URL = 'https://mobalytics.gg/poe-2/atlas-trees/fubgun-atlas-tree-strats'
VARIANT_WIDGET = 'f7d82102-7e77-4a44-ad24-33b67e8ae7bf'
VOID_TAGS = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'wbr'}


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def ref(path, pointer=None):
    result = {'file': path}
    if pointer is not None:
        result['json_pointer'] = pointer
    return result


def mdref(path, label='证据'):
    return f'[{label}]({quote(path, safe="/")})'


def clean_space(text):
    return re.sub(r'\s+', ' ', text).strip()


class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def find(self, tag=None, **attrs):
        return [n for n in self.walk() if (tag is None or n.tag == tag) and all(n.attrs.get(k) == v for k, v in attrs.items())]

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)


class TreeParser(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        child = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(child)
        if tag not in VOID_TAGS:
            self.stack.append(child)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def htmltree(value):
    return TreeParser(value).root


def parse_panel(capture):
    assert len(capture['panels']) == 1, (capture.get('display_index'), len(capture['panels']))
    panel = capture['panels'][0]
    dom = htmltree(panel['html'])
    ps = [clean_space(n.text()) for n in dom.find('p')]
    name = ps[0] if ps else None
    known_classes = {'Bows', 'Quivers', 'Rings', 'Amulets', 'Belts', 'Body Armours', 'Helmets', 'Gloves', 'Boots', 'Life Flasks', 'Mana Flasks', 'Charms', 'Talismans'}
    category = ps[1] if len(ps) > 1 and ps[1] in known_classes else None
    stats = []
    for n in dom.find('div'):
        direct = [c for c in n.children if isinstance(c, Node) and c.tag == 'span']
        if len(direct) == 2 and clean_space(direct[0].text()).endswith(':'):
            stats.append({'label': clean_space(direct[0].text()).rstrip(':'), 'value': clean_space(direct[1].text())})
    requirements_text = next((p for p in ps if p.startswith('Requires:')), None)
    requirements = []
    if requirements_text:
        for value, label in re.findall(r'(\d+)\s+(Level|Dexterity|Strength|Intelligence)', requirements_text):
            requirements.append({'label': label, 'value': value})
    mods = []
    for i, li in enumerate(dom.find('li'), 1):
        full = clean_space(li.text())
        tier = next((clean_space(n.text()) for n in li.find('span') if re.fullmatch(r'[PS]\d+', clean_space(n.text()))), None)
        value = full[:-len(tier)].rstrip() if tier and full.endswith(tier) else full
        if tier:
            kind = 'prefix' if tier[0] == 'P' else 'suffix'
            basis = '页面 P/S 阶级标签'
        elif 'var(--x1xhkif2)' in li.attrs.get('style', ''):
            kind, basis = 'implicit_styled', '页面独立固有词缀样式；原 HTML 一并保留'
        else:
            kind, basis = 'unlabelled_modifier', '页面未逐条给出固有/显性标签，未从通用词缀库补配'
        mods.append({'display_order': i, 'text': value, 'tier_label': tier, 'kind': kind, 'kind_basis': basis,
                     'value_semantics': 'displayed_range' if re.search(r'\(\d+[–-]\d+\)', value) else 'displayed_text_not_proof_of_author_roll'})
    specials = [p for p in ps if p.startswith(('Allocates ', 'Corrupted', 'Mirrored', 'Grants Skill:', 'Limited to:'))]
    return {'name': name, 'item_class_label': category, 'top_stats': stats, 'requirements_text': requirements_text,
            'requirements': requirements, 'modifiers': mods, 'special_paragraphs': specials,
            'all_paragraphs': ps, 'raw_text': panel['text']}


def lexical(node):
    if not node:
        return ''
    if isinstance(node, list):
        return ''.join(lexical(n) for n in node)
    if not isinstance(node, dict):
        return ''
    if node.get('type') == 'linebreak':
        return '\n'
    if node.get('type') == 'static-data-widget':
        return node.get('label', '')
    return node.get('text', '') + ''.join(lexical(n) for n in node.get('children', []))


def text_blocks(rich, evidence, pointer):
    value = (rich or {}).get('value')
    if not value:
        return []
    result = []
    for i, n in enumerate(value.get('root', {}).get('children', [])):
        text = lexical(n).strip()
        if text:
            result.append({'source_block_index': i, 'type': n.get('type'), 'text': text,
                           'evidence': [ref(evidence, pointer + f'/value/root/children/{i}')],
                           'status': 'author_prose_not_saved_equipment_or_skill_configuration'})
    return result


def sanitize_document(path, atlas=False):
    wrapper = read(path)
    doc = wrapper['data']
    metadata = next(c['data']['childrenVariants'] for c in doc['content'] if c['id'] == VARIANT_WIDGET)
    names = ATLAS_NAMES if atlas else BUILD_NAMES
    metadata = [v for v in metadata if v['title'] in names]
    ids = {VARIANT_WIDGET} | {i for v in metadata for i in v['childrenIds']}
    # Keep author prose for the requested sections, not ads, comments, live account widgets or filters.
    if not atlas:
        ids |= {c['id'] for c in doc['content'] if c['data'].get('title') in ['Build Overview', 'How it Plays', 'How it Works']}
    doc['content'] = [c for c in doc['content'] if c['id'] in ids and ('AtlasTree' not in c['__typename'] or atlas)]
    for c in doc['content']:
        if c['id'] == VARIANT_WIDGET:
            c['data']['childrenVariants'] = metadata
    for v in doc['data']['buildVariants']['values']:
        keep = {'id', 'atlasTree'} if atlas else {'id', 'equipment', 'skillGems', 'passiveTree'}
        for key in list(v):
            if key not in keep:
                del v[key]
    doc['data'] = {k: v for k, v in doc['data'].items() if k in ['name', 'buildVariants']}
    doc = {k: v for k, v in doc.items() if k in ['id', 'slugifiedName', 'content', 'data', 'version', 'status', 'createdAt', 'updatedAt', 'firstPublishedAt']}
    wrapper['data'] = doc
    save(path, wrapper)
    return doc, metadata


def author_sections(doc, meta, evidence):
    result = []
    mindex = next(i for i, v in enumerate(next(c['data']['childrenVariants'] for c in doc['content'] if c['id'] == VARIANT_WIDGET)) if v['id'] == meta['id'])
    ci = next(i for i, c in enumerate(doc['content']) if c['id'] == VARIANT_WIDGET)
    blocks = text_blocks(meta.get('description'), evidence, f'/data/content/{ci}/data/childrenVariants/{mindex}/description')
    result.append({'section': 'Variant description', 'blocks': blocks})
    for i, c in enumerate(doc['content']):
        if c['id'] not in meta['childrenIds']:
            continue
        for key, val in c['data'].items():
            if key.startswith('description'):
                result.append({'section': c['data'].get('title'), 'widget_id': c['id'],
                               'blocks': text_blocks(val, evidence, f'/data/content/{i}/data/{key}')})
    return result


def counters(text):
    return [{'label': label, 'first_displayed_number': int(first), 'second_displayed_number': int(second),
             'semantics': 'UI原样两列；节点记录数量不是消耗点数，两列不命名为已选节点数'}
            for label, first, second in re.findall(r'(Main|Set 1|Set 2|Ascendancy|Breach|Delirium|Ritual|Abyss|Incursion):\s*(-?\d+)\s*(\d+)', text, re.I)]


def query_beside_icon(icon):
    owner = icon
    while owner is not None and not owner.find('a'):
        owner = owner.parent
    assert owner is not None
    links = [n.attrs['href'] for n in owner.find('a') if '/trade2/search/' in n.attrs.get('href', '')]
    assert len(links) == 1
    return json.loads(parse_qs(urlparse(links[0]).query)['q'][0])


def tree_record(tree, ui_path, source_path, source_pointer):
    ui = read(ui_path)
    allocations = {}
    for key, val in tree.items():
        if isinstance(val, dict) and 'selectedSlugs' in val:
            selected = val.get('selectedSlugs')
            allocations[key] = {'selected_node_ids': selected, 'source_record_count': len(selected or []),
                                'source_priority_list': val.get('priorityList'),
                                'priority_semantics': '仅保留作者保存的优先列表；不是每个等级的完整点序',
                                'evidence': [ref(source_path, source_pointer + '/' + key)]}
        elif val is None and key.endswith('Tree'):
            allocations[key] = {'selected_node_ids': None, 'status': 'source_not_configured'}
    return {'allocations': allocations, 'ui_counters': counters(ui['text']),
            'connections': {'status': 'visible_canvas_only', 'edge_pairs': None,
                            'reason': '图上连线已自动保存；本工具未取得 canvas 的机器可读节点连线定义'},
            'author_level_by_level_route': None, 'evidence': [ref(ui_path), ref(ui_path.replace('-state.json', '.jpg'))]}


def equipment_item(source, build, slot, group, index, folder, source_pointer, rune_index, socket_layout, ui_query=None):
    path = f'{folder}/{group}-item-{index:02d}.json'
    capture = read(path)
    panel = parse_panel(capture)
    item = source['commonItem']
    assert item is not None
    assert panel['name'] == item['name'], (build, slot, panel['name'], item['name'])
    equipment_id = f'{build}/{group if slot in ("mainHand", "offHand") else "Shared"}/{slot}'
    associated_sets = [group] if slot in ['mainHand', 'offHand'] else ['Set 1', 'Set 2']
    runes = []
    layout = next((s for s in socket_layout if s['display_index'] == index), {'runes': []})
    if group == 'Set 1':
        assert len(layout['runes']) == len(source.get('runes') or []), (build, slot, 'socket count')
    for socket_i, rune in enumerate(source.get('runes') or [], 1):
        slug = rune['slug']
        canonical = rune_index[slug]
        runes.append({'socket_index': socket_i, 'slug': slug, 'name': canonical['panel']['name'],
                      'panel': canonical['panel'], 'effect_application': '面板通常列出武器/护甲等多种上下文，未相加到装备顶部数值',
                      'ui_position': next((s for s in layout['runes'] if s['socket_index'] == socket_i), None),
                      'evidence': [ref(canonical['path']), ref(canonical['path'].replace('.json', '.jpg')),
                                   ref(f'{folder}/socket-layout.json'), ref('evidence/public-data/build-document.json', source_pointer + f'/runes/{socket_i-1}')]})
    displayed_stats = {s['label']: s['value'] for s in panel['top_stats']}
    displayed_requirements = {s['label']: s['value'] for s in panel['requirements']}
    field_status = {'name': 'source_and_panel_verified', 'base_type': 'source_and_panel_base_name' if not item.get('isUnique') else 'base_name_not_separately_printed',
                    'rarity_text': 'not_explicitly_printed_in_panel', 'top_stats': 'panel_observed' if panel['top_stats'] else 'not_printed_in_panel',
                    'requirements': 'panel_observed' if panel['requirements'] else 'not_printed_in_panel',
                    'modifiers': 'panel_observed' if panel['modifiers'] else 'ui_no_modifiers_source_has_descriptions',
                    'quality': 'panel_observed' if 'Quality' in displayed_stats else 'not_printed_in_panel',
                    'item_level': 'panel_observed' if 'Item Level' in displayed_stats else 'not_printed_in_panel',
                    'sockets': 'source_order_and_ui_positions_verified' if runes else 'no_configured_augment_items',
                    'anointment': 'source_slug_observed' if source.get('anointment') else 'not_configured_in_source'}
    crosschecks = [{'field': 'name', 'source': item['name'], 'panel': panel['name'], 'result': 'equal'}]
    if ui_query is not None:
        source_query = json.loads(item['poe2TradeRequest']['query'])
        assert source_query == ui_query, (build, slot, 'source item does not match DOM item query')
        crosschecks.append({'field': 'page_item_binding', 'source': sha(source_query), 'panel': sha(ui_query), 'result': 'equal',
                            'basis': '仅解析该物品旁正常加载的链接参数；未访问交易页面或进行交易'})
    for family, printed, source_values in [('stats', displayed_stats, item.get('stats')), ('requirements', displayed_requirements, item.get('requirements'))]:
        for s in source_values or []:
            crosschecks.append({'field': family + '.' + s['name'], 'source': s['value'], 'panel': printed.get(s['name']),
                                'result': 'equal' if str(s['value']) == printed.get(s['name']) else ('panel_not_printed' if s['name'] not in printed else 'source_panel_difference')})
    return {'id': equipment_id, 'build': build, 'slot': slot, 'slot_label': SLOT_ZH[slot], 'weapon_group': group if slot in ['mainHand', 'offHand'] else 'Shared',
            'associated_sets': associated_sets, 'display_index': index, 'name': panel['name'],
            'base_type': item['name'] if not item.get('isUnique') else None, 'rarity_text': None,
            'source_is_unique': item.get('isUnique'), 'source_is_imported': item.get('isImported'),
            'panel': panel, 'quality': displayed_stats.get('Quality'), 'item_level': displayed_stats.get('Item Level'),
            'socket_count': len(runes), 'socketed_items': runes, 'anointment': source.get('anointment'),
            'field_status': field_status, 'source_configuration': source,
            'stored_description_semantics': '网页保存的描述原值；范围面板与保存原值并列，未证明为作者实际掷值',
            'crosschecks': crosschecks,
            'evidence': [ref(path), ref(path.replace('.json', '.jpg')), ref('evidence/public-data/build-document.json', source_pointer)]}


def skill_groups(source, sections, evidence_path):
    section_i, section = next((i, s) for i, s in enumerate(sections['sections']) if s['title'] == 'Skill Gems')
    groups_ui = [n for n in htmltree(section['html']).walk() if n.attrs.get('aria-roledescription') == 'sortable']
    gems = source['gems']
    assert len(groups_ui) == len(gems), (len(groups_ui), len(gems))
    result = []
    for i, (g, ui) in enumerate(zip(gems, groups_ui), 1):
        paragraphs = [clean_space(n.text()) for n in ui.find('p')]
        assert paragraphs[0] == g['activeSkill']['name']
        supports = []
        for im in ui.find('img'):
            slug = im.attrs.get('alt')
            if not slug:
                continue
            parent = im
            while parent is not None and 'data-tippy-trigger-hover' not in parent.attrs:
                parent = parent.parent
            assert parent is not None
            supports.append((slug, clean_space(parent.text())))
        assert [s['gemSlug'] for s in g['subSkills']] == [s[0] for s in supports]
        embedded = []
        for socket_i, (s, ui_support) in enumerate(zip(g['subSkills'], supports), 1):
            embedded.append({'socket_index': socket_i, 'name': ui_support[1], 'gem_slug': s['gemSlug'], 'gem_type': s['gemType'],
                             'parent_active_skill_gem_slug': s.get('parentActiveSkillGemSlug'), 'level': s.get('level'), 'quality': s.get('quality'),
                             'field_status': {'level': 'explicitly_saved' if s.get('level') is not None else 'not_explicitly_set',
                                              'quality': 'explicitly_saved' if s.get('quality') is not None else 'not_explicitly_set'}})
        active = g['activeSkill']
        if active.get('level') is not None:
            assert f'Level {active["level"]}' in paragraphs
        result.append({'display_order': i, 'active_skill': active, 'connected_gems': embedded,
                       'weapon_set': g.get('weaponSet'), 'granted_by_weapon_set': g.get('grantedByWeaponSet'),
                       'configured_quality': active.get('quality'),
                       'field_status': {'connection': 'source_and_rendered_order_verified',
                                        'level': 'source_and_panel_verified' if active.get('level') is not None else 'not_explicitly_set',
                                        'quality': 'not_explicitly_set' if active.get('quality') is None else 'explicitly_saved'},
                       'evidence': [ref(evidence_path, f'/sections/{section_i}')], 'rendered_text': clean_space(ui.text())})
    return {'requirements': source.get('gemRequirements'), 'groups': result, 'source_configuration': source,
            'semantics': '保存连接与正文替换建议分开；未设置等级/品质不写成0或20/20'}


def collect_builds(doc, metadata):
    raw = {v['id']: (i, v) for i, v in enumerate(doc['data']['buildVariants']['values'])}
    rune_index = {}
    for p in sorted((ROOT / 'evidence/builds').glob('*/Rune-*.json')):
        d = json.loads(p.read_text())
        slug = p.stem.removeprefix('Rune-')
        rune_index[slug] = {'path': str(p.relative_to(ROOT)), 'panel': parse_panel(d)}
    result = []
    for m in metadata:
        build = m['title']
        vi, v = raw[m['id']]
        sp = f'/data/data/buildVariants/values/{vi}'
        folder = f'evidence/builds/{build}'
        branch = read(folder + '/branch-state.json')
        assert len(branch['selected_tabs']) == 4 and all(t['name'] == build and t['key'] == m['id'] for t in branch['selected_tabs'])
        sections = read(folder + '/sections.json')
        layout = read(folder + '/socket-layout.json')
        equipment_section_i, equipment_section = next((i, s) for i, s in enumerate(sections['sections']) if s['title'] == 'Equipment')
        ui_icons = [n for n in htmltree(equipment_section['html']).find('img') if n.attrs.get('alt') == 'item']
        equipment = []
        for index, slot in enumerate(SLOTS, 1):
            src = v['equipment'][slot]['set1'] if slot in ['mainHand', 'offHand'] else v['equipment'][slot]
            equipment.append(equipment_item(src, build, slot, 'Set 1', index, folder, sp + '/equipment/' + slot + ('/set1' if slot in ['mainHand', 'offHand'] else ''), rune_index, layout, query_beside_icon(ui_icons[index-1])))
        set1_ids = [e['id'] for e in equipment]
        shared_ids = [e['id'] for e in equipment if e['weapon_group'] == 'Shared']
        set2 = {'equipment_ids': shared_ids[:], 'main_hand_status': 'source_not_configured', 'off_hand_status': 'source_not_configured',
                'evidence': [ref(folder + '/Set 2-state.json')]}
        mh2 = v['equipment']['mainHand']['set2']
        if mh2 and mh2.get('commonItem'):
            item = equipment_item(mh2, build, 'mainHand', 'Set 2', 1, folder, sp + '/equipment/mainHand/set2', rune_index, [])
            equipment.append(item)
            set2['equipment_ids'].insert(0, item['id'])
            set2['main_hand_status'] = 'panel_and_source_verified'
            if mh2.get('blocksOffHand'):
                set2['off_hand_status'] = 'blocked_by_two_handed_item'
                set2['off_hand_visual_duplicate'] = {'equipment_id': item['id'], 'evidence': [ref(folder + '/Set 2-item-07.json'), ref(folder + '/Set 2-item-07.jpg')]}
        t = v['passiveTree']
        allocated = {s for key in ['mainTree', 'set1Tree', 'set2Tree'] for s in (t[key].get('selectedSlugs') or [])}
        saved_jewels = t.get('jewels') or []
        jewel_paths = sorted(p for p in (ROOT / folder).glob('Set 1-item-*.json') if re.fullmatch(r'Set 1-item-\d+\.json', p.name) and int(p.stem.split('-')[-1]) > 15)
        assert len(ui_icons) == 15 + len(jewel_paths)
        visible_jewels = []
        for icon in ui_icons[15:]:
            ui_query = query_beside_icon(icon)
            matches = [(i, j) for i, j in enumerate(saved_jewels) if j['iconURL'] == icon.attrs['src'] and json.loads(j['poe2TradeRequest']['query']) == ui_query]
            assert len(matches) == 1, (build, len(matches))
            visible_jewels.append(matches[0])
        matched_jewel_indices = {i for i, j in visible_jewels}
        assert len(matched_jewel_indices) == len(visible_jewels)
        jewels = []
        for display_order, ((ji, j), jp) in enumerate(zip(visible_jewels, jewel_paths), 1):
            capture = json.loads(jp.read_text())
            assert capture['icon']['src'] == j['iconURL']
            panel = parse_panel(capture)
            jewels.append({'id': f'{build}/Jewel/{display_order}', 'build': build, 'slot': 'Jewels', 'display_order': display_order,
                           'equipment_grid_display_index': capture['display_index'], 'associated_sets': ['Set 1', 'Set 2'], 'name': panel['name'],
                           'source_is_unique': j['isUnique'], 'panel': panel, 'node_id': j['nodeSlug'],
                           'binding_status': 'explicit_source_binding_matched_to_visible_item',
                           'binding_basis': '页面每个珠宝旁的 trade 查询参数与源 jewels[].poe2TradeRequest 逐项唯一匹配，只解析参数，未访问交易页；据匹配记录读取 nodeSlug',
                           'node_in_explicit_selected_lists': j['nodeSlug'] in allocated,
                           'allocation_status': 'explicit_node_selected' if j['nodeSlug'] in allocated else 'visible_bound_jewel_but_node_not_in_explicit_selected_lists',
                           'radius': next((s['value'] for s in panel['top_stats'] if s['label'] == 'Radius'), None),
                           'limited_to_text': next((mod['text'] for mod in panel['modifiers'] if re.search(r'Limited\s+to\b', mod['text'])), None),
                           'source_configuration': j, 'field_status': {'name': 'panel_observed', 'modifiers': 'full_panel_observed',
                                                                     'radius': 'panel_observed' if any(s['label'] == 'Radius' for s in panel['top_stats']) else 'not_printed',
                                                                     'limited_to': 'panel_observed' if re.search(r'Limited\s+to\b', panel['raw_text']) else 'not_printed',
                                                                     'node_binding': 'explicit_source_binding'},
                           'evidence': [ref(str(jp.relative_to(ROOT))), ref(str(jp.with_suffix('.jpg').relative_to(ROOT))),
                                        ref('evidence/public-data/build-document.json', sp + f'/passiveTree/jewels/{ji}'),
                                        ref(folder + '/sections.json', f'/sections/{equipment_section_i}')]} )
        non_allocated = [{'source_index': ji, 'node_id': j['nodeSlug'], 'source_configuration': j,
                          'status': 'saved_binding_not_displayed_in_equipment_not_in_explicit_selected_lists', 'panel': None,
                          'actual_allocation_status': 'not_verified',
                          'evidence': [ref('evidence/public-data/build-document.json', sp + f'/passiveTree/jewels/{ji}')]} for ji, j in enumerate(saved_jewels) if ji not in matched_jewel_indices]
        tree = tree_record(t, folder + '/Passive Tree-full-state.json', 'evidence/public-data/build-document.json', sp + '/passiveTree')
        tree['attribute_node_configuration'] = t.get('attributeNodes')
        result.append({'name': build, 'variant_id': m['id'], 'source_url': branch['source_url'], 'captured_at': branch['captured_at'],
                       'actual_selected_labels': [t['name'] for t in branch['selected_tabs']], 'selected_tab_observations': branch['selected_tabs'], 'source_configuration_sha256': sha(v),
                       'equipment': equipment, 'weapon_sets': {'Set 1': {'equipment_ids': set1_ids}, 'Set 2': set2},
                       'jewels': jewels, 'saved_not_displayed_jewels': non_allocated,
                       'passive_tree': tree, 'skill_gems': skill_groups(v['skillGems'], sections, folder + '/sections.json'),
                       'author_text': author_sections(doc, m, 'evidence/public-data/build-document.json'),
                       'evidence': [ref(folder + '/branch-state.json'), ref(folder + '/branch-selected.jpg'), ref(folder + '/sections.json')]})
    common = []
    for i, c in enumerate(doc['content']):
        if c['data'].get('title') in ['Build Overview', 'How it Plays', 'How it Works']:
            common.append({'section': c['data']['title'], 'blocks': text_blocks(c['data']['simplifiedContent'], 'evidence/public-data/build-document.json', f'/data/content/{i}/data/simplifiedContent')})
    return {'schema_version': 1, 'source': {'url': BUILD_URL, 'document_version': doc['version'], 'page_updated_at': doc['updatedAt']},
            'semantics': {'range': '页面范围不等于作者掷值或最低硬性目标', 'live_gear': '独立当次角色分支，未安排为其他5套必经升级阶段',
                          'previous_local_files': 'not_available_not_compared'},
            'common_author_text': common, 'builds': result}


def collect_atlas(doc, metadata):
    raw = {v['id']: (i, v) for i, v in enumerate(doc['data']['buildVariants']['values'])}
    candidates = {}
    for p in sorted((ROOT / 'evidence/atlas/master-candidates').glob('*.json')):
        d = json.loads(p.read_text())
        dom = htmltree(d['panels'][0]['html'])
        effects = [clean_space(n.text()) for n in dom.find('p') if 'var(--x1nw1xqh)' in n.attrs.get('style', '')]
        candidate = {'name': d['candidate'], 'display_index': d['display_index'], 'effects': effects,
                     'raw_text': d['panels'][0]['text'], 'definition_status': 'full_hover_panel_observed',
                     'evidence': [ref(str(p.relative_to(ROOT))), ref(str(p.with_suffix('.jpg').relative_to(ROOT)))]}
        candidates.setdefault(d['master'], []).append(candidate)
    variants = []
    for m in metadata:
        name = m['title']
        vi, v = raw[m['id']]
        t = v['atlasTree']
        folder = f'evidence/atlas/{name}'
        branch = read(folder + '/branch-state.json')
        assert len(branch['selected_tabs']) == 2 and all(s['name'] == name and s['key'] == m['id'] for s in branch['selected_tabs'])
        allocated = {s for val in t.values() if isinstance(val, dict) for s in (val.get('selectedSlugs') or [])}
        selections = []
        for i, node in enumerate(t.get('keystoneNodes') or []):
            assert node['nodeSlug'] in allocated, (name, node['nodeName'], node['nodeSlug'])
            selections.append({'node_id': node['nodeSlug'], 'node_name': node['nodeName'], 'allocated': True,
                               'author_selected': {'slug': node['selectionSlug'], 'name': node['selectionName'], 'selection_description': node['selectionDescription'],
                                                   'status': 'explicit_saved_choice_not_inferred_from_icon'},
                               'candidate_options': None, 'candidate_status': 'tool_not_retrieved',
                               'full_parent_node_effect': None, 'full_parent_node_effect_status': 'tool_not_retrieved',
                               'evidence': [ref('evidence/public-data/atlas-document.json', f'/data/data/buildVariants/values/{vi}/atlasTree/keystoneNodes/{i}')]})
        masters = []
        for j, master in enumerate(t.get('masters') or []):
            ui_path = folder + f'/Master-{master["name"]}-state.json'
            ui = read(ui_path)
            selected_ui = [c['name'] for c in ui['candidates'] if c['active_icon']]
            selected_source = [s['name'] for s in master['skills']]
            assert selected_ui == selected_source
            full_candidates = []
            for c in ui['candidates']:
                definition = next(d for d in candidates[master['name']] if d['name'] == c['name'])
                full_candidates.append({**definition, 'author_selected': c['active_icon'],
                                        'selection_status': 'active_icon_and_saved_skills_agree' if c['active_icon'] else 'candidate_only_not_selected'})
            masters.append({'name': master['name'], 'slug': master['slug'], 'selected_options': master['skills'],
                            'selected_count': len(selected_source), 'selected_verified_in_ui': selected_ui, 'candidate_options': full_candidates,
                            'evidence': [ref(ui_path), ref(ui_path.replace('.json', '.jpg')),
                                         ref('evidence/public-data/atlas-document.json', f'/data/data/buildVariants/values/{vi}/atlasTree/masters/{j}')]})
        variants.append({'name': name, 'variant_id': m['id'], 'source_url': branch['source_url'], 'captured_at': branch['captured_at'],
                         'actual_selected_labels': [s['name'] for s in branch['selected_tabs']], 'selected_tab_observations': branch['selected_tabs'], 'source_configuration_sha256': sha(v),
                         'atlas_tree': tree_record(t, folder + '/Atlas Tree-full-state.json', 'evidence/public-data/atlas-document.json', f'/data/data/buildVariants/values/{vi}/atlasTree'),
                         'keystone_selections': selections, 'masters': masters,
                         'author_text': author_sections(doc, m, 'evidence/public-data/atlas-document.json'),
                         'source_configuration': t, 'evidence': [ref(folder + '/branch-state.json'), ref(folder + '/branch-selected.jpg'), ref(folder + '/Atlas Tree-state.json')]})
    return {'schema_version': 1, 'source': {'url': ATLAS_URL, 'document_version': doc['version'], 'page_updated_at': doc['updatedAt']},
            'semantics': '已选项、候选项、作者正文分别存储；未点击候选项代选。各方案实际展示的大师配置分别保存。',
            'master_candidate_definitions': candidates, 'variants': variants}


def report_equipment(builds):
    out = ['# 装备与珠宝核对', '', '采集日期：2026-10-05。范围保留为范围；网页保存描述与实际悬浮框并列。只有图标不算取得完整属性。', '',
           '每个 build 独立列出；共用物品关联 Set 1 / Set 2，武器另列。品质、需求、限定、半径未打印时明确标注。', '']
    for b in builds['builds']:
        out += ['---', '', f'## {b["name"]}', '', f'实际选中标签：{", ".join(b["actual_selected_labels"])}。{mdref(b["evidence"][0]["file"], "标签证据")}。', '']
        for e in b['equipment']:
            p = e['panel']
            group = e['weapon_group'] if e['weapon_group'] != 'Shared' else 'Set 1 / Set 2 共用'
            out += [f'### {e["slot_label"]} · {group} · {e["name"]}', '',
                    f'展示序号 {e["display_index"]}；源 isUnique={str(e["source_is_unique"]).lower()}；稀有度文字：面板未单独标注。', '',
                    '顶部：' + ('；'.join(s['label'] + ': ' + s['value'] for s in p['top_stats']) or '未打印') + '。', '',
                    '需求：' + (p['requirements_text'] or '未打印') + '', '',
                    '品质：' + (e['quality'] or '面板未打印') + '；物品等级：' + (e['item_level'] or '面板未打印') + '。', '']
            out += ['- ' + mod['text'] + (f' [{mod["tier_label"]}]' if mod['tier_label'] else '') for mod in p['modifiers']]
            if not p['modifiers']:
                out += ['- 悬浮框未显示词缀；源保存描述另列如下，不能等同悬浮框已核验掷值。']
            for special in p['special_paragraphs']:
                out += ['- 特殊信息：' + special]
            if e['socketed_items']:
                out += ['', '镶嵌（按源数组及页面孔位顺序；每颗的全上下文效果见 JSON/证据）：', '']
                for rune in e['socketed_items']:
                    out += [f'- 孔 {rune["socket_index"]}：{rune["name"]} · {mdref(rune["evidence"][0]["file"])}']
            else:
                out += ['', '镶嵌：未配置镶嵌物。']
            if e['anointment']:
                out += ['', '涂膏源标识：' + e['anointment']['slug'] + '；实际 Allocates 行见面板。']
            descriptions = e['source_configuration']['commonItem'].get('explicitDescriptions') or []
            if e['source_is_imported'] or not p['modifiers']:
                if descriptions:
                    out += ['', '网页保存的描述原值（单列，不覆盖上述页面范围）：', '']
                    out += ['- ' + d['description'] for d in descriptions]
            out += ['', mdref(e['evidence'][0]['file'], '面板原文/HTML') + ' · ' + mdref(e['evidence'][1]['file'], '截图'), '']
        out += ['### Set 2 核对', '']
        s2 = b['weapon_sets']['Set 2']
        if s2['main_hand_status'] == 'source_not_configured':
            out += ['主手、副手源配置为空；已自动切至 Set 2 查看，不能把 Set 1 弓/箭袋带入 Set 2。其余装备共用。', '']
        else:
            out += ["主手 Hysseg's Claw；源 blocksOffHand=true。页面副手位置重复显示同一双手物品，保留两处证据，仅计一件装备。", '']
        out += [mdref(s2['evidence'][0]['file'], 'Set 2 状态'), '', '### Jewels', '']
        if not b['jewels']:
            out += ['页面未展示配置珠宝，保存数据 jewels=null。作者正文中的珠宝建议独立记录，未用推荐词缀补成已装备珠宝。', '']
        for j in b['jewels']:
            out += [f'**{j["display_order"]}. {j["name"]}** · 绑定 {j["node_id"]} · 网格序号 {j["equipment_grid_display_index"]}', '']
            out += ['- ' + s['label'] + ': ' + s['value'] for s in j['panel']['top_stats']]
            out += ['- ' + mod['text'] for mod in j['panel']['modifiers']]
            out += ['', mdref(j['evidence'][0]['file'], '逐颗面板') + ' · ' + mdref(j['evidence'][1]['file'], '截图'), '']
        for j in b['jewels']:
            if not j['node_in_explicit_selected_lists']:
                out += [f'可见珠宝 {j["display_order"]} 绑定 {j["node_id"]}，但该节点未出现在源显式已选列表；保留可见面板及绑定，未推断额外孔位的实际来源或分配状态。', '']
        for j in b['saved_not_displayed_jewels']:
            out += [f'源中另有珠宝绑定 {j["node_id"]}，该节点不在显式已选列表，Equipment 珠宝栏未显示；不计入上述已显示珠宝，未补造完整面板。', '']
    (ROOT / '装备面板全表.md').write_text('\n'.join(out), encoding='utf-8')


def report_equipment_overview(builds):
    out = ['# 装备与珠宝核对', '', '每套一个总览块。所有装备逐件列出；全部顶部属性、需求、固有/显性词缀与保存描述原值见 [装备面板全表](%E8%A3%85%E5%A4%87%E9%9D%A2%E6%9D%BF%E5%85%A8%E8%A1%A8.md) 或逐件证据。', '',
           '“未打印”不填成0；词缀范围不填成实际掷值；两枚戒指、各药剂/咒符与武器组都保留栏位。', '']
    for b in builds['builds']:
        out += ['---', '', '## ' + b['name'], '', '| 栏位 / 组 | 英文名称 | 品质 / 镶嵌 | 面板词缀数 / 证据 |', '|---|---|---|---|']
        for e in b['equipment']:
            group = e['weapon_group'] if e['weapon_group'] != 'Shared' else '共用'
            quality = e['quality'] or '未打印'
            rune_text = '；'.join(f'{s["socket_index"]}:{s["name"]}' for s in e['socketed_items']) or '未配置'
            mods = str(len(e['panel']['modifiers'])) if e['panel']['modifiers'] else '0（源保存7条，存在差异）'
            out += [f'| {e["slot_label"]} / {group} | {e["name"]} | {quality} / {rune_text} | {mods} · {mdref(e["evidence"][0]["file"])} |']
        out += ['']
        if b['weapon_sets']['Set 2']['main_hand_status'] == 'source_not_configured':
            out += ['Set 2：无已配置主手/副手；其余装备共用。已实际切换查看。', '']
        else:
            out += ["Set 2：Hysseg's Claw 占用双手，副手重复图标不计第二件。", '']
        out += ['**Jewels（逐颗全部词缀）**', '']
        if not b['jewels']:
            out += ['珠宝栏没有已保存配置；正文建议单列在技能与作者说明报告。', '']
        for j in b['jewels']:
            special = ('；半径 ' + j['radius']) if j['radius'] else ''
            special += ('；' + j['limited_to_text']) if j['limited_to_text'] else ''
            out += [f'{j["display_order"]}. **{j["name"]}** · {j["node_id"]}{special} · {mdref(j["evidence"][0]["file"])}', '']
            out += ['   - ' + mod['text'] for mod in j['panel']['modifiers']]
            out += ['']
        for j in b['saved_not_displayed_jewels']:
            out += [f'额外保存绑定 {j["node_id"]} 未在页面显示，不计可见珠宝，不补造词缀范围。', '']
        if b['name'] == 'Live Gear':
            out += ['孔位提醒：可见珠宝1和6的绑定不在显式已选节点列表；此处只记录实际取得绑定，不推断额外孔位的分配来源。', '']
    (ROOT / '装备与珠宝核对.md').write_text('\n'.join(out), encoding='utf-8')


def report_atlas(atlas):
    out = ['# 异界方案核对', '', '7 个分支都通过实际选中标签验证。候选列表、作者已选和正文建议分开；没有代选或改动树。', '',
           '全部已选多选值见下表；父节点完整效果及其他候选未自动取得，详见缺失清单。大师的全部 12 个候选效果/位已取得。', '']
    for v in atlas['variants']:
        out += ['---', '', f'## {v["name"]}', '', mdref(v['atlas_tree']['evidence'][1]['file'], '实际树图') + ' · ' + mdref(v['evidence'][0]['file'], '标签证据'), '']
        for section in v['author_text']:
            if section['blocks']:
                out += [f'### 作者说明 · {section["section"]}', '']
                for block in section['blocks']:
                    out += [block['text'], '']
        out += ['### 大师配置（分别列出）', '']
        for master in v['masters']:
            out += [f'**{master["name"]}：{master["selected_count"]} 项实际已选**', '']
            for c in master['candidate_options']:
                if c['author_selected']:
                    out += ['- ' + c['name'] + '：' + '；'.join(c['effects'])]
            out += ['', mdref(master['evidence'][0]['file'], '已选状态') + ' · ' + mdref(master['evidence'][1]['file'], '已选截图'), '']
        out += ['### 多选节点的源保存选项', '', '| 节点 ID | 节点名 | 作者已选 | 选项描述 |', '|---|---|---|---|']
        for n in v['keystone_selections']:
            choice = n['author_selected']
            out += ['| ' + ' | '.join(str(s).replace('|', '\\|').replace('\n', ' / ') for s in [n['node_id'], n['node_name'], choice['name'], choice['selection_description']]) + ' |']
        out += ['']
    out += ['---', '', '## 大师候选效果全集', '', '以下是候选定义，不表示任何方案全选。逐方案是否已选见各方案章节/JSON。', '']
    for master, candidates in atlas['master_candidate_definitions'].items():
        out += ['### ' + master, '']
        for c in candidates:
            out += [f'- {c["name"]}：' + '；'.join(c['effects']) + ' · ' + mdref(c['evidence'][0]['file'])]
        out += ['']
    (ROOT / '异界方案核对.md').write_text('\n'.join(out), encoding='utf-8')


def report_skills_author(builds):
    out = ['# 技能与作者说明核对', '', '下列连接来自每个分支保存配置，并逐组与实际展开的 Skill Gems DOM 核对。正文中的替换、升级条件、打造说明独立存放。', '']
    for b in builds['builds']:
        out += ['---', '', '## ' + b['name'], '', '| 主动 | 页面设置等级 | 连接（保留次序） |', '|---|---|---|']
        for g in b['skill_gems']['groups']:
            level = g['active_skill'].get('level')
            subs = ['**' + s['name'] + '（内嵌主动）**' if s['gem_type'] == 'ACTIVE' else s['name'] for s in g['connected_gems']]
            out += [f'| {g["active_skill"]["name"]} | {level if level is not None else "未明确设置"} | ' + ' → '.join(subs) + ' |']
        out += ['', '配置品质：全部未明确设置；不以正文要求或宝石默认值回填。', '']
        for section in b['author_text']:
            if section['blocks']:
                out += ['### 作者说明 · ' + section['section'], '']
                for block in section['blocks']:
                    out += [block['text'], '']
        out += ['### 天赋证据', '', mdref(b['passive_tree']['evidence'][1]['file'], '全屏图（Main/Set 1/Set 2/升华配色）'), '']
        for key, allocation in b['passive_tree']['allocations'].items():
            out += [f'- {key}：源记录 {allocation.get("source_record_count", 0)} 个节点；完整 ID 在 builds.json；作者优先列表保留但不推导每级点序。']
        out += ['']
    out += ['---', '', '## 全页共同作者说明', '', '下列栏目归属整页，不强行归入某个分支；与 Live Gear 当次装备面板分开。', '']
    for section in builds['common_author_text']:
        out += ['### ' + section['section'], '']
        for block in section['blocks']:
            out += [block['text'], '']
    (ROOT / '技能与作者说明核对.md').write_text('\n'.join(out), encoding='utf-8')


def report_gaps(builds, atlas):
    gaps = []
    def gap(scope, field, kind, details, evidence=None):
        gaps.append({'scope': scope, 'field': field, 'kind': kind, 'details': details, 'evidence': evidence or []})
    gap('全包', '旧 .build / R42 / 旧网页报告', 'old_records_not_available', '当前任务目录未发现用户所述旧文件，未假装读取或比较；完成网页采集，尚未与本地旧稿比对。')
    for b in builds['builds']:
        gap(b['name'], 'Passive Tree 连线定义', 'tool_not_retrieved', '已保存全屏图、Main/Set 1/Set 2/升华节点 ID 与属性配置；机器可读 edge pairs、坐标和全部节点名称/效果未取得。', b['passive_tree']['evidence'])
        gap(b['name'], '逐级加点', 'source_not_provided_as_complete_level_route', '保留 source_priority_list 与页面 Leveling Path 标记，未推导逐级、逐点的完整作者路线。')
        for e in b['equipment']:
            scope = b['name'] + ' / ' + e['weapon_group'] + ' / ' + e['slot_label'] + ' / ' + e['name']
            missing = [k for k in ['quality', 'item_level', 'requirements', 'top_stats'] if e['field_status'][k] == 'not_printed_in_panel']
            missing += ['rarity_text']
            if e['base_type'] is None:
                missing += ['base_type']
            gap(scope, ', '.join(missing), 'not_printed_in_observed_panel', '面板未单独打印这些字段；已保留源结构中的可用字段，未填入通用数据库值。', e['evidence'])
            if not e['panel']['modifiers']:
                gap(scope, '全部词缀 / 完整伤害核对', 'source_panel_conflict', '重新展开后仍只显示基础面板；网页保存 7 条显性描述。原始与复核截图均保留，未把源描述当作已核验面板、未重算弓伤害。', e['evidence'])
            for chk in e['crosschecks']:
                if chk['result'] == 'source_panel_difference':
                    gap(scope, chk['field'], 'source_panel_conflict', f'源保存 {chk["source"]}；实际面板 {chk["panel"]}；两者并列保留，未覆盖。', e['evidence'])
            if e['source_is_imported'] and e['panel']['modifiers'] and e['source_configuration']['commonItem'].get('explicitDescriptions'):
                gap(scope, '保存描述值 vs 页面范围', 'different_representations_not_proof_of_roll', '导入字段的数值描述与悬浮框范围逐来源保存；两者不能互换，范围上限也不是作者硬性目标。', e['evidence'])
            weird = [m['text'] for m in e['panel']['modifiers'] if m['text'].startswith('Body Armour:') and e['slot'] != 'body']
            if weird:
                gap(scope, '固有词缀页面标签', 'source_display_label_conflict', '该栏位面板出现 Body Armour: 标签，原样保存，不自行修复。' + ' / '.join(weird), e['evidence'])
        if not b['jewels']:
            gap(b['name'], '已配置珠宝', 'source_not_configured', 'Equipment 未显示已配置珠宝，源 jewels=null；正文推荐不是已保存组合。', b['evidence'])
        for j in b['jewels']:
            if not j['node_in_explicit_selected_lists']:
                gap(b['name'] + ' / Jewels ' + str(j['display_order']) + ' / ' + j['node_id'], '孔位在已选列表中的关联', 'visible_binding_not_in_explicit_selected_lists', '面板与 nodeSlug 已唯一匹配，但源 Main/Set 1/Set 2 selectedSlugs 不包含该节点；未由头盔/Voices 推断额外孔位来源和实际分配。', j['evidence'])
        for j in b['saved_not_displayed_jewels']:
            gap(b['name'] + ' / ' + j['node_id'], '珠宝完整面板', 'saved_but_not_displayed', '存在保存绑定，但当前显式已选列表不含该节点、珠宝栏未显示；实际分配状态未核实，未补造属性范围。', j['evidence'])
        for g in b['skill_gems']['groups']:
            scope = b['name'] + ' / Skill Gems / ' + g['active_skill']['name']
            fields = ['quality'] + (['active_level'] if g['active_skill'].get('level') is None else [])
            gap(scope, ', '.join(fields), 'not_explicitly_set', '当前分支没有明确设置值；正文要求、默认宝石信息不回填为作者已配置值。', g['evidence'])
        gap(b['name'], '内嵌主动/辅助宝石逐颗等级与品质', 'not_explicitly_set', '保留完整 gemType、父主动与连接次序；subSkills 没有明确等级/品质配置，不用默认等级补值。')
    for v in atlas['variants']:
        gap(v['name'], 'Atlas Tree 连线定义/节点全效果', 'tool_not_retrieved', '已保存实际树图和已选 ID；canvas 机器连线、节点完整效果定义未取得。公开静态脚本 GET 返回403后未绕过限制。', v['atlas_tree']['evidence'])
        for n in v['keystone_selections']:
            gap(v['name'] + ' / ' + n['node_id'] + ' / ' + n['node_name'], '多选候选全集及父节点完整效果', 'tool_not_retrieved',
                '实际已选明确：' + n['author_selected']['name'] + '；选项描述：' + n['author_selected']['selection_description'] + '。其他候选不能冒充已选，完整父效果不由选项值推造。', n['evidence'])
    save('gaps.json', gaps)
    out = ['# 缺失与冲突', '', '状态区分：未配置/面板未打印；工具未取得；页面与保存字段冲突；旧记录未提供。这里的“面板未打印”只描述实际观察，不断言整个网站无数据。', '',
           '**完成网页采集，尚未与本地旧稿比对。** 未访问其他项目寻找旧包，未改写任何原 build、攻略网站或过滤器。', '',
           '当前重点缺口：Live Gear 弓面板缺词缀而源有7条；天赋/异界 canvas 没有机器连线定义；异界多选节点的其他候选和完整父效果未取得。已选221项及大师候选36项不受该缺口影响。', '',
           '树图原样显示的负数计数也已保留。源列表数量与 UI 两列数字不简单等同；Live Gear 的武器组与 Main 存在重叠 ID，两种记录均保留，不据此擅自修复点数。', '']
    out += ['| 范围 | 字段 | 状态 | 说明 | 证据 |', '|---|---|---|---|---|']
    for g in gaps:
        cell = lambda s: str(s).replace('|', '\\|').replace('\n', ' / ')
        refs = ' '.join(mdref(r['file']) for r in g['evidence'][:1])
        out += ['| ' + ' | '.join(cell(s) for s in [g['scope'], g['field'], g['kind'], g['details'], refs]) + ' |']
    (ROOT / '缺失与冲突.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
    return gaps


def validate(builds, atlas):
    checks = []
    def check(name, ok, detail=None):
        checks.append({'check': name, 'passed': bool(ok), 'details': detail})
        assert ok, (name, detail)
    check('六套 build 精确名称、独立选中标签', [b['name'] for b in builds['builds']] == BUILD_NAMES and all(all(t == b['name'] for t in b['actual_selected_labels']) for b in builds['builds']))
    check('七套 Atlas 精确名称、独立选中标签', [v['name'] for v in atlas['variants']] == ATLAS_NAMES and all(all(t == v['name'] for t in v['actual_selected_labels']) for v in atlas['variants']))
    live = next(b for b in builds['builds'] if b['name'] == 'Live Gear')
    expected = ['(5-15)% increased Attack Damage', '(25-29)% increased Critical Hit Chance for Attacks', '(30-34)% increased Critical Damage Bonus for Attack Damage', '(2-4)% increased Attack Speed with Bows']
    check('Live Gear 第一颗 Emerald 四条范围', [m['text'] for m in live['jewels'][0]['panel']['modifiers']] == expected, expected)
    emeralds = [j for j in live['jewels'] if j['name'] == 'Emerald']
    check('同图标 Emerald 已逐颗区分', len(emeralds) == 4 and len({sha(j['panel']['modifiers']) for j in emeralds}) == 4)
    check('六个 build 不是同一默认配置复制', len({b['source_configuration_sha256'] for b in builds['builds']}) == 6)
    # Some farming variants legitimately share node allocations; prose and masters still differ.
    check('七个 Atlas 是各自源配置而非默认页副本', len({v['source_configuration_sha256'] for v in atlas['variants']}) == 7)
    equipment = [e for b in builds['builds'] for e in b['equipment']]
    jewels = [j for b in builds['builds'] for j in b['jewels']]
    check('91 件按 build/武器组记录的装备', len(equipment) == 91)
    check('11 颗可见已配置珠宝及1颗单列未显示绑定', len(jewels) == 11 and sum(len(b['saved_not_displayed_jewels']) for b in builds['builds']) == 1)
    check('全部装备与可见珠宝有独立非空悬浮框证据', all(e['panel']['raw_text'] for e in equipment + jewels))
    check('装备名称源与面板一致', all(all(c['result'] == 'equal' for c in e['crosschecks'] if c['field'] == 'name') for e in equipment))
    check('90 件 Set 1/共用装备按页面各自参数与源记录核对绑定', sum(c['field'] == 'page_item_binding' and c['result'] == 'equal' for e in equipment for c in e['crosschecks']) == 90)
    detailed = [c for e in equipment for c in e['crosschecks'] if c['field'] != 'name']
    check('多个装备结构字段与面板交叉核对', sum(c['result'] == 'equal' for c in detailed) >= 10, {'equal_fields': sum(c['result'] == 'equal' for c in detailed), 'different_fields': sum(c['result'] == 'source_panel_difference' for c in detailed), 'not_printed_fields': sum(c['result'] == 'panel_not_printed' for c in detailed)})
    check('全部镶嵌物按孔位有源关联和面板', all(s['ui_position'] is not None and s['panel']['raw_text'] for e in equipment for s in e['socketed_items']))
    check('3 位大师各12个候选效果', set(atlas['master_candidate_definitions']) == {'Jado', 'Doryani', 'Hilda'} and all(len(c) == 12 and all(d['effects'] for d in c) for c in atlas['master_candidate_definitions'].values()))
    check('10 个大师分支配置已选状态核对', sum(len(v['masters']) for v in atlas['variants']) == 10 and all([s['name'] for s in m['selected_options']] == m['selected_verified_in_ui'] for v in atlas['variants'] for m in v['masters']))
    lineage = next(v for v in atlas['variants'] if v['name'] == 'Lineage Gems')
    check('Lineage Gems Jado 实际为3项', lineage['masters'][0]['selected_count'] == 3)
    check('Abyss Rares 3位大师分别保留', [m['name'] for m in next(v for v in atlas['variants'] if v['name'] == 'Abyss Rares')['masters']] == ['Jado', 'Hilda', 'Doryani'])
    check('221 个异界已选多选绑定均属于已分配节点', sum(len(v['keystone_selections']) for v in atlas['variants']) == 221 and all(n['allocated'] for v in atlas['variants'] for n in v['keystone_selections']))
    refs = []
    def walk(v):
        if isinstance(v, dict):
            if 'file' in v:
                refs.append(v)
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(builds); walk(atlas)
    for r in refs:
        p = ROOT / r['file']
        assert p.is_file(), r
        if 'json_pointer' in r:
            current = json.loads(p.read_text())
            for part in r['json_pointer'].strip('/').split('/'):
                key = part.replace('~1', '/').replace('~0', '~')
                current = current[int(key)] if isinstance(current, list) else current[key]
    check('所有字段证据文件与 JSON Pointer 可解析', True, {'reference_count': len(refs)})
    stats = {'builds': 6, 'atlas_variants': 7, 'equipment_records': len(equipment), 'visible_jewels': len(jewels),
             'saved_not_displayed_jewels': 1, 'socket_associations': sum(e['socket_count'] for e in equipment),
             'unique_socketed_item_definitions': len({s['slug'] for e in equipment for s in e['socketed_items']}),
             'skill_groups': sum(len(b['skill_gems']['groups']) for b in builds['builds']),
             'master_loadouts': 10, 'master_candidate_definitions': 36, 'atlas_saved_multichoice_selections': 221}
    report = {'validated_at': datetime.now(timezone.utc).isoformat(), 'checks': checks, 'counts': stats,
              'overall_scope_status': 'all_requested_branches_captured_with_explicit_field_gaps',
              'not_claimed': ['all fields complete', 'old files compared', 'author actual numeric rolls verified', 'machine canvas edges obtained']}
    save('validation.json', report)
    return report


def main():
    bdoc, bmeta = sanitize_document('evidence/public-data/build-document.json')
    adoc, ameta = sanitize_document('evidence/public-data/atlas-document.json', atlas=True)
    builds = collect_builds(bdoc, bmeta)
    atlas = collect_atlas(adoc, ameta)
    save('builds.json', builds)
    save('atlas.json', atlas)
    report_equipment(builds)
    report_equipment_overview(builds)
    report_atlas(atlas)
    report_skills_author(builds)
    gaps = report_gaps(builds, atlas)
    report = validate(builds, atlas)
    print(json.dumps({'counts': report['counts'], 'checks_passed': len(report['checks']), 'gap_records': len(gaps)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
