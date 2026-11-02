# -*- coding: utf-8 -*-
"""v7-Phase2：第 1 話背景底圖產線（方法A：背景不含角色，角色用去背定裝貼上）。

產出 4 張 4:3 空景，供 v3 合成器把 cg_* 定裝貼入：
  bg_beach_wide  P1/P3 日出金沙灘大遠景（含擱淺探給箱）
  bg_sand_close  P2/P4 沙地近景（沙面＋貝殼亮點，P4 圓圈由合成器畫）
  bg_sandcastle  P5   氣派大沙堡中景
  bg_sunset_glow P6   夕陽海面逆光（伴 cg_man_side 捧碎片特寫）
風格鎖 3A 遊戲 CG＋與定裝同一暖金晨光；全空景、無角色、無文字。
鏈式參考：前一張 bg 作下一張的風格參考，維持色調一致。
用法：python _gen_bgs_v7.py [name ...]（無參數=全部；已存在則跳過）
"""
import base64
import io
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
OUT = HERE / "_raw" / "_bgs"
OUT.mkdir(parents=True, exist_ok=True)

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

STYLE = (
    "Rendered in 3A game cinematic quality, Pixar-level 3D animation CG: PBR materials, soft global "
    "illumination, volumetric warm light. Warm early-morning golden sunlight raking from the upper left, "
    "gentle atmospheric haze. The scene is a completely EMPTY stage - absolutely NO people, NO creatures, "
    "NO characters, NO faces, NO text, NO watermark, NO logo. Match the warm golden palette and cinematic "
    "lighting of the reference image."
)

BGS = [
    ("bg_beach_wide", None, "4:3",
     "Wide establishing shot of a golden-sand beach at sunrise: sparkling fine sand with soft dunes in the "
     "foreground, a weathered wooden explorer supply crate (dark iron-banded chest, adventure gear beside "
     "rope and canvas) half-buried near the tideline, calm shallow water with warm mirror-like reflections "
     "of the low sun, a distant green headland on the left, gulls in the far sky. "
     f"{STYLE}"),
    ("bg_sand_close", "_prev", "4:3",
     "Close-up of the golden beach sand surface filling the whole frame: fine rippled sand grains with a "
     "few small sparkling seashells and tiny glinting specks, one faint colorful glimmer (tiny rainbow "
     "shard corner) barely poking out of the sand near lower-left, soft warm light and shallow depth of "
     "field blurring the far edge. "
     f"{STYLE}"),
    ("bg_sandcastle", "_prev", "4:3",
     "Mid shot on the golden beach: a grand majestic multi-towered sandcastle with tall spiral shell-topped "
     "turrets, shell decorations and a little flagless wooden pole, toy bucket and shovel lying beside it, "
     "sand freshly dug around its base, warm late-morning sunlight, sparkling sea in the soft-focus "
     "background. "
     f"{STYLE}"),
    ("bg_sunset_glow", "_prev", "4:3",
     "Golden-hour sunset seascape for a backlit close-up: the low sun sitting on the calm sea horizon, warm "
     "orange-pink sky with soft clouds, sparkling bokeh light dots on gentle waves, strong warm lens flare "
     "and rim-light glow filling the frame, shallow depth of field. "
     f"{STYLE}"),
]


def flat_png(path, max_side=1024):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg = bg.convert("RGB")
    bg.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    bg.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def call(model, prompt, ref_b64, aspect):
    parts = [{"text": prompt}]
    if ref_b64:
        parts.append({"inline_data": {"mime_type": "image/png", "data": ref_b64}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": aspect}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:160]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts_out if "inlineData" in p), None)
    return (base64.b64decode(img) if img else None), ("no image part" if not img else "ok")


only = set(sys.argv[1:])
ok_all = True
prev_path = None
for name, ref, aspect, prompt in BGS:
    if only and name not in only:
        prev_path = OUT / f"{name}.png"
        continue
    out = OUT / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        prev_path = out
        continue
    ref_path = prev_path if ref == "_prev" else ref
    ref_b64 = flat_png(ref_path) if ref_path and Path(ref_path).exists() else None
    got = None
    for model in MODELS:
        img, msg = call(model, prompt, ref_b64, aspect)
        if img:
            got = img
            print(f"{name}: OK via {model} ({len(img)} bytes)", flush=True)
            break
        print(f"{name}: fail {model} -> {msg}", flush=True)
        time.sleep(2)
    if got:
        out.write_bytes(got)
        prev_path = out
    else:
        ok_all = False
        print(f"{name}: ALL_FAILED", flush=True)

print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
