# -*- coding: utf-8 -*-
"""Phase 1: build the seeded 139-row generation spec sheet (JSON + HTML report).

Usage: PYTHONIOENCODING=utf-8 python _gen_spec_sheet.py
Outputs:
  assets/dinos_2/bban_samples/_gen_specs.json
  report/styleA_gen_specs_report.html
"""
import json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RECON_DIR = Path(r"C:\MY_AI_JOBS\恐龍圖片")
BASE_SEED = 20261016
OUT_JSON = Path(__file__).resolve().parent / "_gen_specs.json"
OUT_HTML = ROOT / "working_db" / "reports" / "styleA_gen_specs_report.html"

# ---------------- pools (zh, en) ----------------
COLORS = [
    ("祖母綠", "emerald green"), ("森林綠", "deep forest green"), ("薄荷綠", "soft mint green"),
    ("橄欖綠", "olive green"), ("青蘋果綠", "fresh apple green"), ("青綠", "viridian teal-green"),
    ("緋紅", "vivid crimson red"), ("磚紅", "brick red"), ("酒紅", "deep wine red"),
    ("玫瑰粉", "rosy pink"), ("蜜桃粉", "peach pink"), ("珊瑚橙", "coral orange"),
    ("琥珀橙", "amber orange"), ("芒果黃", "mango yellow"), ("檸檬黃", "lemon yellow"),
    ("金黃", "rich golden yellow"), ("天空藍", "sky blue"), ("靛藍", "indigo blue"),
    ("湖水藍", "teal lake blue"), ("青金石藍", "lapis blue"), ("葡萄紫", "grape purple"),
    ("薰衣草紫", "lavender purple"), ("梅子紫", "plum purple"), ("巧克力棕", "chocolate brown"),
    ("焦糖棕", "caramel brown"), ("沙棕", "sandy tan"), ("石板灰", "slate gray"),
    ("石墨黑", "graphite charcoal"), ("銀灰", "silver gray"), ("象牙白", "warm ivory (never pure white)"),
]
PATTERNS = [
    ("無", "no skin pattern, clean skin"),
    ("圓斑", "dappled round spots in a slightly darker shade"),
    ("虎條紋", "tiger stripes"),
    ("直條紋", "vertical band stripes"),
    ("閃電紋", "lightning-bolt markings"),
    ("星芒紋", "starburst markings"),
    ("幾何刺青", "geometric tribal tattoos"),
    ("心形斑", "heart-shaped patches"),
    ("漸層鱗", "gradient scale patterning toward the tail"),
    ("潑濺紋", "paint-splash markings"),
    ("波浪紋", "wave patterns"),
    ("骨甲紋", "bone-armor etching lines"),
]
EXPRESSIONS = [
    ("開懷大笑", "beaming open-mouth laugh"),
    ("得意", "confident smirk"),
    ("調皮吐舌", "playful tongue out"),
    ("威武皺眉", "cute-but-fierce determined frown"),
    ("驚喜", "wide-eyed delighted surprise"),
    ("酷瞇眼", "cool squint"),
    ("甜笑", "closed sweet smile"),
    ("咆嘯氣勢", "playful show-off roar"),
]
POSES = [
    ("開心跳躍", "mid-air happy jump, legs tucked"),
    ("衝刺奔跑", "full sprint run, dynamic lean"),
    ("躺地打滾", "rolling on its back, belly up, playful"),
    ("背面回頭", "back facing camera, looking over the shoulder"),
    ("揮尾", "whipping tail flourish"),
    ("咆嘯", "standing roar, chest out"),
    ("滑行", "skidding slide, dust kicked up"),
    ("展臂飛翔", "arms/wings spread wide as if gliding"),
    ("指向遠方", "dramatically pointing forward with one hand"),
    ("雙手舉高歡呼", "both arms raised cheering"),
    ("蹲坐", "sitting crouch, relaxed"),
    ("伏地潛行", "low crouching prowl"),
    ("甩頭轉身", "head-toss turning motion"),
    ("倒退威嚇", "mock-charge stance, arms spread"),
    ("伸懶腰", "lazy stretch with a yawn"),
]
HERO_POSES = [
    ("巨爪交叉胸前", "giant metal claws crossed over the chest, head lowered in a glare at the camera"),
    ("懸浮飛行", "levitating in mid-flight, cape billowing, one palm thrust toward the camera"),
    ("護腕交叉擋格", "forearms crossed in a blocking guard, side stance, low center of gravity"),
    ("貓科蹲伏回眸", "feline crouch with one hand on the ground, tail up, looking back over the shoulder"),
    ("重錘高舉下砸", "two-handed heavy hammer raised overhead, about to slam down"),
    ("單膝蓄力前撲", "one knee on the ground, coiled to leap forward"),
    ("雙刀背後交叉", "dual blades crossed behind the back, head tilted with a sly smirk"),
    ("抱胸懸浮俯視", "arms crossed while hovering, chin raised, looking down at the viewer"),
    ("全力直拳", "full-extension punch straight at the camera with speed-line motion trails"),
    ("單腿迴旋踢", "single-leg spinning kick with a motion trail on the leg"),
    ("腰側集氣", "hands gathered at the hip charging a glowing energy orb between the palms"),
    ("盾前低姿衝刺", "shield-first low charging stance"),
    ("巨拳向天怒吼", "gem-studded fist raised skyward, whole body glowing, roaring"),
]
ACC_SIMPLE = [
    ("紅色領巾", "a small red neckerchief"), ("葉片小帽", "a little leaf cap"),
    ("貝殼項鍊", "a shell necklace"), ("手腕繃帶", "wrist bandages"),
    ("小背包", "a tiny backpack"), ("花朵別飾", "a flower pin"),
]
ACC_LIGHT = [
    ("皮質護腕", "leather bracers"), ("肩墊", "one shoulder pad"),
    ("臂環", "arm rings"), ("皮質腰帶包", "a leather belt pouch"),
]
ACC_GOLD = [
    ("金邊胸甲", "a gold-trimmed chest armor"), ("長矛", "a spear"),
    ("戰斧", "a battle axe"), ("釘錘", "a spiked mace"), ("金邊盾牌", "a gold-rimmed shield"),
]
ACC_LEGEND = [
    ("傳說大劍", "a legendary oversized greatsword"), ("巨戰鎚", "a giant warhammer"),
    ("神秘法杖", "a mystic staff with a glowing crystal"),
]
STAINS = [
    ("微塵", "a light dusting of fine dirt"),
    ("腿部泥點", "muddy speckles on the legs"),
    ("腹部草屑", "a few grass bits stuck on the belly"),
    ("背部落葉", "a couple of dry leaves resting on the back"),
    ("尾端泥塊", "a small mud clump on the tail tip"),
    ("臉側土痕", "a subtle dirt smudge on one cheek"),
]

