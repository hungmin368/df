#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_dist.py — 恐龍快找出貨包產生器（一次性維護工具）

只複製遊戲實際需要的檔案到 dist/，排除素材工作區（assets/dinos_2/）、
備份檔（*.bak*）、暫存腳本與報告。執行後會逐一核對 index.html/css/js
內的 assets/ 引用在 dist 中是否存在。
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

COPY_FILES = [
    "index.html",
    "manifest.webmanifest",
    "sw.js",
]
COPY_DIRS = [
    "css",
    "assets/fonts",
    "assets/dinos",
    "assets/story",
    "assets/icons",
]
SINGLE_ASSETS = [
    "assets/cursor.png",
    "assets/map.png",
    "assets/game.mp4",
    "assets/story_lv4_720p.mp4",
    "assets/dinos_2/game_logo.png",
]
JS_FILES = ["data.js", "tower.js", "main.js", "tower_comments.js", "ads.js"]


def clean():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)


def copy_file(rel):
    src = os.path.join(ROOT, rel)
    dst = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def copy_dir(rel, skip_ext=None):
    src = os.path.join(ROOT, rel)
    dst = os.path.join(DIST, rel)
    for base, _dirs, files in os.walk(src):
        for f in files:
            if skip_ext and f.endswith(skip_ext):
                continue
            if ".bak" in f:
                continue
            s = os.path.join(base, f)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)


def collect_references():
    """收集 index.html / css / js 內所有 assets/ 引用路徑。"""
    refs = set()
    re_path = re.compile(r"assets/[A-Za-z0-9_\-./]+?\.(?:webp|png|jpg|svg|woff2|mp4|ico)")
    sources = [os.path.join(ROOT, "index.html")]
    sources += [
        os.path.join(ROOT, "css", f)
        for f in os.listdir(os.path.join(ROOT, "css"))
        if f.endswith(".css")
    ]
    sources += [os.path.join(ROOT, "js", f) for f in JS_FILES if f != "ads.js"]
    for p in sources:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for m in re_path.findall(fh.read()):
                refs.add(m)
    return refs


def main():
    clean()
    for f in COPY_FILES:
        copy_file(f)
    copy_file("css/fonts.css")
    copy_file("css/style.css")
    for j in JS_FILES:
        copy_file(os.path.join("js", j))
    for d in COPY_DIRS:
        copy_dir(d)
    for a in SINGLE_ASSETS:
        copy_file(a)

    # 核對所有 assets/ 引用
    refs = collect_references()
    missing = [r for r in sorted(refs) if not os.path.exists(os.path.join(DIST, r))]
    if "assets/icons/favicon.ico" in refs and not os.path.exists(os.path.join(DIST, "assets/icons/favicon.ico")):
        missing.append("assets/icons/favicon.ico")

    total = 0
    count = 0
    for base, _dirs, files in os.walk(DIST):
        for f in files:
            count += 1
            total += os.path.getsize(os.path.join(base, f))

    print(f"dist 檔案數：{count}")
    print(f"dist 總大小：{total/1024/1024:.1f} MB")
    if missing:
        print("!! 引用缺檔：")
        for m in missing:
            print("   -", m)
        sys.exit(1)
    print("所有 assets/ 引用皆已包含 [OK]")


if __name__ == "__main__":
    main()
