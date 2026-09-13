# 任务：重做「第一天开荒天赋树」+ 两次独立验证（PoE2 国服 0.5.5 锐眼冰射）

用户对我当前那份 D1 的反馈原话：**「不对的地方太多了」**。
所以这次不是让你复核，是**请你重做**，并且给出**两次独立验证**。

---

## 一、先明确这次和上次的关键区别

上次你给的 93 个节点 string id，和我原来的**完全一致**（集合相等，你自己也写了「本次新增0、删除0」）。
所以上次那份回答没有产生任何改变。**这次请你不要做"复核确认"，要么给出真正修改过的节点表，要么给出"具体哪几个点是错的"的清单。**

**允许你说「我无法确定」** —— 但必须说清卡在哪里。不允许为了交差再确认一遍。

## 二、这一页能看到的东西（附件在下文附录 A）

- 当前两份文件的**全部节点表**（含 string id、数值 ID、节点名、属性、是否大点）：
  `GPT-Task-D1-Fix-素材.md`
- 站点（含他文档里的 5 张天赋树截图）：https://harryghost.github.io/poe2-guide/
- 下载：`POE2-Author-Tree-D1.build`、`POE2-Author-Tree-D2.build`（同站根目录）

---

## 三、请交四样东西

### ① 重做后的第一天节点表（string id 全表）

要求：
- 目标：70 级 / **93 个普通天赋点**（公式 (70−1)+24；升华另计、不写进 `passives`）
- 每个 `string id` 一行，我整棵替换
- **必须只有一份**，不要再给「增删差集」

### ② 第一次验证：结构/数据层（可机器复算）

逐项给出结论，格式就用「通过 / 不通过 + 数字」：

| 检查项 | 要求 |
|---|---|
| ID 合法性 | 每个 string id 都存在于 `src/TreeData/0_5/tree.json` |
| 连通性 | **只用已选节点 + 免费职业起点（数值ID 50459，stringId `ranger596`）** 就能从起点到达全部 93 个节点；说明用的是什么方法 |
| 点数 | 93 个付费普通节点，不含升华/涂油/免费起点 |
| 无第二天装备 | 不含 `criticals*`、`daze*`、`shock*`、`passive_keystone_resonance`、涂油 |
| 技能可用性 | 93 点里，覆盖第一天要用的技能所需方向：冰霜射击（冰冷穿透/冰冻积累）、狙击、冰冻印记、冻结齐射、弹幕（狂怒球来源，所以**不能有共鸣**） |

### ③ 第二次验证：交叉证据层（必须换一种方法）

**不允许重复第②次的口径。** 从下面任选，并说明你选哪个、为什么：

- **A. 与作者第二天的树对照**：逐个说明「D2 里有、D1 没要」的每个节点，是**因为第二天才点**（并给出依据：是暴击/眩晕/感电类，还是需要第二天才有的装备/技能），还是**第一天就该点但我漏了**
- **B. 与第一天技能做联动核对**：对 D1 里每一个大点，写清它服务于哪个第一天的技能/机制（不能只写"冰系可用"这种笼统理由）
- **C. 与作者文档里的 5 张天赋树截图对照**（网站上有原图）：
  ⚠️ 警告：我实测过这条路**很难** —— 截图 1500px 宽，我检出的「已点节点」大半是背景噪点；
  用你的真实导出树去拟合，最多也只覆盖 5/10 个亮点。
  **如果你能用视觉从图里认出 3~5 个大点**（比如能看清的大圈），请把它们列出来，并说明和你的节点表是否一致。
  **认不出就直说认不出**，不要编。

### ④ 你判定「哪些点不对」的依据清单

用户说「不对的地方太多了」。请你**明确指出**：
- 我当前那 93 个节点里，你认为是错的**具体是哪几个**（给 string id）
- 每个的错误原因是什么（例如：属于第二天才点的、对第一天没用、机制冲突、纯属路径冗余）
- 如果换掉了它们，**补进来的是哪几个**

