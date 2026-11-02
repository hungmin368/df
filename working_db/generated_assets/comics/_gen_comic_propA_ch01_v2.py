# -*- coding: utf-8 -*-
"""方案A第1話 v3：少年漫畫分格＋寫實背景＋3D 立體感（正式模型 gemini-2.5-flash-image）

v3 與 v2 差異（用戶 2026-10-22 指示）：
- 正式製作模型維持 gemini-2.5-flash-image。
- 背景寫實：真實沙粒／海水／棕櫚／天空質感。
- 整體 3D 立體感：角色維持遊戲美術的 3D 玩具體積感、方向光＋投射陰影＋AO、
  大氣透視與景深，讀起來像 3D CG 動畫電影劇照。
- 角色鎖定與六格分鏡不變；舊版 v2/m31/mnb 底圖留在 _raw/。
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

STYLE = ("Full-color Japanese SHONEN MANGA panel illustration that looks like a still from a modern 3D CG animated "
         "film. Characters keep clean bold outlines but are shaded with dimensional 3D-toy volume: soft rounded "
         "forms, gloss-free satin material feel, realistic directional sunlight, strong cast shadows on the ground, "
         "ambient occlusion where characters and props touch the sand. Backgrounds are PHOTO-REALISTIC and "
         "hyper-detailed: real wet sand with grains, shells and footprints, realistic transparent turquoise sea "
         "water with foam and sparkling sun reflections, real palm leaves, driftwood and rock textures, volumetric "
         "sunbeams, a deep sky with soft realistic clouds. Strong atmospheric perspective and gentle depth of field "
         "so every panel reads fully three-dimensional. Vivid saturated colors, dynamic manga composition, subtle "
         "speed-line accents only during action beats. High detail. "
         "Absolutely NO text, NO speech bubbles, NO letters, NO sound-effect lettering, NO watermark, NO panel borders. "
         "Landscape composition.")

LOCK = (
    "CHARACTER LOCK (strict): "
    "Dragon A = the baby dragon shown in reference image 1: a chubby VIVID PURPLE baby dragon with slightly darker "
    "purple round spots on head/back/haunches, very large round GOLDEN-AMBER eyes with big white specular highlights, "
    "TWO thick golden-yellow segmented horns on the head plus smaller golden cone spikes along the neck, back and "
    "tail, large purple bat-style wings whose membranes gradient from magenta-pink at the leading edge to warm "
    "orange at the trailing edge, dotted with round magenta spots (exactly as reference image 1), big PINK "
    "inner ears, cream-ivory belly plates, chunky golden-yellow claws, and a cheerful open smile showing tiny white "
    "fangs and a pink tongue. Reproduce Dragon A with EXACTLY this "
    "design - identical colors, markings, proportions "
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
        f"with purple body, golden horns and magenta-to-orange gradient wing membranes exactly like the reference - "
        f"leaps mid-air beside the "
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
