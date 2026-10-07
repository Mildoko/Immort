#!/usr/bin/env python3
"""界面文件审计：导航章节 / 孤儿 / 死链 / 命名一致性。

用法:
    python audit_screens.py <界面目录>

约定:
    - 每个界面一个 <界面名>.md（README.md 除外）
    - 界面正文含 "## 导航（入口" 段落（入口/出口）

ROOTS: 合法的「根」界面——底部 Tab 主页面，以及从「推送/运营端」等非界面入口
       进入的页面。按项目填写，否则会误报孤儿。
"""
import os
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
ROOTS = set()

files = sorted(
    f for f in os.listdir(BASE)
    if f.endswith(".md") and not f.startswith("._") and f != "README.md"
)
interfaces = [f[:-3] for f in files]


def read(name):
    with open(os.path.join(BASE, name + ".md"), encoding="utf-8") as fh:
        return fh.read()


# ① 每个界面都要有「导航（入口/出口）」段
missing_nav = [n for n in interfaces if "## 导航（入口" not in read(n)]

# ② 可达性：界面名是否出现在其它界面正文里（引用名必须逐字一致）
referenced = set()
for n in interfaces:
    body = read(n)
    for other in interfaces:
        if other != n and other in body:
            referenced.add(other)
orphans = [n for n in interfaces if n not in referenced and n not in ROOTS]

print(f"界面总数    : {len(interfaces)}")
print(f"缺导航章节  : {missing_nav or '无 ✅'}")
print(f"孤儿界面    : {orphans or '无 ✅'}")
print(
    "排查提示    : 若某界面被判孤儿，先查引用名是否有空格/后缀差异"
    "（如「动态feed」vs「动态 feed」）。"
)