**如果你认为没有具体错误**，就直接说「没有找到具体错误点」——
那样我会按「无法验证、按参考配置发布」处理，不会再改。

---

## 四、可用的权威数据源

1. **PoB2 天赋树**：`https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2`
   - `src/TreeData/0_5/tree.json`：`stringId` / `connections` / `orbit` / `orbitIndex` / `group` / `isNotable` / `stats`
   - ⚠️ `groups[].x/y` 是**组中心**，不是节点位置。真实坐标：
     ```
     节点坐标 = 组中心 + 轨道半径 × (sinθ, cosθ)
     θ = constants.orbitAnglesByOrbit[orbit][orbitIndex]
     orbitRadii = [0, 82, 162, 335, 493, 662, 846, 251, 1080, 1322]
     ```
2. **宝石数据**：同仓库 `src/Data/Gems.lua`（967 条，含 `gameId`）
3. **`.build` 规范**：`https://www.pathofexile.com/developer/docs/game`
4. **真实 `.build` 样本**：`https://github.com/chesler410/poe2-build-forge/tree/main/fixtures`
5. **中文资料站**：`https://poe2db.tw/cn/`

## 五、我这边已有的结论（你可以质疑）

- 作者 D2 是 93 级角色，导出 140 个普通节点 → 按 (93−1)+24 = 116 点，**多 24 点**，
  你上次的解释是「两套武器天赋的并集（92 共同 + 24 + 24）」，我采纳但**没有武器组归属数据**
- 我已按你的结论把涂油节点移出 D2 的 `passives`（151 → 150 条）
- 我已把 D1 的 `skills` 段换成第一天配置（战斗狂怒 / 冰冻印记 / 冻结齐射 / 狙击 / 弹幕 / 冰霜射击 /
  龙卷射击 / 逃脱射击 / 寒冰之捷 / 战旗 / 风舞者 / 幻影射手）

## 六、输出格式

```
① 重做后的第一天节点表（string id，一行一个，共 ___ 个）

② 第一次验证（结构层）：逐项通过/不通过 + 数字

③ 第二次验证（交叉证据层）：选 A/B/C，写明方法与结果

④ 我认为原 93 点里错的具体节点：
   - id：原因 →
   如果认为没错：直接写「没有找到具体错误点」

⑤ 仍无法确定的部分
```

我这边有完整的树数据（4903 节点）、宝石数据（967 条）和可复现脚本。
你给 string id，我就能生成 `.build`、跑一次独立校验（连通性/点数/ID合法性）并部署。

---

# 附录 A：当前两份 .build 的全部节点

# 素材：当前两份 .build 的全部节点（含属性，供你核对）

## 一、D1（当前 93 点；用户反馈「不对的地方太多了」）

### POE2-Author-Tree-D1.build（93 个节点）

