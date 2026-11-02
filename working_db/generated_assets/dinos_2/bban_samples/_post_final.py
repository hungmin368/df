#!/usr/bin/env python
"""Post-process the four final AI samples into game-ready tiles.

Explicit target list (not a glob): parallel candidate files such as
ai_300_ptero_s<seed>.png from other tooling must not be picked up.
Same ops as _post_ai.py: rembg -> RGBA -> trim/center -> 512 master + 200x200 webp.
"""
import pathlib

import rembg
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
TARGETS = ["ai_21_triceratops", "ai_11_stegosaurus", "ai_260_trex", "ai_300_ptero"]


def trim_center(im: Image.Image, margin_frac: float = 0.04) -> Image.Image:
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("empty alpha")
    im = im.crop(bbox)
    side = max(im.size)
    margin = int(side * margin_frac)
    canvas = Image.new("RGBA", (side + margin * 2,) * 2, (0, 0, 0, 0))
    canvas.paste(im, ((canvas.width - im.width) // 2, (canvas.height - im.height) // 2), im)
    return canvas


def main() -> None:
    for stem in TARGETS:
        cut = rembg.remove((HERE / f"{stem}.png").read_bytes())
        (HERE / f"{stem}_rgba.png").write_bytes(cut)
        im = Image.open(HERE / f"{stem}_rgba.png").convert("RGBA")
        master = trim_center(im).resize((512, 512), Image.LANCZOS)
        master.save(HERE / f"{stem}_512.png")
        master.resize((200, 200), Image.LANCZOS).save(
            HERE / f"{stem}.webp", "WEBP", quality=90)
        print(stem, "webp:", (HERE / f"{stem}.webp").stat().st_size // 1024,
              "KB", flush=True)
    print("POST_FINAL_DONE", flush=True)


if __name__ == "__main__":
    main()
