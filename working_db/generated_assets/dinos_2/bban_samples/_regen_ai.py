#!/usr/bin/env python
"""Regenerate species that fail the purple-check with better prompts.

For each target, iterate seeds until the central region's mean hue is purple
(~250-300 deg) and colorful enough, or attempts run out.
"""
import colorsys
import pathlib
import subprocess
import sys
import time
import urllib.parse

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent

STYLE = (", friendly kawaii happy face with a closed smile, "
         "cream colored belly, tiny fangs, "
         "chibi 3D vinyl toy render, soft studio lighting, "
         "plain white background, centered full body")

SPECIES = {
    "ai_21_triceratops": (
        "vibrant purple baby triceratops dinosaur, smooth glossy purple vinyl skin, "
        "large round purple frill with pink inner membrane behind its head, "
        "three golden horns two above the eyes one on the nose, "
        "big round amber orange eyes, chubby quadruped on four short legs", 21),
    "ai_11_stegosaurus": (
        "vibrant purple baby stegosaurus dinosaur, smooth glossy purple vinyl skin, "
        "two rows of golden plates along its back, four golden spikes on tail tip, "
        "big round amber orange eyes, small cute head, chubby quadruped on four legs", 11),
    "ai_260_trex": (
        "vibrant purple baby tyrannosaurus rex, smooth glossy purple vinyl skin, "
        "huge cute head, two small golden horns above amber eyes, "
        "two tiny arms, strong hind legs, long thick tail, standing upright", 260),
    "ai_300_ptero": (
        "vibrant purple baby pterodactyl, smooth glossy purple vinyl skin, "
        "huge pink wings spread wide, long golden beak, golden head crest, "
        "big round amber orange eyes, small body standing", 300),
}


def fetch(prompt: str, seed: int, out: pathlib.Path) -> bool:
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?width=768&height=768&nologo=true&model=flux&seed={seed}")
    r = subprocess.run(["curl", "-sL", "--max-time", "180", "-o", str(out), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    return r.stdout.strip() == "200" and out.exists() and out.stat().st_size > 20000


def purple_score(path: pathlib.Path):
    im = Image.open(path).convert("RGB").resize((256, 256))
    px = list(im.getdata())
    import math
    hues = []
    for r, g, b in px[::5]:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s > 0.35 and 0.2 < v < 0.98:
            hues.append(h * 360)
    if len(hues) < 200:
        return 0, 0, 0
    # circular mean hue of the colorful (character) pixels
    sin = sum(math.sin(math.radians(h)) for h in hues) / len(hues)
    cos = sum(math.cos(math.radians(h)) for h in hues) / len(hues)
    hue = math.degrees(math.atan2(sin, cos)) % 360
    return hue, len(hues) / (len(px) / 5), 0


def is_purple(path: pathlib.Path) -> bool:
    hue, frac, _ = purple_score(path)
    ok = 235 <= hue <= 315 and frac > 0.15
    print(f"  hue={hue:.0f} colorful={frac:.2f} -> {'OK' if ok else 'retry'}", flush=True)
    return ok


def main() -> int:
    only = sys.argv[1:] or list(SPECIES)
    for name in only:
        prompt, base_seed = SPECIES[name]
        done = False
        for i in range(6):
            seed = base_seed + i * 1000
            out = HERE / f"{name}.png"
            if not fetch(prompt + STYLE, seed, out):
                print(f"[gen] {name} seed {seed}: http fail", flush=True)
                out.unlink(missing_ok=True)
                time.sleep(50)
                continue
            print(f"[gen] {name} seed {seed} downloaded", flush=True)
            if is_purple(out):
                done = True
                break
            out.unlink()
            time.sleep(20)
        if not done:
            print(f"[gen] {name}: no purple result after retries", flush=True)
            return 1
        time.sleep(15)
    print("REGEN_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
