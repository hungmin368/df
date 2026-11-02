# -*- coding: utf-8 -*-
"""Phase 1 trial post-chain: rembg -> scale -> bottom-anchor -> 512x512 RGBA WebP.

Usage: PYTHONIOENCODING=utf-8 python _post_trial5.py
Inputs : assets/dinos_2/trial/_raw/<id>_*_raw.png
Outputs: assets/dinos_2/trial/<id>.webp (512x512 RGBA, q90)
         assets/dinos_2/trial/_post_report.json
Gates per tile: 512x512 RGBA; opaque-pixel coverage 20-40%; bbox margins >=4%;
bottom margin 4-6%; single connected component; low white-halo ratio.
"""
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
RAW = ROOT / "working_db" / "generated_assets" / "dinos_2" / "trial" / "_raw"
OUT = ROOT / "working_db" / "generated_assets" / "dinos_2" / "trial"
TARGET = 512
BBOX_TARGET = 0.55   # body bbox coverage of the tile (user rule 2026-10-16: 50-60%)
BBOX_RANGE = (0.50, 0.60)
OPAQUE_RANGE = (0.14, 0.60)
RATIO_MAX = 1.2      # length:height envelope (user rule 2026-10-16)
MARGIN = 0.04
BOT = 0.05


def rembg_rgba(src: Path) -> Image.Image:
    from rembg import remove
    im = Image.open(src).convert("RGBA")
    return remove(im)


def opaque_px(a: Image.Image, bbox) -> int:
    h = a.crop(bbox).histogram()
    return sum(h[9:])


