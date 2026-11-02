#!/usr/bin/env python3
"""Round 7b (v4b): re-roll the two failed v4 species with cutout-based gating.

Failures being fixed:
- v4 ptero s10303: golden-yellow feathered bird on blue SKY — the sky pixels
  passed the blue band gate. Fix: gate on rembg cutout pixels only (alpha>200),
  plus prompts force a plain white studio background (no sky).
- v4 triceratops s10004: cute purple dragon (floppy ears, no frill, no horns).
  Fix: anatomy-first prompt (quadruped walk, big shield frill, three horns,
  no wings, no ears), keep purple.

Accepted outputs are promoted to v4_<name>_s<seed>.png (replacing rejected
earlier files of the same name is fine — none of this round's earlier ptero/
tri files survived review anyway).
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

PROMPTS = {
    "ptero": (
        "A 3D render of a cute baby Pteranodon reptile, the entire body and "
        "both wide bat-like wings are vivid cobalt blue with pink wing "
        "membranes, big round golden eyes, long yellow-orange toothless "
        "pointed beak, tall yellow-orange head crest sweeping backward, "
        "creamy white belly, flying with wings spread, isolated on a plain "
        "pure white studio background, no sky, no clouds, no landscape, "
        "high-resolution digital art style"
    ),
    "triceratops": (
        "A 3D render of a cute chibi baby Triceratops dinosaur walking on "
        "all four legs, entire body vibrant purple scales, big round golden "
        "eyes, a huge scalloped bony neck frill fanning out behind the head "
        "like a wide shield rimmed with yellow-orange, three bright "
        "yellow-orange horns: two long brow horns above the eyes and one "
        "short nose horn on the snout, cheerful smile showing tiny teeth, "
        "creamy white belly, no wings, no ears, isolated on a plain pure "
        "white studio background, high-resolution digital art style"
    ),
}

BANDS = {
    "ptero": (180, 260),
    "triceratops": (230, 320),
}
THR = 0.20

SEEDS = {
    "ptero": [10311, 10312, 10313, 10314, 10315, 10316],
    "triceratops": [10011, 10012, 10013, 10014, 10015, 10016],
}
WANT = 2


def cutout_band_stats(data, lo, hi):
    """Measure hue stats on the rembg cutout (opaque pixels) only."""
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    im = im.resize((256, 256))
    px = list(im.getdata())
    opaque = [(r, g, b) for r, g, b, a in px if a > 200]
    if not opaque:
        return 0.0, 0.0
    n = 0
    in_band = 0
    for r, g, b in opaque:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s > 0.35 and 0.2 < v < 0.98:
            n += 1
            if lo <= h * 360 <= hi:
                in_band += 1
    total = len(opaque)
    frac_opaque = total / len(px)
    frac_colorful = n / total
    frac_band = in_band / total
    return frac_opaque, frac_colorful, frac_band


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
    for name, seeds in SEEDS.items():
        lo, hi = BANDS[name]
        print(f"[{name}] {len(seeds)} seeds, want {WANT}, band {lo}-{hi} "
              f"(cutout-gated)", flush=True)
        got = 0
        for seed in seeds:
            if got >= WANT:
                break
            out = os.path.join(DIR, f"v4_{name}_s{seed}.png")
            if os.path.exists(out):
                data = rembg.remove(out.read_bytes())
                fo, fc, fb = cutout_band_stats(data, lo, hi)
                if passes(fo, fc, fb):
                    got += 1
                    print(f"[{name}] seed {seed}: existing OK "
                          f"(fo={fo} cf={fc} bf={fb})", flush=True)
                    continue
                os.remove(out)
                print(f"[{name}] seed {seed}: existing reject, removed",
                      flush=True)
            tmp = os.path.join(DIR, f"v4_{name}_s{seed}.png.part")
            print(f"[{name}] seed {seed}: fetching...", flush=True)
            if not fetch(URL.format(p=quote(PROMPTS[name]), s=seed), tmp):
                print(f"[{name}] seed {seed}: download failed", flush=True)
                continue
            data = open(tmp, "rb").read()
            cut = rembg.remove(data)
            fo, fc, fb = cutout_band_stats(cut, lo, hi)
            if passes(fo, fc, fb):
                os.replace(tmp, out)
                got += 1
                print(f"[{name}] seed {seed}: OK "
                      f"(fo={fo} cf={fc} bf={fb})", flush=True)
            else:
                os.remove(tmp)
                print(f"[{name}] seed {seed}: reject "
                      f"(fo={fo} cf={fc} bf={fb})", flush=True)
        print(f"[{name}] done: {got}/{WANT}", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
