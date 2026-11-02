# -*- coding: utf-8 -*-
"""v7 方法A：定裝照去背凍結——rembg → 裁透明邊 → _raw/_masters/<name>.png（RGBA）。

用法：python _cut_masters_v7.py [name ...]（無參數=cut _src/ 全部）
"""
import sys
from pathlib import Path
from PIL import Image
from rembg import remove

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
SRC = HERE / "_raw" / "_masters" / "_src"
OUT = HERE / "_raw" / "_masters"

names = sys.argv[1:] or sorted(p.stem for p in SRC.glob("*.png"))
for name in names:
    src = SRC / f"{name}.png"
    if not src.exists():
        print(f"{name}: src missing, skip", flush=True)
        continue
    out = OUT / f"{name}.png"
    if out.exists() and out.stat().st_size > 5000:
        print(f"{name}: exists, skip", flush=True)
        continue
    im = Image.open(src).convert("RGBA")
    cut = remove(im)
    bbox = cut.getbbox()
    if bbox:
        cut = cut.crop(bbox)
    cut.save(out)
    print(f"{name}: cut {im.size} -> {cut.size}", flush=True)

print("CUT_DONE", flush=True)
