#!/usr/bin/env python3
"""Round 5 (v3): recognizability-first prompts.

User feedback on v2: the four dinos read as generic purple blobs. v3 front-loads
species anatomy (silhouette-defining features) BEFORE the BanBan material words,
uses side/profile views so the silhouette reads, and keeps the purple identity gate.

Generates up to 2 purple-gated candidates per species (768x768) as
v3_<name>_s<seed>.png. Files are written via .part + replace, and targets are
explicit (no globs) so a parallel session's files are never touched.
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
    "triceratops": (
        "Triceratops chibi mascot, side three-quarter view, "
        "huge scalloped bone frill fanning out behind the head like a wide shield, "
        "three long golden horns with two brow horns pointing up and forward and one "
        "short nose horn, parrot-like beak, four sturdy legs"
    ),
    "stegosaurus": (
        "Stegosaurus chibi mascot, side profile view, "
        "two neat rows of large flat golden leaf-shaped plates standing along the "
        "arched back, flat plates not spikes, small head held low, "
        "stiff tail ending in four golden spikes"
    ),
    "trex": (
        "Tyrannosaurus rex chibi mascot, side profile view, "
        "enormous head almost half the body, wide open grinning mouth full of white "
        "fangs, comically tiny two-fingered arms on the chest, thick powerful hind "
        "legs, long heavy tail"
    ),
    "ptero": (
        "Pteranodon chibi mascot, side view, "
        "large leathery bat-like wings spread wide, long golden pointed beak, "
        "tall golden head crest sweeping backward, small body"
    ),
}

STYLE = (
    "cute chibi 3D vinyl toy render, body of smooth glossy purple vinyl like a "
    "designer toy, deep purple spots, big round amber orange eyes with sparkles, "
    "cream belly, pink blush cheeks, soft studio lighting, plain pure white "
    "background, centered full body, clear silhouette, designer mascot character"
)

SEEDS = {
    "triceratops": [7001, 7002, 7003, 7004],
    "stegosaurus": [7101, 7102, 7103, 7104],
    "trex": [7201, 7202, 7203, 7204],
    "ptero": [7301, 7302, 7303, 7304],
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
    # main hue in purple band (230-320) OR enough purple area (gold plates/beak
    # can pull the circular mean, so area of purple is the tiebreaker)
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
