# -*- coding: utf-8 -*-
"""試做：3A 遊戲 CG 皮膚（用戶附圖為參考）單張場景試驗圖。

輸出 _raw/_trials/gamecg_skin_trial1.png
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
OUTDIR = HERE / "_raw" / "_trials"
OUTDIR.mkdir(parents=True, exist_ok=True)
REF = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_raw" / "_masters" / "_refs" / "gamecg_ref.png"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

PROMPT = (
    "Cinematic 3A game cutscene render, Pixar-level 3D animation CG quality with PBR materials: a cute "
    "7-year-old East Asian boy with big expressive amber eyes, wearing a khaki safari hat, a cream explorer "
    "vest over an orange T-shirt, brown cargo shorts, sturdy brown boots and a small green backpack, "
    "crouching on a sunny tropical beach. Beside him in the foreground, a cute chubby purple dragon - the "
    "same design as reference image 1 - sniffs at a glowing rainbow crystal shard half-buried in the golden "
    "sand. The dragon has REAL detailed reptile skin: fine granular purple scales catching the warm morning "
    "sunlight, slightly darker purple round spots, thick golden segmented horns, purple bat wings with "
    "magenta-to-orange gradient membranes dotted with dark purple, big round golden eyes, a cream belly. "
    "Boy and dragon share the SAME unified warm golden morning lighting with soft contact shadows in the "
    "sand; turquoise sea, palm trees and blue sky with fluffy clouds behind; shallow depth of field; "
    "subsurface scattering on the boy's skin; every scale on the dragon readable. Absolutely NO text, "
    "NO watermark, NO UI elements."
)


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


out = OUTDIR / "gamecg_skin_trial1.png"
ref_b64 = flat_png(REF) if REF.exists() else None
got = None
for model in MODELS:
    img, msg = call(model, PROMPT, ref_b64, "4:3")
    if img:
        got = img
        print(f"trial: OK via {model} ({len(img)} bytes)", flush=True)
        break
    print(f"trial: fail {model} -> {msg}", flush=True)
    time.sleep(2)
if got:
    out.write_bytes(got)
    print("TRIAL_DONE", flush=True)
else:
    print("TRIAL_FAILED", flush=True)
