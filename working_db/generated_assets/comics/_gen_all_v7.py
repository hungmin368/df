# -*- coding: utf-8 -*-
"""v7 全角色定裝總產線（規則改版 2026-10-23：恐龍一律以遊戲既有圖為造型錨）。

用戶規則：
1. 登場恐龍角色必須按照遊戲現有恐龍圖片製作，不可重新設計造型；
2. 每個角色至少含 正面／左側面／右側面／背面／跑步／走路 六張基本定裝；
3. 生成後逐角色檢查體型比例、臉部、特徵一致性。

做法：每個角色的每一張 pose 都掛同一張「造型錨」（遊戲圖或既有定裝圖）當參考圖 1，
提示詞強制「同一個體、同樣配色花紋、同樣臉部特徵」，以錨定圖自身保證跨張一致性。

流水號配置（共 298 張）：
001-018 雷恩   （001-006 基本六姿新製；007-018 既有 12 張）
019-035 伴伴   （019-024 基本六姿新製；025-035 既有 11 張）
036-047 薩爾塔龍（12 張全新＝六姿＋劇情動作，錨定 game_db/assets/dinos/9.webp）
048-059 格雷   （048-053 基本六姿新製；054-059 既有 6 張）
060-070 雷鐸   （060-065 老年基本六姿新製；066-070 既有 5 張）
071-298 篇章嘉賓 19 組×12（六姿＋劇情動作，各錨定其遊戲圖）

執行：python _gen_all_v7.py [manifest|core|g1|g2|g3|all]
  manifest＝只重建 _cast_manifest.json；其餘＝重建後生成對應批次（已存在自動跳過，可安全重跑）。
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
ROOT = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
SRC = HERE / "_raw" / "_masters" / "_src"
MANIFEST = HERE / "_cast_manifest.json"
G_DINOS = ROOT / "game_db" / "assets" / "dinos"
G_DINOS2 = ROOT / "game_db" / "assets" / "dinos_2"

MODELS = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"]

CANON = [
    ("正面", "standing FRONT view facing the camera, full body visible, head turned to look at the viewer"),
    ("左側面", "LEFT-side profile view, full body visible, facing to the left"),
    ("右側面", "RIGHT-side profile view, full body visible, facing to the right"),
    ("背面", "BACK view seen directly from behind, full body visible"),
    ("跑步", "RUNNING mid-stride in a dynamic side view, full of energy"),
    ("走路", "WALKING mid-step in a relaxed side view"),
]
CANON_SWIM = CANON[:4] + [
    ("快速游動", "fast SWIMMING pose gliding through water with a sense of motion, full body side view"),
    ("緩慢游動", "slowly CRUISING underwater in a calm graceful glide, full body side view"),
]

DINO_IDENT = ("Draw the exact same dinosaur as reference image 1: keep the identical body color, markings, "
              "proportions, face, eyes and every feature — a character turnaround of the SAME individual in "
              "the SAME art style as the reference. ")

# 篇章嘉賓：(key, 遊戲圖 id, 中文名, 簡介, 額外造型指令)
GUESTS = [
    ("tri_baby", 21, "小三角龍", "第二篇・迷路事件主角，哭著追丟隊伍的小傢伙（造型＝遊戲三角龍的幼體）。", "This is a BABY of the reference species: keep the same body colors and markings as reference image 1, but as a small chubby juvenile with an oversized head and big round eyes. "),
    ("tri_mom", 21, "三角龍媽媽", "第二篇・平原賽區評審，挑剔但溫柔的媽媽。", ""),
    ("ptero_mom", 300, "無齒翼龍媽媽", "第二篇・把彩虹碎片當蛋孵的翼龍媽媽。", ""),
    ("emu", 69, "似鴯鶓龍三兄弟", "第二篇・草原捉迷藏賽的對手，搞笑擔當三胞胎（造型＝遊戲似鴯鶓龍）。", ""),
    ("pachy", 101, "腫頭龍", "第二篇・回音谷守門人，『腦袋清楚的傢伙才能進』。", ""),
    ("tree_dw", 135, "樹息龍", "第三篇・霧林掌燈一族，夜視導航。", ""),
    ("compso", 83, "小美頜龍", "第三篇・被困霧中的小家伙，救援對象（造型＝遊戲美頜龍的幼體）。", "This is a small juvenile of the reference species: same colors as reference image 1, tiny body. "),
    ("spino", 202, "棘龍", "第三篇・月光沼澤守潭站長，外冷內熱。", ""),
    ("digger", 212, "掘龍", "第三篇・愛收集石頭的『水裡住戶』，碎片六持有者。", ""),
    ("carno", 121, "食肉牛龍警長", "第四篇・峽谷警長，探險隊恐龍夥伴的後代。", "Add ONLY a small brass sheriff star badge on a strap across the chest; change nothing else about the dinosaur. "),
    ("alberto", 117, "艾伯塔龍", "第四篇・雪嶺雪巡隊，熱情到可怕的地主選手。", "Add ONLY a green patrol scarf around the neck; change nothing else about the dinosaur. "),
    ("ovi", 67, "竊蛋龍盜團", "第五篇・王陵機關攻防的對手，亦敵亦友。", ""),
    ("quetzal", 301, "風神翼龍三姊妹", "第五篇・雲海神殿守門人，風之試煉考官。", ""),
    ("emp", 272, "超帝王龍", "第六篇・巔峰守門王者，最終試煉主考官。", ""),
    ("trex", 260, "霸王龍", "第六篇・巔峰王者群像，讓出上山道。", ""),
    ("spino_king", 324, "棘龍王", "第六篇・熔火龍穴鍛造師，火焰試煉引路人。", ""),
    ("dunhuang", 244, "敦煌龍商隊", "第七篇・流沙王陵商隊長，斷後護航。", "Add ONLY small saddle bags on the back; change nothing else about the dinosaur. "),
    ("haiwang", 286, "海霸龍", "第七篇・碧海龍宮海王者，開啟潮門。", "Add ONLY a small coral-gold crown on the head; change nothing else about the dinosaur. "),
    ("plesio", 276, "蛇頸龍（海王者列隊）", "第七篇・龍宮護衛隊代表（滑齒龍、海王龍共用此列隊造型）。",
     "Keep the slate-navy blue body, cyan diamond/lightning markings, small golden nose horn, pink inner ears and "
     "big amber eyes exactly as in reference image 1, same cute chibi proportions; never lighten the body color. "),
]
MARINE = {"haiwang", "plesio"}

# 劇情動作（沿用已寫好的分鏰對應；編號 p07-p12）
THEMATIC = {
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
    "ptero_mom": [("巢中孵蛋", "sitting on a nest hugging a glowing rainbow crystal shard tucked under her wings as if it were an egg, protective gentle eyes"),
                  ("飛翔護送", "soaring with wings fully spread, looking back kindly"),
                  ("降落", "gliding down with wings spread wide and legs reaching forward to land"),
                  ("警戒張翼", "standing with wings spread wide and beak open in a warning cry"),
                  ("溫柔注視", "perched, tilting her head down with a warm motherly gaze"),
                  ("收翅休息", "folded wings, dozing peacefully, beak tucked")],
    "emu": [("賽跑衝刺", "sprinting at top speed leaning forward, wind lines, determined grin"),
            ("捉迷藏探頭", "peeking out from behind an invisible rock, one eye covered by a wing tip"),
            ("三兄弟疊羅漢", "THREE identical copies of the same dinosaur stacked in a totem pole: one standing, one on its shoulders, one on top waving"),
            ("得意叉腰", "standing proudly with wings on hips, chest puffed, smug grin"),
            ("啄食種子", "pecking seeds off the ground, tail up"),
            ("驚訝跳起", "jumping back startled, wings flapping, beak wide open")],
    "pachy": [("頭槌頂碎石", "headbutting a cracked rock, pebbles flying, eyes squeezed shut"),
              ("抱頭喊痛", "holding its dome head with both hands, wincing in comic pain"),
              ("驕傲挺胸", "thumping its chest proudly with one hand, beaming"),
              ("貼石聽回音", "pressing its dome ear against a rock surface, listening carefully with a sly smile"),
              ("低頭衝撞", "running with head lowered ready to ram, determined"),
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
              ("溫泉閉目", "soaking contentedly up to the shoulders in an invisible hot spring, eyes closed serene smile"),
              ("指路", "extending one arm showing the direction, reassuring nod"),
              ("憂慮望潭", "looking down at water with worried knowing eyes, sail drooping slightly"),
              ("怒吼護潭", "roaring with jaws wide open, sail fully raised, protective fury"),
              ("低音唱歌", "eyes closed humming a deep tune, gentle ripples drawn at the feet")],
    "digger": [("搬石頭", "carrying a big stone hugged to the chest, waddling"),
               ("巢中囤積", "sitting in a nest of piled shiny stones hugging a glowing rainbow crystal shard, possessive happy grin"),
               ("被發現驚訝", "frozen mid-dig, head snapped up, wide guilty eyes"),
               ("讓出寶物", "pushing the glowing shard forward with both claws, reluctant but sincere"),
               ("挖掘", "digging energetically, dirt flying backward"),
               ("害羞", "toeing the ground, claws together, blushing smile")],
    "carno": [("警長站姿", "standing upright with thumbs hooked on the belt, brass star badge gleaming, firm kind eyes"),
              ("指揮交通", "raising one arm directing firmly, commanding but fair"),
              ("低聲訴說", "leaning close, one hand cupped beside the mouth telling a secret softly"),
              ("奔跑追緝", "charging after something with badge bouncing, determined"),
              ("敬禮", "saluting sharply with a respectful smile"),
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
    "emp": [("王座站姿", "standing colossal with arms crossed, crown of golden horns gleaming, supreme dignity"),
            ("俯視群山", "looking down from a great height pose, vast wings half-spread, contemplative"),
            ("讓道", "stepping aside and lowering the head, granting passage with grace"),
            ("注視試煉", "leaning forward observing intently with wise evaluating eyes"),
            ("點頭認可", "a slow solemn approving nod, slight warm smile"),
            ("雲上背影", "massive back view standing above clouds, wings folded, golden rim light")],
    "trex": [("吼叫", "roaring with jaws wide open, tiny arms flapping, mighty but friendly"),
             ("讓路上山道", "stepping aside and gesturing an arm forward politely, toothy grin"),
             ("小短手搆不到", "struggling to reach its own back with tiny arms, comic frustration"),
             ("打瞌睡", "dozing standing up, wobbling, mouth slightly open"),
             ("奔雷衝刺", "thundering run, earth-shaking stomps, focused eyes"),
             ("溫柔鼻尖輕觸", "lowering its huge head to gently touch noses with an invisible small friend, eyes soft")],
    "spino_king": [("鍛造站姿", "standing at an invisible anvil with a hammer on the shoulder, ember-lit stern kind face"),
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

EXIST_MAN = [("cg_man_stand", "站姿（自信常態）"), ("cg_man_crouch", "蹲下驚喜（發現線索）"),
             ("cg_man_kneel", "單膝挖掘"), ("cg_man_side", "側身捧發光寶物"),
             ("cg_man_run", "全力奔跑（趕路／追逐）"), ("cg_man_point", "推理鎖定・指向遠方"),
             ("cg_man_map", "展開地圖檢視"), ("cg_man_shock", "驚訝後退一步"),
             ("cg_man_thumbs", "過關歡呼・豎拇指燦笑"), ("cg_man_calm", "伸手安撫恐龍"),
             ("cg_man_shardup", "高舉發光碎片（羅盤共鳴）"), ("cg_man_reach", "終章・側身伸手向前（握住格雷）")]
EXIST_DA = [("cg_da_stand", "站姿（好奇常態）"), ("cg_da_sniff", "低頭嗅地面"), ("cg_da_cheer", "雙爪歡呼"),
            ("cg_da_sit", "乖巧坐姿"), ("cg_da_fly", "飛翔（翅膀全開）"), ("cg_da_glow", "額頭羅盤紋發光共鳴"),
            ("cg_da_hug", "緊抱彩虹碎片"), ("cg_da_sleep", "抱蛋蜷睡（序章）"), ("cg_da_hide", "緊張躲在雷恩腿後"),
            ("cg_da_angry", "對格雷張翅生氣"), ("cg_da_tear", "終章・流淚微笑")]
EXIST_GREY = [("cg_grey_back", "背影（飛艇前指揮）"), ("cg_grey_sil", "側影佇立（帽簷遮臉）"),
              ("cg_grey_mega", "手持擴音器（只聞其聲）"), ("cg_grey_face", "終章・露臉大笑"),
              ("cg_grey_hand", "終章・伸出手"), ("cg_grey_pilot", "飛艇駕駛艙坐姿")]
EXIST_GRAND = [("cg_grand_young", "年輕隊長站姿（回憶）"), ("cg_grand_old", "老年撫羅盤坐姿"),
               ("cg_grand_back", "背影望海"), ("cg_grand_glow", "回憶・金色投影顯影"),
               ("cg_grand_photo", "序章・合影站姿")]

SALTAS_THEMATIC = [("戴碎片項鍊炫耀", "proudly wearing a glowing rainbow-crystal shard on a necklace, showing it off"),
                   ("前肢挖沙", "digging the sand with its front feet, sand flying backward"),
                   ("讓出碎片", "gently nudging a glowing rainbow-crystal shard forward with its snout, sharing it"),
                   ("低頭害羞", "bowing its head shyly with eyes averted"),
                   ("湊近好奇", "leaning its body close to the viewer, gentle curious eyes"),
                   ("躍起歡呼", "leaping up in a happy cheer, all four feet off the ground")]

CORE = [
    dict(key="rainer", zh="雷恩", prefix="cg_man", dino=False,
         anchor=SRC / "cg_man_stand.png",
         ident="identical face, hairstyle, adventure explorer outfit, colors and proportions — a character turnaround of the SAME young man. ",
         existing=EXIST_MAN, thematic=[],
         desc="主角・成年探險家「雷恩」，彩虹羅盤持有者。"),
    dict(key="banban", zh="伴伴", prefix="cg_da", dino=True,
         anchor=G_DINOS2 / "DFD-000_伴伴_2star.png", extra="",
         existing=EXIST_DA, thematic=[],
         desc="主角搭檔・額頭羅盤紋小龍「伴伴」，造型以遊戲圖 DFD-000 為錨。"),
    dict(key="saltas", zh="薩爾塔龍", prefix="cg_db", dino=True,
         anchor=G_DINOS / "9.webp",
         extra=("Keep its signature SPIRAL-COILED tail exactly as in reference image 1 — the tail wraps in a "
                "flat spiral against the hip; big golden-amber eyes. "),
         existing=[], thematic=SALTAS_THEMATIC,
         desc="序章登場・愛亮晶晶的薩爾塔龍，把彩虹碎片當項鍊；造型以遊戲圖 9 為錨（灰藍身體、螺旋盤卷長尾）。"),
    dict(key="grey", zh="格雷", prefix="cg_grey", dino=False,
         anchor=SRC / "cg_grey_mega.png",
         ident=("identical outfit: long dark frock coat, wide-brim hat with round brass goggles on the brim, "
                "lower face wrapped in a scarf — the face must stay hidden in shadow, NEVER reveal the face, "
                "no megaphone. A character turnaround of the SAME mysterious man. "),
         existing=EXIST_GREY, thematic=[],
         desc="神秘對手・飛艇船長「格雷」，深色長外套＋寬檐帽＋黃銅護目鏡＋黑鬍；終章前一律蒙面不露臉（p01-06 臉部刻意隱藏屬設計），臉孔基準＝057 終章露臉大笑。"),
    dict(key="grand", zh="雷鐸", prefix="cg_grand", dino=False,
         anchor=SRC / "cg_grand_old.png",
         ident="identical face, white hair and short white beard, warm elderly explorer coat, colors and proportions — a character turnaround of the SAME elderly man. ",
         existing=EXIST_GRAND, thematic=[],
         desc="雷恩的爺爺・前探險隊隊長「雷鐸」，白髮白鬚；以老年形態為主，年輕形態僅回憶。"),
]

BATCH_KEYS = {"core": [ch["key"] for ch in CORE],
              "g1": [g[0] for g in GUESTS[0:7]],
              "g2": [g[0] for g in GUESTS[7:13]],
              "g3": [g[0] for g in GUESTS[13:19]]}

# 用戶審核意見（2026-10-23）：雷恩臉孔應以 001（cg_man_p01）為基準——
# 008/009/014/015/017 臉孔偏年輕圓潤、016/017 服裝漂成卡其色，定向以 001 為錨重出。
MANFIX_ANCHOR = SRC / "cg_man_p01.png"
MANFIX_IDENT = ("identical FACE as reference image 1 — the SAME mature slim face with a defined jaw and "
                "short neat dark-brown hair, no rounder or younger face, normal eye size; identical "
                "olive-green field shirt over a tan undershirt with brown leather vest straps and gear, "
                "same colors and proportions — the SAME young man. ")
MANFIX = [("cg_man_crouch", "crouching down with both hands on the knees, eyes wide in delighted surprise at a tiny clue on the ground"),
          ("cg_man_kneel", "kneeling on one knee, brushing dirt away with a small brush, focused gentle smile"),
          ("cg_man_shock", "stepping back in shock, both hands raised, mouth open in surprise"),
          ("cg_man_thumbs", "thumbs-up toward the viewer with a big bright grin, other hand resting on the hip"),
          ("cg_man_calm", "kneeling and reaching one hand out gently to calm a small dinosaur, warm soft smile"),
          ("cg_man_shardup", "holding a glowing rainbow-crystal shard high overhead with one hand, looking up at it, "
                             "warm glow on the crystal only — keep skin tone and clothing colors natural")]


def all_chars():
    chars = list(CORE)
    for key, gid, zh, desc, extra in GUESTS:
        chars.append(dict(key=key, zh=zh, prefix=key, dino=True,
                          anchor=G_DINOS / f"{gid}.webp", extra=extra,
                          existing=[], thematic=THEMATIC[key], desc=desc))
    return chars


def dino_prompt(extra, pose_en):
    return (f"{DINO_IDENT}{extra}Full body, {pose_en}. "
            "Plain pure white background, no shadow, no text, no scenery, "
            "the character centered and filling most of the frame.")


def human_prompt(ident, pose_en):
    return (f"Draw the exact same character as reference image 1: {ident}Full body, {pose_en}. "
            "Plain pure white studio background, no text, no scenery, "
            "the character centered and filling most of the frame.")


def build_manifest():
    rows, order = [], []
    sn = 1
    for ch in all_chars():
        zh = ch["zh"]
        order.append(zh)
        canon = CANON_SWIM if ch["key"] in MARINE else CANON
        poses = list(canon) + ch["thematic"]
        for idx, (azh, aen) in enumerate(poses, 1):
            file = f"{ch['prefix']}_p{idx:02d}"
            if ch["dino"]:
                prompt = dino_prompt(ch.get("extra", ""), aen)
            else:
                prompt = human_prompt(ch["ident"], aen)
            rows.append(dict(serial=f"{sn:03d}", char=zh, file=file, action=azh,
                             prompt=prompt, desc=ch["desc"]))
            sn += 1
        for file, azh in ch["existing"]:
            rows.append(dict(serial=f"{sn:03d}", char=zh, file=file, action=azh,
                             prompt=None, desc=ch["desc"]))
            sn += 1
    return {"char_order": order, "cast": rows}


def flat_png(path, max_side=1024):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg = bg.convert("RGB")
    bg.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    bg.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def call(model, prompt, ref_b64, aspect="1:1"):
    parts = [{"text": prompt},
             {"inline_data": {"mime_type": "image/png", "data": ref_b64}}]
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


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    data = build_manifest()
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manifest rebuilt: {len(data['cast'])} serials / {len(data['char_order'])} chars", flush=True)
    if mode == "manifest":
        return
    if mode == "manfix":
        anchor_b64 = flat_png(MANFIX_ANCHOR)
        failed = []
        for file, action_en in MANFIX:
            out = SRC / f"{file}.png"
            if out.exists():
                print(f"{file}: skip (exists)", flush=True)
                continue
            img = None
            for model in MODELS:
                got, msg = call(model, human_prompt(MANFIX_IDENT, action_en), anchor_b64)
                if got:
                    img = got
                    print(f"{file}: OK via {model} ({len(got)} bytes)", flush=True)
                    break
                print(f"{file}: fail {model} -> {msg}", flush=True)
                time.sleep(2)
            if img:
                out.write_bytes(img)
            else:
                failed.append(file)
                print(f"{file}: ALL_FAILED", flush=True)
            time.sleep(1.5)
        print(f"DONE ok={len(MANFIX) - len(failed)} failed={failed if failed else 0}", flush=True)
        return
    keys = set()
    for k in (BATCH_KEYS if mode == "all" else [mode]):
        keys.update(BATCH_KEYS[k])
    chars = {ch["key"]: ch for ch in all_chars()}
    jobs = [r for r in data["cast"] if r["char"] in {chars[k]["zh"] for k in keys} and r["prompt"]]
    todo = [r for r in jobs if not (SRC / f"{r['file']}.png").exists()]
    print(f"mode={mode} keys={sorted(keys)} jobs={len(jobs)} todo={len(todo)}", flush=True)
    anchor_cache, failed = {}, []
    for r in todo:
        ch = next(c for c in chars.values() if c["zh"] == r["char"])
        out = SRC / f"{r['file']}.png"
        if ch["key"] not in anchor_cache:
            anchor_cache[ch["key"]] = flat_png(ch["anchor"])
        got = None
        for model in MODELS:
            img, msg = call(model, r["prompt"], anchor_cache[ch["key"]])
            if img:
                got = img
                print(f"{r['serial']} {r['file']}: OK via {model} ({len(img)} bytes)", flush=True)
                break
            print(f"{r['serial']} {r['file']}: fail {model} -> {msg}", flush=True)
            time.sleep(2)
        if got:
            out.write_bytes(got)
        else:
            failed.append(r["serial"])
            print(f"{r['serial']} {r['file']}: ALL_FAILED", flush=True)
        time.sleep(1.5)
    print(f"DONE ok={len(todo) - len(failed)} failed={failed if failed else 0}", flush=True)


if __name__ == "__main__":
    main()
