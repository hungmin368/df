# -*- coding: utf-8 -*-
"""為每個角色產生全部定裝並排 montage（_qc_m/<key>.jpg），供逐角色一致性 QC。"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).parent
CUT = HERE / "_raw" / "_masters"
SRC = CUT / "_src"
OUT = HERE / "_qc_m"
OUT.mkdir(exist_ok=True)

KEYS = {"雷恩": "rainer", "伴伴": "banban", "薩爾塔龍": "saltas", "格雷": "grey", "雷鐸": "grand"}

data = json.loads((HERE / "_cast_manifest.json").read_text(encoding="utf-8"))
by_char = {}
for row in data["cast"]:
    by_char.setdefault(row["char"], []).append(row["file"])

for char, files in by_char.items():
    key = KEYS.get(char, char)
    ims = []
    for f in files:
        p = CUT / f"{f}.png"
        if not p.exists():
            p = SRC / f"{f}.png"
        if not p.exists():
            continue
        ims.append(Image.open(p).convert("RGBA"))
    if not ims:
        continue
    H = 300
    ims = [im.resize((max(1, int(im.width * H / im.height)), H)) for im in ims]
    W = sum(im.width for im in ims) + 8 * (len(ims) + 1)
    out = Image.new("RGB", (W, H + 16), (240, 240, 240))
    x = 8
    for im in ims:
        out.paste(im, (x, 8), im)
        x += im.width + 8
    out.save(OUT / f"{key}.jpg", quality=85)
    print(f"{key}: {len(ims)} imgs")
print("MONTAGE_DONE")
