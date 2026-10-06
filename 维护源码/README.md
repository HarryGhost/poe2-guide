# 维护

本次为R45和R46的独立网站范围重组。build47.py按自身目录中的r45/和r46/Ghostliness_当前使用版_R46/读取基线，接受全新输出目录参数，拒绝覆盖；test47.py读取build_paths.json进行检查。需要Python3；语法检查需Node，页面检查需Playwright和Chromium。用户正常阅读不需要这些工具。

finalize47.py中原始诊断资料从/mnt/data读取，换机器须调整路径。旧源文件不在本包重复打包；使用此前已交付的基线。
