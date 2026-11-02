#!/usr/bin/env python
"""Build a labeled contact sheet of v4_*.png candidates for visual review."""
import pathlib

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
CELL = 384
PAD = 8
LABEL = 22

files = sorted(HERE.glob("v4_*.png"))
if not files:
    raise SystemExit("no v4_*.png candidates")

cols = 4
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (CELL + PAD) + PAD, rows * (CELL + LABEL + PAD) + PAD),
                  (245, 242, 238))
draw = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((CELL, CELL), Image.LANCZOS)
    x = PAD + (i % cols) * (CELL + PAD)
    y = PAD + (i // cols) * (CELL + LABEL + PAD)
    sheet.paste(im, (x, y))
    draw.text((x + 2, y + CELL + 4), f.name, fill=(40, 30, 30))
out = HERE / "_sheet_v4.png"
sheet.save(out)
print("sheet:", out, sheet.size, len(files), "cells")
