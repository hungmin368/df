#!/usr/bin/env python3
"""Generate the 9-shot "Forest Adventure" film (A-Bao / B-Bao / BanBan) via
SophNet videogenerator + happyhorse r2v (reference-to-video, kid photos as
reference_image data URIs; probe-confirmed format 2026-10-16).

Usage: python _gen_sophnet_forest_story.py [s1 s2 ...]   (default: all shots)
Resumable: skips shots whose clip already exists (>500 KB). State (task ids)
is appended to _forest_story_state.json. Cost: 720P ~Y0.9/s x 5s = ~Y4.5/shot.

Camera/transition notes per shot live in bban_forest_story_camerawork_report.html.
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
CLIPS = HERE / "_forest_story_clips"
STATE = HERE / "_forest_story_state.json"
ATTACH = Path(r"C:\Users\hungm\AppData\Roaming\@sophclaw\desktop\attachments")
REFS = [  # kid reference photo (kept local; only sent to SophNet as a data URI)
    # both boys, clear faces - the single proven reference (probe S1, 2026-10-16);
    # kept identical across all shots so the characters stay consistent.
    ATTACH / "6ef208b4-49cc-4184-affa-aa38b043fb7e" / "image.png",
]

STYLE = (
    "電影級實拍質感（真人電影），真實熱帶雨林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，"
    "空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色，畫面穩定流暢。"
)
CAST = (
    "主角為參考圖片中的兩兄弟（容貌與髮型參照參考圖）：哥哥 A寶（九歲、短黑髮、無眼鏡、淺藍色短袖T恤、"
    "卡其短褲），弟弟 B寶（七歲、短黑髮、透明圓框眼鏡、橘色短袖T恤、深色短褲）。表情生動、勇敢。"
)
EGG = "一顆米白色帶紫色圓斑的巨大恐龍蛋。"
REX = "一隻巨大寫實的暴龍（T-Rex）。"
BANBAN = (
    "一隻圓滾滾的寶寶小龍「伴伴」：紫紅色細緻鱗片、奶油白肚皮、金橘色分節小角與背脊小刺、"
    "粉色內耳與粉紅翼膜、金黃琥珀色大圓眼、小尖牙與粉紅舌。"
)
TAIL = "電影級高細節、畫面穩定流暢，無字幕、無文字、無浮水印。"

SHOTS = {
    # S1 dolly-in through ferns -> both kids hiding, T-Rex looming over egg
    "s1": (
        STYLE + "\n\n"
        "前景的巨大蕨葉後面躲著兩個亞洲小男孩，屏住呼吸偷偷往外看：" + CAST + "\n\n"
        "前方空地中央，" + EGG + "立在苔蘚上微微透光；" + REX + "低著頭、張開長滿利牙的大嘴，"
        "慢慢逼近這顆蛋準備一口吞下。\n\n鏡頭穿過前景蕨葉緩慢向前推近（dolly-in）。" + TAIL
    ),
    # S2 A shouts, rex whips around and roars (in-shot whip pan to rex close-up)
    "s2": (
        STYLE + "\n\n"
        "哥哥 A寶從大樹後跳出來，雙手圈在嘴邊，對暴龍大喊，嘴巴張大、表情誇張勇敢；"
        "弟弟 B寶躲在另一棵大樹後緊張探頭。" + CAST + "\n\n"
        + REX + "猛地轉頭，怒目瞪視，張開大嘴對空怒吼，聲波震得樹葉紛飛。"
        "手持鏡頭先拍 A寶大喊，再快速甩向暴龍（whip pan），特寫暴龍的獠牙與怒目。\n\n" + TAIL
    ),
    # S3 low-angle slow-mo: B swings in on vine, snatches the egg
    "s3": (
        STYLE + "\n\n"
        "低角度仰拍＋慢動作：弟弟 B寶抓著一條長藤蔓從高處盪下，身體盪出大弧線，"
        "掠過暴龍的手爪旁邊，一把抱起苔蘚上的紫斑巨蛋，順勢盪離畫面；哥哥 A寶在對面樹上伸手準備接應。"
        + CAST + "\n\n" + REX + "撲空，憤怒甩頭。" + EGG + "在 B寶懷中微微透光。藤蔓與落葉飛舞，緊張刺激。\n\n" + TAIL
    ),
    # S4 lateral tracking: vine chase, pass the egg, rex crashing behind
    "s4": (
        STYLE + "\n\n"
        "橫向平移跟拍（一鏡到底感）：兩個男孩在巨大樹幹之間一前一後抓著藤蔓盪躍前進，"
        "合作把發光紫斑巨蛋互相傳接，神情專注興奮；後方暴龍怒吼著撞倒小樹與蕨葉，緊追不捨。"
        + CAST + "\n\n速度感十足、動態飛躍。" + TAIL
    ),
    # S5 cliff edge standoff, orbit + eye-line match
    "s5": (
        STYLE + "\n\n"
        "黃昏懸崖邊：兩個男孩落地急停、同時回頭轉身，背對萬丈深谷；" + REX + "從林中一躍而出，"
        "重重落在幾步之外，兩邊眼神對上（暴龍與兩個男孩的視線正反打）。" + CAST + "\n\n"
        "環繞鏡頭繞著雙方轉半圈（orbit），風聲與落葉飛舞，金色逆光。" + TAIL
    ),
    # S6 jaws open -> egg blazes white, rex blinded
    "s6": (
        STYLE + "\n\n"
        "千鈞一髮：" + REX + "張開血盆大口傾身撲向兩個男孩；就在這一瞬間，A寶懷中的紫斑巨蛋綻放刺眼白光，"
        "光芒像衝擊波一樣掃開落葉與塵土，暴龍被強光逼得閉眼撇頭、雙爪遮臉。"
        "弟弟 B寶緊緊抓住 A寶的手臂。" + CAST + "\n\n鏡頭快速推近巨蛋，然後白光炸滿全畫面。\n\n" + TAIL
    ),
    # S7 white light fades, BanBan hatches, yawns at the rex
    "s7": (
        "電影級實拍質感（真人電影），真實熱帶雨林，柔美逆光，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色。\n\n"
        "白光漸退：A寶雙手中的蛋殼出現裂痕、啪地破開，" + BANBAN + "在 A寶手中登場，"
        "慢慢睜開眼睛，對著暴龍打了一個大大的哈欠，慵懶可愛。兩個男孩睜大眼睛、驚喜地看著牠：" + CAST + "\n\n"
        + REX + "愣在原地。微距推近鏡頭。\n\n" + TAIL
    ),
    # S8 white vortex sucks everything (rocks stay), rex hugs tree and is taken
    "s8": (
        STYLE + "\n\n"
        + BANBAN + "（體型與剛破殼時相同、約幼兒雙手可捧的大小）嘴裡冒出一個白色漩渦，越轉越大，"
        "像龍捲風一樣掃過森林：樹木、藤蔓、落葉、塵土全被吸進漩渦裡；"
        + REX + "驚恐地想逃，緊緊抱住一棵大樹，結果連人帶樹一起被吸走消失。"
        "兩個男孩站在伴伴身旁、毫髮無傷，服裝與配件必須清楚可辨、不得被任何光暈沖淡或改變："
        "哥哥 A寶穿淺藍色短袖T恤與卡其短褲、無眼鏡；弟弟 B寶穿橘色短袖T恤、戴透明圓框眼鏡；"
        "地面上的岩石與石頭紋絲不動。\n\n"
        "廣角環繞鏡頭（swirl），氣流狂舞後歸於平靜。" + TAIL
    ),
    # S9 hiccup, hop down, walk, turn back and smile (end line is added in post)
    "s9": (
        STYLE + "\n\n"
        "風平浪靜、陽光灑落。" + BANBAN + "打了一個小小的嗝，輕巧地跳下地，搖著尾巴往前走幾步，"
        "停下來回頭看向兩個男孩，露出燦爛笑容，抬起小爪對他們招手，眼睛笑成彎月。"
        "兩個男孩開心地互看、跟上前去：" + CAST + "\n\n鏡頭低角度跟拍再慢慢拉背（dolly-out），"
        "畫面溫暖明亮，最後定格。" + TAIL
    ),
}


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
    im = Image.open(path).convert("RGB")
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


def generate(shot: str, ref_uris: list) -> bool:
    out = CLIPS / f"{shot}.mp4"
    if out.exists() and out.stat().st_size > 500_000:
        print(f"[{shot}] exists ({out.stat().st_size} B) -> skip")
        return True
    content = [{"type": "text", "text": SHOTS[shot]}]
    content += [{"type": "image_url", "image_url": u, "role": "reference_image"} for u in ref_uris]
    body = {"model": MODEL, "content": content,
            "parameters": {"duration": 5, "resolution": "720P", "ratio": "16:9"}}
    print(f"[{shot}] submit ...", flush=True)
    sub = call("POST", BASE, body)
    if sub.get("status") != 0 or not sub.get("result"):
        print(f"[{shot}] SUBMIT FAILED: {json.dumps(sub, ensure_ascii=False)[:400]}")
        log_state({"shot": shot, "status": "submit-failed", "resp": sub})
        return False
    task_id = sub["result"].get("task_id") or sub["result"].get("id")
    print(f"[{shot}] task_id = {task_id}", flush=True)
    last = None
    for i in range(150):  # up to ~20 min
        time.sleep(8)
        try:
            poll = call("GET", f"{BASE}/{task_id}")
        except urllib.error.HTTPError as e:
            print(f"[{shot}] [poll {i}] HTTP {e.code} (retrying)")
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
                log_state({"shot": shot, "status": "no-url", "task_id": task_id})
                return False
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", str(out), urls[0]], check=True)
            size = out.stat().st_size
            print(f"[{shot}] saved {out} ({size} B)", flush=True)
            log_state({"shot": shot, "status": "succeeded", "task_id": task_id, "bytes": size})
            return size > 500_000
        if status in ("failed", "fail", "error"):
            print(f"[{shot}] FAILED: {json.dumps(result.get('error'), ensure_ascii=False)[:300]}")
            log_state({"shot": shot, "status": "failed", "task_id": task_id, "error": result.get("error")})
            return False
    print(f"[{shot}] TIMEOUT")
    log_state({"shot": shot, "status": "timeout", "task_id": task_id})
    return False


def main() -> int:
    CLIPS.mkdir(exist_ok=True)
    want = sys.argv[1:] or list(SHOTS)
    want = [w for w in want if w in SHOTS]
    print(f"REFS = {[p.name for p in REFS]}")
    ref_uris = [data_uri(p) for p in REFS]
    print(f"ref data URIs built: {[len(u) for u in ref_uris]} chars", flush=True)
    ok = 0
    for shot in want:
        if generate(shot, ref_uris):
            ok += 1
        time.sleep(3)
    print(f"== done: {ok}/{len(want)} ==")
    return 0 if ok == len(want) else 1


if __name__ == "__main__":
    raise SystemExit(main())
