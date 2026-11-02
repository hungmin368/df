#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_dist.py — 恐龍快找出貨包產生器（一次性維護工具）

以 game_db/ 為唯一來源，完整複製到 working_db/builds/dist/，
再核對 index.html、css、js、manifest 內的執行期引用是否都存在。
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "game_db")
DIST = os.path.join(ROOT, "working_db", "builds", "dist")

REF_RE = re.compile(r"(?:assets|css|js)/[A-Za-z0-9_\-./]+?\.(?:webp|png|jpg|jpeg|svg|woff2|mp4|ico)")


def clean():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.dirname(DIST), exist_ok=True)


def collect_references():
    refs = set()
    sources = [os.path.join(DIST, "index.html")]
    for sub in ("css", "js"):
        d = os.path.join(DIST, sub)
        if os.path.isdir(d):
            sources += [os.path.join(d, f) for f in os.listdir(d) if f.endswith((".css", ".js"))]
    for p in sources:
        with open(p, encoding="utf-8") as fh:
            refs.update(REF_RE.findall(fh.read()))
    manifest = os.path.join(DIST, "manifest.webmanifest")
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as fh:
            data = json.load(fh)
        for icon in data.get("icons", []):
            if icon.get("src"):
                refs.add(icon["src"])
    return refs


def main():
    if not os.path.isdir(SRC):
        print(f"!! 找不到來源目錄：{SRC}")
        sys.exit(1)
    clean()
    shutil.copytree(
        SRC,
        DIST,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.bak*"),
    )

    missing = [r for r in sorted(collect_references())
               if not os.path.exists(os.path.join(DIST, r))]

    total = 0
    count = 0
    for base, _dirs, files in os.walk(DIST):
        for f in files:
            count += 1
            total += os.path.getsize(os.path.join(base, f))

    print(f"dist 檔案數：{count}")
    print(f"dist 總大小：{total / 1024 / 1024:.1f} MB")
    if missing:
        print("!! 引用缺檔：")
        for m in missing:
            print("   -", m)
        sys.exit(1)
    print("所有執行期引用皆已包含 [OK]")


if __name__ == "__main__":
    main()