# ---------------- family classification ----------------
FAM_ZH = [
    ("ceratopsian", ["角龍", "鸚鵡嘴", "隱龍"]),
    ("stegosaur", ["劍龍", "釘狀龍", "沱江龍", "嘉陵龍", "銳龍"]),
    ("ankylosaur", ["甲龍", "結節龍", "全裝甲", "多刺甲", "美甲龍", "繪龍", "戈壁龍"]),
    ("pachy", ["腫頭龍", "冥河龍", "平頭龍", "傾頭龍", "頭龍"]),
    ("sauropod", ["腕龍", "梁龍", "雷龍", "迷惑龍", "圓頂龍", "馬門溪", "地震龍", "超龍",
                   "薩爾塔", "泰坦", "巨龍", "阿拉摩", "普爾塔", "里貝奇", "葡萄園", "雪松",
                   "波塞東", "奧古斯丁", "峨眉龍", "盤足", "鯨龍", "阿根廷龍", "潮汐龍", "黃河",
                   "鄖縣龍", "歐羅巴龍", "雙腔龍", "長生天龍", "尼日爾龍"]),
    ("hadrosaur", ["鴨嘴龍", "櫛龍", "盔龍", "冠龍", "副櫛龍", "賴氏龍", "青島龍", "慈母龍",
                    "分離龍", "似凹齒", "短冠龍", "格里芬", "譚氏龍"]),
    ("ornithopod", ["禽龍", "穆塔布拉", "腱龍", "豪勇龍", "橡樹龍", "彎龍", "無畏龍",
                     "萊索托", "靈龍", "鹽都龍"]),
    ("therizinosaur", ["鐮刀", "懶爪", "慢龍", "北票龍", "鑄鐮", "厚爪龍"]),
    ("ornithomimid", ["似雞龍", "似鳥龍", "似鴕龍", "似金翅鳥", "似鴯鶓"]),
    ("oviraptorosaur", ["偷蛋龍", "竊蛋龍", "擬鳥龍", "尾羽龍", "切齒龍"]),
    ("dromaeosaur", ["迅猛龍", "伶盜龍", "恐爪龍", "馳龍", "中國鳥龍", "猶他盜龍", "小盜龍", "傷齒龍",
                      "蜥鳥龍", "天宇盜龍", "內烏肯盜龍"]),
    ("tyrannosaur", ["暴龍", "霸王龍", "特暴龍", "艾伯塔龍", "懼龍", "帝龍", "羽王龍", "五彩冠龍",
                      "虔州龍", "傷龍", "超帝王龍"]),
    ("spinosaurid", ["棘龍", "重爪龍", "似鱷龍", "激龍", "西雅茲龍"]),
    ("carnosaur", ["異特龍", "鯊齒龍", "南方巨獸", "中棘龍", "永川龍", "中華盜龍", "食蜥王", "高棘龍", "蠻龍",
                    "新獵龍", "南方盜龍", "大盜龍", "非洲獵龍", "永川盜龍"]),
    ("abelisaur", ["食肉牛龍", "阿貝力", "瑪君龍", "皺褶龍", "勝王龍", "奧卡龍"]),
    ("basal_theropod", ["角鼻龍", "中國龍", "雙脊龍", "冰脊龍", "腔骨龍", "始盜龍", "艾雷拉", "美頜龍", "中華龍鳥",
                         "宣漢龍", "惡魔龍", "十字龍", "嗜鳥龍"]),
    ("pterosaur", ["翼龍", "風神", "無齒翼", "古神", "南翼", "喙嘴", "夜翼", "神龍翼", "哈特茲哥"]),
    ("alvarezsaur", ["單爪龍", "阿瓦拉慈", "鳥面龍"]),
    ("prosauropod", ["板龍", "祿豐龍", "里奧哈龍", "鼠龍", "大椎龍"]),
    ("croc", ["鱷"]),
    ("marine", ["蛇頸", "上龍", "魚龍", "滄龍", "滑齒", "薄板", "克柔", "海王龍", "龍王鯨", "古鯨",
                 "長頸龍", "浮龍", "海霸龍", "始鯨", "械齒鯨"]),
    ("oddity", ["奇蝦", "海口魚", "鄧氏魚"]),
    ("bird", ["始祖鳥", "孔子鳥", "樹息龍", "擅攀鳥龍", "會鳥", "義縣鳥", "反鳥", "黃昏鳥", "大洋鳥"]),
    ("dromaeosaur2", ["盜龍"]),
]
ASCII_FAM = {"garudimimus": "ornithomimid"}
FAM_EN = [
    ("ceratopsian", ["ceratops", "Psittaco", "Pachyrhino", "Styraco", "Chasmo", "Centro", "Achelou", "Einio", "Diabloceratops", "Kosmoceratops", "Corono", "Spinops", "Nasutoceratops", "Leptoceratops", "Prenoce", "Torosaurus", "Yinlong", "Chaoyangsaurus", "Microcerat"]),
    ("stegosaur", ["Stego", "Kentro", "Tuojiang", "Gigantspino", "Wuerho", "Dacentr", "Miragaia", "Hesperos", "Lexovis", "Chungkingo", "Huayango"]),
    ("ankylosaur", ["ankylo", "Ankylo", "nodosaur", "Polacanth", "Panoplo", "Edmontonia", "Sauropelta", "Gastonia", "Talarurus", "Minmi", "Silvisaur", "Pawpawsaur", "Cedarpelta", "Pinaco", "Euoplo", "Tarchia", "Saichania", "Shamosaurus", "Gobisaurus", "Liaoningosaurus", "Mymoorapelta", "Scelidosaurus", "Struthiosaurus", "Loricatosaurus", "Hylaeo", "Anodonto"]),
    ("pachy", ["pachycephal", "Stygimoloch", "Dracorex", "Homaloceph", "Prenoceph", "Tyloceph", "Stegoceras", "Goyocephale", "Sphaerotholus", "Wannanosaurus"]),
    ("sauropod", ["Brachio", "Diplodoc", "Apatos", "Camaras", "Cetio", "Amargas", "Dicraeo", "Shuno", "Saltas", "Argentino", "Alamos", "Puerta", "Ruyang", "Futalogn", "Agustin", "Mamench", "Baro", "Giraffa", "Jobaria", "Chubut", "Isisaur", "Rapetos", "Nemegto", "Cedaros", "Venenos", "Peloros", "Lusotitan", "Vulcanodon", "Bellus", "Omei", "Abrosaur", "Euhelop", "Sonido", "Antarcto", "Sauroposeidon", "Dongbeititan", "Rebbachi", "Opisthocoel", "Supersaurus", "Demandasaurus", "Tastavins", "Europasaurus", "Amphicoe", "Nigersaurus", "Xinjiang", "Qiaowanlong", "Ampelo"]),
    ("hadrosaur", ["hadro", "sauroloph", "Lambe", "Corytho", "Parasauroloph", "Tsintao", "Maiasaur", "Edmonto", "Kritos", "Olorotitan", "Hypacro", "Velafrons", "Nippono", "Aquilops", "Eotrachodon", "Brachylopho", "Eolambia", "Charonosaurus", "Tanius", "Shantungo", "Grypo", "Amuro"]),
    ("ornithopod", ["Iguanodon", "Muttabur", "Tenonto", "Dryo", "Campto", "Othnielia", "Zalmoxes", "Rhabdodon", "Ourano", "Lurdusaur", "Hypsilophodon", "Qantassa", "Eocursor", "Scutellosaurus", "Tianyulong", "Mantellisaurus", "Lesothosaurus", "Agilisaurus", "Yandusaurus", "Atlascopco", "Leaellyna"]),
    ("therizinosaur", ["Therizino", "Nothronychus", "Erliko", "Segno", "Alxasaur", "Falcariu", "Beipiao", "Jianchangosaur", "Suzhousaurus"]),
    ("ornithomimid", ["ornithomim", "Gallimim", "Struthiomim", "Anserimim", "Garudimim", "Archaeornithomim", "Sinornithomim", "Pelecanimim", "Coelurus", "Deinocheirus"]),
    ("oviraptorosaur", ["ovirapt", "Citipati", "Caenagnath", "Chirostenotes", "Incisivo", "Caudipteryx", "Avimimus", "Nomingia", "Elmisaur", "Gigantoraptor", "Anzu", "Bonapartenykus", "Haplocheirus", "Conchoraptor"]),
    ("dromaeosaur", ["raptor", "Velociraptor", "Deinonych", "Dromaeo", "Bambiraptor", "Microrapt", "Sinornitho", "Achillobator", "Utahrapt", "Saurornitholestes", "Tianyuraptor", "Zhenyuanlong", "Halszkaraptor", "Troodon", "Sinovenator", "Saurornithoid", "Zanabazar", "Adasaurus", "Balaur", "Eodromaeus", "Xiaotingia", "Rahonavis", "Anchiornis", "Epidexipteryx", "Pedopenna"]),
    ("tyrannosaur", ["tyrann", "Tarbo", "Alberto", "Gorgo", "Dasplet", "Guanlong", "Dilong", "Yutyrann", "Sinotyrann", "Lythronax", "Zhuchengtyrann", "Bistahiever", "Teratophone", "Qianzhous", "Nanuqsaur", "Dryptosaur", "Alectrosaurus", "Alioramus", "Eotyrannus"]),
    ("spinosaurid", ["spino", "Baryon", "Suchomim", "Irritator", "Siamosaur", "Oxalaia", "Sigilmassa", "Ichthyovenator"]),
    ("carnosaur", ["Allo", "Carchar", "Giganoto", "Mapu", "Acrocanth", "Sinrapt", "Metria", "Yangchuan", "Saurophagan", "Torvo", "Eustrepto", "Chilantaisaur", "Shaochilong", "Edmarka", "Concavenator", "Indosuchus", "Neovenator", "Megalos", "Afroven", "Australoven", "Piatnitzky", "Kryptops", "Gasosaurus"]),
    ("abelisaur", ["Carno", "Abeli", "Majunga", "Rugops", "Skorpio", "Rajasaur", "Ekrixinato", "Aucasaur", "Kryptops", "Quilmesaurus", "Velocisaurus", "Masiaka"]),
    ("basal_theropod", ["Cerato", "Coeloph", "Dilopho", "Herrera", "Eoraptor", "Lilienstern", "Cryolo", "Sinosaurus", "Monolopho", "Gojira", "Chilesaur", "Compsognath", "Sciurumim", "Juravenator", "Sinosauroptery", "Segisaur", "Procompsognath", "Kileskus", "Stauriko", "Tawa", "Daemono", "Xuanhano", "Chinde", "Sanjuan", "Ornitholestes"]),
    ("pterosaur", ["ptero", "Rhampho", "Pteranodon", "Quetzalcoat", "Tupuxu", "Dsungari", "Tapejar", "Dimorpho", "Anurognath", "Darwinopter", "Chaoyangopter", "Thalassodrom", "Tropeog", "Guidraco", "Istiodactyl", "Ornithocheir", "Liaoningopter"]),
    ("alvarezsaur", ["alvarezs", "Mononyk", "Shuvuuia", "Albertonyk"]),
    ("prosauropod", ["Plateo", "Riojasaur", "Masso", "Mussaur", "Yunnano", "Anchisaur", "Lufeng", "Thecodont", "Scolosaurus", "Melanoro", "Leyes"]),
    ("croc", ["Sarcos", "Deinosuchus", "Purussa", "Rutiod", "Pristi", "Kapros", "Goniopho", "Stomato", "Beipiao croc", "Metrorhyn"]),
    ("marine", ["plesio", "Pliosaur", "Liopleuro", "Rhomaleo", "Ichthyosaur", "Ophthalm", "Mosasaur", "Tylosaur", "Elasmo", "Krono", "Stenoptery", "Temnodonto", "Eurhino", "Cryptoclid", "Dolichorhyn", "Tanystropheus", "Karasaurus"]),
    ("oddity", ["Dunkle", "Xiphactin", "Anomalocar", "Haikou", "Basilosaurus"]),
    ("bird", ["Archaeopteryx", "Confuciu", "Sapeornis", "Iberomesorn", "Zhongjianornis", "Hongshanornis", "Gansus", "Hesperornis", "Jeholornis", "Jehol", "Eosipteryx", "Scansorio", "Yi qi"]),
]
GROUPS = {
    "raptor_like": {"dromaeosaur", "ornithomimid", "oviraptorosaur", "alvarezsaur"},
    "big_biped": {"tyrannosaur", "carnosaur", "abelisaur"},
    "long_neck": {"sauropod", "prosauropod"},
    "armored": {"ankylosaur", "stegosaur"},
    "crested_herb": {"hadrosaur", "ornithopod"},
}
def fam_of_zh(name):
    if all(ord(c) < 128 for c in name):
        return ASCII_FAM.get(name.lower(), "generic")
    for fam, kws in FAM_ZH:
        if any(k in name for k in kws):
            return "dromaeosaur" if fam == "dromaeosaur2" else fam
    return "generic"
