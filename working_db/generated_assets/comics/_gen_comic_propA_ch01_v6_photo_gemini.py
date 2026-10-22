# -*- coding: utf-8 -*-
"""方案A第1話 v6：攝影寫真變體（photo）六格生成（Gemini）

用戶 2026-10-22 指示（第 10 輪回饋後改道）：
- 棄 SophNet/Wan 油畫線；改用 Gemini 重跑六格。
- 風格＝變體 photo「攝影寫真」：85mm 人像鏡雜誌級攝影、真實男孩、
  恐龍＝收藏級玩具立在真實沙灘（沿用 _gen_kid_style_variants.py 的 photo 文案，用戶已看過認可）。
- 跨格一致：每格內嵌伴伴2star＋薩爾塔9.webp 參考圖；P1 完成後其縮圖作為第三張
  「同男孩同龍」連鎖參考餵給 P2–P6；角色 LOCK 用第 9 輪 canonical 數值（深紫斑點）。

用法：python _gen_comic_propA_ch01_v6_photo_gemini.py [pN ...]（無參數=全部；已存在則跳過）
"""
import base64, io, json, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
REPO = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
RAW = HERE / "_raw"
RAW.mkdir(exist_ok=True)

BBAN_SRC = REPO / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_2star.png"
SALTA_SRC = REPO / "game_db" / "assets" / "dinos" / "9.webp"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]
RATIO = "4:3"

STYLE = ("High-end editorial photography composite at magazine quality, shot on an 85mm portrait lens: "
         "the human boy is a real photograph - DSLR sharpness, natural sunlight, true-to-life colors, shallow "
         "depth of field with creamy bokeh, real sand grains and fabric fibers visible. The stylized baby "
         "dragons stand on the photographed sand like real physical collectible vinyl toys come to life, with "
         "studio-grade lighting, soft realistic contact shadows and sand interaction, keeping their exact "
         "reference designs. The beach is real location photography. ")

KID = ("a real 10-year-old East Asian boy photographed with an 85mm portrait lens: tack-sharp pore-level skin "
       "detail, visible skin texture and tiny blemishes, natural catchlights in dark-brown eyes, realistic "
       "wind-touched short dark-brown hair with straight bangs; wearing a khaki safari hat, cream sleeveless "
       "vest over an orange T-shirt, brown shorts, sturdy brown boots and a small green backpack - every fabric "
       "fiber visible")

LOCK = (
    "CHARACTER LOCK (strict, identical in every panel): "
    "Dragon A = the baby dragon in reference image 1, reproduced EXACTLY - a chubby VIVID PURPLE baby dragon "
    "with slightly darker PURPLE round spots on head/back/haunches, very large round GOLDEN-AMBER eyes with big "
    "white specular highlights, EXACTLY ONE pair of thick golden-yellow segmented horns on the head plus ONE "
    "single row of small golden cone spikes along the neck, back and tail, large purple bat-style wings whose "
    "membranes gradient from magenta-pink at the leading edge to warm orange at the trailing edge, dotted with "
    "round DARK-PURPLE spots, ONE pair of big PINK inner ears, cream-ivory belly plates, chunky golden-yellow "
    "claws, round snout with nostrils, cheerful open smile with tiny white fangs and pink tongue. Identical "
    "colors, markings, proportions and face in every panel; only pose and expression may change. "
    "Dragon B = a baby long-necked sauropod toy: a slate-blue-grey satin body carrying small orange cone "
    "spikes along its neck, back and tail, a cream belly, round friendly amber eyes with white catchlights, "
    "soft pink inner ears, four stubby legs, a long elegant neck about as long as its torso with a small "
    "head, and a long tapering tail. It has NO wings and NO horns - never give it bat wings. Its colors "
    "follow reference image 2 (slate-grey body, orange spikes, pink inner ears) but its body form is the "
    "long-necked sauropod described here, NOT the coiled pose of the reference photo; keep its neck "
    "length, head size and body proportions identical in every panel. "
    "Never recolor or redesign either dragon; reference image 3 (when present) shows the same boy and "
    "the same two dragons rendered in this exact photographic style - keep them identical to it. "
)

NEG = ("Absolutely NO text, NO speech bubbles, NO letters, NO sound-effect lettering, NO watermark, NO panel "
       "borders, NO toy packaging, NO price tags. Landscape composition.")

