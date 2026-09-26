# R9当前维护入口

全站重建：`python 源码/build.py`。R9按步操作数据：`generate_guided_data.py`；对应测试：`check_guided_r9.py`与`check_stage_regression_r9.py`。详见根目录“给DSH_更新说明.md”。

---
以下为继承的R8生成器说明，历史脚本的选择器断言不直接作为R9新打造页测试。

# R8 可维护源码

在完整解压目录中运行：`python 源码/build.py`。要求Python 3.12或更新版本；生成器仅依赖Python标准库，不需要联网。
生成器读取相邻data目录，原地生成26份HTML和assets资源；不会修改构筑文件目录的原件。

## 重点维护位置
- `data/转换检查清单.json`：10条明确的fromStage→toStage转换检查项。
- `data/全站阶段与核算.json`：阶段、整套参考、装备/技能需求记录。原始导出在original内保留。
- `源码/review_r8.py`：同步参考装备展示、转换清单、打造案例和关键天赋定位。
- `源码/app.js`：属性/装备/宝石等级联动、键位、搜索、资源与节点筛选。
- `data/打造教学实例.json`、`源码/examples.js`：教学案例与物理面板算术演示；不模拟真实打造或游戏DPS。
- `data/关键天赋点位核对.json`：只存已核对名称、效果、ID。无坐标不伪造地图。
- `源码/early_crafting.py`：Early12个部位教程；`源码/crafting.py`保留作者8条进阶工艺。

## 回归要点
下一阶段从当前ID查边，不要再用下一阶段profile.gate。
新转换勾选键单独带r8，不继承R7错位勾选；其它用户键位和属性编辑尽量保留。
切换参考必须同步两个select、三个属性总值、装备面板和宝石等级。作者原始词条独立显示。
所有阶段入口均为正常链接，不依赖进度解锁。
更新脚本/样式时同步修改缓存版本参数。不要只改生成的HTML，否则下次重建会被覆盖。

测试脚本在同目录。需运行网页测试时，安装playwright、beautifulsoup4及Chromium；此环境采用内存资源载入，不能声称真实线上测试。

静态复核：`python 源码/check_static.py 旧R7解压目录`。没有旧目录时只做当前结构复核，不能据此宣称已比对历史原件。