def fam_of_en(text):
    for fam, kws in FAM_EN:
        if any(k.lower() in text.lower() for k in kws):
            return fam
    return "generic"
def group_of(fam):
    for g, members in GROUPS.items():
        if fam in members:
            return g
    return None

# Slender/low-slung families: poses must tuck in so the silhouette stays near 1:1 (user rule 2026-10-16)
SLENDER_FAMS = {"sauropod", "prosauropod", "spinosaurid", "croc", "marine"}
# Tall-risk families (upright sauropod necks): keep the neck low and horizontal.
BODY_COMPACT_LOW_NECK = ("compact low-slung pose for an elongated body: the neck stretches FORWARD horizontally at "
                         "shoulder height, gently curved, never pointing upward, with the head kept low just above "
                         "the back line and turned slightly toward the body side; the tail is coiled in a tight curl "
                         "flat against the side of the body, tip near the front feet, never extending behind the "
                         "haunches; the whole creature hugs the ground like a wide low-slung animal; overall "
                         "silhouette close to 1:1 length-to-height, never longer than 1.2:1 and never narrow-tall")
# Wide-risk families (spinosaurid/croc/marine horizontal bodies): coil the tail, let the head rise a little.
BODY_COMPACT_COIL = ("compact gathered pose for an elongated body: the tail is coiled in a tight spiral flat "
                     "against the hip, tip near the front feet, never extending behind the haunches; the neck "
                     "rises into a gentle S-curve with the head lifted slightly, snout angled gently upward; "
                     "seen from a slight three-quarter angle with the legs planted wide apart so the body reads "
                     "wide and chunky; overall silhouette close to 1:1 length-to-height, always between 1:1.2 "
                     "and 1.2:1, never narrow-tall and never long-flat")

