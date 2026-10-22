#!/usr/bin/env python3
"""Forest Adventure film V2 (A-Bao / B-Bao / BanBan) via SophNet happyhorse r2v.

V2 changes vs V1 (diagnosed from the delivered V1 frames, 2026-10-16):
- New authoritative kid photo (A-Bao wears a WHITE tee; V1 text card wrongly
  said light blue and the film drifted).
- BanBan shots (s7-s9) send the DFD-000 1-star asset flattened onto white as a
  SECOND reference_image (V1 described BanBan as 紫紅色 in text only and the
  model rendered a crimson reptile). If the endpoint rejects 2 refs, fall back
  to kids-only + corrected text.
- Continuity clause in every shot: fixed wardrobe / rex / egg appearance.
- Anti-blooper clause: one egg only, normal limbs, no clones.
- s3: only B swings one clean arc, A stays on the branch (V1 had A flying).
- s4: no mid-air egg passing (V1 duplicated the egg); B clutches the egg.
- s5: B shoves the egg into A's arms before they turn (explains the transfer).

Usage: python _gen_sophnet_forest_story_v2.py [s1 s2 ...] [--single]
  --single forces kids-only reference even for s7-s9.
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
CLIPS = HERE / "_forest_story_v2_clips"
STATE = HERE / "_forest_story_v2_state.json"
ATTACH = Path(r"C:\Users\hungm\AppData\Roaming\@sophclaw\desktop\attachments")
KIDS = ATTACH / "1b2e6e21-f6fd-4a81-8015-faa01ea03538" / "image.png"
BANBAN_REF = HERE.parents[3] / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_1star.png"

STYLE = (
    "電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，"
    "空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色，畫面穩定流暢。"
)
CAST = (
    "主角為參考圖片中的兩兄弟（容貌、髮型與服裝嚴格參照參考圖）："
    "哥哥 A寶（九歲、短黑髮、無眼鏡、白色圓領短袖T恤、卡其短褲），"
    "弟弟 B寶（七歲、短黑髮、細金屬框圓形眼鏡、橘色圓領短袖T恤、深色短褲）。表情生動、勇敢。"
)
CONT = (
    "全片連戲規範：兩兄弟服裝髮型前後完全一致；暴龍固定為深棕綠色鱗片、金黃色眼睛、滿口利牙；"
    "蛋固定為米白色蛋殼帶圓形紫色斑點；場景與黃昏金色光線前後一致。"
)
ANTI = (
    "動作自然合理：畫面中每個人物都只有雙手雙腳、五根手指、臉部與肢體不變形、無重影無複製人；"
    "恐龍蛋全片只有一顆。"
)
EGG = "米白色蛋殼帶圓形紫色斑點的巨大恐龍蛋"
REX = "深棕綠色鱗片、金黃色眼睛的巨大寫實暴龍（T-Rex）"
BANBAN = (
    "寶寶小龍「伴伴」（外觀嚴格遵照第二張參考圖）：紫水晶色細緻鱗片帶深紫色斑點、奶油白肚皮、"
    "頭頂一對金橘色分節大彎角、背脊到尾巴一排金橘色小刺、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼、"
    "白色小尖牙與粉紅舌頭、橘色小爪；圓滾滾、Q版可愛。"
)
TAIL = "電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。"

SHOTS = {
    # S1 dolly-in through ferns -> both kids hiding, T-Rex looming over egg
    "s1": (
        STYLE + "\n\n"
        "前景的巨大蕨葉後面躲著兩個亞洲小男孩，屏住呼吸偷偷往外看：" + CAST + "\n\n"
        "前方空地中央，" + EGG + "立在苔蘚上微微透光；" + REX + "低著頭、張開長滿利牙的大嘴，"
        "慢慢逼近這顆蛋準備一口吞下。\n\n鏡頭穿過前景蕨葉緩慢向前推近（dolly-in）。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S2 A shouts, rex whips around and roars
    "s2": (
        STYLE + "\n\n"
        "哥哥 A寶從大樹後跳出來，雙手圈在嘴邊，對暴龍大喊，嘴巴張大、表情誇張勇敢；"
        "弟弟 B寶躲在另一棵大樹後緊張探頭。" + CAST + "\n\n"
        + REX + "猛地轉頭，怒目瞪視，張開大嘴對空怒吼，聲波震得樹葉紛飛。"
        "手持鏡頭先拍 A寶大喊，再快速甩向暴龍（whip pan），特寫暴龍的獠牙與怒目。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S3 low-angle slow-mo: B swings ONE clean arc, snatches the egg; A stays on branch
    "s3": (
        STYLE + "\n\n"
        "低角度仰拍＋慢動作：弟弟 B寶雙手抓著一條長藤蔓從高處盪下，身體劃出一道乾淨的大弧線，"
        "掠過暴龍的手爪旁邊，雙臂一把抱起苔蘚上的" + EGG + "，順勢盪回高處；"
        "哥哥 A寶全程站在對面大樹的粗枝上，只伸手準備接應，不跳不飛。" + CAST + "\n\n"
        + REX + "撲空，憤怒甩頭。藤蔓與落葉飛舞，緊張刺激。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S4 lateral tracking vine chase; B clutches the egg, no passing
    "s4": (
        STYLE + "\n\n"
        "橫向平移跟拍（一鏡到底感）：兩個男孩在巨大樹幹之間一前一後抓著藤蔓盪躍前進，"
        "弟弟 B寶雙臂把" + EGG + "緊緊抱在懷裡（蛋不離手、不拋不接），哥哥 A寶在他前方回頭伸手拉他一把；"
        "後方" + REX + "怒吼著撞倒小樹與蕨葉，緊追不捨。" + CAST + "\n\n速度感十足、動態飛躍。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S5 cliff edge: B shoves egg to A, both turn, rex lands, eye-line standoff
    "s5": (
        STYLE + "\n\n"
        "黃昏懸崖邊：兩個男孩落地急停，弟弟 B寶迅速把" + EGG + "塞進哥哥 A寶懷裡，"
        "兩人同時回頭轉身、背對萬丈深谷；" + REX + "從林中一躍而出，重重落在幾步之外，"
        "兩邊眼神對上（暴龍與兩個男孩的視線正反打）。" + CAST + "\n\n"
        "環繞鏡頭繞著雙方轉半圈（orbit），風聲與落葉飛舞，金色逆光。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S6 jaws open -> egg blazes white (spots still visible), rex blinded
    "s6": (
        STYLE + "\n\n"
        "千鈞一髮：" + REX + "張開血盆大口傾身撲向兩個男孩；就在這一瞬間，A寶懷中的" + EGG +
        "綻放刺眼白金色光芒（蛋殼的紫色斑點在光芒中仍隱約可辨），"
        "光芒像衝擊波一樣掃開落葉與塵土，暴龍被強光逼得閉眼撇頭、雙爪遮臉。"
        "弟弟 B寶緊緊抓住 A寶的手臂。" + CAST + "\n\n鏡頭快速推近巨蛋，然後白光炸滿全畫面。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S7 light fades, BanBan hatches (2nd ref = BanBan asset), yawns at rex
    "s7": (
        "電影級實拍質感（真人電影），真實熱帶雨林，柔美逆光，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色。\n\n"
        "白光漸退：A寶雙手中的蛋殼出現裂痕、啪地破開，" + BANBAN + "在 A寶手中登場，"
        "慢慢睜開眼睛，對著暴龍打了一個大大的哈欠，慵懶可愛。兩個男孩睜大眼睛、驚喜地看著牠：" + CAST + "\n\n"
        + REX + "愣在原地。微距推近鏡頭。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S8 white vortex sucks plants + rex-with-tree; rocks stay; kids & BanBan safe
    "s8": (
        STYLE + "\n\n"
        + BANBAN + "嘴裡冒出一個白色漩渦，越轉越大，像龍捲風一樣掃過森林：樹木、藤蔓、落葉、塵土全被吸進漩渦裡；"
        + REX + "驚恐地想逃，緊緊抱住一棵大樹，結果連龍帶樹一起被吸走消失。"
        "伴伴和兩個男孩站在原地，被柔和白光罩住、毫髮無傷；地面上的岩石與石頭紋絲不動。\n\n"
        "廣角環繞鏡頭（swirl），氣流狂舞後歸於平靜。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S9 hiccup, hop down, walk, turn back and wave (end line is added in post)
    "s9": (
        STYLE + "\n\n"
        "風平浪靜、陽光灑落。" + BANBAN + "打了一個小小的嗝，輕巧地跳下地，搖著尾巴往前走幾步，"
        "停下來回頭看向兩個男孩，露出燦爛笑容，抬起小爪對他們招手，眼睛笑成彎月。"
        "兩個男孩開心地互看、跟上前去：" + CAST + "\n\n鏡頭低角度跟拍再慢慢拉背（dolly-out），"
        "畫面溫暖明亮，最後定格。\n\n" + CONT + "\n" + ANTI + "\n" + TAIL
    ),
}

# ref configs per shot, tried in order (fallback if the endpoint rejects 2 refs)
BANBAN_SHOTS = ("s7", "s8", "s9")


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
        print(f"[{shot}] exists ({out.stat().st_size} B) -> skip")
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
    print(f"REFS = {names} (single={single})")
    uris_by_n = {KIDS.name: data_uri(KIDS), BANBAN_REF.name: data_uri(BANBAN_REF)}
    print(f"ref data URIs built: {[len(u) for u in uris_by_n.values()]} chars", flush=True)
    ok = 0
    for shot in want:
        if generate(shot, uris_by_n, single):
            ok += 1
        time.sleep(3)
    print(f"== done: {ok}/{len(want)} ==")
    return 0 if ok == len(want) else 1


if __name__ == "__main__":
    raise SystemExit(main())
