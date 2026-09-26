# R7：Early优先的打造教学层

## 重建
使用Python 3.12+，在当前解压目录运行：

```sh
python 源码/build.py
```

生成器无需网络或第三方依赖，不会自动更新游戏版本。
`data/Early起步打造教学.json`保存12个部位/功能组和5个进阶阶段。
`源码/early_crafting.py`生成新入口和Early全展开页，`early-crafting.js`仅切换显示。
原工艺模块继续生成`craft-advanced.html`与`craft-all.html`。八条工艺的原文/步骤未重写。
源码完整，生成文件不能替代修改源文件。

## 路由
- craft.html 默认Early；#early-bow、#early-quiver等为部位；#stage-mid等为阶段。
- craft-early-all.html 全展开，不依赖脚本。
- craft-advanced.html#bow-noncrit 等为8条原工艺。
- 历史craft.html高级锚点在脚本开启时兼容转到工艺库。生成器已重写本网站内部旧链接，不依赖兼容跳转。
- 全部阶段随时可用；没有存档门槛、锁定按钮或“完成后解锁”。

## 内容边界
作者目标、原件数据、编辑普通加工建议明确分开。不要把编辑建议改称作者的确定性工艺。
物品等级与装备需求等级不是人物等级；Early原件展示不是最低要求。
06保持只读冲突文件。数据源和已声明未核实部分不得静默替换。
