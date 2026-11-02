# -*- coding: utf-8 -*-
"""v7 方法A：角色定裝照生成（Gemini，鏈式參考＋淺背景利去背）。

同角色所有姿勢皆以該角色「首張定裝」為參考圖（inline），保跨姿勢一致性。
產出 _raw/_masters/_src/<name>.png（白底原始圖），去背在 _cut_masters_v7.py。
用法：python _gen_masters_v7.py [name ...]（無參數=全部；已存在則跳過）
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
REPO = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
SRC = HERE / "_raw" / "_masters" / "_src"
SRC.mkdir(parents=True, exist_ok=True)

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

BOY_LOCK = (
    "the SAME real 10-year-old East Asian boy exactly as in reference image 1 - identical face, hairstyle, "
    "skin tone and outfit: khaki safari hat, cream sleeveless explorer vest over an orange T-shirt, brown "
    "shorts, sturdy brown boots, white socks and a small green backpack. Photographed like an editorial "
    "magazine portrait with an 85mm lens: tack-sharp pore-level skin, natural catchlights, every fabric "
    "fiber visible. "
)
MATERIAL = (
    "The shell is PREMIUM COLLECTIBLE DESIGNER VINYL with a HARD HIGH-GLOSS CLEARCOAT: "
    "mirror-sharp specular highlights, crisp elongated softbox reflections sliding across every "
    "curved surface, faint molded seams at the joints, a rigid hard shell that would clack if "
    "tapped like an expensive designer toy figure. Absolutely NOT soft rubber, NOT matte, NOT "
    "satin, NOT squishy or clay-like. "
)

DA_LOCK = (
    "the SAME glossy collectible vinyl toy dragon exactly as in reference image 1 - identical design: chubby "
    "VIVID PURPLE body with slightly darker purple round spots, very large round golden-amber eyes with white "
    "specular highlights, EXACTLY ONE pair of thick golden-yellow segmented horns plus ONE single row of small "
    "golden cone spikes along neck/back/tail, large purple bat wings with magenta-to-orange gradient membranes "
    "dotted with round DARK-PURPLE spots, ONE pair of big pink inner ears, cream-ivory belly plates, chunky "
    "golden claws, round snout, cheerful face. A physical designer toy photographed on location. " + MATERIAL
)
DB_LOCK = (
    "the SAME glossy collectible vinyl toy sauropod exactly as in reference image 1 - identical design: "
    "slate-blue-grey body, small orange cone spikes along neck/back/tail, cream belly, round friendly "
    "amber eyes, soft pink inner ears, four stubby legs, a long elegant neck about as long as its torso with a "
    "small head, long tapering tail, NO wings, NO horns. A physical designer toy photographed on location. " + MATERIAL
)

STUDIO = ("Plain pure WHITE seamless studio backdrop, no props, no scenery. Warm early-morning sunlight "
          "raking in from the upper left, soft realistic contact shadow under the feet. "
          "Absolutely NO text, NO watermark, NO packaging, NO price tag.")

MASTERS = [
    # (name, chain_key, aspect, prompt)
    ("boy_stand", None, "2:3",
     f"Full-body 3/4 front view of {BOY_LOCK} standing relaxed with a cheerful adventurous smile, "
     f"arms at his sides, facing slightly left. {STUDIO}"),
    ("boy_crouch", "boy_stand", "2:3",
     f"Full-body side-ish view of {BOY_LOCK} crouching down low on his haunches, hands on his knees, "
     f"leaning forward looking down-left with wide curious eyes and an amazed open-mouth smile. {STUDIO}"),
    ("boy_kneel", "boy_stand", "2:3",
     f"Full-body 3/4 view of {BOY_LOCK} kneeling on one knee on the ground, both arms reaching forward and "
     f"down as if pulling something out of sand, joyful excited grin. {STUDIO}"),
    ("boy_side", "boy_stand", "2:3",
     f"Full-body pure side profile of {BOY_LOCK} standing, both hands cupped together held up at chest height "
     f"as if cradling a small glowing treasure, gazing down into his hands with a soft warm smile. {STUDIO}"),
    ("da_stand", None, "1:1",
     f"A {DA_LOCK} Standing upright on its hind legs with wings half-spread, cheerful open smile, "
     f"full body with tail, front 3/4 view. {STUDIO}"),
    ("da_sniff", "da_stand", "1:1",
     f"A {DA_LOCK} Crouched low with its nose pressed down to the ground sniffing, eyes squeezed shut in "
     f"delight, tail up, full body side view. {STUDIO}"),
    ("da_cheer", "da_stand", "1:1",
     f"A {DA_LOCK} Standing on hind legs with BOTH front paws raised high in the air cheering, wings spread "
     f"wide, biggest happy open-mouth smile, full body front view. {STUDIO}"),
    ("da_sit", "da_stand", "1:1",
     f"A {DA_LOCK} Sitting down on its haunches like a little gargoyle, wings folded, looking slightly up "
     f"with big sparkling eyes and a gentle smile, full body 3/4 view. {STUDIO}"),
    ("db_stand", None, "1:1",
     f"A {DB_LOCK} Standing tall with its long neck raised high, head turned slightly toward camera with a "
     f"calm friendly smile, full body side view. {STUDIO}"),
    ("db_lean", "db_stand", "1:1",
     f"A {DB_LOCK} Leaning forward curiously, its long neck curving gracefully down and forward at a low "
     f"height as if inspecting something near the ground, full body side view. {STUDIO}"),
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
    ref_b64 = flat_png(SRC / f"{chain_key}.png") if chain_key else None
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
