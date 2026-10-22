#!/usr/bin/env python3
"""Generate the game opening movie V3 (lost kids -> rescue egg -> BanBan
hatches with the dex -> black-hole capture -> first steps -> title line)
via SophNet videogenerator/generate + happyhorse-1.0-r2v.

Continuity design (user directive 2026-10-21: 電影要連貫、角色模型過場不改變):
- Every shot ships the SAME fixed kids reference (_movie_kids_ref.jpg, cut
  from the user's 2026-10-21 photos) as reference_image.
- BanBan shots (s8-s11) add the SAME BanBan reference (_movie_bban_ref.jpg,
  flattened from DFD-000 1star) as a second reference_image; if the endpoint
  rejects 2 refs, fall back to kids-only + BanBan identity text (embedded in
  every prompt below).
- Every prompt embeds the same style card, cast card, continuity card
  (wardrobe / glasses / neck headphones / rex / egg / dex), anti-blooper card,
  and the no-subtitle tail. One egg only, no mid-air passing, no clones.

Design doc: report/game_opening_movie_storyboard_report.html
Usage: python _gen_opening_movie.py [s1 s2 ...] [--single]
  --single forces kids-only reference even for s8-s11.
Resumable: skips shots whose clip exists (>500 KB). Cost: ~Y4.5/shot.
"""
import base64
import io
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
KEY = (HERE / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/generate"
MODEL = "happyhorse-1.0-r2v"
CLIPS = HERE / "_opening_movie_clips"
STATE = HERE / "_opening_movie_state.json"
KIDS = Path(r"C:\Users\hungm\AppData\Roaming\@sophclaw\desktop\attachments\1b2e6e21-f6fd-4a81-8015-faa01ea03538\_movie_kids_ref.jpg")
BANBAN_REF = HERE / "_movie_bban_ref.jpg"

STYLE_FOREST = (
    "電影級實拍質感（真人電影），真實原始森林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，"
    "空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色，畫面穩定流暢。"
)
CONT = (
    "全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致（同款米白細條紋短袖T恤、黑色耳機掛頸）；"
    "暴龍固定為深棕綠色鱗片、金黃色眼睛、滿口利牙的寫實巨獸；"
    "恐龍蛋固定為米白色蛋殼帶圓形紫色斑點、全片只有一顆。"
)
ANTI = (
    "動作自然合理：每個人物都只有雙手雙腳、五根手指、臉部與肢體不變形、無重影無複製人；"
    "禁止空中拋接蛋；場景物理合理，無穿幫。"
)
TAIL = "電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。"

SHOTS = {
    # S1 lost in the park at dusk, fog swallows the path
    "s1": """電影級實拍質感（真人電影），真實都會公園，黃昏金色斜陽拖出長長人影，手持鏡頭微晃，淺景深、背景柔焦，溫暖電影調色。

黃昏的公園步道，哥哥 A寶（九歲、短黑髮側分、單眼皮笑眼、無眼鏡、米白細條紋短袖T恤、黑色耳機掛頸、淺綠短褲、黑色洞洞鞋）舉著手機四處張望，皺眉搖頭；弟弟 B寶（七歲、齊瀏海短黑髮、圓大眼、金色細框圓眼鏡、同款條紋T恤、黑色耳機掛頸、卡其束口長褲、黑色洞洞鞋）緊緊抓著哥哥的衣角，緊張地左右看。前方步道被詭異濃霧整條吞沒，A寶指向霧中，B寶搖頭往後退半步。微風吹動樹葉，氣氛由悠閒轉為不安，兩人對看一眼。

動作自然合理：每個人物都只有雙手雙腳、五根手指、臉部與肢體不變形、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S2 cross the glowing-fern barrier into the other world
    "s2": """電影級實拍質感（真人電影），真實原始森林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色。

兩兄弟牽著手小心走進濃霧，穿過一道由巨大發光蕨葉構成的無形結界——霧氣散開的瞬間，眼前的世界完全變了：參天巨木高聳入雲、比自己還高的巨大蕨類、空氣中漂浮金色光塵，黃昏天空掛著兩顆淡淡的月亮。兩人瞪大眼睛、慢慢轉頭環顧四周，B寶張大嘴驚嘆，A寶本能地把弟弟護在身後。鏡頭跟著兩人穿過結界後緩慢環視（orbit）。

主角為參考圖片中的兩兄弟（容貌、髮型、眼鏡與服裝嚴格參照參考圖）：哥哥 A寶（九歲、短黑髮側分、單眼皮笑眼、無眼鏡、米白底深褐細條紋短袖T恤、黑色頭戴式有線耳機掛在脖子上、淺綠色短褲、黑色洞洞鞋），弟弟 B寶（七歲、齊瀏海短黑髮、圓大眼、金色細框圓眼鏡、同款條紋T恤、黑色耳機掛頸、卡其色束口長褲、黑色洞洞鞋）。兩人脖子上的黑色耳機全片不摘除。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S3 peek through ferns: rex cornering the glowing egg
    "s3": """電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，空氣中漂浮微塵與光斑，淺景深、背景柔焦，手持鏡頭。

前景的巨大蕨葉後面躲著兩個亞洲小男孩，屏住呼吸偷偷往外看：哥哥 A寶（九歲、短黑髮側分、無眼鏡、米白細條紋T恤、頸掛黑耳機、淺綠短褲），弟弟 B寶（七歲、齊瀏海、金色圓框眼鏡、同款條紋T恤、頸掛黑耳機、卡其束口長褲）。

前方空地中央，一顆米白色蛋殼帶圓形紫色斑點的巨大恐龍蛋立在苔蘚上、殼面微微透光；一隻深棕綠色鱗片、金黃色眼睛、滿口利牙的寫實巨獸暴龍（T-Rex）低著頭，張開長滿利牙的大嘴，慢慢逼近這顆蛋，低吼震動空氣。鏡頭穿過前景蕨葉緩慢向前推近（dolly-in）。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後完全一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋固定為米白色蛋殼帶圓形紫色斑點。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人；恐龍蛋全片只有一顆。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S4 decoy shout -> B snatches the egg (one clean action)
    "s4": """電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束，手持鏡頭。

聲東擊西：哥哥 A寶（九歲、無眼鏡、米白細條紋T恤、頸掛黑耳機、淺綠短褲）從大樹後跳出來，雙手圈在嘴邊對暴龍大喊挑釁，表情誇張勇敢；深棕綠色鱗片、金黃色眼睛的寫實暴龍猛地轉頭怒視 A寶。同一時間，弟弟 B寶（七歲、金色圓框眼鏡、同款條紋T恤、頸掛黑耳機、卡其長褲）從反方向低身衝出，雙臂一把抱起苔蘚上米白色帶紫色斑點的恐龍蛋，轉身就跑，蛋緊緊抱在懷裡不離手。手持鏡頭先拍 A寶大喊，快速甩向暴龍轉頭（whip pan），再切低角度跟拍 B寶抱蛋衝刺。一個乾淨動作，無空中拋接。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋固定為米白色蛋殼帶圓形紫色斑點，全片只有一顆。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S5 lateral tracking chase through giant trunks
    "s5": """電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束穿過樹冠，空氣中漂浮微塵與光斑。

橫向平移跟拍（一鏡到底感）：兩個男孩在巨大樹幹之間一前一後狂奔，弟弟 B寶（七歲、金色圓框眼鏡、條紋T恤、卡其長褲）雙臂把米白色帶紫色斑點的恐龍蛋緊緊抱在懷裡（蛋不離手、不拋不接），哥哥 A寶（九歲、無眼鏡、條紋T恤、淺綠短褲）在他前方回頭伸手拉他一把；後方深棕綠色鱗片、金黃色眼睛的寫實暴龍怒吼著撞斷小樹、踩碎蕨葉緊追不捨，泥土與落葉飛濺，速度感十足、動態飛躍。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋固定為米白色蛋殼帶圓形紫色斑點，全片只有一顆。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S6 dead-end cliff, rex lands and roars (music-cut moment)
    "s6": """電影級實拍質感（真人電影），真實熱帶雨林邊緣的斷崖，黃昏金色逆光，雲霧繚繞的深谷，手持鏡頭。

兩個男孩衝出樹林後急停——前方是萬丈深谷，退無可退。A寶（九歲、無眼鏡、條紋T恤、淺綠短褲）把抱著蛋的 B寶（七歲、金色圓框眼鏡、條紋T恤、卡其長褲）護在身後，兩人緩緩後退。深棕綠色鱗片、金黃色眼睛的寫實暴龍從林中一躍而出，重重落地，步步逼近，背後夕陽逆光成巨大剪影；牠對兩人張開血盆大口巨吼，聲波震得碎石滾落谷中。低角度仰拍緩慢推近暴龍的獠牙與金黃怒目，兩兄弟在畫面邊緣顯得渺小。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋固定為米白色蛋殼帶圓形紫色斑點，全片只有一顆。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S7 hug over the egg -> white blaze fills the screen
    "s7": """電影級實拍質感（真人電影），真實熱帶雨林斷崖邊，黃昏金色逆光，手持鏡頭。

千鈞一髮：退無可退，A寶（九歲、無眼鏡、條紋T恤、頸掛黑耳機）把抱著蛋的 B寶（七歲、金色圓框眼鏡、條紋T恤）連同米白色帶紫色斑點的恐龍蛋一起緊緊抱進懷裡，兩兄弟背貼岩壁、緊閉眼睛低下頭，用身體護住蛋。就在暴龍撲下的瞬間，懷中的蛋綻放柔和白光，越來越亮（蛋殼的紫色斑點在光芒中仍隱約可辨），光芒像衝擊波一樣掃開落葉與塵土，深棕綠色鱗片的暴龍被強光逼得閉眼撇頭、雙爪遮臉。鏡頭環繞兩兄弟半圈（orbit）後快速推近巨蛋，白光炸滿全畫面、一片純白收尾。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋固定為米白色蛋殼帶圓形紫色斑點，全片只有一顆。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S8 shell cracks, BanBan appears holding the dex, yawns at rex
    "s8": """電影級實拍質感（真人電影），真實熱帶雨林，柔美逆光，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色。

白光漸退：A寶雙手中的蛋殼龜裂、啪地破開成幾片，一隻圓滾滾的寶寶小龍坐在破蛋殼中登場，雙爪還抱著一本厚重古書（深紫絨面封面、琥珀金色金屬邊框與護角、封面中央鑲一顆金黃色立體星星寶石）。寶寶小龍「伴伴」外觀嚴格遵照第二張參考圖：紫水晶色細緻鱗片帶深紫色斑點、奶油白肚皮、頭頂一對金橘色分節大彎角、背脊到尾巴一排金橘色小刺、粉色內耳與帶紫斑的粉紅翼膜、金黃琥珀色大圓眼、白色小尖牙與粉紅舌頭、橘色小爪。牠慢慢睜開眼睛，對著暴龍方向打了一個大大的哈欠，慵懶可愛；深棕綠色鱗片、金黃色眼睛的暴龍愣在原地。微距推近鏡頭。兩兄弟睜大眼睛驚喜地看著牠。

全片連戲規範：兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致；暴龍固定為深棕綠色鱗片、金黃色眼睛；蛋殼碎片與圖鑑造型前後一致。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人；只有一隻小龍。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S9 the dex opens a black-hole vortex and swallows the rex
    "s9": """電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束，空氣中漂浮微塵與光斑，廣角環繞鏡頭（swirl）。

圓滾滾的寶寶小龍「伴伴」（紫水晶色細鱗帶深紫斑點、奶油白肚皮、金橘色分節大彎角、粉紅翼膜、金黃琥珀色大圓眼）單爪舉起那本深紫絨面、琥珀金邊、封面鑲金黃星星寶石的古書圖鑑，對準暴龍；星星寶石中心張開成一個旋轉的黑色漩渦、越轉越大，像黑洞一樣吸扯周圍的一切：落葉、藤蔓、碎石紛紛飛起被吸入；深棕綠色鱗片、金黃色眼睛的寫實暴龍驚恐地用後爪扒住地面仍被緩緩拖走，最後整隻暴龍被捲入漩渦、消失不見，漩渦收攏成一滴金色光點回到書中。伴伴與兩個男孩（條紋T恤無眼鏡的哥哥、條紋T恤戴金色圓框眼鏡的弟弟）被柔和白光罩住、毫髮無傷；地面岩石紋絲不動。氣流狂舞後歸於平靜。

全片連戲規範：伴伴外觀嚴格遵照參考圖；圖鑑造型固定；兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人；只有一隻小龍。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S10 calm: BanBan climbs out, unsteady first steps
    "s10": """電影級實拍質感（真人電影），真實熱帶雨林，暴風過後陽光灑落，空氣清新、金色光斑漂浮，淺景深，低角度跟拍。

風平浪靜、陽光灑落。寶寶小龍「伴伴」（外觀嚴格遵照第二張參考圖：紫水晶色細鱗帶深紫斑點、奶油白肚皮、金橘色分節大彎角、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼）手腳並用從破蛋殼裡爬出來，站在殘殼上搖搖晃晃——牠邁出不穩的第一步，翅膀張開保持平衡，尾巴晃來晃去，差點跌倒又努力站穩，表情認真又呆萌可愛。旁邊地面放著那本深紫絨面、金黃星星寶石封面的古書圖鑑。兩兄弟（條紋T恤無眼鏡的哥哥、條紋T恤戴金色圓框眼鏡的弟弟）蹲在旁邊看得入迷，忍不住微笑。低角度跟拍。

全片連戲規範：伴伴外觀嚴格遵照參考圖；蛋殼碎片與圖鑑造型前後一致；兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人；只有一隻小龍。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
    # S11 turns back, waves, kids follow (subtitle + endcard land here in post)
    "s11": """電影級實拍質感（真人電影），真實熱帶雨林，陽光溫暖明亮，金色光斑漂浮，淺景深。

寶寶小龍「伴伴」（外觀嚴格遵照第二張參考圖：紫水晶色細鱗帶深紫斑點、奶油白肚皮、金橘色分節大彎角、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼）搖搖晃晃往前走幾步，慢慢走穩，停下來回頭看向兩個男孩，露出燦爛笑容（小尖牙與粉紅舌頭），抬起小爪對他們招手、眼睛笑成彎月，尾巴開心地擺動。哥哥 A寶（條紋T恤、頸掛黑耳機、淺綠短褲）牽起弟弟 B寶（同款條紋T恤、金色圓框眼鏡、卡其長褲）的手，開心地互看一眼、跟上前去。鏡頭低角度跟拍再慢慢拉背（dolly-out），畫面溫暖明亮，最後定格並在畫面上方留出乾淨空間。

全片連戲規範：伴伴外觀嚴格遵照參考圖；兩兄弟服裝髮型眼鏡與頸上黑耳機前後一致。
動作自然合理：每個人物都只有雙手雙腳、五根手指、無重影無複製人；只有一隻小龍。
電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。""",
}

# ref configs per shot, tried in order (fallback if the endpoint rejects 2 refs)
BANBAN_SHOTS = ("s8", "s9", "s10", "s11")


def ref_configs(shot: str, single: bool) -> list:
    if shot in BANBAN_SHOTS and not single:
        return [[KIDS, BANBAN_REF], [KIDS]]
    return [[KIDS]]


def call(method: str, url: str, payload: dict | None = None, timeout: int = 120):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
            "User-Agent": "Mozilla/5.0",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_urls(obj) -> list:
    out = []
    if isinstance(obj, str):
        if obj.startswith("http"):
            out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(find_urls(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(find_urls(v))
    return out


def data_uri(path: Path, maxpx: int = 768, quality: int = 86) -> str:
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > maxpx:
        s = maxpx / max(w, h)
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def log_state(entry: dict) -> None:
    state = []
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))
    state.append(entry)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def generate_once(shot: str, ref_uris: list, nrefs: int) -> bool:
    out = CLIPS / f"{shot}.mp4"
    content = [{"type": "text", "text": SHOTS[shot]}]
    content += [{"type": "image_url", "image_url": u, "role": "reference_image"} for u in ref_uris]
    body = {"model": MODEL, "content": content,
            "parameters": {"duration": 5, "resolution": "720P", "ratio": "16:9"}}
    print(f"[{shot}] submit (refs={nrefs}) ...", flush=True)
    sub = call("POST", BASE, body)
    if sub.get("status") != 0 or not sub.get("result"):
        print(f"[{shot}] SUBMIT REJECTED (refs={nrefs}): {json.dumps(sub, ensure_ascii=False)[:300]}")
        log_state({"shot": shot, "status": "submit-rejected", "refs": nrefs, "resp": sub})
        return False
    task_id = sub["result"].get("task_id") or sub["result"].get("id")
    print(f"[{shot}] task_id = {task_id}", flush=True)
    last = None
    for i in range(300):  # up to ~40 min (platform queues can be long)
        time.sleep(8)
        try:
            poll = call("GET", f"{BASE}/{task_id}")
        except urllib.error.HTTPError as e:
            print(f"[{shot}] [poll {i}] HTTP {e.code} (retrying)")
            time.sleep(12)
            continue
        except Exception as e:
            print(f"[{shot}] [poll {i}] {type(e).__name__} (retrying)")
            time.sleep(12)
            continue
        result = poll.get("result") or {}
        status = str(result.get("status") or "").lower()
        if status != last:
            print(f"[{shot}] [poll {i}] status={status}", flush=True)
            last = status
        if status in ("succeeded", "success", "completed", "done", "finished"):
            urls = [u for u in find_urls(result) if ".mp4" in u or "video" in u.lower()] or find_urls(result)
            if not urls:
                print(f"[{shot}] success but no URL: {json.dumps(result, ensure_ascii=False)[:300]}")
                log_state({"shot": shot, "status": "no-url", "task_id": task_id, "refs": nrefs})
                return False
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", str(out), urls[0]], check=True)
            size = out.stat().st_size
            print(f"[{shot}] saved {out} ({size} B)", flush=True)
            log_state({"shot": shot, "status": "succeeded", "task_id": task_id, "bytes": size, "refs": nrefs})
            return size > 500_000
        if status in ("failed", "fail", "error"):
            print(f"[{shot}] FAILED: {json.dumps(result.get('error'), ensure_ascii=False)[:300]}")
            log_state({"shot": shot, "status": "failed", "task_id": task_id, "refs": nrefs, "error": result.get("error")})
            return False
    print(f"[{shot}] TIMEOUT")
    log_state({"shot": shot, "status": "timeout", "task_id": task_id, "refs": nrefs})
    return False


def generate(shot: str, uris_by_n: dict, single: bool) -> bool:
    out = CLIPS / f"{shot}.mp4"
    if out.exists() and out.stat().st_size > 500_000:
        print(f"[{shot}] exists ({out.stat().st_size} B) -> skip", flush=True)
        return True
    for paths in ref_configs(shot, single):
        uris = [uris_by_n[p.name] for p in paths]
        if generate_once(shot, uris, len(paths)):
            return True
    return False


def main() -> int:
    CLIPS.mkdir(exist_ok=True)
    args = sys.argv[1:]
    single = "--single" in args
    want = [w for w in args if w in SHOTS] or list(SHOTS)
    names = sorted({KIDS.name, BANBAN_REF.name})
    print(f"REFS = {names} (single={single})", flush=True)
    print(f"KIDS exists: {KIDS.exists()}  BANBAN exists: {BANBAN_REF.exists()}", flush=True)
    uris_by_n = {KIDS.name: data_uri(KIDS), BANBAN_REF.name: data_uri(BANBAN_REF)}
    print(f"ref data URIs built: {[len(u) for u in uris_by_n.values()]} chars", flush=True)
    ok = 0
    for shot in want:
        if generate(shot, uris_by_n, single):
            ok += 1
        time.sleep(3)
    print(f"== done: {ok}/{len(want)} ==", flush=True)
    return 0 if ok == len(want) else 1


if __name__ == "__main__":
    raise SystemExit(main())
