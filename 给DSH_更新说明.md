# R9：把打造入口改为按步操作

## 部署
保持原GitHub Pages目录结构，整体同步根目录HTML、`assets/`、`data/`、`构筑文件/`、`原文资料/`和`.nojekyll`。源码和检查文件可以留存，不影响站点。不要仅替换首页。

`craft.html`现在是新操作入口；原页面保留为`craft-reference.html`。原`craft.html#early-bow`等部位书签兼容，新书签可带步骤，例如`craft.html#early-bow/augment`。原高级工艺地址仍保留，新格式为`craft.html#bow-noncrit/essence`。

## 数据与页面
- `data/打造按步操作_R9.json`：20条路线，121个阅读步骤；有些是准备、验收或只读边界，不代表121次必做材料操作。
- `源码/guided_crafting.py`：生成新入口和完整无脚本页。
- `源码/guided-crafting.js`：阶段/装备/状态导航、材料说明、复制、打印；没有进度门槛。
- `源码/guided-crafting.css`：只影响打造模块，沿用C配色。
- `源码/generate_guided_data.py`：从已有工艺数据与明确教学说明重建新数据；不覆盖原八条工艺JSON。
- `源码/build.py`：全站统一生成器，已接入新页面与全站搜索。

## 重建与测试
在根目录运行：
```sh
python 源码/build.py
```
需要重建新步骤数据时先运行：
```sh
python 源码/generate_guided_data.py
python 源码/build.py
```
浏览器检查需要Playwright、BeautifulSoup及Chromium：
```sh
python 源码/check_guided_r9.py
python 源码/check_stage_regression_r9.py
```
测试脚本的Chromium路径目前为`/usr/bin/chromium`，不同系统需调整。旧`check_browser.py`等脚本保留作为历史源代码，针对R9请运行上面两份；旧脚本可能仍假定旧打造入口结构。

## 状态与限制
- 页面只保存阅读位置，不保存“你的装备已经加工成功”。LocalStorage不可用时不崩溃，可使用带步骤的书签。
- 剪贴板不可用时打开可手动Ctrl+C的文本框。
- “打印本路线”会打印当前路线全部步骤，不是只打印正在读的一步。
- `.build`及原始阶段数据与R8保持字节一致。
- 测试在Chromium内加载生成HTML及内联相同本地JS/CSS；受环境策略限制，未验证实际GitHub Pages部署、真实file://权限或跨会话保存。请部署后额外检查资源加载、刷新、复制和保存。
- 攻略没有执行国服打造实测。未验证的高投入前提不能删除警示后冒充可直接执行。
