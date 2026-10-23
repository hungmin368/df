# -*- coding: utf-8 -*-
"""v7 篇章嘉賓恐龍定裝產線（流水號 043 起，依 _cast_manifest.json 續編）。

每隻 6 張、動作對應其在該篇的劇情（見全篇分鏡腳本報告的篇章嘉賓速查表）。
造型以文字鎖定物種特徵（沿用 3A-CG 皮膚質感），首張參考 _refs/gamecg_ref.png 定渲染質感，
之後鏈式凍結。批次：A=第二、三篇（043–096），B=第四、五篇（097–120），C=第六、七篇（121–156）。
執行：python _gen_guests_v7.py [A|B|C|all]（預設 all；已存在跳過，可安全重跑）
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
QUAL = ("a cute chibi 3D CG creature with fine detailed granular reptile SCALES, big round golden-amber eyes "
        "with white specular highlights, cheerful expressive face, chunky proportions "
        "(borrow only this Pixar-level render quality from the reference image). ")

LOCKS = {
    "tri_baby": ("a cute baby triceratops: mint-green scaly body, ONE tiny blunt nose horn and TWO tiny brow "
                 "horns, a small rounded neck frill with soft orange rim, big round eyes, stubby legs. "),
    "tri_mom": ("a gentle mother triceratops: deep forest-green scaly body, THREE stout horns, a large neck "
                "frill with cream markings, warm patient eyes, massive sturdy body. "),
    "ptero_mom": ("a mother pterosaur: soft blue-grey scaly body, a long crest curving back from her head, "
                  "leathery wings with pink membranes, kind amber eyes, small beak with no teeth. "),
    "emu": ("a cute oviraptor-like running dinosaur: sandy-yellow scaly body with brown stripes, a short "
            "toothless beak, a small head crest, long slender running legs, long tail. "),
    "pachy": ("a cute pachycephalophosaurus: warm ochre scaly body with cream belly, a thick rounded bony "
              "dome on top of the head with small spikes at the back, short snout, stocky body. "),
    "tree_dw": ("a cute tree-dwelling small gliding dinosaur: jade-green scaly body, big dark eyes adapted to "
                "night, soft gliding membrane wings between limbs, a long balancing tail, tiny claws. "),
    "compso": ("a tiny cute compsognathus: bright yellow-green scaly body, big curious eyes, a long thin tail, "
               "slender hind legs, small clawed arms, chirpy expression. "),
    "spino": ("a majestic yet friendly spinosaurus: deep blue-grey scaly body, a tall sail on the back with "
              "orange rippled pattern, a long crocodile-like snout, strong arms, calm station-master dignity. "),
    "digger": ("a cute digging dinosaur: dusty brown scaly body, strong short front claws made for digging, a "
               "small horn on the snout, round hoarding eyes, compact body. "),
    "carno": ("a sturdy carnotaurus sheriff: vibrant crimson scaly body, TWO short thick horns above the eyes, "
              "a stocky build, a shiny brass star badge on a leather strap across the chest, upright proud "
              "posture, firm kind eyes. "),
    "alberto": ("a friendly albertosaurus snow-patroller: icy blue-grey scaly body with white belly, small "
                "crest above the eyes, a warm energetic smile, light snow-dusted shoulders. "),
    "ovi": ("a sneaky cute oviraptor thief: rust-orange scaly body with a tall head crest, feathered arms, a "
            "long tail, sly but lovable grin. "),
    "quetzal": ("an elegant quetzalcoatlus sister: snow-white scaly body with gold-tipped long head crest, "
                "wide majestic wings with pale gold membranes, serene confident eyes. "),
    "emp": ("a colossal super-emperor dragon dinosaur: imperial gold-and-deep-violet scaly body, a crown of "
            "golden horns, huge wise eyes, massive yet dignified body with wing-like arm frills. "),
    "trex": ("a mighty but friendly tyrannosaurus: earthy brown scaly body with cream belly, tiny two-fingered "
             "arms, huge head with a toothy good-natured grin. "),
    "spino_king": ("an elderly spinosaurus blacksmith king: charcoal-dark scaly body, a tall worn sail with "
                   "ember-orange glow at the edges, a long snout, muscular arms, wise stern kind eyes. "),
    "dunhuang": ("a wise dunhuanglong caravan elder: sand-gold scaly body with painted mural-like spiral "
                 "patterns in red and jade, a calm merchant smile, saddle bags on the back. "),
    "haiwang": ("a noble marine pliosaur king: deep teal scaly body with a white underbelly, four powerful "
                "flippers, a long head with interlocking teeth closed in a regal smile, coral-gold crown "
                "ridge on the head. "),
    "plesio": ("a graceful plesiosaur: smooth turquoise scaly body, four diamond-shaped flippers, a small head "
               "on a long elegant curved neck, gentle eyes. "),
}

POSES = {
    "tri_baby": [("迷路哭泣", "sitting down crying loudly with big tears, mouth wailing, looking around lost"),
                 ("破涕為笑", "breaking into a sunny smile with dried tears, jumping with joy"),
                 ("跟隨奔跑", "trotting happily, tail bouncing"),
                 ("埋頭吃草", "head down munching a mouthful of grass, cheeks stuffed"),
                 ("依偎", "nuzzling against an invisible large companion's leg, eyes closed content"),
                 ("崇拜抬頭", "looking straight up in awe and admiration, eyes sparkling")],
    "tri_mom": [("溫柔俯身", "lowering her huge head gently down to nuzzle, soft eyes"),
                ("警戒護崽", "stepping in front protectively, horns lowered, fierce watchful eyes"),
                ("感激低頭", "bowing her head deeply in gratitude, eyes closed"),
                ("陪伴前行", "walking calmly side by side"),
                ("呼喚", "lifting her head calling out with open mouth, gentle expression"),
                ("奔馳", "charging forward at full gallop, dust at the feet")],
    "ptero_mom": [("巢中孵蛋", "sitting on a nest hugging a glowing rainbow crystal shard tucked under her "
                    "wings as if it were an egg, protective gentle eyes"),
                  ("飛翔護送", "soaring with wings fully spread, looking back kindly"),
                  ("降落", "gliding down with wings spread wide and legs reaching forward to land"),
                  ("警戒張翼", "standing with wings spread wide and beak open in a warning cry"),
                  ("溫柔注視", "perched, tilting her head down with a warm motherly gaze"),
                  ("收翅休息", "folded wings, dozing peacefully, beak tucked")],
    "emu": [("賽跑衝刺", "sprinting at top speed leaning forward, wind lines, determined grin"),
            ("捉迷藏探頭", "peeking out from behind an invisible rock, one eye covered by a wing tip"),
            ("三兄弟疊羅漢", "THREE of the same dinosaur stacked in a totem pole: one standing, one on its "
             "shoulders, one on top waving - identical triplets"),
            ("得意叉腰", "standing proudly with wings on hips, chest puffed, smug grin"),
            ("啄食種子", "pecking seeds off the ground, tail up"),
            ("驚訝跳起", "jumping back startled, wings flapping, beak wide open")],
    "pachy": [("頭槌頂碎石", "headbutting a cracked rock, pebbles flying, eyes squeezed shut"),
              ("抱頭喊痛", "holding its dome head with both hands, wincing in comic pain"),
              ("驕傲挺胸", "thumping its chest proudly with one hand, beaming"),
              ("貼石聽回音", "pressing its dome ear against a rock surface, listening carefully with a sly smile"),
              ("奔跑", "running with head lowered ready to ram, determined"),
              ("微笑讓路", "stepping aside with a polite welcoming gesture, gentle smile")],
    "tree_dw": [("倒掛樹枝", "hanging upside down from an invisible branch by its feet, wings folded, waving"),
                ("滑翔", "gliding with membrane wings spread, mid-air, joyful"),
                ("捧螢菇燈", "holding a glowing mushroom lamp with both hands, lighting its own smile"),
                ("霧中指路", "pointing one wing forward into fog, serious helpful expression"),
                ("微笑", "perched upright with a soft knowing smile"),
                ("鞠躬", "bowing deeply with wings crossed on chest, respectful")],
    "compso": [("受困哭哭", "crouched trembling, tears welling, squeaking for help"),
               ("獲救擁抱", "hugging an invisible rescuer's finger with both arms, eyes closed in relief"),
               ("開心轉圈", "spinning in place gleefully, tail whirling"),
               ("躲葉子下", "hiding under a big leaf held above its head, peeking out"),
               ("跟隨", "trotting after something with eager chirpy hops"),
               ("大笑", "head thrown back laughing heartily, mouth wide open")],
    "spino": [("沉穩站姿", "standing tall and calm with hands clasped behind, station-master dignity"),
              ("溫泉閉目", "soaking contentedly in an invisible hot spring up to the shoulders, eyes closed "
               "serene smile"),
              ("指路", "extending one arm showing the direction, reassuring nod"),
              ("憂慮望潭", "looking down at water with worried knowing eyes, sail drooping slightly"),
              ("怒吼護潭", "roaring with jaws wide open, sail fully raised, protective fury"),
              ("低音唱歌", "eyes closed humming a deep tune, gentle ripples drawn at the feet")],
    "digger": [("搬石頭", "carrying a big stone hugged to the chest, waddling"),
               ("巢中囤積", "sitting in a nest of piled shiny stones hugging a glowing rainbow crystal shard, "
                "possessive happy grin"),
               ("被發現驚訝", "frozen mid-dig, head snapped up, wide guilty eyes"),
               ("讓出寶物", "pushing the glowing shard forward with both claws, reluctant but sincere"),
               ("挖掘", "digging energetically, dirt flying backward"),
               ("害羞", "toeing the ground, claws together, blushing smile")],
    "carno": [("警長站姿", "standing upright with thumbs hooked on the belt, brass star badge gleaming, firm "
               "kind eyes"),
              ("指揮交通", "raising one arm directing firmly, commanding but fair"),
              ("低聲訴說", "leaning close, one hand cupped beside the mouth telling a secret softly"),
              ("奔跑追緝", "charging after something with badge bouncing, determined"),
              ("敬礼", "saluting sharply with a respectful smile"),
              ("溫柔注視", "looking down softly at an invisible child, tough-guy tenderness")],
    "alberto": [("雪巡站姿", "standing proud with a green patrol scarf, snow-dusted shoulders, warm grin"),
                ("挖雪救援", "digging snow with both arms flying, urgent hopeful eyes"),
                ("極光下昂首", "looking up at the sky in awe, bathed in imagined aurora glow, smiling"),
                ("合影摟肩", "draping an arm around an invisible friend's shoulders, photobomb grin"),
                ("滾雪球", "pushing a huge snowball bigger than itself, tongue out in effort"),
                ("道別揮手", "waving both arms high with a big farewell smile")],
    "ovi": [("潛行", "sneaking on tiptoes, body low, sly sideways glance"),
            ("抱蛋偷笑", "hugging a swiped egg, stifling a giggle"),
            ("機關操作", "pulling an invisible lever with both hands, tongue out concentrating"),
            ("被抓包舉手", "frozen with both hands raised in surrender, sheepish grin"),
            ("分贓炫耀", "proudly presenting a pile of shiny loot"),
            ("改過鞠躬", "bowing apologetically with the loot offered back, sincere")],
    "quetzal": [("雲端站姿", "standing on an invisible cloud edge, wings folded elegantly, serene"),
                ("試煉宣佈", "one wing raised in proclamation, noble commanding gaze"),
                ("高空護送", "soaring upward carrying an invisible passenger on her back, protective"),
                ("三姊妹合舞", "THREE identical sisters flying in formation, wings overlapping gracefully"),
                ("微笑頷首", "a gentle approving nod with a soft smile"),
                ("逆光剪影", "backlit pose with wings spread wide and crest glowing rim light")],
    "emp": [("王座站姿", "standing colossal with arms crossed, crown of golden horns gleaming, supreme "
             "dignity"),
            ("俯視群山", "looking down from a great height pose, vast wings half-spread, contemplative"),
            ("讓道", "stepping aside and lowering the head, granting passage with grace"),
            ("注視試煉", "leaning forward observing intently with wise evaluating eyes"),
            ("點頭認可", "a slow solemn approving nod, slight warm smile"),
            ("雲上背影", "massive back view standing above clouds, wings folded, golden rim light")],
    "trex": [("吼叫", "roaring with jaws wide open, tiny arms flapping, mighty but friendly"),
             ("讓路上山道", "stepping aside and gesturing an arm forward politely, toothy grin"),
             ("小短手搆不到", "struggling to reach its own back with tiny arms, comic frustration"),
             ("打瞌睡", "dozing standing up, wobbling, mouth slightly open"),
             ("奔跑", "thundering run, earth-shaking stomps, focused eyes"),
             ("溫柔鼻尖輕觸", "lowering its huge head to gently touch noses with an invisible small friend, "
              "eyes soft")],
    "spino_king": [("鍛造站姿", "standing at an invisible anvil with a hammer on the shoulder, ember-lit "
                    "stern kind face"),
                   ("淬火焰中凝視", "gazing into flames with reflected firelight in the eyes, ominous wisdom"),
                   ("幻象灰白驚覺", "rearing back from a greyscale fading vision, shielding eyes"),
                   ("點燃爐心", "both hands raised kindling a blazing core of light above, triumphant"),
                   ("撫背安慰", "one huge hand gently patting an invisible companion's back"),
                   ("交托重任", "holding out a glowing shard on both palms, solemn entrusting gaze")],
    "dunhuang": [("商隊站姿", "standing with saddle bags and a merchant staff, wise hospitable smile"),
                 ("斷後阻敵", "rearing up blocking the way with staff planted, brave protective"),
                 ("指點水路", "pointing at an underground waterway map, instructing"),
                 ("駝隊前行", "walking with a caravan stride, bells implied, calm"),
                 ("講古", "sitting telling an old tale with one hand raised mid-gesture"),
                 ("合掌祝福", "palms together in a blessing bow, serene")],
    "haiwang": [("開潮門", "rearing up with flippers spread commanding the tide gates to open, majestic"),
                ("護送游弋", "cruising with neck curved in a regal S, escorting"),
                ("水晶宮站姿", "standing guard before an invisible crystal palace, noble"),
                ("怒吼破浪", "roaring with jaws open, water bursting around, kingly fury"),
                ("低頭致謝", "bowing the long head in gratitude"),
                ("沉睡守門", "coiled asleep around a gate post, peaceful guardian")],
    "plesio": [("優雅游弋", "gliding with flippers spread, neck in a gentle curve, serene"),
               ("列隊敬禮", "holding a flipper up in a neat salute, playful"),
               ("探頭好奇", "craning the small head forward curiously at something"),
               ("載客護送", "carrying invisible passengers on the back, careful gentle swim pose"),
               ("轉圈舞蹈", "twirling the body in a spiral dance, joyful"),
               ("噴水嬉笑", "spouting an imagined water fountain from the mouth, laughing")],
}

CHAR_META = {
    "tri_baby": ("小三角龍", "第二篇・迷路事件主角，哭著追丟隊伍的小傢伙。"),
    "tri_mom": ("三角龍媽媽", "第二篇・平原賽區評審，挑剔但溫柔的媽媽。"),
    "ptero_mom": ("無齒翼龍媽媽", "第二篇・把彩虹碎片當蛋孵的翼龍媽媽。"),
    "emu": ("似鴯鶓龍三兄弟", "第二篇・草原捉迷藏賽的對手，搞笑擔當三胞胎。"),
    "pachy": ("腫頭龍", "第二篇・回音谷守門人，『腦袋清楚的傢伙才能進』。"),
    "tree_dw": ("樹息龍", "第三篇・霧林掌燈一族，夜視導航。"),
    "compso": ("小美頜龍", "第三篇・被困霧中的小家伙，救援對象。"),
    "spino": ("棘龍", "第三篇・月光沼澤守潭站長，外冷內熱。"),
    "digger": ("掘龍", "第三篇・愛收集石頭的『水裡住戶』，碎片六持有者。"),
    "carno": ("食肉牛龍警長", "第四篇・峽谷警長，探險隊恐龍夥伴的後代。"),
    "alberto": ("艾伯塔龍", "第四篇・雪嶺雪巡隊，熱情到可怕的地主選手。"),
    "ovi": ("竊蛋龍盜團", "第五篇・王陵機關攻防的對手，亦敵亦友。"),
    "quetzal": ("風神翼龍三姊妹", "第五篇・雲海神殿守門人，風之試煉考官。"),
    "emp": ("超帝王龍", "第六篇・巔峰守門王者，最終試煉主考官。"),
    "trex": ("霸王龍", "第六篇・巔峰王者群像，讓出上山道。"),
    "spino_king": ("棘龍王", "第六篇・熔火龍穴鍛造師，火焰試煉引路人。"),
    "dunhuang": ("敦煌龍商隊", "第七篇・流沙王陵商隊長，斷後護航。"),
    "haiwang": ("海霸龍", "第七篇・碧海龍宮海王者，開啟潮門。"),
    "plesio": ("蛇頸龍（海王者列隊）", "第七篇・龍宮護衛隊代表（滑齒龍、海王龍共用此列隊造型）。"),
}

BATCHES = {
    "A": ["tri_baby", "tri_mom", "ptero_mom", "emu", "pachy", "tree_dw", "compso", "spino", "digger"],
    "B": ["carno", "alberto", "ovi", "quetzal"],
    "C": ["emp", "trex", "spino_king", "dunhuang", "haiwang", "plesio"],
}

START_SERIAL = {"A": 43, "B": 97, "C": 121}


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


which = sys.argv[1] if len(sys.argv) > 1 else "all"
groups = list(BATCHES) if which == "all" else [which]

# 建立 流水號→key 對照（依 CAST 順序同批內遞增）
jobs = []          # (serial, key, file, action, prompt)
for g in groups:
    serial = START_SERIAL[g]
    for key in BATCHES[g]:
        zh_name, desc = CHAR_META[key]
        for idx, (pose_zh, pose_en) in enumerate(POSES[key], 1):
            file = f"{key}_p{idx:02d}"
            prompt = (f"A {LOCKS[key]}{QUAL} full body, {pose_en}. {CG}")
            jobs.append((serial, key, zh_name, desc, file, pose_zh, prompt))
            serial += 1

# 並依既有 manifest 的既有流水號遞增（若已跑過一部份）
data = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"char_order": [], "cast": []}
done_serials = {int(r["serial"]) for r in data["cast"]}
jobs = [j for j in jobs if j[0] not in done_serials]

ok_all = True
ref_quality = flat_png(REFS / "gamecg_ref.png")
prev = None
for serial, key, zh_name, desc, file, pose_zh, prompt in jobs:
    out = SRC / f"{file}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{file}: exists, skip", flush=True)
        prev = out
        continue
    ref_b64 = flat_png(prev) if prev else ref_quality
    got = None
    for model in MODELS:
        img, msg = call(model, prompt, ref_b64, "1:1")
        if img:
            got = img
            print(f"{serial} {file}: OK via {model} ({len(img)} bytes)", flush=True)
            break
        print(f"{serial} {file}: fail {model} -> {msg}", flush=True)
        time.sleep(2)
    if got:
        out.write_bytes(got)
        prev = out
        data["cast"].append({"serial": f"{serial:03d}", "char": zh_name, "file": file,
                             "action": pose_zh, "prompt": prompt, "desc": desc})
        if zh_name not in data["char_order"]:
            data["char_order"].append(zh_name)
        MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        ok_all = False
        print(f"{serial} {file}: ALL_FAILED", flush=True)

print("DONE_OK" if ok_all else "DONE_PARTIAL", flush=True)
