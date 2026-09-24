# 锐眼冰射 · Fubgun 版 · 0.5.5 国服

一个纯静态攻略站（单文件 `index.html` + 几个下载文件），部署在 GitHub Pages：
**https://HarryGhost.github.io/poe2-guide/**

来源：Mobalytics 上 Fubgun 的 [0.5.5 Ice Shot Deadeye](https://mobalytics.gg/poe-2/builds/ice-shot-deadeye)（英文），本仓库是中文整理版，
并把技能 / 辅助 / 升华 / 天赋大点 / 装备的名字换成了国服中文名。

## 文件

| 文件 | 说明 |
|---|---|
| `index.html` | 攻略本体（单文件，无外部依赖，无构建步骤） |
| `POE2-Fubgun-Ice-Shot-Deadeye.build` | **主下载文件**：93 点天赋（已排加点顺序）+ 11 组技能（含武器组、辅助宝石） |
| `锐眼冰射-Fubgun版.build` | 上面那份的副本（中文文件名） |
| `术语对照.md` | 中英文术语对照（技能 / 辅助 / 升华 / 天赋大点 / 装备 / 打造通货） |
| `外网资料/` | Fubgun 英文原文存档、国服实况角色配置快照、外网攻略汇总 |
| `归档-lowK版/` | 旧版（另一位国服作者 lowK 的版本）存档，含天赋树查看器 `tree-viewer.html` |

## 页面结构

总览 / 路线（6 阶段）/ 装备 / 技能 / 天赋 / 打造 / 要诀 / 下载 / 问答，共 9 个 hash 路由。
`index.html` 由 `/tmp/site/gen2.py` 生成（本机脚本，不在仓库里）；直接手改 `index.html` 也可以，
但下次重新生成会覆盖。

## 数据来源与边界

- 技能、辅助、传奇中文名：`poe2db.tw/cn` 逐条核对。
- 天赋大点中文名：国服 WeGame 天赋模拟器节点数据。
- 打造通货：**未找到统一官方译名**，保留英文，并在文中标 ⚠。
- `.build` 里的 93 个天赋节点来自一位国服实况锐眼角色的公开数据，**不是** Fubgun 本人那份图的逐点复刻；
  技能组、升华顺序、装备方向与 Fubgun 的说明一致。

## 更新方式

```bash
git add -A && git commit -m "..." && git push   # main 分支，GitHub Pages 自动发布
```
