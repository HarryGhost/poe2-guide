# 重建 R40

Python3标准库即可生成：

```sh
python build_r40.py --base /path/to/R39 --out /path/to/new_R40
```

必须输入完整R39，输出新目录。基础业务数据和旧资源保留，新界面以新的哈希文件名引用。
浏览器检查另需 playwright、Chromium；检查脚本的路径按本机修改。原包历史检查不等于本轮重跑。