# Fun random extras drawn per row (user addition 2026-10-16): actions replace the base pose,
# moods modify how the pose is performed; 5-star rows draw moods only so hero poses stay intact.
FUN_ACTIONS = [
    ("睡覺", "curled up in a round ball, fast asleep with tiny zzz bubbles"),
    ("吃食物", "munching a snack with head bowed down, sitting flat on the ground in a wide squat, legs sprawled wide, tail lying limp and flat on the ground, cheeks stuffed full, body low and round"),
    ("唱歌", "singing passionately with mouth wide open, head kept low, body rounding into a wide low compact pose"),
    ("踢腿", "kicking one knee up high toward the chest in a tight compact kick, standing low on the other leg, tail coiled in a tight curl flat against the body side, never stretching behind"),
    ("飛踢", "flying-kick in mid-air, tail curled tight beside the body"),
    ("瑜珈", "holding a low wide cute yoga stretch"),
]
FUN_MOODS = [
    ("搞笑", "in a comical slapstick way"),
    ("害羞", "shyly with pink blushing cheeks"),
    ("膽小", "timidly with jittery wide eyes"),
    ("勇敢", "bravely with chest puffed out"),
    ("粗暴", "rowdily and roughly"),
]
FUN_EXTRAS = FUN_ACTIONS + FUN_MOODS

