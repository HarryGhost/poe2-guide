# R43 维护与重建

本轮是 R42 的增量展示层；作者原 `.build`、原 `.filter`、R28 档案及 Codex 采集文件均不改写。

## 重建现行页面

输入必须是独立的 R42 完整解压目录；输出目录必须尚不存在。Python 标准库足以执行生成器，不能将 R43 再当 R42 叠加。

```bash
python R43维护源码/build_r43.py /新目录/R43重建 \
  --baseline /R42完整解压目录 \
  --capture /R43目录/采集证据_20261005 \
  --overlay /R43目录/data/R43_capture_overlay.json
```

`extension_r43.js` 处理新页面，`style_r43.css` 为新增样式，`data/R43_capture_overlay.json` 为可追溯的显示层数据。构建生成哈希命名资源并更新首页。不会发布域名，也不会向作者网站写入内容。

构建输出不包含最后添加的发布说明、最终测试日志与 SHA256SUMS_R43.txt；发布时重新生成当前清单，不能继续拿旧版清单校验新首页。

## 本次数据准备与检查

`prepare_r43.py`、`inspect_data.py` 和 `test_r43.py` 保留实际执行版本。它们的工作目录约定为脚本同目录下 `baseline/`、`capture/fubgun_capture_2026-10-05/`、`old_data.json`、`raw_compare.json`、`overlay43.json`、`build_paths.json`。这些是制作检查的中间目录，不是读网页需要的依赖。

准备脚本用于按原始记录生成显示层，不应在缺少对应输入时直接运行。中间比对数据已另保存在 `R43检查`，原始 R42 数据仍在既有 assets 中。

页面检查需要 Playwright 与 Chromium。脚本保存的可执行路径为 `/usr/bin/chromium`，不同系统需调整；`build_paths.json` 指向待测网站。实际 HTTP/file 访问失败与内存文档交互检查分开记录，不能把内存检查写成真实部署或游戏验收。

本轮的重复生成验证针对发布收尾之前的生成输出。最终整包以 `SHA256SUMS_R43.txt` 为准。不要用历史 R37/R38/R42 维护脚本覆盖当前工程。
