#!/usr/bin/env python
"""Post-process chosen v3 winner renders into game-ready tiles.

Usage: python _post_v3.py v3_triceratops_s7001 v3_stegosaurus_s7101 ...

Targets are passed explicitly on the command line (never a glob), so
parallel-session candidate files can't be picked up by accident.
Outputs per target: <stem>_rgba.png, <stem>_512.png, <stem>.webp
"""
import pathlib
import sys

import rembg
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent


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
    stems = sys.argv[1:]
    if not stems:
        raise SystemExit("usage: _post_v3.py <stem> [<stem> ...]")
    for stem in stems:
        src = HERE / f"{stem}.png"
        if not src.exists():
            raise SystemExit(f"missing source: {src}")
        cut = rembg.remove(src.read_bytes())
        (HERE / f"{stem}_rgba.png").write_bytes(cut)
        im = Image.open(HERE / f"{stem}_rgba.png").convert("RGBA")
        master = trim_center(im).resize((512, 512), Image.LANCZOS)
        master.save(HERE / f"{stem}_512.png")
        master.resize((200, 200), Image.LANCZOS).save(
            HERE / f"{stem}.webp", "WEBP", quality=90)
        print(stem, "webp:", (HERE / f"{stem}.webp").stat().st_size // 1024,
              "KB", flush=True)
    print("POST_V3_DONE", flush=True)


if __name__ == "__main__":
    main()
