#!/usr/bin/env python3
"""Round 6c: stegosaurus plates + pteranodon crest, third attempt.

v3b review: stego 7401 came back all spikes / 7402 only tiny nubs — the
iconic double row of large flat plates never rendered. Ptero 7501 is usable
(long beak + pink membranes) but 7502 is a fierce dragon; try a few more
seeds for a friendlier, more Pteranodon-explicit render.

Same gate as _gen_v3.py. Outputs v3_<name>_s<seed>.png.
"""
import colorsys
import math
import os
import subprocess
import time
from urllib.parse import quote

from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
URL = ("https://image.pollinations.ai/prompt/{p}"
       "?width=768&height=768&nologo=true&model=flux&seed={s}")

ANATOMY = {
    "stegosaurus": (
        "Stegosaurus chibi mascot, side profile view, entire body vibrant purple, "
        "classic stegosaurus silhouette: a double row of very large flat "
        "kite-shaped golden bone plates standing tall along the arched back from "
        "neck to tail, tall flat plates like kite-shaped leaves clearly separated "
        "from each other, small head held low near the ground, four sturdy legs, "
        "stiff tail raised with golden spikes"
    ),
    "ptero": (
        "Pteranodon chibi mascot, flying pose, side view, entire body and both "
        "wide bat-like wings vibrant purple with pink wing membranes, both wings "
        "spread wide, long golden toothless beak, very tall golden head crest "
        "sweeping backward from the head, small cute body"
    ),
}

STYLE = (
    "cute chibi 3D vinyl toy render, vibrant purple smooth glossy vinyl skin "
    "like a designer toy, deep purple spots, big round amber orange eyes with "
    "sparkles, cream belly, pink blush cheeks, soft studio lighting, plain "
    "pure white background, centered full body, clear silhouette, designer "
    "mascot character"
)

SEEDS = {
    "stegosaurus": [7601, 7602, 7603, 7604],
    "ptero": [7701, 7702, 7703],
}
WANT = 2


def purple_stats(path):
    im = Image.open(path).convert("RGB").resize((192, 192))
    px = list(im.getdata())[::5]
    xs = ys = 0.0
    n = 0
    purple = 0
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s > 0.35 and 0.2 < v < 0.98:
            n += 1
            a = h * 2 * math.pi
            xs += math.cos(a)
            ys += math.sin(a)
            if 230 <= h * 360 <= 320:
                purple += 1
    frac_colorful = n / len(px)
    frac_purple = purple / len(px)
    if not n:
        return None, round(frac_colorful, 2), round(frac_purple, 2)
    hue = math.degrees(math.atan2(ys, xs)) % 360
    return round(hue, 1), round(frac_colorful, 2), round(frac_purple, 2)


def is_purple(hue, frac_colorful, frac_purple):
    if frac_colorful < 0.15:
        return False
    return (hue is not None and 230 <= hue <= 320) or frac_purple > 0.22


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
        prompt = ANATOMY[name] + ", " + STYLE
        print(f"[{name}] {len(seeds)} seeds, want {WANT}", flush=True)
        got = 0
        for seed in seeds:
            if got >= WANT:
                break
            out = os.path.join(DIR, f"v3_{name}_s{seed}.png")
            if os.path.exists(out):
                hue, fc, fp = purple_stats(out)
                if is_purple(hue, fc, fp):
                    got += 1
                    print(f"[{name}] seed {seed}: existing OK "
                          f"(hue={hue} cf={fc} pf={fp})", flush=True)
                    continue
                os.remove(out)
            print(f"[{name}] seed {seed}: fetching...", flush=True)
            if not fetch(URL.format(p=quote(prompt), s=seed), out):
                print(f"[{name}] seed {seed}: download failed", flush=True)
                continue
            hue, fc, fp = purple_stats(out)
            if is_purple(hue, fc, fp):
                got += 1
                print(f"[{name}] seed {seed}: OK "
                      f"(hue={hue} cf={fc} pf={fp})", flush=True)
            else:
                os.remove(out)
                print(f"[{name}] seed {seed}: reject "
                      f"(hue={hue} cf={fc} pf={fp})", flush=True)
        print(f"[{name}] done: {got}/{WANT}", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
