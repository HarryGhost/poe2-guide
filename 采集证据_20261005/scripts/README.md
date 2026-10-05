# 本次实际使用的代码

采集已经由 Codex 执行。这些代码用于保留方法和复核结果，不是把采集任务转交给用户。

- `public-document-extraction.js`：通过浏览器只读 DOM 读取公开预载 script 中的目标文档。大字符串在本次调用中分为 80,000 字符片段，再保存 JSON，以避免工具的对象深度/长度截断。
- `browser-capture-helpers.js`：实际使用的分支切换、装备/珠宝悬浮框、镶嵌物、武器组及人物树采集函数。
- `passive-full-capture.js`：补存无遮挡的全屏人物天赋路径图。仅切换查看、缩放，不修改节点。
- `atlas-capture-helpers.js`：实际使用的分支、树图、大师已选状态和大师候选悬浮框采集函数。候选只悬浮读取，不点击代选。
- `normalize_capture.py`：只读取包内本次证据，整理两个 JSON、中文核对表、缺失清单并执行字段/分支/证据引用校验。
- `package_capture.py`：检查文件、JSON、链接、图片签名、敏感值模式；生成 SHA-256 清单；以不覆盖方式创建 ZIP，再执行 ZIP CRC 和全部清单哈希核验。

浏览器函数运行环境是 Codex 的 `cua_repl`，需要已绑定的目标 `tab`、`node:fs/promises`、新建且没有旧内容的 `captureRoot`，以及相应公开文档包装对象与 `childrenVariants` 元数据。它们不是独立的普通 Node/Playwright 安装脚本，不要求安装新的扩展或全局修改电脑设置。

两个本地整理程序只使用 Python 3 标准库，无网络、无 Cookie、无账户配置。离线复核运行目录为解压后的采集目录：

```text
python3 scripts/normalize_capture.py
```

该程序会重生成本采集目录中的整理结果，不读取原 `.build`、`.filter` 或其他项目。打包程序在输出路径已有同名 ZIP 时拒绝覆盖。

本次浏览器原始采集使用的是未裁剪的目标公开文档；交付前只保留六套人物配置、七套异界配置及相关作者栏目。删除了无关广告、推荐、评论、实时账户栏目及过滤器字段。因此这些 JSON 是有范围的公开文档摘录，不是整个浏览器会话或 HAR。
