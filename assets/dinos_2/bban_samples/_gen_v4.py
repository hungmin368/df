#!/usr/bin/env python3
"""Round 7 (v4): color-differentiated 伴伴-family dinos via pollinations/flux.

User's brief: keep the 伴伴 family look (3D render, big golden eyes,
yellow-orange horns/accents, cheerful smile + tiny teeth, creamy white belly,
white background) but make each species instantly recognizable with a
distinct body color:
  triceratops = purple, stegosaurus = green, T-Rex = orange, pteranodon = blue

Gate per species: fraction of colorful pixels inside the target hue band
must exceed THR (body color dominates), overall colorful fraction >= 0.15.
Outputs v4_<name>_s<seed>.png (up to WANT=2 per species).
"""
import colorsys
import os
import subprocess
import time
from urllib.parse import quote

from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
URL = ("https://image.pollinations.ai/prompt/{p}"
       "?width=768&height=768&nologo=true&model=flux&seed={s}")

ANATOMY = {
    "triceratops": (
        "A 3D render of a cute baby Triceratops with vibrant purple scales, "
        "big round golden eyes, three bright yellow-orange horns: two long "
        "brow horns above the eyes pointing up and forward, and one short "
        "nose horn, a huge scalloped bony neck frill rimmed with "
        "yellow-orange, cheerful smile showing tiny teeth, creamy white "
        "belly, four sturdy little legs, standing in a dynamic pose, "
        "high-resolution digital art style, clean white background"
    ),
    "stegosaurus": (
        "A 3D render of a cute baby Stegosaurus with grass-green scales, "
        "big round golden eyes, a single row of large golden kite-shaped "
        "back plates standing upright along the whole back from neck to "
        "tail, four yellow-orange spikes on the tail, cheerful smile "
        "showing tiny teeth, creamy white belly, four chubby legs, side "
        "view walking in a dynamic pose, high-resolution digital art "
        "style, clean white background"
    ),
    "trex": (
        "A 3D render of a cute baby T-Rex with warm orange scales and an "
        "oversized head, big round golden eyes, wide cheerful smile showing "
        "tiny white teeth, creamy white belly, tiny little arms, long thick "
        "tail, standing on two hind legs in a dynamic pose, "
        "high-resolution digital art style, clean white background"
    ),
    "ptero": (
        "A 3D render of a cute baby Pteranodon with sky-blue scales, big "
        "round golden eyes, long yellow-orange toothless beak pointing "
        "forward, tall yellow-orange head crest sweeping backward, soft "
        "wings with pink membranes spread wide, cheerful friendly "
        "expression, creamy white belly, flying in a dynamic pose, "
        "high-resolution digital art style, clean white background"
    ),
}

BANDS = {
    "triceratops": (230, 320),
    "stegosaurus": (70, 170),
    "trex": (5, 45),
    "ptero": (180, 260),
}
THR = 0.20

SEEDS = {
    "triceratops": [10001, 10002, 10003, 10004],
    "stegosaurus": [10101, 10102, 10103, 10104],
    "trex": [10201, 10202, 10203, 10204],
    "ptero": [10301, 10302, 10303, 10304],
}
WANT = 2


def band_stats(path, lo, hi):
    im = Image.open(path).convert("RGB").resize((192, 192))
    px = list(im.getdata())[::5]
    n = 0
    in_band = 0
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s > 0.35 and 0.2 < v < 0.98:
            n += 1
            if lo <= h * 360 <= hi:
                in_band += 1
    frac_colorful = n / len(px)
    frac_band = in_band / len(px)
    return round(frac_colorful, 2), round(frac_band, 2)


def passes(frac_colorful, frac_band):
    return frac_colorful >= 0.15 and frac_band > THR


def fetch(url, out):
    tmp = out + ".part"
    for attempt in range(1, 6):
        r = subprocess.run(
            ["curl", "-sS", "-m", "150", "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True)
        code = r.stdout.strip()
        ok = (code == "200" and os.path.exists(tmp)
              and os.path.getsize(tmp) > 10000)
        if ok:
            os.replace(tmp, out)
            return True
        if os.path.exists(tmp):
            os.remove(tmp)
        wait = 45 if code == "402" else 8
        print(f"    attempt {attempt}: http {code}, wait {wait}s", flush=True)
        time.sleep(wait)
    return False


def main():
    for name, seeds in SEEDS.items():
        prompt = ANATOMY[name]
        lo, hi = BANDS[name]
        print(f"[{name}] {len(seeds)} seeds, want {WANT}, band {lo}-{hi}",
              flush=True)
        got = 0
        for seed in seeds:
            if got >= WANT:
                break
            out = os.path.join(DIR, f"v4_{name}_s{seed}.png")
            if os.path.exists(out):
                fc, fb = band_stats(out, lo, hi)
                if passes(fc, fb):
                    got += 1
                    print(f"[{name}] seed {seed}: existing OK "
                          f"(cf={fc} bf={fb})", flush=True)
                    continue
                os.remove(out)
            print(f"[{name}] seed {seed}: fetching...", flush=True)
            if not fetch(URL.format(p=quote(prompt), s=seed), out):
                print(f"[{name}] seed {seed}: download failed", flush=True)
                continue
            fc, fb = band_stats(out, lo, hi)
            if passes(fc, fb):
                got += 1
                print(f"[{name}] seed {seed}: OK (cf={fc} bf={fb})",
                      flush=True)
            else:
                os.remove(out)
                print(f"[{name}] seed {seed}: reject (cf={fc} bf={fb})",
                      flush=True)
        print(f"[{name}] done: {got}/{WANT}", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
