# 任务：核对 / 输出「第一天开荒天赋树」（PoE2 锐眼冰射，国服 0.5.5）

## 背景

国服《流放之路：降临》0.5.5，BD 是 B 站 UP 主 **网瘾老年人lowK** 的「锐眼冰射狙击」。
他把这个 BD 分成两个阶段：

- **第一天**：非暴击冰射开荒（1~70 级），练到能刷异界 T15
- **第二天**：转暴击后的后期（70 级起）

现在需要的是**第一天那棵天赋树**。

## 可直接下载的文件（公开链接，直接抓）

- 第二天（他本人导出，100% 原版）：`https://harryghost.github.io/poe2-guide/POE2-Author-Tree-D2.build`
- 第一天（我推的版本，需要你核对）：`https://harryghost.github.io/poe2-guide/POE2-Author-Tree-D1.build`
- 攻略站（含他文档里的天赋树截图）：`https://harryghost.github.io/poe2-guide/`

文件格式：`.build`，JSON，关键是 `passives` 数组，每项形如 `{"id": "cold_penetration24"}`。
id 用的是游戏 PassiveSkills 表的 string id。

## 我推的第一天树是怎么来的

拿他第二天那 151 个节点当底，**剔除**：

- 所有 `criticals*` 前缀节点（暴击系）
- 所有 `daze*`（眩晕）、`shock*`（感电）、`DeliriumAnoint`（涂油）
- 属性文本里含 `critical` 的大点

**保留**：冰霜穿透 / 冰冻积累 / 投射物 / 弓（含「额外箭矢几率」）/ 属性点 / 珠宝孔 /
闪避+护盾 / 移速 / 印记 / 敏捷。

结果：**104 个天赋节点**，用全图最短路径校验过是 **1 个完整连通块**（合法）。

## 依据（他的原话，来自他的视频）

- 「70 级左右就可以转暴击」「转暴击需要留 100 万金币洗点」→ 所以第一天不点暴击系
- 第一天输出靠：闪电箭矢 / 引雷针过渡 → **31 级转冰霜射击** → 狙击 →
  冰冻印记 + 冻结齐射 + 弹幕
- 他视频里讲第一天天赋原话：「这里要加**投射物速度跟攻击速度**，还有石的敏捷是一个比较实惠的点」
  「因为我们暴击比较**缺命中**」

## 请你做两件事（核对 + 输出）

### 1. 核对点数
按「每级 1 点 + 任务/间章 24 点」算：
- 104 点 → 约 **80 级**
- 但第一天按他的视频是 **70 级左右**打完 T15 → 应该是 **90~95 点**

**问题**：第一天合理的点数应该是多少？我现在这版是多了还是少了？

### 2. 输出修订后的第一天节点表
如果你认为 104 点不对，请给出修订版：

- **要删的节点**：列出 string id（或节点名）
- **要加的节点**：列出 string id（或节点名）
- 修订后的总节点数

要求：**保持从锐眼起点连通**（游戏规则），并且**至少覆盖他第一天要用的技能**
（冰霜射击 / 狙击 / 冰冻印记 / 冻结齐射 / 弹幕 相关的关键点，比如冰冷穿透、冰冻积累、投射物、命中）。

## 可用的数据源

1. **PoB2 仓库（权威）**：`https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2`
   - `src/TreeData/0_5/tree.json` —— 节点、连接、坐标、大点标记
   - 注意：`groups[id].x/y` 是**组中心**，不是节点真实坐标。真实坐标公式：
     ```
     节点坐标 = group中心 + 轨道半径 × (sinθ, cosθ)
     θ = constants.orbitAnglesByOrbit[orbit][orbitIndex]
     orbitRadii = [0, 82, 162, 335, 493, 662, 846, 251, 1080, 1322]
     ```
2. **GGG 官方 `.build` 规范**：`https://www.pathofexile.com/developer/docs/game`
3. **真实可用的 .build 样本**（对照格式用）：
   `https://github.com/chesler410/poe2-build-forge/tree/main/fixtures`
4. **中文资料站**：`https://poe2db.tw/cn/`

## 输出格式（照这个回）

```
① 第一天合理点数：___ 点（依据：____）

② 要删的节点：
   - cold_penetration1（Damage Penetrates 6% Cold Resistance）
   - ...

③ 要加的节点：
   - xxx（说明为什么第一天就需要）
   - ...

④ 修订后总节点数：___

⑤ 你认为我哪里判断错了（如果有）
```

## 协作说明

你只需要给出**节点级别的判断**（哪些留、哪些删、哪些加）。
我这边有完整的树数据、宝石数据和可复现脚本，落地（重新生成 .build、部署、回读验证）我来做。

---

## 附：我当前 D1 的全部 104 个节点（方便你逐个核对）

