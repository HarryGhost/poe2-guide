# R41 维护

构建需要Python 3.10+，标准库即可。将完整R40解压到单独目录，运行：

```sh
python build_r41.py --baseline /path/to/R40 --output /path/to/new/R41
```

输出不得等于输入、在输入内或为输入父目录；现有输出目录会清空，务必指定独立可删除目录。输入必须是未叠补的R40。craft41.json和atlas41.json为新增编辑数据；new_data.py为其生成源。

该命令产生777份可重复的站点文件，不包含发布收尾时添加的说明、维护源副本、检查副本与最终校验清单。finalize_r41.py是本次发布环境的收尾脚本，含/mnt/data路径，换机器须先调整目录，不能不看直接执行。

测试需要Node、Python Playwright及Chromium。test_flows41.py、test_scan41.py保留本次/mnt/data/work_R41检查环境路径和/usr/bin/chromium位置；换机器须设置相同工作目录或修改W与浏览器位置。content.json为输入R40数据的提取，build_result.json由构建脚本生成。真实网站部署应另做网络导航检查，内存文档验证不替代上线。

不要覆盖或重新生成任何原版.filter内容。新增Atlas建议另存字段，不得写回作者原图选值。
