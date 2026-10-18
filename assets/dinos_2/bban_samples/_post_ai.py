import glob
import os
import pathlib

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
    for png in sorted(glob.glob(str(HERE / "ai_*.png"))):
        stem = pathlib.Path(png).stem
        with open(png, "rb") as f:
            cut = rembg.remove(f.read())
        raw_path = HERE / f"{stem}_rgba.png"
        raw_path.write_bytes(cut)
        im = Image.open(raw_path).convert("RGBA")
        square = trim_center(im)
        master = square.resize((512, 512), Image.LANCZOS)
        master.save(HERE / f"{stem}_512.png")
        master.resize((200, 200), Image.LANCZOS).save(
            HERE / f"{stem}.webp", "WEBP", quality=90)
        print(stem, "512:", os.path.getsize(HERE / f"{stem}_512.png") // 1024, "KB",
              "webp:", os.path.getsize(HERE / f"{stem}.webp") // 1024, "KB", flush=True)
    print("POST_DONE", flush=True)


if __name__ == "__main__":
    main()
