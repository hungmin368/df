# -*- coding: utf-8 -*-
"""v7 全角色定裝產線：依全篇分鏡腳本的劇情動作，為登場角色產出定裝照（含流水號）。

- 每個角色首張以其造型錨為參考，之後鏈式參考前一張，凍結造型。
- 已存在的 cg_* 定裝（Phase 1）不重新生成，直接編入流水號 001–010。
- 產出 _src/<file>.png → _cut_masters_v7.py 去背 → _raw/_masters/<file>.png。
- 完成後寫入 _cast_manifest.json（流水號→角色／動作／檔案／提示詞），供送審頁與重做指認使用。
用法：python _gen_cast_v7.py [file ...]（無參數=全部缺漏者；已存在則跳過）
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
MANIFEST = HERE / "_cast_manifest.json"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

CG = ("Rendered in 3A game cinematic quality, Pixar-level 3D animation CG: PBR materials, subsurface "
      "scattering, soft global illumination. Plain pure WHITE seamless studio backdrop, warm early-morning "
      "golden sunlight raking from the upper left, soft contact shadow under the feet. "
      "Absolutely NO text, NO watermark, NO scenery.")

DA_CG = ("the SAME cute chubby purple dragon exactly as in reference image 1 - identical design: fine detailed "
         "granular reptile SCALES covering the whole vivid purple body, slightly darker purple round spots, TWO "
         "thick golden segmented horns on the head plus ONE small golden nose horn and ONE single row of small "
         "golden cone spikes along neck/back/tail, one pair of big pink inner ears, purple bat wings with "
         "pink-to-orange gradient membranes dotted with darker purple spots, cream-ivory belly and lower jaw, "
         "chunky golden claws, big round golden-amber eyes with white specular highlights, cheerful open smile "
         "with tiny white fangs and a pink tongue, round snout, chibi cute proportions. ")
DB_CG = ("the SAME cute long-necked sauropod exactly as in reference image 1 - identical design: fine detailed "
         "granular reptile SCALES covering the whole slate-blue-grey body, slightly darker blue-grey spots, small "
         "orange cone spikes along neck/back/tail, cream belly, round friendly amber eyes with white highlights, "
         "soft pink inner ears, four stubby legs, a long elegant neck about as long as its torso with a small "
         "head, long tapering tail, NO wings, NO horns. ")
MAN_LOCK = ("the SAME young adult male explorer exactly as in reference image 1 - identical face: short side-swept "
            "brown hair, light stubble; identical outfit and gear: olive-green safari jacket over grey-green tee, "
            "olive cargo pants, brown leather belt with pouches compass and sheathed knife, worn brown boots, large "
            "brown canvas backpack with rolled bedroll, map scroll tubes and coiled rope. ")
GREY_LOCK = ("a tall imposing middle-aged collector airship captain (a DIFFERENT person from reference image 1, "
             "borrow only the Pixar-level CG render quality): long dark charcoal frock coat with brass buttons, "
             "dark leather gloves, tall polished black boots, wide-brim dark hat with brass goggles; in most poses "
             "his face stays completely hidden in shadow under the hat brim; neatly trimmed dark beard and sharp "
             "triumphant grin ONLY in the face-reveal pose; he carries a brass-bound specimen collection case. ")
GRAND_LOCK = ("an elderly male explorer about 70 years old (the same explorer family look as reference image 1 "
              "but aged: the young explorer's grandfather - weathered kind face, full white hair, short white "
              "beard): worn olive safari jacket with leather patches, brown trousers, old brass captain compass "
              "hanging on his chest, gentle wise eyes. ")

A23 = "2:3"
SQ = "1:1"

# (serial, char, file, action_zh, aspect, ref, prompt)  ref: 路徑 | "_prev"
CAST = [
    # ── 雷恩（成年探險家）────────────────────────────
    ("001", "雷恩", "cg_man_stand", "站姿（自信常態）", A23, None, None),
    ("002", "雷恩", "cg_man_crouch", "蹲下驚喜（發現線索）", A23, None, None),
    ("003", "雷恩", "cg_man_kneel", "單膝挖掘", A23, None, None),
    ("004", "雷恩", "cg_man_side", "側身捧發光寶物", A23, None, None),
    ("011", "雷恩", "cg_man_run", "全力奔跑（趕路／追逐）", A23, "_src:cg_man_side.png",
     f"A {MAN_LOCK} Full-body side view sprinting fast with a determined grin, one arm pumping forward, "
     f"backpack bouncing, coiled rope swinging. {CG}"),
    ("012", "雷恩", "cg_man_point", "推理鎖定・指向遠方", A23, "_prev",
     f"A {MAN_LOCK} Full-body 3/4 view standing tall, one arm stretched out pointing far into the distance, "
     f"eyes narrowed with a confident clever smile, the other hand on his belt. {CG}"),
    ("013", "雷恩", "cg_man_map", "展開地圖檢視", A23, "_prev",
     f"A {MAN_LOCK} Full-body 3/4 view standing, both hands holding an open old parchment map, looking down "
     f"at it with focused curious eyes. {CG}"),
    ("014", "雷恩", "cg_man_shock", "驚訝後退一步", A23, "_prev",
     f"A {MAN_LOCK} Full-body front view taking a startled step backward, shoulders raised, eyes wide and "
     f"mouth open in surprise, one hand half-raised. {CG}"),
    ("015", "雷恩", "cg_man_thumbs", "過關歡呼・豎拇指燦笑", A23, "_prev",
     f"A {MAN_LOCK} Full-body 3/4 view standing, beaming bright sunny smile, giving a big thumbs-up with one "
     f"hand, the other hand on his hip. {CG}"),
    ("016", "雷恩", "cg_man_calm", "伸手安撫恐龍", A23, "_prev",
     f"A {MAN_LOCK} Full-body 3/4 view kneeling on one knee, one arm stretched out forward at a small creature's "
     f"head height with an open gentle palm, soft reassuring smile. {CG}"),
    ("017", "雷恩", "cg_man_shardup", "高舉發光碎片（羅盤共鳴）", A23, "_prev",
     f"A {MAN_LOCK} Full-body front view standing, one arm raised high holding up a small glowing rainbow "
     f"crystal shard that emits warm light onto his amazed smiling face. {CG}"),
    ("018", "雷恩", "cg_man_reach", "終章・側身伸手向前（握住格雷）", A23, "_prev",
     f"A {MAN_LOCK} Full-body side profile standing, one arm reaching straight forward at chest height with an "
     f"open welcoming hand, calm warm earnest expression. {CG}"),
    # ── 伴伴（額頭羅盤紋小龍）─────────────────────────
    ("005", "伴伴", "cg_da_stand", "站姿（好奇常態）", SQ, None, None),
    ("006", "伴伴", "cg_da_sniff", "低頭嗅地面", SQ, None, None),
    ("007", "伴伴", "cg_da_cheer", "雙爪歡呼", SQ, None, None),
    ("008", "伴伴", "cg_da_sit", "乖巧坐姿", SQ, None, None),
    ("019", "伴伴", "cg_da_fly", "飛翔（翅膀全開）", SQ, "_src:cg_da_sit.png",
     f"A {DA_CG} flying with wings spread wide and flapping, hind legs tucked up, body slightly tilted upward, "
     f"joyful excited open-mouth smile, full body side view. {CG}"),
    ("020", "伴伴", "cg_da_glow", "額頭羅盤紋發光共鳴", SQ, "_prev",
     f"A {DA_CG} standing upright looking straight ahead in awe, the round compass-shaped pattern on its "
     f"forehead GLOWING bright golden light with soft light rays, eyes wide with wonder. {CG}"),
    ("021", "伴伴", "cg_da_hug", "緊抱彩虹碎片", SQ, "_prev",
     f"A {DA_CG} sitting hugging a small glowing rainbow crystal shard tight against its chest with both front "
     f"paws, eyes closed in a blissful happy smile. {CG}"),
    ("022", "伴伴", "cg_da_sleep", "抱蛋蜷睡（序章）", SQ, "_prev",
     f"A {DA_CG} curled up asleep on its side hugging a pale blue dino egg, eyes closed, gentle peaceful "
     f"smile, wings folded, tail curled around the egg, full body side view. {CG}"),
    ("023", "伴伴", "cg_da_hide", "緊張躲在雷恩腿後", SQ, "_prev",
     f"A {DA_CG} half-hiding: crouched low peeking out from behind an invisible person's legs, only its head "
     f"and one wing visible, ears flattened, nervous wide eyes, small worried frown. {CG}"),
    ("024", "伴伴", "cg_da_angry", "對格雷張翅生氣", SQ, "_prev",
     f"A {DA_CG} standing with wings spread wide and flared, brows lowered, puffing its cheeks in anger, "
     f"pointing one front claw forward accusingly, full body front view. {CG}"),
    ("025", "伴伴", "cg_da_tear", "終章・流淚微笑", SQ, "_prev",
     f"A {DA_CG} sitting with tears of joy welling in its big golden eyes, a warm deeply-moved smile, one paw "
     f"touching its own chest, full body 3/4 view. {CG}"),
    # ── 薩爾塔龍寶寶（愛亮晶晶）──────────────────────
    ("009", "薩爾塔龍", "cg_db_stand", "站姿（叼項鍊得意）", SQ, None, None),
    ("010", "薩爾塔龍", "cg_db_lean", "長頸彎下湊近", SQ, None, None),
    ("026", "薩爾塔龍", "cg_db_necklace", "戴碎片項鍊炫耀", SQ, "_src:cg_db_lean.png",
     f"A {DB_CG} standing tall proudly displaying a small glowing rainbow crystal shard hanging on a braided "
     f"grass cord around its neck like a necklace, head lifted high with a smug delighted smile. {CG}"),
    ("027", "薩爾塔龍", "cg_db_dig", "前肢挖沙", SQ, "_prev",
     f"A {DB_CG} happily digging in sand: front half of the body lowered, both front legs scooping, little "
     f"sand piles flying, tail up, excited open-mouth smile, full body side view. {CG}"),
    ("028", "薩爾塔龍", "cg_db_offer", "讓出碎片（分你一半）", SQ, "_prev",
     f"A {DB_CG} holding out a small glowing rainbow crystal shard on its extended front foot toward the "
     f"viewer, neck lowered in a gentle generous gesture, warm friendly smile. {CG}"),
    ("029", "薩爾塔龍", "cg_db_run", "跟隨奔跑", SQ, "_prev",
     f"A {DB_CG} running at full speed with stubby legs a blur, neck stretched forward, big joyful grin, "
     f"small dust puffs at the feet, full body side view. {CG}"),
    ("030", "薩爾塔龍", "cg_db_bash", "低頭害羞", SQ, "_prev",
     f"A {DB_CG} with its long neck curved down low so its head is near the ground, eyes looking away "
     f"sheepishly, a shy blushing smile, one front foot shuffling. {CG}"),
    ("031", "薩爾塔龍", "cg_db_jump", "躍起歡呼", SQ, "_prev",
     f"A {DB_CG} leaping into the air with all four stubby legs off the ground, neck arched up, mouth wide "
     f"open in a cheer, eyes squeezed shut with joy, full body side view. {CG}"),
    # ── 格雷（收藏家・終章前不露臉）───────────────────
    ("032", "格雷", "cg_grey_back", "背影（飛艇前指揮）", A23, "_refs:gamecg_ref.png",
     f"A {GREY_LOCK} Full-body back view standing with coat tails swaying, one gloved hand raised giving an "
     f"order, looking at an invisible airship. {CG}"),
    ("033", "格雷", "cg_grey_sil", "側影佇立（帽簷遮臉）", A23, "_prev",
     f"A {GREY_LOCK} Full-body pure side profile standing still, hands clasped behind his back, face entirely "
     f"shadowed under the wide hat brim. {CG}"),
    ("034", "格雷", "cg_grey_mega", "手持擴音器（只聞其聲）", A23, "_prev",
     f"A {GREY_LOCK} Full-body 3/4 view holding a brass megaphone up to where his mouth would be behind the "
     f"shadowed hat brim, other hand gesturing grandly. {CG}"),
    ("035", "格雷", "cg_grey_face", "終章・露臉大笑", A23, "_prev",
     f"A {GREY_LOCK} Full-body front view, head lifted so the hat no longer shadows his face: a sharply "
     f"dressed middle-aged man with a neatly trimmed dark beard and a wide surprised-then-moved laugh, eyes "
     f"crinkled, one hand on his chest. {CG}"),
    ("036", "格雷", "cg_grey_hand", "終章・伸出手", A23, "_prev",
     f"A {GREY_LOCK} Full-body side profile standing, one arm reaching straight forward at chest height with "
     f"an open gloved hand, hesitant then sincere posture. {CG}"),
    ("037", "格雷", "cg_grey_pilot", "飛艇駕駛艙坐姿", A23, "_prev",
     f"A {GREY_LOCK} Seated in an invisible seat as if at an airship helm: leaning forward with both gloved "
     f"hands gripping a control yoke, eager predatory grin hidden under the hat brim. {CG}"),
    # ── 雷鐸（爺爺・探險隊隊長）──────────────────────
    ("038", "雷鐸", "cg_grand_young", "年輕隊長站姿（回憶）", A23, "_refs:man_ref.png",
     f"A {GRAND_LOCK} but as his YOUNGER SELF at age 25: same face without wrinkles, dark brown side-swept "
     f"hair like the young explorer in reference image 1, standing tall and heroic with a brass captain "
     f"compass raised in one hand, fearless inspiring smile. {CG}"),
    ("039", "雷鐸", "cg_grand_old", "老年撫羅盤坐姿", A23, "_prev",
     f"A {GRAND_LOCK} sitting on an invisible stool, hunched gently, both hands cradling an old brass compass, "
     f"a nostalgic bittersweet smile, full body 3/4 view. {CG}"),
    ("040", "雷鐸", "cg_grand_back", "背影望海", A23, "_prev",
     f"A {GRAND_LOCK} Full-body back view standing at a shoreline looking out to the sea, coat and white hair "
     f"ruffled by wind, hands clasped behind. {CG}"),
    ("041", "雷鐸", "cg_grand_glow", "回憶・金色投影顯影", A23, "_prev",
     f"A {GRAND_LOCK} Full-body front view standing tall, his whole form rendered as a translucent glowing "
     f"golden hologram made of light particles and soft god rays, serene expression. {CG}"),
    ("042", "雷鐸", "cg_grand_photo", "序章・合影站姿", A23, "_prev",
     f"A {GRAND_LOCK} Full-body 3/4 front view standing straight with one arm around an invisible companion's "
     f"shoulders, proud warm captain's smile, slightly vintage photo posture. {CG}"),
]

CHAR_ORDER = ["雷恩", "伴伴", "薩爾塔龍", "格雷", "雷鐸"]


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


def resolve_ref(ref, prev_src):
    if ref is None:
        return None
    if ref == "_prev":
        return prev_src
    kind, rel = ref.split(":", 1)
    base = {"_src": SRC, "_refs": REFS}[kind]
    return base / rel


only = set(sys.argv[1:])
ok_all = True
prev_src = None
prev_char = None
for serial, char, name, action, aspect, ref, prompt in CAST:
    if prompt is None:            # 已存在定裝，僅編號
        prev_src = SRC / f"{name}.png"
        prev_char = char
        continue
    if char != prev_char:         # 換角色時 _prev 鏈不可沿用
        prev_src = None
    if only and name not in only:
        continue
    out = SRC / f"{name}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{name}: exists, skip", flush=True)
        prev_src = out
        prev_char = char
        continue
    ref_path = resolve_ref(ref, prev_src)
    ref_b64 = flat_png(ref_path) if ref_path and Path(ref_path).exists() else None
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
        prev_src = out
        prev_char = char
    else:
        ok_all = False
        print(f"{name}: ALL_FAILED", flush=True)

manifest = [{"serial": s, "char": c, "file": f, "action": a, "prompt": p or "(Phase 1 已存在)"}
            for s, c, f, a, _asp, _r, p in CAST]
MANIFEST.write_text(json.dumps({"char_order": CHAR_ORDER, "cast": manifest},
                               ensure_ascii=False, indent=1), encoding="utf-8")
print("MANIFEST_WRITTEN", flush=True)
print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
