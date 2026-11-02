# -*- coding: utf-8 -*-
"""v7：龍A「皮膚質感」候選——同一造型同一站姿，四種真實生物皮膚。

參考圖：_src/da_stand.png（亮面玩具版，僅作造型/姿態參考）。
輸出 _src/da_skin_v1..v4.png；用戶選定皮膚後再以同款文字重出全部定裝動作。
用法：python _gen_skin_variants_v7.py [name ...]
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
REF = SRC / "da_stand.png"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

BASE = (
    "Use reference image 1 for the EXACT character design and the SAME pose (standing upright on hind legs "
    "with wings half-spread, cheerful open smile, front 3/4 view): a cute chubby dragon with a vivid purple "
    "body patterned with slightly darker purple round spots, one pair of thick golden segmented horns, purple "
    "bat wings with magenta-to-orange gradient membranes dotted with round dark-purple spots, one pair of "
    "pink inner ears, a cream-ivory belly, chunky golden claws, big round golden-amber eyes. "
    "BUT render it as a REAL LIVING CREATURE, not a toy: absolutely NO plastic, NO vinyl, NO molded seams, "
    "NO painted-on look, NO packaging. Photographed for real with an 85mm lens. "
    "Plain pure WHITE seamless studio backdrop, warm early-morning sunlight from the upper left, soft "
    "realistic contact shadow under the feet. Absolutely NO text, NO watermark, NO scenery."
)

TEXTURES = {
    "da_skin_v1": (
        "TEXTURE - DRY REPTILE SCALES: its entire body is covered in thousands of small granular real "
        "reptile scales like a bearded dragon or monitor lizard - slightly rough matte hide with natural "
        "skin folds around the neck, joints and belly plates, and only a faint natural sheen where the "
        "light grazes the scales."),
    "da_skin_v2": (
        "TEXTURE - SOFT DOWNY FUR: its entire body is covered in short dense plush downy fur like a baby "
        "animal - soft purple base fur with the darker spots reading as deeper-toned fur patches, a cream "
        "fluffy belly, short fur on the face, and the wings remain leathery with a fine fuzz at the edges."),
    "da_skin_v3": (
        "TEXTURE - MOIST GLOSSY AMPHIBIAN SKIN: its entire body has smooth moist glistening amphibian skin "
        "like a frog or a wet salamander - wet high-sheen surface with tiny water droplets beading on the "
        "back and head, rich saturated purple, slightly translucent quality on the ears and wing edges."),
    "da_skin_v4": (
        "TEXTURE - FINE VELVETY PLUMAGE: its entire body is covered in fine velvety down feathers like a "
        "baby bird-dinosaur - soft purple plumage with the darker spots rendered as feather-tip patterns, "
        "a cream fluffy feathered belly, and small covert feathers fringing the wing arms."),
}


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
ref_b64 = flat_png(REF)
for name, tex in TEXTURES.items():
    if only and name not in only:
        continue
    out = SRC / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        continue
    got = None
    for model in MODELS:
        img, msg = call(model, tex + " " + BASE, ref_b64, "1:1")
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
