# 当前使用版维护

阅读只需解压打开index.html，不需要安装任何依赖。

本版用白名单从R45和角色快照生成，没有覆盖原包。复建需要Python、jinja2及以下三个旧输入：R45解压目录、Ghostliness角色诊断解压目录、复核行动单。

```sh
python build46.py --baseline /path/to/R45 --character /path/to/Ghostliness_角色诊断_2026-10-06 --plan /path/to/Ghostliness_当前阶段与三步调整_20261006.md --output /path/to/new/output
```

输出必须为不存在的新目录。源码中的事实只来自已有资料；不是游戏扫描或自动配装脚本。构建不会运行任何游戏操作、外部网站请求或交易。
