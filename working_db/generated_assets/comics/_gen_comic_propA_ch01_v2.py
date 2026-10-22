# -*- coding: utf-8 -*-
"""方案A第1話 v2：日本少年漫畫風 6 格（Gemini；遊戲角色圖作嚴格內容參照）

v2 與 v1 差異：
- 角色必須與遊戲圖一致：伴伴＝紫色寶寶龍（2星立姿圖），薩爾塔寶寶＝石板灰螺旋捲尾（9.webp）。
- 畫風改為日本少年漫畫風（彩色、粗墨線、速度線）。
- 各格指定寬高比（跨格用 21:9），合成時再依版面 cover-crop。
"""
import base64, io, json, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
REPO = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
RAW = HERE / "_raw"
RAW.mkdir(exist_ok=True)

BBAN_SRC = REPO / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_2star.png"
SALTA_SRC = REPO / "game_db" / "assets" / "dinos" / "9.webp"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

KID = ("a cheerful 10-year-old explorer kid with short dark-brown hair, wearing a khaki safari hat, "
       "cream sleeveless vest over an orange T-shirt, brown shorts, sturdy little boots and a small green backpack")

STYLE = ("Full-color Japanese SHONEN MANGA panel illustration: bold clean black ink outlines, dynamic anime-manga "
         "linework, vivid saturated cel-shaded colors, dramatic perspective and energetic composition, subtle manga "
         "speed-line accents in the background where natural. High detail. "
         "Absolutely NO text, NO speech bubbles, NO letters, NO sound-effect lettering, NO watermark, NO panel borders. "
         "Landscape composition.")

LOCK = (
    "CHARACTER LOCK (strict): "
    "Dragon A = the baby dragon shown in reference image 1: a chubby VIVID PURPLE baby dragon with slightly darker "
    "purple round spots on head/back/haunches, very large round GOLDEN-AMBER eyes with big white specular highlights, "
    "TWO thick golden-yellow segmented horns on the head plus smaller golden cone spikes along the neck, back and "
    "tail, large purple bat-style wings with bright PINK-MAGENTA membranes dotted with round purple spots, big PINK "
    "inner ears, cream-ivory belly plates, chunky golden-yellow claws, and a cheerful open smile showing tiny white "
    "fangs and a pink tongue. Reproduce Dragon A with EXACTLY this design - identical colors, markings, proportions "
    "and face as reference image 1; only pose and expression may change. "
    "Dragon B = the baby sauropod shown in reference image 2: a chubby SLATE-GRAY baby long-necked dinosaur whose "
    "tail curls into a tight spiral resting against its hip, with big round golden-amber eyes, small golden-yellow "
    "cone spikes on the head and along the neck ridge and back, one big PINK inner ear, a soft cream-tan underside, "
    "tiny golden claws and a gentle smile. Reproduce Dragon B EXACTLY as in reference image 2; when Dragon B stands "
    "or holds something the spiral tail stays visible against its hip. "
    "Never recolor or redesign these characters; each must stay instantly recognizable as its reference.")