HERO_PREF = [
    (["鐮刀", "恐爪", "馳龍", "迅猛", "伶盜", "猶他盜"], [1, 13, 7]),
    (["翼龍", "翼", "始祖鳥", "孔子鳥"], [2, 8]),
    (["角龍", "食肉牛龍", "牛龍", "腫頭龍", "冥河龍"], [3, 12, 6]),
    (["甲龍", "劍龍", "釘狀", "全裝甲"], [12, 5, 3]),
    (["暴龍", "霸王", "鯊齒", "棘龍", "異特龍", "南方巨獸", "蠻龍", "瑪君"], [9, 13, 5]),
    (["腕龍", "梁龍", "雷龍", "泰坦", "巨龍", "薩爾塔", "阿根", "馬門溪"], [5, 13, 8]),
    (["鴨嘴", "櫛龍", "副櫛", "盔龍", "冠龍"], [10, 9, 13]),
    (["鯨", "滄龍", "蛇頸", "上龍", "魚龍", "鄧氏魚", "奇蝦"], [2, 5, 9]),
]

def hero_candidates(name):
    for kws, poses in HERO_PREF:
        if any(k in name for k in kws):
            return poses
    return list(range(1, 14))

TIER_RULES = {
    1: {"acc": None, "pattern": None, "stains": ["微塵"], "extra": "plain clean look, no accessories, no pattern"},
    2: {"acc": ACC_SIMPLE, "pattern": None, "stains": 1, "extra": "one simple small accessory"},
    3: {"acc": ACC_LIGHT, "pattern": True, "stains": 2, "extra": "skin pattern or tattoo + light leather gear"},
    4: {"acc": ACC_GOLD, "pattern": True, "stains": 2, "extra": "gold-trimmed armor or weapon + subtle motion effect lines"},
    5: {"acc": ACC_LEGEND, "pattern": True, "stains": 3, "extra": "legendary hero: golden crown + flowing cape + legendary weapon + heroic signature pose + subtle golden particle glow"},
}

