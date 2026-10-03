# R39 增量构建与检查

依赖：Python 3、Node（语法检查）、Python playwright与Chromium。检查脚本当前浏览器路径为/usr/bin/chromium，其他系统请在check_r39.py调整该路径。

构建输入必须是完整的已交付R38目录，而不是R37/R37.1。脚本先核对R38标识和GoldFix哈希，复制整包再增加珠宝页面，原始资料不改。输出应使用新建的独立目录；已有输出目录会被重建，不要把后续工作放在该目录后再次直接运行。

```sh
python build_r39.py /path/to/R38 /path/to/new_R39
python check_r39.py /path/to/R38 /path/to/new_R39 /path/to/test_reports
```

构建主体会复现722个站点文件；交付包额外包含本维护目录、最终说明、检查记录和SHA256SUMS_R39.txt。历史R38/R37脚本仅作为档案保留，不可用其直接覆盖R39。

后续正常编辑以交付R39为基线。需要重新生成时应在保留R39之后所有新修改的前提下维护相应增量，而非无差别重放旧补丁。

测试优先尝试真实HTTP/file导航，受阻时记录错误并使用实际HTML/CSS/JS的内存文档；报告写明具体模式。没有游戏实测或用户域名部署能力。
