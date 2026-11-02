# -*- coding: utf-8 -*-
"""Post-process the Gemini chest raws into game-ready transparent WebP icons.

rembg -> trim alpha -> square canvas with 6% margin -> 512px master + 256px webp.
"""
from pathlib import Path

import rembg
from PIL import Image

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"
MASTER = HERE / "_master"
TIERS = ["iron", "gold", "plat"]
MARGIN_FRAC = 0.06


def trim_center(im: Image.Image) -> Image.Image:
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("empty alpha")
    im = im.crop(bbox)
    side = max(im.size)
    margin = int(side * MARGIN_FRAC)
    canvas = Image.new("RGBA", (side + margin * 2,) * 2, (0, 0, 0, 0))
    canvas.paste(im, ((canvas.width - im.width) // 2, (canvas.height - im.height) // 2), im)
    return canvas


def main() -> None:
    MASTER.mkdir(exist_ok=True)
    for tier in TIERS:
        cut = rembg.remove((RAW / f"{tier}_raw.png").read_bytes())
        tmp = RAW / f"{tier}_rgba.png"
        tmp.write_bytes(cut)
        im = Image.open(tmp).convert("RGBA")
        master = trim_center(im).resize((512, 512), Image.LANCZOS)
        master.save(MASTER / f"{tier}_512.png")
        icon = master.resize((256, 256), Image.LANCZOS)
        out = HERE / f"{tier}.webp"
        icon.save(out, "WEBP", quality=92, method=6)
        a = master.getchannel("A")
        opaque = sum(1 for v in a.getdata() if v > 200) / (512 * 512)
        print(f"{tier}: {out.name} {out.stat().st_size // 1024} KB, opaque {opaque:.2%}", flush=True)
    print("POST_CHESTS_DONE", flush=True)


if __name__ == "__main__":
    main()
