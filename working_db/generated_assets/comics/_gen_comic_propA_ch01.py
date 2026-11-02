# -*- coding: utf-8 -*-
"""方案A第1話「沙灘上的第一片彩虹」彩色漫畫試刊：6格分格圖生成（Gemini, Style A）"""
import base64, io, json, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
REPO = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
RAW = HERE / "_raw"
RAW.mkdir(exist_ok=True)

BBAN_SRC = REPO / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_1star.png"
SALTA_SRC = REPO / "game_db" / "assets" / "dinos" / "9.webp"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

KID = ("a cheerful 10-year-old explorer kid with short dark-brown hair, wearing a khaki safari hat, "
       "cream sleeveless vest over an orange T-shirt, brown shorts, sturdy little boots and a small green backpack")
BBAN = ("the small baby dragon from the reference image exactly (cream satin body, big golden-amber eyes, "
        "tiny yellow horns, cheerful face, baby form)")
SALTA = ("the baby long-necked sauropod from the second reference image exactly (small blue-grey sauropod, "
         "round friendly eyes, chubby cute proportions)")
STYLE = ("COLOR COMIC PANEL illustration drawn in the exact same soft 3D toy-render art style as the reference "
         "images: cute chibi proportions, satin matte skin, warm storybook lighting, high-resolution digital art. "
         "This is a full comic-panel illustration WITH a painted background, NOT a white studio cutout. "
         "Absolutely NO text, NO speech bubbles, NO letters, NO watermark, NO panel borders anywhere in the image. "
         "Wide 4:3 landscape composition.")

PANELS = [
    dict(id=1, refs=["bban"], prompt=(
        f"Early-morning establishing shot of a golden tropical beach. {KID} walks along the shoreline toward an old "
        f"shipwrecked wooden supply crate half-buried in the sand, reinforced with iron straps and faded rainbow paint, "
        f"with a few smaller crates scattered behind the dunes in the distance. {BBAN} trots happily beside the kid. "
        f"Gentle turquoise waves, seabirds crossing the pale sunrise sky, long soft shadows. Characters seen from a "
        f"three-quarter back view, sense of adventure.")),
    dict(id=2, refs=["bban"], prompt=(
        f"Close-up discovery shot on the golden beach. {BBAN} presses its nose into the sand sniffing eagerly with its "
        f"tail up; a corner of a RAINBOW-COLORED crystal compass shard peeks out of the sand right in front of its nose, "
        f"glittering. {KID} crouches beside it, eyes wide with wonder, hands on knees. Warm morning sun glow, soft sparkles.")),
    dict(id=3, refs=["bban", "salta"], prompt=(
        f"Funny comedy beat on the beach. The {SALTA} now wears the rainbow-colored crystal compass shard as a shiny "
        f"necklace around its neck, chin raised, smug and proud, basking happily in the sun. {KID} and {BBAN} stand at "
        f"the side comically stunned: the kid sweat-dropping with mouth open in mid-protest, the baby dragon's jaw dropped. "
        f"Sand dunes and driftwood in the background, bright daylight.")),
    dict(id=4, refs=["bban", "salta"], prompt=(
        f"Deduction scene on the beach. {KID} kneels drawing circles and arrows in the sand with a small stick, explaining "
        f"with a confident grin; in the far background near the waterline stands a row of small sandcastles and one BIG "
        f"impressive sandcastle. {BBAN} listens with head tilted and one paw raised as if understanding. The {SALTA} leans "
        f"in curiously from the other side. Warm mid-morning light.")),
    dict(id=5, refs=["bban", "salta"], prompt=(
        f"Treasure-dig climax beside the big sandcastle. {KID} pulls the RAINBOW-COLORED crystal compass shard free from "
        f"the sand, and it glints with rainbow light; {BBAN} cheers with both paws raised; the {SALTA} happily nudges the "
        f"shard toward the kid with its snout as if offering it. Joyful energy, a little spray of sand, sparkling ocean "
        f"behind, rainbow light reflections.")),
    dict(id=6, refs=["bban"], prompt=(
        f"Heart-warming close-up finale. The hands of {KID} hold a glowing RAINBOW-COLORED crystal compass shard up "
        f"against the morning sun with a soft lens-flare-like glow; {BBAN} perches on the kid's shoulder, eyes shining, "
        f"both smiling at each other. Blurred golden sea horizon background with gentle bokeh sparkles, emotional warm tone.")),
]

def flat_ref(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg = bg.convert("RGB")
    bg.thumbnail((1024, 1024), Image.LANCZOS)
    buf = io.BytesIO()
    bg.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

REFS = {"bban": flat_ref(BBAN_SRC), "salta": flat_ref(SALTA_SRC)}

def call(model, prompt, ref_keys, aspect=True):
    parts = [{"text": f"{STYLE} {prompt}"}]
    for k in ref_keys:
        parts.append({"inline_data": {"mime_type": "image/png", "data": REFS[k]}})
    gc = {"responseModalities": ["IMAGE"]}
    if aspect:
        gc["imageConfig"] = {"aspectRatio": "4:3"}
    body = {"contents": [{"parts": parts}], "generationConfig": gc}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:200]
        return None, f"HTTP {e.code}: {msg}"
    parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts_out if "inlineData" in p), None)
    return (base64.b64decode(img) if img else None), ("no image part" if not img else "ok")

ok_all = True
for p in PANELS:
    out = RAW / f"propA_ch01_p{p['id']}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"p{p['id']}: exists, skip")
        continue
    got = None
    for model in MODELS:
        for aspect in (True, False):
            img, msg = call(model, p["prompt"], p["refs"], aspect)
            if img:
                got = img
                print(f"p{p['id']}: OK via {model} aspect={aspect} ({len(img)} bytes)")
                break
            print(f"p{p['id']}: fail {model} aspect={aspect} -> {msg}")
        if got:
            break
        time.sleep(2)
    if got:
        out.write_bytes(got)
    else:
        ok_all = False
        print(f"p{p['id']}: ALL_FAILED")

print("DONE_OK" if ok_all else "DONE_PARTIAL")