| # | string id | 数值ID | 节点名 | 属性 | 大点 |
|---|---|---|---|---|---|
| 1 | `projectiles15` | 56651 | Projectile Damage | 10% increased Projectile Damage |  |
| 2 | `dexterity17` | 38143 | Attribute | +5 to any Attribute |  |
| 3 | `dexterity16` | 43746 | Attribute | +5 to any Attribute |  |
| 4 | `dexterity15` | 16460 | Attribute | +5 to any Attribute |  |
| 5 | `ranger_huntress_notable2` | 28992 | Honed Instincts | 8% increased Projectile Speed / 8% increased Attack Speed / +10 to Dexterity | ★ |
| 6 | `dexterity18` | 6772 | Attribute | +5 to any Attribute |  |
| 7 | `dexterity19` | 60505 | Attribute | +5 to any Attribute |  |
| 8 | `dexterity20` | 28050 | Attribute | +5 to any Attribute |  |
| 9 | `attributes29` | 63888 | Attribute | +5 to any Attribute |  |
| 10 | `dexterity34` | 35901 | Attribute | +5 to any Attribute |  |
| 11 | `attack35` | 26068 | Attack Damage | 10% increased Attack Damage |  |
| 12 | `attack36` | 37389 | Attack Damage | 10% increased Attack Damage |  |
| 13 | `jewel_slot1960` | 60735 | Jewel Socket |  |  |
| 14 | `elemental28` | 41096 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 15 | `elemental27` | 144 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 16 | `elemental32` | 12611 | Harness the Elements | 20% increased Damage for each type of Elemental Ailment on Enemy | ★ |
| 17 | `dexterity12_` | 11825 | Attribute | +5 to any Attribute |  |
| 18 | `elemental26` | 61246 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 19 | `dexterity85_` | 26432 | Attribute | +5 to any Attribute |  |
| 20 | `elemental25` | 25700 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 21 | `elemental54` | 28061 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 22 | `cold_penetration6` | 28086 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 23 | `cold_penetration1` | 57088 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 24 | `elemental55` | 35878 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 25 | `elemental_attacks6` | 42794 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 26 | `dexterity57` | 12890 | Attribute | +5 to any Attribute |  |
| 27 | `elemental18` | 32155 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 28 | `dexterity54` | 54984 | Attribute | +5 to any Attribute |  |
| 29 | `elemental16` | 64213 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 30 | `elemental56` | 50884 | Primal Sundering | Damage Penetrates 12% Elemental Resistances / 8% increased Area of Effect for Attacks | ★ |
| 31 | `elemental_attacks8` | 31433 | Catalysis | 20% increased Elemental Damage with Attacks / 5% of Physical Damage from Hits taken as Dam | ★ |
| 32 | `cold_penetration7` | 54557 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 33 | `dexterity58` | 2408 | Attribute | +5 to any Attribute |  |
| 34 | `attributes74` | 42118 | Attribute | +5 to any Attribute |  |
| 35 | `dexterity55` | 34015 | Attribute | +5 to any Attribute |  |
| 36 | `attack6` | 36576 | Attack Damage | 10% increased Attack Damage |  |
| 37 | `dexterity102` | 58397 | Proficiency | +25 to Dexterity | ★ |
| 38 | `cold_penetration24` | 9421 | Snowpiercer | Damage Penetrates 15% Cold Resistance / +10 to Intelligence | ★ |
| 39 | `jewel_slot1961` | 61834 | Jewel Socket |  |  |
| 40 | `marks32` | 35534 | Mark Use Speed | Mark Skills have 10% increased Use Speed |  |
| 41 | `dexterity82_` | 24287 | Attribute | +5 to any Attribute |  |
| 42 | `attack2` | 25055 | Attack Damage and Movement Speed | 2% increased Movement Speed / 8% increased Attack Damage |  |
| 43 | `dexterity52` | 48116 | Attribute | +5 to any Attribute |  |
| 44 | `jewel_slot1976` | 32763 | Jewel Socket |  |  |
| 45 | `attack5` | 41580 | Maiming Strike | 25% increased Attack Damage / Attacks have 25% chance to Maim on Hit | ★ |
| 46 | `dexterity51` | 2582 | Attribute | +5 to any Attribute |  |
| 47 | `intelligence25` | 51741 | Attribute | +5 to any Attribute |  |
| 48 | `dexterity110` | 2334 | Dexterity | +8 to Dexterity |  |
| 49 | `marks29` | 21279 | Mark Effect and Blind Effect | 8% increased Effect of your Mark Skills / 10% increased Blind Effect |  |
| 50 | `intelligence66` | 16705 | Attribute | +5 to any Attribute |  |
| 51 | `dexterity50` | 48773 | Attribute | +5 to any Attribute |  |
| 52 | `movement_speed5` | 5305 | Skill Speed | 3% increased Skill Speed |  |
| 53 | `dexterity48` | 14267 | Attribute | +5 to any Attribute |  |
| 54 | `dexterity81` | 24786 | Attribute | +5 to any Attribute |  |
| 55 | `marks28` | 23305 | Mark Use Speed | Mark Skills have 10% increased Use Speed |  |
| 56 | `heralds12_` | 56847 | Herald Damage | 12% increased Damage while affected by a Herald |  |
| 57 | `attributes10` | 27705 | Attribute | +5 to any Attribute |  |
| 58 | `bow19` | 52800 | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |  |
| 59 | `attributes11` | 30808 | Attribute | +5 to any Attribute |  |
| 60 | `movement_speed4` | 3431 | Skill Speed | 3% increased Skill Speed |  |
| 61 | `evasion26` | 3209 | Evasion | 15% increased Evasion Rating |  |
| 62 | `attributes9` | 30657 | Attribute | +5 to any Attribute |  |
| 63 | `dexterity9` | 57821 | Attribute | +5 to any Attribute |  |
| 64 | `evasion24_` | 44776 | Evasion | 15% increased Evasion Rating |  |
| 65 | `evasion33` | 59720 | Beastial Skin | 100% increased Evasion Rating from Equipped Body Armour | ★ |
| 66 | `movement_speed9` | 43082 | Acceleration | 3% increased Movement Speed / 10% increased Skill Speed | ★ |
| 67 | `marks27` | 51602 | Unsight | Enemies near Enemies you Mark are Blinded / Enemies you Mark cannot deal Critical Hits | ★ |
| 68 | `bow20` | 57615 | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |  |
| 69 | `dexterity7` | 31765 | Attribute | +5 to any Attribute |  |
| 70 | `evasion21` | 1841 | Evasion | 15% increased Evasion Rating |  |
| 71 | `dexterity47` | 15775 | Attribute | +5 to any Attribute |  |
| 72 | `heralds10` | 28835 | Herald Damage | 12% increased Damage while affected by a Herald |  |
| 73 | `evasion_and_energy_shield5` | 26034 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 74 | `marks16` | 59064 | Mark Effect | 10% increased Effect of your Mark Skills |  |
| 75 | `heralds16_` | 28044 | Coming Calamity | 40% increased Cold Damage while affected by Herald of Ice / 40% increased Fire Damage whil | ★ |
| 76 | `evasion_and_energy_shield8` | 42805 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 77 | `bow21` | 32319 | Surpassing Arrow Chance | +10% Surpassing chance to fire an additional Arrow |  |
| 78 | `marks5_` | 28258 | Mark Effect | 10% increased Effect of your Mark Skills |  |
| 79 | `intelligence67` | 59538 | Attribute | +5 to any Attribute |  |
| 80 | `evasion28` | 9405 | Evasion | 15% increased Evasion Rating |  |
| 81 | `dexterity46` | 722 | Attribute | +5 to any Attribute |  |
| 82 | `bow23` | 33542 | Quick Fingers | +24% Surpassing chance to fire an additional Arrow | ★ |
| 83 | `evasion_and_energy_shield22` | 56838 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 84 | `marks15` | 13624 | Mark Duration | Mark Skills have 25% increased Skill Effect Duration |  |
| 85 | `attributes12` | 47976 | Attribute | +5 to any Attribute |  |
| 86 | `evasion_and_energy_shield11` | 34324 | Spectral Ward | +1 to Maximum Energy Shield per 12 Item Evasion on Equipped Body Armour | ★ |
| 87 | `marks12` | 63830 | Marked for Sickness | Enemies you Mark have 10% reduced Accuracy Rating / Enemies you Mark take 10% increased Da | ★ |
| 88 | `intelligence68` | 14446 | Attribute | +5 to any Attribute |  |
| 89 | `cold3` | 22713 | Cold Damage | 10% increased Cold Damage |  |
| 90 | `cold32` | 19722 | Thin Ice | 20% increased Freeze Buildup / 50% increased Damage with Hits against Frozen Enemies | ★ |
| 91 | `cold33` | 4959 | Heavy Frost | 20% increased Freeze Buildup / Hits ignore non-negative Elemental Resistances of Frozen En | ★ |
| 92 | `accuracy9` | 43923 | Accuracy | 8% increased Accuracy Rating |  |
| 93 | `accuracy18` | 19104 | Eagle Eye | +30 to Accuracy Rating / 10% increased Accuracy Rating | ★ |