PANELS = [
    dict(id=1, refs=("bban",), prompt=(
        f"Early-morning establishing wide panoramic shot on a real golden tropical beach, editorial travel "
        f"photography. {KID} walks along the shoreline toward an old shipwrecked wooden supply crate half-buried "
        f"in the sand, reinforced with iron straps and faded rainbow paint, a few smaller crates scattered behind "
        f"the dunes. Dragon A trots happily beside the boy like a living collectible toy. IMPORTANT COMPOSITION: "
        f"keep the boy's full body, hat and the dragon entirely inside the vertical MIDDLE band of the frame - "
        f"place their heads and feet well away from the top and bottom edges, with open sky above and open sand "
        f"below, so the scene survives a wide horizontal strip crop. Gentle turquoise waves, seabirds crossing the "
        f"pale sunrise sky, long soft shadows, both characters seen from a three-quarter back view.")),
    dict(id=2, refs=("bban",), prompt=(
        f"Close-up discovery beat on the photographed beach, creamy bokeh background. Dragon A presses its nose "
        f"deep into the real sand sniffing intensely, eyes squeezed then popping wide in surprise; a corner of a "
        f"RAINBOW-COLORED HEXAGONAL crystal shard - a broken piece of a compass, NOT a round dial - peeks out of "
        f"the sand right in front of its nose with bright sparkle effects. {KID} crouches just behind, leaning in "
        f"close with curious wide eyes and an amazed open-mouth smile. Warm morning sunlight.")),
    dict(id=3, refs=("bban", "salta"), prompt=(
        f"Funny comedy beat on the beach, photographed like a magazine lifestyle spread. Dragon B now wears the "
        f"rainbow-colored hexagonal crystal shard as a shiny pendant on a cord around its long neck, chin raised, "
        f"smug and proud, basking in the sun. {KID} and Dragon A stand at the side comically stunned: the boy "
        f"sweat-dropping with mouth open in mid-protest, Dragon A's jaw dropped. Sand dunes and driftwood in the "
        f"softly blurred background, bright daylight.")),
    dict(id=4, refs=("bban", "salta"), prompt=(
        f"Deduction scene on the beach, warm mid-morning light, shallow depth of field. {KID} kneels drawing "
        f"circles and arrows in the real sand with a small stick, explaining with a confident grin; in the far "
        f"blurred background near the waterline stands a row of small sandcastles and one BIG impressive "
        f"sandcastle. Dragon A listens with head tilted and one paw raised as if understanding. Dragon B leans in "
        f"curiously from the other side, its long neck curving gracefully down to sand level.")),
    dict(id=5, refs=("bban", "salta"), prompt=(
        f"Treasure-dig climax beside the big sandcastle, joyful energy, a little spray of sand, sparkling ocean "
        f"behind. {KID} pulls the RAINBOW-COLORED HEXAGONAL crystal shard free from the sand and it glints with "
        f"rainbow light; Dragon A cheers with both paws raised; Dragon B happily nudges the shard toward the boy "
        f"with its snout as if offering it. Rainbow light reflections on real sand, photographed like an "
        f"adventure-magazine cover moment.")),
    dict(id=6, refs=("bban",), prompt=(
        f"Heart-warming close-up finale, blurred golden sea horizon with gentle bokeh sparkles behind. The hands "
        f"of {KID} hold the glowing RAINBOW-COLORED HEXAGONAL crystal shard up against the morning sun with a "
        f"soft lens flare; Dragon A perches on the boy's shoulder, eyes shining, both smiling at each other. "
        f"Emotional warm editorial tone, tack-sharp foreground, dreamy background.")),
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


def chain_ref():
    p1 = RAW / "propA_ch01_v6_p1.png"
    if not p1.exists():
        return None
    im = Image.open(p1).convert("RGB")
    im.thumbnail((1024, 1024), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def call(model, prompt, ref_imgs, aspect=True):
    parts = [{"text": prompt}]
    for b64 in ref_imgs:
        parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})
    gc = {"responseModalities": ["IMAGE"]}
    if aspect:
        gc["imageConfig"] = {"aspectRatio": RATIO}
    body = {"contents": [{"parts": parts}], "generationConfig": gc}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts_out if "inlineData" in p), None)
    return (base64.b64decode(img) if img else None), ("no image part" if not img else "ok")


only = {int(a) for a in sys.argv[1:] if a.isdigit()}
ok_all = True
for p in PANELS:
    if only and p["id"] not in only:
        continue
    out = RAW / f"propA_ch01_v6_p{p['id']}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"p{p['id']}: exists, skip", flush=True)
        continue
    ref_imgs = [REFS[k] for k in p["refs"]]
    chain = chain_ref() if p["id"] > 1 else None
    if chain:
        ref_imgs = ref_imgs + [chain]
    prompt = f"{STYLE} {LOCK} {p['prompt']} {NEG}"
    got = None
    for model in MODELS:
        for aspect in (True, False):
            img, msg = call(model, prompt, ref_imgs, aspect)
            if img:
                got = img
                print(f"p{p['id']}: OK via {model} aspect={aspect} ({len(img)} bytes)", flush=True)
                break
            print(f"p{p['id']}: fail {model} aspect={aspect} -> {msg}", flush=True)
        if got:
            break
        time.sleep(2)
    if got:
        out.write_bytes(got)
    else:
        ok_all = False
        print(f"p{p['id']}: ALL_FAILED", flush=True)

print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
