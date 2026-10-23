# -*- coding: utf-8 -*-
"""v7 男孩定裝變體：4 款臉型/氣場供用戶挑選（服裝髮型一致，僅神韻不同）。

產出 _raw/_masters/_src/boy_v1..v4.png；用戶選定後以其為鏈式基準凍結。
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

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

OUTFIT = ("khaki safari hat, cream sleeveless explorer vest over an orange T-shirt, brown cargo shorts, "
          "sturdy brown boots, white socks and a small green backpack")

VARIANTS = [
    ("boy_v1", "the INTELLIGENT type: bright sparkling dark-brown eyes full of wit and curiosity behind "
               "straight bangs, a calm knowing smile, an observant strategic gaze like a young leader "
               "sizing up the horizon"),
    ("boy_v2", "the COURAGEOUS type: bold determined dark-brown eyes, chin lifted, a fearless adventurous "
               "grin, fists loosely clenched at his sides radiating bravery and can-do energy"),
    ("boy_v3", "the PROTAGONIST type: a warm, gentle but firm smile with unshakable confidence and quiet "
               "leadership aura, steady heroic eyes with natural catchlights, an everyman-hero presence"),
    ("boy_v4", "the SPIRITED type: lively mischievous sparkle in his eyes, slightly raised eyebrows, an "
               "energetic ready-for-action half-grin full of optimism and quick wit"),
]

STUDIO = ("Full-body 3/4 front view of a real 10-year-old East Asian boy photographed with an 85mm portrait "
          "lens at editorial magazine quality: tack-sharp pore-level skin detail, natural catchlights in "
          "dark-brown eyes, realistic short dark-brown hair with straight bangs, every fabric fiber visible. "
          "He has a MAIN-CHARACTER aura - ")
STUDIO_TAIL = (f" Wearing exactly: {OUTFIT}. Plain pure WHITE seamless studio backdrop, no props. "
               "Warm early-morning sunlight raking in from the upper left, soft realistic contact shadow "
               "under the boots. Absolutely NO text, NO watermark.")


def call(model, prompt, aspect):
    body = {"contents": [{"parts": [{"text": prompt}]}],
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
for name, vibe in VARIANTS:
    if only and name not in only:
        continue
    out = SRC / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        continue
    prompt = f"{STUDIO}{vibe}.{STUDIO_TAIL}"
    got = None
    for model in MODELS:
        img, msg = call(model, prompt, "2:3")
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