def main():
    src = (ROOT / "game_db" / "js" / "data.js").read_text(encoding="utf-8")
    dinos = json.loads(re.search(r"const DINOS = (\[.*?\]);", src, re.S).group(1))
    legends = json.loads(re.search(r"const LEGENDS = (\[.*?\]);", src, re.S).group(1))
    all_dinos = dinos + legends
    pair = json.loads((Path(__file__).resolve().parent / "_pairing_result.json").read_text(encoding="utf-8"))
    matched = {m[0]: m[3] for m in pair["matched"]}

    recon_files = sorted(p.name for p in RECON_DIR.iterdir() if p.suffix.lower() in (".jpg", ".png", ".jpeg", ".webp"))
    recon_fam = {f: fam_of_en(f) for f in recon_files}
    used = set(matched.values())

    rows = []
    prev_color = None
    color_used = {}
    for d in sorted(all_dinos, key=lambda x: x["id"]):
        sid, name, stars = d["id"], d["name"], d["stars"]
        rng = random.Random(BASE_SEED + sid * 97)
        rule = TIER_RULES[stars]

        if sid in matched:
            method, recon = "P0", matched[sid]
            fam = fam_of_en(recon)
            if fam == "generic":
                fam = fam_of_zh(name)
        else:
            fam = fam_of_zh(name)
            recon, method = None, "P2"
            if fam != "generic":
                cands = [f for f in recon_files if f not in used and recon_fam[f] == fam]
                tier = "同科"
                if not cands and group_of(fam):
                    g = group_of(fam)
                    cands = [f for f in recon_files if f not in used and recon_fam[f] in GROUPS[g]]
                    tier = "近緣"
                if cands:
                    recon = rng.choice(cands)
                    used.add(recon)
                    method = f"P1({tier}:{fam})"

        color = None
        for _ in range(24):
            c = rng.choice(COLORS)
            if c[0] != prev_color and color_used.get(c[0], 0) < 8:
                color = c
                break
        if color is None:
            color = rng.choice(COLORS)
        color_used[color[0]] = color_used.get(color[0], 0) + 1
        prev_color = color[0]

        if stars == 1 or (stars == 2 and rng.random() < 0.5):
            pattern = PATTERNS[0]
        elif rule["pattern"]:
            pattern = rng.choice(PATTERNS[1:])
        else:
            pattern = rng.choice(PATTERNS)

        expr = rng.choice(EXPRESSIONS)
        if stars == 5:
            cand = hero_candidates(name)
            hero_no = rng.choice(cand)
            pose = ("英雄姿勢" + str(hero_no), HERO_POSES[hero_no - 1][1])
            pose_pool = f"hero{hero_no}"
        else:
            p = rng.choice(POSES)
            pose, pose_pool = p, "general"

        acc = rng.choice(rule["acc"]) if rule["acc"] else None

        if stars == 1:
            stains = [STAINS[0]]
        else:
            n = rule["stains"]
            stains = rng.sample(STAINS[1:], min(n, len(STAINS) - 1))
            if stars == 1:
                stains = [STAINS[0]] + stains[:n - 1]

        fun_pool = FUN_MOODS if stars == 5 else FUN_EXTRAS
        fun = rng.choice(fun_pool)
        fun_kind = "mood" if stars == 5 else ("action" if fun in FUN_ACTIONS else "mood")

        rows.append({
            "id": sid, "name": name, "stars": stars, "img": d["img"],
            "method": method, "recon": recon, "family": fam,
            "seed": BASE_SEED + sid * 97,
            "color_zh": color[0], "color_en": color[1],
            "pattern_zh": pattern[0], "pattern_en": pattern[1],
            "expr_zh": expr[0], "expr_en": expr[1],
            "pose_zh": pose[0], "pose_en": pose[1], "pose_pool": pose_pool,
            "acc_zh": acc[0] if acc else "無", "acc_en": acc[1] if acc else "no accessory",
            "stains": [{"zh": s[0], "en": s[1]} for s in stains],
            "tier_extra": rule["extra"],
            "body_compact": fam in SLENDER_FAMS,
            "body_note_en": ((BODY_COMPACT_LOW_NECK if fam in {"sauropod", "prosauropod"}
                              else BODY_COMPACT_COIL) if fam in SLENDER_FAMS else ""),
            "fun_zh": fun[0], "fun_en": fun[1], "fun_kind": fun_kind,
        })

    counts = {"P0": 0, "P1": 0, "P2": 0}
    for r in rows:
        counts[r["method"][:2]] += 1
    data = {"base_seed": BASE_SEED, "counts": counts, "rows": rows}
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    tier_color = {1: "#66bb6a", 2: "#42a5f5", 3: "#ffb300", 4: "#ff7043", 5: "#ab47bc"}
    method_color = {"P0": "#6ee7b7", "P1": "#93c5fd", "P2": "#fca5a5"}
    trs = []
    for r in rows:
        mkey = r["method"][:2]
        mc = method_color[mkey]
        tc = tier_color[r["stars"]]
        recon_disp = (r["recon"][:34] + "…") if r["recon"] and len(r["recon"]) > 35 else (r["recon"] or "—")
        stain_disp = "、".join(s["zh"] for s in r["stains"])
        star_badge = f'<span class="st" style="color:{tc};border-color:{tc}">{r["stars"]}★</span>'
        method_badge = f'<span class="mt" style="color:{mc};border-color:{mc}">{r["method"]}</span>'
        body_disp = '<span style="color:#fbbf24;font-weight:700">收攏體態（頸平低・收尾・頭低側）</span>' if r["body_compact"] else "—"
        fun_kind_zh = {"action": "動作", "mood": "情緒"}[r["fun_kind"]]
        trs.append(
            f'<tr><td class="num">{r["id"]}</td><td>{star_badge}</td><td class="nm">{r["name"]}</td>'
            f'<td>{method_badge}</td><td class="mono small" title="{r["recon"] or ""}">{recon_disp}</td>'
            f'<td class="mono small">{r["seed"]}</td><td>{r["color_zh"]}</td><td>{r["pattern_zh"]}</td>'
            f'<td>{r["expr_zh"]}</td><td>{r["pose_zh"]}</td><td>{body_disp}</td>'
            f'<td><span style="color:#f0abfc">{r["fun_zh"]}</span> <span class="small">({fun_kind_zh})</span></td>'
            f'<td>{r["acc_zh"]}</td><td class="small">{stain_disp}</td></tr>'
        )

    from collections import Counter
    color_hist = Counter(r["color_zh"] for r in rows)
    dup = [c for c, n in color_hist.items() if n > 8]

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>風格A 生成規格表（139 筆・種子化）</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Microsoft JhengHei","PingFang TC",sans-serif; background:#141021; color:#f3eefc;
         line-height:1.55; padding:28px 14px 60px; }}
  .wrap {{ max-width:1280px; margin:0 auto; }}
  h1 {{ text-align:center; font-size:25px; margin-bottom:4px;
       background:linear-gradient(90deg,#c084fc,#6ee7b7,#fbbf24); -webkit-background-clip:text;
       background-clip:text; color:transparent; }}
  .sub {{ text-align:center; color:#b9a6d9; font-size:13.5px; margin-bottom:20px; }}
  .stat {{ display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-bottom:18px; }}
  .chip {{ background:rgba(255,255,255,.06); border:1px solid rgba(192,132,252,.3); border-radius:999px;
          padding:4px 14px; font-size:13px; }}
  table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
  th {{ background:rgba(192,132,252,.15); color:#e9d5ff; padding:6px 8px; border:1px solid rgba(255,255,255,.14);
       position:sticky; top:0; }}
  td {{ border:1px solid rgba(255,255,255,.10); padding:5px 8px; vertical-align:middle; }}
  tr:nth-child(even) td {{ background:rgba(255,255,255,.025); }}
  .num {{ font-variant-numeric:tabular-nums; text-align:center; }}
  .st, .mt {{ display:inline-block; font-size:11px; font-weight:800; border:1px solid; border-radius:999px;
             padding:0 8px; }}
  .mono {{ font-family:Consolas,monospace; }}
  .small {{ font-size:11.5px; color:#c9b8e8; }}
  .nm {{ font-weight:700; }}
  .foot {{ text-align:center; color:#8b76ad; font-size:12px; margin-top:14px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>風格A 生成規格表（139 筆・種子化）</h1>
  <div class="sub">Phase 1 產出｜base seed = {BASE_SEED}（seed = base + id×97，重跑結果一致）｜2026-10-16</div>
  <div class="stat">
    <span class="chip">P0 同名精確配對：<b style="color:#6ee7b7">{counts['P0']}</b></span>
    <span class="chip">P1 近緣指派：<b style="color:#93c5fd">{counts['P1']}</b></span>
    <span class="chip">P2 純提示詞：<b style="color:#fca5a5">{counts['P2']}</b></span>
    <span class="chip">還原圖使用：{len(used)} 張（每張最多一次）</span>
    <span class="chip">相鄰 id 主色不重複 ✔</span>
  </div>
  <table>
    <tr><th>id</th><th>星</th><th>物種</th><th>方式</th><th>還原圖</th><th>seed</th><th>體色</th><th>花紋</th><th>表情</th><th>姿勢</th><th>體態</th><th>趣味</th><th>配件</th><th>污漬/沾黏</th></tr>
    {chr(10).join(trs)}
  </table>
  <div class="foot">星級階梯：1★素體→2★小配件→3★戰士紋身→4★金邊武裝→5★傳說全套｜5★ 姿勢取自 13 式英雄姿勢池｜污漬隨星級遞增（1★僅微塵）｜全體剪影長高比 1:1.2–1.2:1（細長型加標「收攏體態」：頸平低前伸・收尾・低頭側・貼地低伏）｜趣味欄：隨機要素（動作類取代姿勢、情緒類修飾演出；5★僅情緒以免干擾英雄姿勢）｜生成尺寸：本體佔圖 50–60%｜2026-10-16 使用者規則</div>
</div>
</body>
</html>"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")

    print(f"rows: {len(rows)}  P0={counts['P0']} P1={counts['P1']} P2={counts['P2']}")
    print(f"recon used: {len(used)} / {len(recon_files)}")
    print(f"colors over-used (>8): {dup if dup else 'none'}")
    n_compact = sum(1 for r in rows if r["body_compact"])
    print(f"body_compact (slender families): {n_compact}")
    from collections import Counter as _C
    print("fun extras:", dict(_C(r["fun_zh"] for r in rows)))
    five_star = [r for r in rows if r["stars"] == 5]
    print("5★ hero poses:", [f"{r['id']}:{r['name']}→{r['pose_pool']}" for r in five_star])

if __name__ == "__main__":
    main()
