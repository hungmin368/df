#!/usr/bin/env python
"""Post-process gemini_styleA_stegosaurus.png into a game-ready tile.

Pipeline per AGENTS.md Style A recipe + batch spec element 1 (bottom-anchored):
rembg -> RGBA -> trim -> square canvas, horizontal center, bottom margin 4%
-> 512x512 RGBA master -> 512x512 RGBA WebP q90.
"""
import pathlib

import rembg
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
STEM = "gemini_styleA_stegosaurus"
MARGIN_FRAC = 0.04


def trim_bottom_anchor(im: Image.Image) -> Image.Image:
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("empty alpha")
    im = im.crop(bbox)
    side = max(im.size)
    margin = int(side * MARGIN_FRAC)
    canvas = Image.new("RGBA", (side + margin * 2,) * 2, (0, 0, 0, 0))
    x = (canvas.width - im.width) // 2
    y = canvas.height - im.height - margin
    canvas.paste(im, (x, y), im)
    return canvas


def main() -> None:
    cut = rembg.remove((HERE / f"{STEM}.png").read_bytes())
    (HERE / f"{STEM}_rgba.png").write_bytes(cut)
    im = Image.open(HERE / f"{STEM}_rgba.png").convert("RGBA")
    master = trim_bottom_anchor(im).resize((512, 512), Image.LANCZOS)
    master.save(HERE / f"{STEM}_512.png")
    master.save(HERE / f"{STEM}_512.webp", "WEBP", quality=90)
    print("webp KB:", (HERE / f"{STEM}_512.webp").stat().st_size // 1024, flush=True)
    print("POST_DONE", flush=True)


if __name__ == "__main__":
    main()