## 二、D2（作者原版导出，150 条 = 140 普通 + 8 付费升华 + 2 免费结构）

### POE2-Author-Tree-D2.build（150 个节点）

| # | string id | 数值ID | 节点名 | 属性 | 大点 |
|---|---|---|---|---|---|
| 1 | `AscendancyRanger1Notable3` | 30 |  | Gain Tailwind on Skill use / Lose all Tailwind when Hit |  |
| 2 | `elemental27` | 144 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 3 | `criticals45` | 535 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 4 | `dexterity46` | 722 | Attribute | +5 to any Attribute |  |
| 5 | `evasion21` | 1841 | Evasion | 15% increased Evasion Rating |  |
| 6 | `dexterity51` | 2582 | Attribute | +5 to any Attribute |  |
| 7 | `criticals57_` | 2936 | Attack Critical Damage | 15% increased Critical Damage Bonus for Attack Damage |  |
| 8 | `evasion26` | 3209 | Evasion | 15% increased Evasion Rating |  |
| 9 | `movement_speed4` | 3431 | Skill Speed | 3% increased Skill Speed |  |
| 10 | `AscendancyRanger1Small3` | 3987 |  | 4% increased Skill Speed |  |
| 11 | `criticals13` | 4346 | Critical Chance | 10% increased Critical Hit Chance |  |
| 12 | `criticals18` | 4519 | Damage on Critical | 10% increased Damage if you've dealt a Critical Hit Recently |  |
| 13 | `movement_speed5` | 5305 | Skill Speed | 3% increased Skill Speed |  |
| 14 | `AscendancyRanger1Notable4` | 5817 |  | Grants Skill: Mirage Deadeye |  |
| 15 | `dexterity18` | 6772 | Attribute | +5 to any Attribute |  |
| 16 | `criticals89` | 6891 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 17 | `criticals92` | 7353 | Critical Chance | 10% increased Critical Hit Chance |  |
| 18 | `criticals47` | 9046 | Critical Chance | 10% increased Critical Hit Chance |  |
| 19 | `evasion28` | 9405 | Evasion | 15% increased Evasion Rating |  |
| 20 | `cold_penetration24` | 9421 | Snowpiercer | Damage Penetrates 15% Cold Resistance / +10 to Intelligence | ★ |
| 21 | `criticals44` | 9782 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 22 | `dexterity12_` | 11825 | Attribute | +5 to any Attribute |  |
| 23 | `AscendancyRanger1Notable1` | 12033 |  | Skills fire an additional Projectile |  |
| 24 | `elemental32` | 12611 | Harness the Elements | 20% increased Damage for each type of Elemental Ailment on Enemy | ★ |
| 25 | `criticals54_` | 13407 | Heartbreaking | 25% increased Critical Damage Bonus / +10 to Strength | ★ |
| 26 | `criticals50` | 13724 | Deadly Force | 15% increased Damage if you've dealt a Critical Hit in the past 8 seconds / 15% increased  | ★ |
| 27 | `attributes27` | 14262 | Attribute | +5 to any Attribute |  |
| 28 | `dexterity48` | 14267 | Attribute | +5 to any Attribute |  |
| 29 | `dexterity47` | 15775 | Attribute | +5 to any Attribute |  |
| 30 | `dexterity15` | 16460 | Attribute | +5 to any Attribute |  |
| 31 | `intelligence66` | 16705 | Attribute | +5 to any Attribute |  |
| 32 | `intelligence7` | 17088 | Attribute | +5 to any Attribute |  |
| 33 | `criticals29` | 20677 | For the Jugular | 25% increased Critical Damage Bonus / +10 to Intelligence | ★ |
| 34 | `daze_3` | 21945 | Damage and Criticals vs Dazed Enemies | 5% chance to Daze on Hit |  |
| 35 | `criticals58` | 23040 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 36 | `dexterity82_` | 24287 | Attribute | +5 to any Attribute |  |
| 37 | `attack2` | 25055 | Attack Damage and Movement Speed | 2% increased Movement Speed / 8% increased Attack Damage |  |
| 38 | `passive_keystone_resonance` | 25520 | Resonance | Gain Power Charges instead of Frenzy Charges / Gain Frenzy Charges instead of Endurance Ch |  |
| 39 | `elemental25` | 25700 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 40 | `evasion_and_energy_shield5` | 26034 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 41 | `attack35` | 26068 | Attack Damage | 10% increased Attack Damage |  |
| 42 | `attributes10` | 27705 | Attribute | +5 to any Attribute |  |
| 43 | `heralds16_` | 28044 | Coming Calamity | 40% increased Cold Damage while affected by Herald of Ice / 40% increased Fire Damage whil | ★ |
| 44 | `dexterity20` | 28050 | Attribute | +5 to any Attribute |  |
| 45 | `cold_penetration6` | 28086 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 46 | `heralds10` | 28835 | Herald Damage | 12% increased Damage while affected by a Herald |  |
| 47 | `ranger_huntress_notable2` | 28992 | Honed Instincts | 8% increased Projectile Speed / 8% increased Attack Speed / +10 to Dexterity | ★ |
| 48 | `criticals87` | 29959 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 49 | `attributes11` | 30808 | Attribute | +5 to any Attribute |  |
| 50 | `elemental_attacks8` | 31433 | Catalysis | 20% increased Elemental Damage with Attacks / 5% of Physical Damage from Hits taken as Dam | ★ |
| 51 | `dexterity7` | 31765 | Attribute | +5 to any Attribute |  |
| 52 | `elemental18` | 32155 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 53 | `jewel_slot1976` | 32763 | Jewel Socket |  |  |
| 54 | `dexterity55` | 34015 | Attribute | +5 to any Attribute |  |
| 55 | `evasion_and_energy_shield11` | 34324 | Spectral Ward | +1 to Maximum Energy Shield per 12 Item Evasion on Equipped Body Armour | ★ |
| 56 | `criticals10` | 34621 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 57 | `dexterity34` | 35901 | Attribute | +5 to any Attribute |  |
| 58 | `attack6` | 36576 | Attack Damage | 10% increased Attack Damage |  |
| 59 | `dexterity17` | 38143 | Attribute | +5 to any Attribute |  |
| 60 | `criticals52` | 38493 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 61 | `criticals53` | 38537 | Heartstopping | +10 to Intelligence / 20% increased Critical Hit Chance | ★ |
| 62 | `criticals17` | 38541 | Critical Chance | 10% increased Critical Hit Chance |  |
| 63 | `criticals55_` | 39369 | Struck Through | Attacks have +1% to Critical Hit Chance | ★ |
| 64 | `criticals46` | 39569 | Critical Damage | 15% increased Critical Damage Bonus |  |
| 65 | `AscendancyRanger1Small8` | 39723 |  | 12% increased Projectile Damage |  |
| 66 | `elemental28` | 41096 | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |  |
| 67 | `attack5` | 41580 | Maiming Strike | 25% increased Attack Damage / Attacks have 25% chance to Maim on Hit | ★ |
| 68 | `AscendancyRanger1Notable2_2` | 41875 |  | Projectiles deal 20% more Hit damage to targets in the first 3.5 metres of their movement, |  |
| 69 | `attributes25` | 42379 | Attribute | +5 to any Attribute |  |
| 70 | `AscendancyRanger1Notable2_Choice` | 42416 |  |  |  |
| 71 | `elemental_attacks6` | 42794 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 72 | `evasion_and_energy_shield8` | 42805 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 73 | `movement_speed9` | 43082 | Acceleration | 3% increased Movement Speed / 10% increased Skill Speed | ★ |
| 74 | `dexterity16` | 43746 | Attribute | +5 to any Attribute |  |
| 75 | `evasion24_` | 44776 | Evasion | 15% increased Evasion Rating |  |
| 76 | `AscendancyRanger1Small1__` | 46854 |  | 10% increased Projectile Speed |  |
| 77 | `AscendancyRanger1Start` | 46990 |  |  |  |
| 78 | `dexterity52` | 48116 | Attribute | +5 to any Attribute |  |
| 79 | `dexterity50` | 48773 | Attribute | +5 to any Attribute |  |
| 80 | `intelligence25` | 51741 | Attribute | +5 to any Attribute |  |
| 81 | `bow19` | 52800 | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |  |
| 82 | `cold_penetration7` | 54557 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 83 | `criticals59` | 54983 | Attack Critical Chance | 10% increased Critical Hit Chance for Attacks |  |
| 84 | `dexterity54` | 54984 | Attribute | +5 to any Attribute |  |
| 85 | `criticals56` | 55621 | Critical Chance | 10% increased Critical Hit Chance |  |
| 86 | `criticals90` | 56265 | Throatseeker | 60% increased Critical Damage Bonus / 20% reduced Critical Hit Chance | ★ |
| 87 | `projectiles15` | 56651 | Projectile Damage | 10% increased Projectile Damage |  |
| 88 | `criticals49` | 56776 | Cooked | 60% increased Critical Damage Bonus / 25% reduced Armour, Evasion and Energy Shield | ★ |
| 89 | `evasion_and_energy_shield22` | 56838 | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |  |
| 90 | `heralds12_` | 56847 | Herald Damage | 12% increased Damage while affected by a Herald |  |
| 91 | `cold_penetration1` | 57088 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 92 | `dexterity9` | 57821 | Attribute | +5 to any Attribute |  |
| 93 | `evasion33` | 59720 | Beastial Skin | 100% increased Evasion Rating from Equipped Body Armour | ★ |
| 94 | `dexterity19` | 60505 | Attribute | +5 to any Attribute |  |
| 95 | `jewel_slot1960` | 60735 | Jewel Socket |  |  |
| 96 | `elemental26` | 61246 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 97 | `AscendancyRanger1Small2` | 61461 |  | 10% increased Projectile Speed |  |
| 98 | `criticals28` | 61601 | True Strike | +10 to Dexterity / 20% increased Critical Hit Chance | ★ |
| 99 | `daze_4` | 61718 | Damage vs Dazed Enemies | 15% increased Damage against Dazed Enemies |  |
| 100 | `jewel_slot1961` | 61834 | Jewel Socket |  |  |
| 101 | `attributes29` | 63888 | Attribute | +5 to any Attribute |  |
| 102 | `elemental16` | 64213 | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |  |
| 103 | `dexterity110` | 2334 | Dexterity | +8 to Dexterity |  |
| 104 | `cold33` | 4959 | Heavy Frost | 20% increased Freeze Buildup / Hits ignore non-negative Elemental Resistances of Frozen En | ★ |
| 105 | `intelligence68` | 14446 | Attribute | +5 to any Attribute |  |
| 106 | `cold32` | 19722 | Thin Ice | 20% increased Freeze Buildup / 50% increased Damage with Hits against Frozen Enemies | ★ |
| 107 | `cold_penetration3` | 20909 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 108 | `cold3` | 22713 | Cold Damage | 10% increased Cold Damage |  |
| 109 | `daze_7` | 26572 | Criticals vs Dazed Enemies | 12% increased Critical Hit Chance against Dazed Enemies |  |
| 110 | `elemental54` | 28061 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 111 | `criticals83` | 31692 | Critical Chance | 10% increased Critical Hit Chance |  |
| 112 | `bow21` | 32319 | Surpassing Arrow Chance | +10% Surpassing chance to fire an additional Arrow |  |
| 113 | `bow23` | 33542 | Quick Fingers | +24% Surpassing chance to fire an additional Arrow | ★ |
| 114 | `elemental55` | 35878 | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |  |
| 115 | `attack36` | 37389 | Attack Damage | 10% increased Attack Damage |  |
| 116 | `daze_2` | 38342 | Stupefy | 10% chance to Daze on Hit / 30% increased Damage against Dazed Enemies | ★ |
| 117 | `cold_penetration2` | 44891 | Cold Penetration | Damage Penetrates 6% Cold Resistance |  |
| 118 | `criticals86` | 45702 | Critical Chance | 10% increased Critical Hit Chance |  |
| 119 | `criticals84` | 46197 | Careful Assassin | 20% reduced Critical Damage Bonus / 50% increased Critical Hit Chance | ★ |
| 120 | `daze_19` | 47514 | Dizzying Hits | 10% chance to Daze on Hit / 25% increased Critical Hit Chance against Dazed Enemies | ★ |
| 121 | `attributes12` | 47976 | Attribute | +5 to any Attribute |  |
| 122 | `elemental56` | 50884 | Primal Sundering | Damage Penetrates 12% Elemental Resistances / 8% increased Area of Effect for Attacks | ★ |
| 123 | `cold_penetration23` | 55835 | Exposed to the Cosmos | Damage Penetrates 18% Cold Resistance / 20% increased chance to inflict Ailments against E | ★ |
| 124 | `bow20` | 57615 | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |  |
| 125 | `dexterity102` | 58397 | Proficiency | +25 to Dexterity | ★ |
| 126 | `intelligence67` | 59538 | Attribute | +5 to any Attribute |  |
| 127 | `dexterity58` | 2408 | Attribute | +5 to any Attribute |  |
| 128 | `azmerianimals48` | 2745 | The Noble Wolf | 25% increased Magnitude of Ailments you inflict against Marked Enemies / 20% increased Cri | ★ |
| 129 | `azmerianimals43` | 12174 | Ailment Magnitude | 10% increased Magnitude of Ailments you inflict |  |
| 130 | `dexterity57` | 12890 | Attribute | +5 to any Attribute |  |
| 131 | `marks15` | 13624 | Mark Duration | Mark Skills have 25% increased Skill Effect Duration |  |
| 132 | `azmerianimals44` | 18864 | Ailment Magnitude | 10% increased Magnitude of Ailments you inflict |  |
| 133 | `marks29` | 21279 | Mark Effect and Blind Effect | 8% increased Effect of your Mark Skills / 10% increased Blind Effect |  |
| 134 | `marks28` | 23305 | Mark Use Speed | Mark Skills have 10% increased Use Speed |  |
| 135 | `dexterity81` | 24786 | Attribute | +5 to any Attribute |  |
| 136 | `dexterity85_` | 26432 | Attribute | +5 to any Attribute |  |
| 137 | `marks5_` | 28258 | Mark Effect | 10% increased Effect of your Mark Skills |  |
| 138 | `attributes9` | 30657 | Attribute | +5 to any Attribute |  |
| 139 | `shock6` | 32301 | Frazzled | 15% increased Mana Regeneration Rate / 30% increased Magnitude of Shock you inflict | ★ |
| 140 | `marks32` | 35534 | Mark Use Speed | Mark Skills have 10% increased Use Speed |  |
| 141 | `attributes74` | 42118 | Attribute | +5 to any Attribute |  |
| 142 | `marks17` | 44756 | Marked Agility | 60% increased Mana Cost Efficiency of Marks / 4% increased Movement Speed if you've used a | ★ |
| 143 | `marks13` | 44841 | Mark Duration | Mark Skills have 25% increased Skill Effect Duration |  |
| 144 | `shock3` | 44932 | Shock Effect | 15% increased Magnitude of Shock you inflict |  |
| 145 | `azmerianimals47` | 49485 | Dexterity | +8 to Dexterity |  |
| 146 | `shock15` | 50277 | Shock Effect | 15% increased Magnitude of Shock you inflict |  |
| 147 | `shock4` | 50701 | Shock Effect | 15% increased Magnitude of Shock you inflict |  |
| 148 | `marks27` | 51602 | Unsight | Enemies near Enemies you Mark are Blinded / Enemies you Mark cannot deal Critical Hits | ★ |
| 149 | `marks16` | 59064 | Mark Effect | 10% increased Effect of your Mark Skills |  |
| 150 | `marks12` | 63830 | Marked for Sickness | Enemies you Mark have 10% reduced Accuracy Rating / Enemies you Mark take 10% increased Da | ★ |