PANELS = [
    dict(id=1, refs=["bban"], ratio="21:9", prompt=(
        f"Ultra-wide establishing shot of a golden tropical beach at bright morning. {KID} walks along the shoreline "
        f"toward an old shipwrecked wooden supply crate half-buried in the sand, reinforced with iron straps and faded "
        f"rainbow paint, a faint mysterious glint on its lid. Dragon A trots happily beside the kid, tail up. Turquoise "
        f"waves, palm trees, seabirds. Three-quarter back view, strong sense of adventure. Keep both characters and the "
        f"crate fully inside the central horizontal band of the frame.")),
    dict(id=2, refs=["bban"], ratio="3:2", prompt=(
        f"Close-up discovery beat. Dragon A presses its nose deep into the sand sniffing intensely, eyes squeezed then "
        f"popping wide in surprise; a corner of a RAINBOW-COLORED crystal compass shard peeks out of the sand right "
        f"in front of its nose with bright sparkle effects. {KID} crouches just behind, leaning in with wide shining "
        f"eyes. Exaggerated manga expressions, warm morning light.")),
    dict(id=3, refs=["salta"], ratio="16:9", prompt=(
        f"Dramatic low-angle beat on the beach. Dragon B stands proudly on a driftwood log, holding the RAINBOW-COLORED "
        f"crystal compass shard up between its tiny front paws like a trophy, chin raised, smug delighted smile, its "
        f"spiral-coiled tail visible against its hip. Sunbeams and a few sparkle effects around the shard, sand dunes "
        f"and turquoise sea behind, shonen-style heroic framing.")),
    dict(id=4, refs=["bban", "salta"], ratio="21:9", prompt=(
        f"Full-throttle shonen comedy shock wide shot. Dragon B now wears the rainbow crystal shard as a necklace "
        f"strung on seaweed, posing proudly with a wink. {KID} does an exaggerated anime jaw-drop shock pose, arms "
        f"flailing, giant sweat drop flying; Dragon A beside him freezes mid-gasp with wings popped up, jaw dropped. "
        f"Dramatic RADIAL SPEED LINES burst across the background from the center, exaggerated expressions, peak "
        f"comedy energy. Keep all three characters fully inside the central horizontal band of the frame.")),
    dict(id=5, refs=["bban", "salta"], ratio="16:9", prompt=(
        f"Determination beat. {KID} kneels drawing a big circle-and-arrow plan in the sand with a stick, confident "
        f"grin, pointing at a BIG impressive sandcastle nearby; Dragon A leans in on one side with a pumped fist, "
        f"Dragon B leans in from the other side, both fired up with tiny flame-like determination sparks in their "
        f"eyes; the faint glow of a rainbow crystal tip pokes out of a sand mound beside the sandcastle. Warm "
        f"mid-morning light, dynamic shonen framing.")),
    dict(id=6, refs=["bban", "salta"], ratio="3:2", prompt=(
        f"Triumphant shonen finale. {KID} hoists a blazing HEXAGONAL rainbow crystal shard - a broken piece of the "
        f"rainbow compass, NOT a round compass, no dial, no needle - high overhead in both hands, classic hero pose, "
        f"rainbow light rays bursting from it. Dragon A - the VIVID PURPLE baby dragon, exactly as reference image 1 "
        f"with purple body, golden horns and PINK-MAGENTA wing membranes (never orange) - leaps mid-air beside the "
        f"kid cheering with both golden claws raised. Dragon B - the SLATE-GRAY sauropod baby with spiral-coiled "
        f"tail, exactly as reference image 2 - bounces joyfully on the sand wearing its seaweed necklace. All three "
        f"characters clearly visible. A big vivid rainbow arcs across the golden sunset sky above the sea, sparkles "
        f"everywhere, maximum joyful energy.")),
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

def call(model, prompt, ref_keys, ratio):
    parts = [{"text": f"{STYLE} {LOCK} {prompt}"}]
    for k in ref_keys:
        parts.append({"inline_data": {"mime_type": "image/png", "data": REFS[k]}})
    gc = {"responseModalities": ["IMAGE"]}
    if ratio:
        gc["imageConfig"] = {"aspectRatio": ratio}
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
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts_out if "inlineData" in p), None)
    return (base64.b64decode(img) if img else None), ("no image part" if not img else "ok")

ok_all = True
args = sys.argv[1:]
prefix = "v2"
model_filter = None
only = []
i = 0
while i < len(args):
    if args[i] == "--model":
        model_filter = args[i + 1]
        i += 2
    elif args[i] == "--prefix":
        prefix = args[i + 1]
        i += 2
    else:
        only.append(args[i])
        i += 1
if not only:
    only = [str(p["id"]) for p in PANELS]
models = [model_filter] if model_filter else MODELS
for p in PANELS:
    if str(p["id"]) not in only:
        continue
    out = RAW / f"propA_ch01_{prefix}_p{p['id']}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"p{p['id']}: exists, skip")
        continue
    got = None
    for model in models:
        for ratio in (p["ratio"], "16:9", "4:3", None):
            img, msg = call(model, p["prompt"], p["refs"], ratio)
            if img:
                got = img
                print(f"p{p['id']}: OK via {model} ratio={ratio} ({len(img)} bytes)")
                break
            print(f"p{p['id']}: fail {model} ratio={ratio} -> {msg}")
        if got:
            break
        time.sleep(2)
    if got:
        out.write_bytes(got)
    else:
        ok_all = False
        print(f"p{p['id']}: ALL_FAILED")

print("DONE_OK" if ok_all else "DONE_PARTIAL")