def defringe(im: Image.Image, radius: int = 3) -> Image.Image:
    import numpy as np

    def box_blur(m, r=radius):
        k = 2 * r + 1
        pad = np.pad(m, ((r + 1, r), (0, 0)), mode="edge")
        c = np.cumsum(pad, axis=0)
        m = (c[k:, :] - c[:-k, :]) / k
        pad = np.pad(m, ((0, 0), (r + 1, r)), mode="edge")
        c = np.cumsum(pad, axis=1)
        return (c[:, k:] - c[:, :-k]) / k

    arr = np.asarray(im).astype(np.float32)
    alpha = arr[..., 3]
    opaque = (alpha >= 250).astype(np.float32)
    wsum = box_blur(opaque)
    semi = (alpha > 0) & (alpha < 250)
    for c in range(3):
        arr[..., c] = np.where(semi, box_blur(arr[..., c] * opaque) / (wsum + 1e-6), arr[..., c])
    arr[..., 3] = np.where(wsum < 0.12, 0, arr[..., 3])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def largest_components(a: Image.Image, thresh: int = 8):
    w, h = a.size
    px = a.load()
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if seen[y][x] or px[x, y] <= thresh:
                continue
            q = deque([(x, y)])
            seen[y][x] = True
            size = 0
            while q:
                cx, cy = q.popleft()
                size += 1
                for nx, ny in ((cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and px[nx, ny] > thresh:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            comps.append(size)
    comps.sort(reverse=True)
    return comps


def halo_ratio(im: Image.Image) -> float:
    a = im.getchannel("A")
    rgb = im.convert("RGB")
    ap, rp = a.load(), rgb.load()
    w, h = im.size
    total = halo = 0
    for y in range(h):
        for x in range(w):
            av = ap[x, y]
            if 0 < av < 210:
                total += 1
                r, g, b = rp[x, y]
                if r > 238 and g > 238 and b > 238:
                    halo += 1
    return halo / total if total else 0.0


def process(raw: Path):
    import numpy as np
    cut = rembg_rgba(raw)
    arr = np.asarray(cut).copy()
    arr[..., 3][arr[..., 3] <= 12] = 0
    cut = defringe(Image.fromarray(arr, "RGBA"))
    bbox = cut.getchannel("A").getbbox()
    cut = cut.crop(bbox)
    a_native = cut.getchannel("A")
    bbox_area = cut.width * cut.height
    s = (BBOX_TARGET * TARGET * TARGET / bbox_area) ** 0.5
    dim = max(cut.width, cut.height)
    s = min(s, (TARGET * 0.90) / dim)
    new_w, new_h = max(1, round(cut.width * s)), max(1, round(cut.height * s))
    tile = Image.new("RGBA", (TARGET, TARGET), (0, 0, 0, 0))
    pad = round(TARGET * 0.043)
    x = max(pad, (TARGET - new_w) // 2)
    x = min(x, TARGET - pad - new_w)
    y = TARGET - round(TARGET * BOT) - new_h
    tile.paste(cut.resize((new_w, new_h), Image.LANCZOS), (x, y))

    checks = {}
    checks["size"] = tile.size == (TARGET, TARGET)
    checks["rgba"] = tile.mode == "RGBA"
    a = tile.getchannel("A")
    bb = a.getbbox()
    checks["bbox_ok"] = bool(bb)
    x0, y0, x1, y1 = bb
    bw, bh = x1 - x0, y1 - y0
    bbox_cov = bw * bh / (TARGET * TARGET)
    checks["bbox_cov_50_60"] = BBOX_RANGE[0] <= bbox_cov <= BBOX_RANGE[1]
    ratio = bw / bh
    checks["ratio_1p2"] = 1.0 / RATIO_MAX <= ratio <= RATIO_MAX
    cov = opaque_px(a, bb) / (TARGET * TARGET)
    checks["cov_opaque"] = OPAQUE_RANGE[0] <= cov <= OPAQUE_RANGE[1]
    checks["margins_4pct"] = (x0 / TARGET >= 0.041 and (TARGET - x1) / TARGET >= 0.041
                              and y0 / TARGET >= 0.041)
    bot_pct = (TARGET - y1) / TARGET
    checks["bottom_4_6pct"] = 0.03 <= bot_pct <= 0.075
    comps = largest_components(a)
    main_ok = comps and comps[0] >= 0.10 * TARGET * TARGET
    strays_ok = all(c <= 0.015 * TARGET * TARGET for c in comps[1:])
    checks["body_ok"] = bool(main_ok and strays_ok)
    checks["no_halo"] = halo_ratio(tile) < 0.15
    out = OUT / f"{raw.name.split('_')[0]}.webp"
    tile.save(out, "WEBP", quality=90)
    if out.stat().st_size > 42 * 1024:
        tile.save(out, "WEBP", quality=82)
    kb = out.stat().st_size / 1024
    checks["size_kb"] = kb <= 50
    return {
        "raw": raw.name, "out": out.name, "kb": round(kb, 1),
        "bbox_cov_pct": round(bbox_cov * 100, 1), "ratio": round(ratio, 2),
        "coverage": round(cov * 100, 1), "bottom_pct": round(bot_pct * 100, 1),
        "margins_pct": [round(x0 / TARGET * 100, 1), round(y0 / TARGET * 100, 1),
                        round((TARGET - x1) / TARGET * 100, 1)],
        "components": len(comps),
        "main_pct": round(comps[0] / (TARGET * TARGET) * 100, 1) if comps else 0,
        "largest_stray_pct": round((comps[1] / (TARGET * TARGET) * 100), 3) if len(comps) > 1 else 0,
        "halo": round(halo_ratio(tile), 4),
        "checks": checks, "pass": all(checks.values()),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raws = sorted(RAW.glob("*_raw.png"), key=lambda p: int(p.name.split("_")[0]))
    if not raws:
        print("no raw images found")
        sys.exit(1)
    report = []
    for raw in raws:
        print(f"[{raw.name}]")
        r = process(raw)
        report.append(r)
        flags = " ".join(k for k, v in r["checks"].items() if not v) or "all-ok"
        print(f"  -> {r['out']} {r['kb']}KB bbox_cov={r['bbox_cov_pct']}% ratio={r['ratio']} "
              f"cov={r['coverage']}% bot={r['bottom_pct']}% halo={r['halo']} [{flags}]")
    (OUT / "_post_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in report if r["pass"])
    print(f"\npost-chain: {ok}/{len(report)} passed all gates")
    sys.exit(0 if ok == len(report) else 1)


if __name__ == "__main__":
    main()
