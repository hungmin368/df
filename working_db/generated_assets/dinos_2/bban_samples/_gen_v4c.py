#!/usr/bin/env python3
"""Round 7c (v4c): frill-first triceratops re-rolls.

Best tri so far (v4 s10012) has three horns + quadruped walk but no clear
neck frill. The frill is THE defining triceratops feature, so this focused
round leads with it. Cutout-based purple gate as in _gen_v4b.py.
"""
import colorsys
import io
import os
import subprocess
import time
from urllib.parse import quote

import rembg
from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
URL = ("https://image.pollinations.ai/prompt/{p}"
       "?width=768&height=768&nologo=true&model=flux&seed={s}")

PROMPT = (
    "A 3D render of a cute baby Triceratops: the huge round bony neck frill "
    "is the most prominent feature, a wide scalloped shield fanning out "
    "behind the head like a lion's mane, golden-yellow with a purple "
    "center, three bright golden horns (two long ones above the eyes and "
    "one on the nose), the rest of the body vibrant purple, big round "
    "amber eyes, cheerful smile with tiny teeth, creamy white belly, "
    "walking on four legs side view, isolated on a plain pure white "
    "background, high-resolution digital art style"
)

LO, HI = 230, 320
THR = 0.20
SEEDS = [10021, 10022, 10023, 10024, 10025, 10026]
WANT = 2


def cutout_band_stats(data):
    im = Image.open(io.BytesIO(data)).convert("RGBA").resize((256, 256))
    px = list(im.getdata())
    opaque = [(r, g, b) for r, g, b, a in px if a > 200]
    if not opaque:
        return 0.0, 0.0, 0.0
    n = 0
    in_band = 0
    for r, g, b in opaque:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s > 0.35 and 0.2 < v < 0.98:
            n += 1
            if LO <= h * 360 <= HI:
                in_band += 1
    total = len(opaque)
    return total / len(px), n / total, in_band / total


def passes(fo, fc, fb):
    return fo > 0.10 and fc >= 0.15 and fb > THR


def fetch(url, tmp):
    for attempt in range(1, 6):
        r = subprocess.run(
            ["curl", "-sS", "-m", "150", "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True)
        code = r.stdout.strip()
        ok = (code == "200" and os.path.exists(tmp)
              and os.path.getsize(tmp) > 10000)
        if ok:
            return True
        if os.path.exists(tmp):
            os.remove(tmp)
        wait = 45 if code == "402" else 8
        print(f"    attempt {attempt}: http {code}, wait {wait}s", flush=True)
        time.sleep(wait)
    return False


def main():
    print(f"[triceratops] {len(SEEDS)} seeds, want {WANT} (frill-first, "
          f"cutout-gated)", flush=True)
    got = 0
    for seed in SEEDS:
        if got >= WANT:
            break
        out = os.path.join(DIR, f"v4_triceratops_s{seed}.png")
        if os.path.exists(out):
            data = rembg.remove(out.read_bytes())
            fo, fc, fb = cutout_band_stats(data)
            if passes(fo, fc, fb):
                got += 1
                print(f"seed {seed}: existing OK ({fo:.2f} {fc:.2f} {fb:.2f})",
                      flush=True)
                continue
            os.remove(out)
            print(f"seed {seed}: existing reject, removed", flush=True)
        tmp = out + ".part"
        print(f"seed {seed}: fetching...", flush=True)
        if not fetch(URL.format(p=quote(PROMPT), s=seed), tmp):
            print(f"seed {seed}: download failed", flush=True)
            continue
        cut = rembg.remove(open(tmp, "rb").read())
        fo, fc, fb = cutout_band_stats(cut)
        if passes(fo, fc, fb):
            os.replace(tmp, out)
            got += 1
            print(f"seed {seed}: OK ({fo:.2f} {fc:.2f} {fb:.2f})", flush=True)
        else:
            os.remove(tmp)
            print(f"seed {seed}: reject ({fo:.2f} {fc:.2f} {fb:.2f})",
                  flush=True)
    print(f"[triceratops] done: {got}/{WANT}", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
