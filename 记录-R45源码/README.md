# R45 维护

输入必须是完整、独立的R44目录，输出必须尚不存在。禁止将R45当R44叠补；不能原地覆盖。

```sh
python build45.py /path/to/R44 /path/to/new/R45
python test45.py tasks
python test45.py stages1
python test45.py stages2
python test45.py stages3
python test45.py atlas
python audit45.py
```

标准生成仅用Python标准库。测试另需Playwright与Chromium，当前脚本使用`/usr/bin/chromium`；别的平台按实际路径调整。真实导航试验需要先启动对应本地HTTP服务，但环境阻止时只能如实记录，不可算部署通过。

`prepare45.py /path/to/R44`可从原字段和明确写入的解释重新生成`guide45.json`；它不联网抓新版本，不改原件。`guide45.json`是显示层选择指导，不是新增作者实装。

基线文件只允许改变index.html、00_先读我.md、README_上线.md。新指导、样式和脚本使用新哈希资产。四份现行原版过滤器及所有原build、采集、历史文件均逐字节保护。

生成步骤不复制本轮文档、测试产物或最终SHA清单；它们是发布收尾。先独立复测，再生成覆盖新文件的清单。测试中的渲染矩阵不等于逐一鼠标点击，也不是游戏实测。
