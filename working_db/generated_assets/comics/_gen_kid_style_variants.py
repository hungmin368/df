# -*- coding: utf-8 -*-
"""寫實人類風格變體試產：同一格 P2 分鏡 × 四種真人渲染流派（供用戶選擇）

用戶否決 v4 第一版真人風後，改以四種流派各生成一張 P2（伴伴嗅碎片＋男孩特寫）：
- film   真人電影實拍風（35mm 電影畫格，恐龍合成進實拍底片）
- photo  人像攝影寫真風（雜誌級 85mm 人像攝影）
- gamecg 3A 遊戲 CG 真人風（電影級 PBR 渲染）
- paint  寫實插畫海報風（油畫筆觸海報插畫）
恐龍 CHARACTER LOCK、寫實背景、分鏡完全一致；正式模型 gemini-2.5-flash-image。
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
MODEL = "gemini-2.5-flash-image"
RATIO = "3:2"

LOCK = (
    "CHARACTER LOCK (strict): "
    "Dragon A = the baby dragon shown in reference image 1: a chubby VIVID PURPLE baby dragon with slightly darker "
    "purple round spots on head/back/haunches, very large round GOLDEN-AMBER eyes with big white specular highlights, "
    "TWO thick golden-yellow segmented horns on the head plus smaller golden cone spikes along the neck, back and "
    "tail, large purple bat-style wings whose membranes gradient from magenta-pink at the leading edge to warm "
    "orange at the trailing edge, dotted with round magenta spots (exactly as reference image 1), big PINK "
    "inner ears, cream-ivory belly plates, chunky golden-yellow claws, and a cheerful open smile showing tiny white "
    "fangs and a pink tongue. Reproduce Dragon A with EXACTLY this design - identical colors, markings, proportions "
    "and face as reference image 1; only pose and expression may change. "
    "Never recolor or redesign this character; it must stay instantly recognizable as its reference."
)

SCENE = ("Close-up discovery beat on a realistic beach. Dragon A presses its nose deep into the sand sniffing "
         "intensely, eyes squeezing then popping wide in surprise; a corner of a RAINBOW-COLORED hexagonal crystal "
         "shard peeks out of the sand right in front of its nose with bright sparkle effects. {kid} crouches just "
         "behind, leaning in close with curious wide eyes and an amazed open-mouth smile. Warm morning light.")

VARIANTS = {
    "film": dict(
        kid=("a REAL 10-year-old East Asian boy actor on a live-action film set: a fully photorealistic human being "
             "- natural skin with visible pores, fine peach fuzz, a few subtle freckles, slightly messy realistic "
             "short dark-brown hair with individual strands, natural facial asymmetry, real hands and fingers; "
             "wearing a khaki safari hat, cream sleeveless vest over an orange T-shirt, brown shorts, sturdy little "
             "boots and a small green backpack with real fabric weave and worn edges"),
        style=("A single frame from a big-budget live-action adventure film shot on a 35mm cinema camera: the human "
               "boy is 100% photorealistic live-action footage with natural film grain, cinematic teal-and-warm "
               "color grading, soft anamorphic bokeh. The cute cartoon baby dragon is seamlessly composited into "
               "the live-action plate like a Hollywood CG creature, keeping its exact stylized toy-game-art design "
               "but with lighting, contact shadows and sand interaction that perfectly match the live-action plate. "
               "The beach environment is a real photographed location. Dynamic manga-style composition. ")),
    "photo": dict(
        kid=("a real 10-year-old East Asian boy photographed with an 85mm portrait lens: tack-sharp pore-level skin "
             "detail, visible skin texture and tiny blemishes, natural catchlights in dark-brown eyes, realistic "
             "wind-touched short dark-brown hair; wearing a khaki safari hat, cream sleeveless vest over an orange "
             "T-shirt, brown shorts, sturdy little boots and a small green backpack - every fabric fiber visible"),
        style=("High-end editorial photography composite at magazine quality: the human boy is a real photograph - "
               "DSLR sharpness, natural sunlight, true-to-life colors, shallow depth of field with creamy bokeh. "
               "The stylized cartoon baby dragon stands on the photographed sand like a real physical collectible "
               "toy come to life, matching studio-grade lighting and contact shadows. Realistic beach background "
               "as location photography. ")),
    "gamecg": dict(
        kid=("a realistic CG human child character at AAA video-game cinematic quality: physically-based skin "
             "shading with subtle subsurface scattering and micro-detail, individually groomed hair strands, "
             "realistic cloth weave on a khaki safari hat, cream sleeveless vest, orange T-shirt, brown shorts, "
             "sturdy little boots and small green backpack, expressive realistic child face"),
        style=("A cinematic still from a AAA video-game cutscene: the human child is a fully realistic high-end CG "
               "character rendered with physically-based rendering, ray-traced soft shadows and volumetric "
               "lighting; the baby dragon keeps its stylized toy-game-art look beside him, both sharing one "
               "unified cinematic lighting rig over a hyper-real CG beach. ")),
    "paint": dict(
        kid=("a realistic human boy painted in rich traditional media: oil-paint skin with visible brushwork "
             "texture, realistic human proportions and anatomy, naturally imperfect features, warm painterly light "
             "on his khaki safari hat, cream sleeveless vest, orange T-shirt, brown shorts, sturdy little boots and "
             "small green backpack"),
        style=("Premium illustrated movie-poster art: the human boy is painted realistically in expressive "
               "traditional oil-paint style with visible brush strokes; the cartoon baby dragon is rendered as "
               "glossy 3D-toy art popping against the painted background; painted realistic beach scenery with "
               "painterly waves and clouds. ")),
}

NEG = ("Absolutely NO text, NO speech bubbles, NO letters, NO sound-effect lettering, NO watermark, NO panel "
       "borders. Landscape composition.")


def flat_ref(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg = bg.convert("RGB")
    bg.thumbnail((1024, 1024), Image.LANCZOS)
    buf = io.BytesIO()
    bg.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


REF = flat_ref(BBAN_SRC)


def call(prompt):
    parts = [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": REF}}]
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": RATIO}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:160]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts_out if "inlineData" in p), None)
    return (base64.b64decode(img) if img else None), ("no image part" if not img else "ok")


only = sys.argv[1:]
ok_all = True
for vid, v in VARIANTS.items():
    if only and vid not in only:
        continue
    out = RAW / f"kidstyle_{vid}_p2.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{vid}: exists, skip")
        continue
    prompt = f"{v['style']} {LOCK} {SCENE.format(kid=v['kid'])} {NEG}"
    img, msg = call(prompt)
    if img:
        out.write_bytes(img)
        print(f"{vid}: OK ({len(img)} bytes)")
    else:
        ok_all = False
        print(f"{vid}: FAIL -> {msg}")
    time.sleep(2)

print("DONE_OK" if ok_all else "DONE_PARTIAL")
