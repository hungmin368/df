# -*- coding: utf-8 -*-
"""v7 方法A：成年探險家主角定裝（用戶附圖為錨點參考，Gemini 鏈式生成）。

參考圖：_raw/_masters/_refs/man_ref.png（用戶提供之成年探險家立繪）。
產出 _raw/_masters/_src/man_<pose>.png（白底原始圖），去背在 _cut_masters_v7.py。
用法：python _gen_man_masters_v7.py [name ...]（無參數=全部；已存在則跳過）
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
SRC = HERE / "_raw" / "_masters" / "_src"
SRC.mkdir(parents=True, exist_ok=True)
REF = HERE / "_raw" / "_masters" / "_refs" / "man_ref.png"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

MAN_LOCK = (
    "the SAME young adult male explorer exactly as in reference image 1 - identical face: short side-swept "
    "brown hair, light stubble, determined gentle eyes; identical outfit: olive-green safari jacket over a "
    "grey-green tee, olive cargo pants, brown leather belt with small pouches a compass and a sheathed knife, "
    "worn brown leather boots, and a large brown canvas backpack with a rolled bedroll map scroll tubes and a "
    "coiled rope. Photographed like an editorial magazine portrait with an 85mm lens: tack-sharp detail, "
    "natural catchlights, every fabric weave visible. "
)

STUDIO = ("Plain pure WHITE seamless studio backdrop, no props, no scenery. Warm early-morning sunlight "
          "raking in from the upper left, soft realistic contact shadow under the feet. "
          "Absolutely NO text, NO watermark, NO background scenery.")

MASTERS = [
    ("man_stand", None, "2:3",
     f"Full-body 3/4 front view of {MAN_LOCK} standing relaxed with a confident adventurous smile, one hand "
     f"resting on his belt, facing slightly left. {STUDIO}"),
    ("man_crouch", "man_stand", "2:3",
     f"Full-body side-ish view of {MAN_LOCK} crouching down low on his haunches, hands on his knees, leaning "
     f"forward looking down-left with wide curious eyes and an amazed open-mouth smile. {STUDIO}"),
    ("man_kneel", "man_stand", "2:3",
     f"Full-body 3/4 view of {MAN_LOCK} kneeling on one knee, both arms reaching forward and down as if "
     f"pulling something up out of the ground, joyful excited grin. The ground under him is the SAME plain "
     f"pure WHITE seamless studio floor as the backdrop - absolutely NO sand, NO dirt, NO scenery. {STUDIO}"),
    ("man_side", "man_stand", "2:3",
     f"Full-body pure side profile of {MAN_LOCK} standing, both hands cupped together held up at chest height "
     f"as if cradling a small glowing treasure, gazing down into his hands with a soft warm smile. {STUDIO}"),
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
for name, chain_key, aspect, prompt in MASTERS:
    if only and name not in only:
        continue
    out = SRC / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        continue
    ref_path = REF if chain_key is None else SRC / f"{chain_key}.png"
    ref_b64 = flat_png(ref_path)
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
    else:
        ok_all = False
        print(f"{name}: ALL_FAILED", flush=True)

print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