| # | string id | 节点名 | 属性 |
|---|---|---|---|
| 1 | `projectiles15` | Projectile Damage | 10% increased Projectile Damage |
| 2 | `dexterity17` | Attribute | +5 to any Attribute |
| 3 | `dexterity16` | Attribute | +5 to any Attribute |
| 4 | `dexterity15` | Attribute | +5 to any Attribute |
| 5 | `ranger_huntress_notable2` | Honed Instincts ★大点 | 8% increased Projectile Speed / 8% increased Attack Speed / +10 to Dex |
| 6 | `dexterity18` | Attribute | +5 to any Attribute |
| 7 | `dexterity19` | Attribute | +5 to any Attribute |
| 8 | `dexterity20` | Attribute | +5 to any Attribute |
| 9 | `attributes29` | Attribute | +5 to any Attribute |
| 10 | `dexterity34` | Attribute | +5 to any Attribute |
| 11 | `attack35` | Attack Damage | 10% increased Attack Damage |
| 12 | `attack36` | Attack Damage | 10% increased Attack Damage |
| 13 | `jewel_slot1960` | Jewel Socket |  |
| 14 | `elemental28` | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |
| 15 | `elemental27` | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |
| 16 | `elemental32` | Harness the Elements ★大点 | 20% increased Damage for each type of Elemental Ailment on Enemy |
| 17 | `dexterity12_` | Attribute | +5 to any Attribute |
| 18 | `elemental26` | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |
| 19 | `dexterity85_` | Attribute | +5 to any Attribute |
| 20 | `elemental25` | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |
| 21 | `elemental54` | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |
| 22 | `cold_penetration6` | Cold Penetration | Damage Penetrates 6% Cold Resistance |
| 23 | `cold_penetration1` | Cold Penetration | Damage Penetrates 6% Cold Resistance |
| 24 | `elemental55` | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |
| 25 | `elemental_attacks6` | Elemental Attack Damage | 12% increased Elemental Damage with Attacks |
| 26 | `dexterity57` | Attribute | +5 to any Attribute |
| 27 | `elemental18` | Elemental Damage and Shock Chance | 10% increased chance to Shock / 8% increased Elemental Damage |
| 28 | `dexterity54` | Attribute | +5 to any Attribute |
| 29 | `elemental16` | Elemental Damage and Freeze Buildup | 10% increased Freeze Buildup / 8% increased Elemental Damage |
| 30 | `elemental56` | Primal Sundering ★大点 | Damage Penetrates 12% Elemental Resistances / 8% increased Area of Eff |
| 31 | `elemental_attacks8` | Catalysis ★大点 | 20% increased Elemental Damage with Attacks / 5% of Physical Damage fr |
| 32 | `cold_penetration7` | Cold Penetration | Damage Penetrates 6% Cold Resistance |
| 33 | `dexterity58` | Attribute | +5 to any Attribute |
| 34 | `attributes74` | Attribute | +5 to any Attribute |
| 35 | `attributes27` | Attribute | +5 to any Attribute |
| 36 | `intelligence7` | Attribute | +5 to any Attribute |
| 37 | `dexterity55` | Attribute | +5 to any Attribute |
| 38 | `attack6` | Attack Damage | 10% increased Attack Damage |
| 39 | `dexterity102` | Proficiency ★大点 | +25 to Dexterity |
| 40 | `cold_penetration24` | Snowpiercer ★大点 | Damage Penetrates 15% Cold Resistance / +10 to Intelligence |
| 41 | `azmerianimals47` | Dexterity | +8 to Dexterity |
| 42 | `jewel_slot1961` | Jewel Socket |  |
| 43 | `marks32` | Mark Use Speed | Mark Skills have 10% increased Use Speed |
| 44 | `dexterity82_` | Attribute | +5 to any Attribute |
| 45 | `attack2` | Attack Damage and Movement Speed | 2% increased Movement Speed / 8% increased Attack Damage |
| 46 | `dexterity52` | Attribute | +5 to any Attribute |
| 47 | `jewel_slot1976` | Jewel Socket |  |
| 48 | `attack5` | Maiming Strike ★大点 | 25% increased Attack Damage / Attacks have 25% chance to Maim on Hit |
| 49 | `dexterity51` | Attribute | +5 to any Attribute |
| 50 | `intelligence25` | Attribute | +5 to any Attribute |
| 51 | `dexterity110` | Dexterity | +8 to Dexterity |
| 52 | `marks29` | Mark Effect and Blind Effect | 8% increased Effect of your Mark Skills / 10% increased Blind Effect |
| 53 | `intelligence66` | Attribute | +5 to any Attribute |
| 54 | `dexterity50` | Attribute | +5 to any Attribute |
| 55 | `azmerianimals43` | Ailment Magnitude | 10% increased Magnitude of Ailments you inflict |
| 56 | `movement_speed5` | Skill Speed | 3% increased Skill Speed |
| 57 | `dexterity48` | Attribute | +5 to any Attribute |
| 58 | `dexterity81` | Attribute | +5 to any Attribute |
| 59 | `marks28` | Mark Use Speed | Mark Skills have 10% increased Use Speed |
| 60 | `heralds12_` | Herald Damage | 12% increased Damage while affected by a Herald |
| 61 | `attributes10` | Attribute | +5 to any Attribute |
| 62 | `bow19` | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |
| 63 | `attributes11` | Attribute | +5 to any Attribute |
| 64 | `movement_speed4` | Skill Speed | 3% increased Skill Speed |
| 65 | `evasion26` | Evasion | 15% increased Evasion Rating |
| 66 | `attributes25` | Attribute | +5 to any Attribute |
| 67 | `azmerianimals44` | Ailment Magnitude | 10% increased Magnitude of Ailments you inflict |
| 68 | `attributes9` | Attribute | +5 to any Attribute |
| 69 | `dexterity9` | Attribute | +5 to any Attribute |
| 70 | `evasion24_` | Evasion | 15% increased Evasion Rating |
| 71 | `evasion33` | Beastial Skin ★大点 | 100% increased Evasion Rating from Equipped Body Armour |
| 72 | `movement_speed9` | Acceleration ★大点 | 3% increased Movement Speed / 10% increased Skill Speed |
| 73 | `marks27` | Unsight ★大点 | Enemies near Enemies you Mark are Blinded / Enemies you Mark cannot de |
| 74 | `azmerianimals48` | The Noble Wolf ★大点 | 25% increased Magnitude of Ailments you inflict against Marked Enemies |
| 75 | `bow20` | Surpassing Arrow Chance | +8% Surpassing chance to fire an additional Arrow |
| 76 | `dexterity7` | Attribute | +5 to any Attribute |
| 77 | `evasion21` | Evasion | 15% increased Evasion Rating |
| 78 | `dexterity47` | Attribute | +5 to any Attribute |
| 79 | `heralds10` | Herald Damage | 12% increased Damage while affected by a Herald |
| 80 | `passive_keystone_resonance` | Resonance | Gain Power Charges instead of Frenzy Charges / Gain Frenzy Charges ins |
| 81 | `evasion_and_energy_shield5` | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |
| 82 | `marks16` | Mark Effect | 10% increased Effect of your Mark Skills |
| 83 | `heralds16_` | Coming Calamity ★大点 | 40% increased Cold Damage while affected by Herald of Ice / 40% increa |
| 84 | `evasion_and_energy_shield8` | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |
| 85 | `bow21` | Surpassing Arrow Chance | +10% Surpassing chance to fire an additional Arrow |
| 86 | `cold_penetration2` | Cold Penetration | Damage Penetrates 6% Cold Resistance |
| 87 | `marks5_` | Mark Effect | 10% increased Effect of your Mark Skills |
| 88 | `intelligence67` | Attribute | +5 to any Attribute |
| 89 | `evasion28` | Evasion | 15% increased Evasion Rating |
| 90 | `dexterity46` | Attribute | +5 to any Attribute |
| 91 | `bow23` | Quick Fingers ★大点 | +24% Surpassing chance to fire an additional Arrow |
| 92 | `evasion_and_energy_shield22` | Evasion and Energy Shield | 12% increased Evasion Rating / 12% increased maximum Energy Shield |
| 93 | `marks13` | Mark Duration | Mark Skills have 25% increased Skill Effect Duration |
| 94 | `marks15` | Mark Duration | Mark Skills have 25% increased Skill Effect Duration |
| 95 | `attributes12` | Attribute | +5 to any Attribute |
| 96 | `cold_penetration3` | Cold Penetration | Damage Penetrates 6% Cold Resistance |
| 97 | `evasion_and_energy_shield11` | Spectral Ward ★大点 | +1 to Maximum Energy Shield per 12 Item Evasion on Equipped Body Armou |
| 98 | `cold_penetration23` | Exposed to the Cosmos ★大点 | Damage Penetrates 18% Cold Resistance / 20% increased chance to inflic |
| 99 | `marks12` | Marked for Sickness ★大点 | Enemies you Mark have 10% reduced Accuracy Rating / Enemies you Mark t |
| 100 | `marks17` | Marked Agility ★大点 | 60% increased Mana Cost Efficiency of Marks / 4% increased Movement Sp |
| 101 | `intelligence68` | Attribute | +5 to any Attribute |
| 102 | `cold3` | Cold Damage | 10% increased Cold Damage |
| 103 | `cold32` | Thin Ice ★大点 | 20% increased Freeze Buildup / 50% increased Damage with Hits against  |
| 104 | `cold33` | Heavy Frost ★大点 | 20% increased Freeze Buildup / Hits ignore non-negative Elemental Resi |
