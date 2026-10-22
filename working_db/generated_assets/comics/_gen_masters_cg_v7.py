# -*- coding: utf-8 -*-
"""v7-CG：3A 遊戲 CG 風格定裝產線（用戶核准 gamecg 皮膚後使用）。

方法A 不變：白棚定裝 → rembg 去背 → PIL 合成。本腳本只負責 CG 版定裝生成。
主角由 PROTAGONIST 決定（"boy" 或 "man"）；男孩氣質由 BOY_VIBE 對應送審頁 A-1..A-4。
參考圖：_refs/gamecg_ref.png（龍A/男孩造型）、_refs/man_ref.png（成年探險家）、
        _src/db_stand.png（龍B造型，僅借造型）。
用法：python _gen_masters_cg_v7.py [name ...]（無參數=全部；已存在則跳過）
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
REFS = HERE / "_raw" / "_masters" / "_refs"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

PROTAGONIST = "man"   # 用戶裁決：成年探險家（"boy" | "man"）
BOY_VIBE = "A-3"      # 僅 PROTAGONIST="boy" 時使用

CG = ("Rendered in 3A game cinematic quality, Pixar-level 3D animation CG: PBR materials, subsurface "
      "scattering, soft global illumination. Plain pure WHITE seamless studio backdrop, warm early-morning "
      "golden sunlight raking from the upper left, soft contact shadow under the feet. "
      "Absolutely NO text, NO watermark, NO scenery.")

DA_CG = (
    "the SAME cute chubby purple dragon exactly as in reference image 1 - identical design: fine detailed "
    "granular reptile SCALES covering the whole vivid purple body, slightly darker purple round spots, TWO "
    "thick golden segmented horns on the head plus ONE small golden nose horn and ONE single row of small "
    "golden cone spikes along neck/back/tail, one pair of big pink inner ears, purple bat wings with "
    "pink-to-orange gradient membranes dotted with darker purple spots, cream-ivory belly and lower jaw, "
    "chunky golden claws, big round golden-amber eyes with white specular highlights, cheerful open smile "
    "with tiny white fangs and a pink tongue, round snout, chibi cute proportions. "
)

DB_CG = (
    "a DIFFERENT character from reference image 1 (borrow only its Pixar-level CG creature quality and fine "
    "granular reptile scale-skin render): a REAL LIVING cute long-necked sauropod - fine detailed granular "
    "reptile SCALES covering the whole slate-blue-grey body, slightly darker blue-grey spots, small orange "
    "cone spikes along neck/back/tail, cream belly, round friendly amber eyes with white highlights, soft "
    "pink inner ears, four stubby legs, a long elegant neck about as long as its torso with a small head, "
    "long tapering tail, NO wings, NO horns. Absolutely NO plastic toy look, NO molded seams, NO vinyl "
    "shell, NO painted-on look. "
)

BOY_CG = {
    "A-1": "a calm knowing smile with a strategic, calculating gaze - the clever strategist look",
    "A-2": "bold determined eyes, chin lifted, fearless grin, fists loosely clenched - the fearless leader look",
    "A-3": "a warm gentle firm smile, quiet unshakable confidence - the natural protagonist look",
    "A-4": "a mischievous sparkle in the eyes, raised brows, energetic half-grin - the spirited mischief look",
}
BOY_LOCK = (
    "the SAME cute 7-year-old East Asian boy exactly as in reference image 1 - identical face, big expressive "
    "amber eyes, short dark hair under a khaki safari hat; identical outfit: cream explorer vest over an "
    "orange T-shirt, brown cargo shorts, sturdy brown boots, white socks, small green backpack. "
)
MAN_LOCK = (
    "the SAME young adult male explorer exactly as in reference image 1 - identical face: short side-swept "
    "brown hair, light stubble; identical outfit and gear: olive-green safari jacket over grey-green tee, "
    "olive cargo pants, brown leather belt with pouches compass and sheathed knife, worn brown boots, large "
    "brown canvas backpack with rolled bedroll, map scroll tubes and coiled rope. "
)

REF_GAMECG = REFS / "banban_ref.png"   # 遊戲伴伴圖（用戶指定：龍A造型基準）
REF_MAN = REFS / "man_ref.png"
REF_DB = SRC / "cg_da_stand.png"   # 借 CG 質感（造型全文字鎖定，防回玩具感）

MASTERS = [
    ("cg_da_stand", str(REF_GAMECG), "1:1",
     f"A {DA_CG} standing upright on its hind legs with wings half-spread, cheerful open smile, full body "
     f"with tail, front 3/4 view. {CG}"),
    ("cg_da_sniff", "_prev", "1:1",
     f"A {DA_CG} crouched low with its nose pressed down to the ground sniffing, eyes squeezed shut in "
     f"delight, tail up, full body side view. {CG}"),
    ("cg_da_cheer", "_prev", "1:1",
     f"A {DA_CG} standing on hind legs with BOTH front paws raised high cheering, wings spread wide, biggest "
     f"happy open-mouth smile, full body front view. {CG}"),
    ("cg_da_sit", "_prev", "1:1",
     f"A {DA_CG} sitting down on its haunches like a little gargoyle, wings folded, looking slightly up with "
     f"big sparkling eyes and a gentle smile, full body 3/4 view. {CG}"),
    ("cg_db_stand", str(REF_DB), "1:1",
     f"A {DB_CG} standing tall with its long neck raised high, head turned slightly toward camera with a "
     f"calm friendly smile, full body side view. {CG}"),
    ("cg_db_lean", "_prev", "1:1",
     f"A {DB_CG} leaning forward curiously: its long neck bends in a smooth S-curve DOWNWARD so the small "
     f"head drops to knee height right in front of the front feet, muzzle pointing down-left at something "
     f"on the ground, body upright, full body side view. The neck MUST be clearly lowered and curved - "
     f"NOT held vertically upright. {CG}"),
]

if PROTAGONIST == "boy":
    MASTERS += [
        ("cg_boy_stand", str(REF_GAMECG), "2:3",
         f"A {BOY_LOCK} Full-body 3/4 front view, standing relaxed with {BOY_CG[BOY_VIBE]}, arms at his "
         f"sides, facing slightly left. {CG}"),
        ("cg_boy_crouch", "_prev", "2:3",
         f"A {BOY_LOCK} Full-body side-ish view crouching down low on his haunches, hands on his knees, "
         f"leaning forward looking down-left with wide curious eyes and an amazed open-mouth smile. {CG}"),
        ("cg_boy_kneel", "_prev", "2:3",
         f"A {BOY_LOCK} Full-body 3/4 view kneeling on one knee, both arms reaching forward and down as if "
         f"pulling something up out of the ground, joyful excited grin. {CG}"),
        ("cg_boy_side", "_prev", "2:3",
         f"A {BOY_LOCK} Full-body pure side profile standing, both hands cupped together held up at chest "
         f"height as if cradling a small glowing treasure, gazing down into his hands with a soft warm "
         f"smile. {CG}"),
    ]
else:
    MASTERS += [
        ("cg_man_stand", str(REF_MAN), "2:3",
         f"A {MAN_LOCK} Full-body 3/4 front view, standing relaxed with a confident adventurous smile, one "
         f"hand resting on his belt, facing slightly left. {CG}"),
        ("cg_man_crouch", "_prev", "2:3",
         f"A {MAN_LOCK} Full-body side-ish view crouching down low on his haunches, hands on his knees, "
         f"leaning forward looking down-left with wide curious eyes and an amazed open-mouth smile. {CG}"),
        ("cg_man_kneel", "_prev", "2:3",
         f"A {MAN_LOCK} Full-body 3/4 view kneeling on one knee, both arms reaching forward and down as if "
         f"pulling something up out of the ground, joyful excited grin. {CG}"),
        ("cg_man_side", "_prev", "2:3",
         f"A {MAN_LOCK} Full-body pure side profile standing, both hands cupped together held up at chest "
         f"height as if cradling a small glowing treasure, gazing down into his hands with a soft warm "
         f"smile. {CG}"),
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
prev_name = None
for name, ref, aspect, prompt in MASTERS:
    if only and name not in only:
        prev_name = name
        continue
    out = SRC / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        prev_name = name
        continue
    if ref == "_prev":
        ref_path = SRC / f"{prev_name}.png"
    else:
        ref_path = Path(ref)
    ref_b64 = flat_png(ref_path) if ref_path.exists() else None
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
    prev_name = name

print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
