# R38维护入口

本轮是直接在已取回R37.1工程上增量生成，不调用旧R37生成器。

生成网站：

```text
python build_r38.py /路径/网站_R37_1 /路径/新R38目录
```

必须使用不同且互不嵌套的基线与输出目录。脚本拒绝直接覆盖基线，并核对R37.1版本及GoldFix哈希。已存在输出目录会被清空后重新生成，请专门指定一个输出目录。

四个生成输入：build_r38.py、new_content.py、additions.js、additions.css。用户原BD、过滤器与R28原站作为基线被完整复制，不从外网获取，不修改原始连接。

check_r38.py和smoke.py是此次检查脚本，开头的W/B/O路径与Chromium路径对应本次容器；跨机器复跑时调整这些路径。new_content.py的apply负责作者原件之外的中文补充，不覆盖原始routes、gems或branches。

检查说明、截图、哈希清单的归档打包属于交付步骤，不是网站运行所需。直接生成可使用的网站与清单不要求Playwright或Node。
