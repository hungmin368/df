#!/usr/bin/env python3
"""Level-clear cute short: 4x4 beach celebration -> set off for the 5x5 plains.

No narration, no on-screen text: the "cleared 4x4, heading to 5x5" story is told
purely by dino actions (glowing 4x4 ground grid completed -> bigger glowing 5x5
grid appears over the plains -> gear up -> march off).

Cast (Style A assets as reference images):
  BanBan   assets/dinos_2/DFD-000_BanBan_2star.png   purple chibi dragon
  Trike    assets/dinos_2/batch/21.webp              mango-yellow triceratops
  Stego    assets/dinos_2/batch/11.webp              peach-pink stegosaurus
  Raptor   assets/dinos_2/batch/200.webp             lapis-blue striped raptor

Reference strategy per shot (tried in order):
  1) two refs: BanBan sheet + square 2x2 grid sheet (all four cast members)
  2) one ref : the square 2x2 grid sheet alone
NOTE (2026-10-17 probe): the videogenerator validates every reference image at
"resolution must be at least 300x300" AFTER our 896px downscale, so wide sheets
(3:1 / 4:1 aspect) were rejected; the square 2x2 grid passes.

Usage:
  python _gen_sophnet_story_lv4.py --dryrun     # build ref sheets, print prompts
  python _gen_sophnet_story_lv4.py              # generate s1..s4
  python _gen_sophnet_story_lv4.py s2 s4        # subset / resume
  python _gen_sophnet_story_lv4.py --single     # force single-sheet ref
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
CLIPS = HERE / "_story_lv4_clips"
STATE = HERE / "_story_lv4_state.json"

BANBAN_REF = HERE.parent / "DFD-000_伴伴_2star.png"
TRIO_SRC = [HERE.parent / "batch" / "21.webp", HERE.parent / "batch" / "11.webp", HERE.parent / "batch" / "200.webp"]
SHEET_GRID = HERE / "_story_lv4_ref_grid2x2.png"

STYLE = (
    "可愛 Q 版 3D 卡通動畫電影質感（高品質卡通渲染、玩具動畫電影感），色彩柔和飽和、"
    "軟緞面鱗片光澤、溫暖明亮的陽光、淺景深、畫面穩定流暢。"
)
CAST = (
    "畫面主角是參考圖中的四隻 Q 版小恐龍（外觀嚴格遵照參考圖，不可走樣）："
    "小龍「伴伴」（紫水晶色細緻鱗片帶深紫斑點、奶油白肚皮、頭頂一對金橘色分節大彎角、"
    "背脊到尾巴一排金橘色小刺、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼、開心笑容露白色小尖牙）；"
    "芒果黃色的圓滾滾小三角龍（奶油白肚、頭盾邊緣一圈小角刺、兩支大眉角＋鼻上小角、開心咧嘴笑）；"
    "蜜桃粉色的小劍龍（背上一排圓潤粉色背板、尾巴末端小刺、奶油白肚）；"
    "青藍色帶深藍條紋的小迅猛龍（金黃大圓眼、頭背一排小金刺、粉色內耳）。"
)
CONT = (
    "全片連戲規範：四隻小恐龍的體色與外觀前後完全一致（伴伴紫水晶色＋金橘角、三角龍芒果黃、"
    "劍龍蜜桃粉、迅猛龍青藍條紋）；場景固定為晴朗熱帶沙灘（白沙、椰子樹）與遠方翠綠草原；"
    "光格固定為金黃色光線構成；光線氛圍全片一致。"
)
ANTI = (
    "動作自然合理、可愛討喜：每種恐龍全片只出現一隻、四肢與身體不變形、無重影無複製體；"
    "畫面中除了各鏡頭場景描述的發光方陣外，不可多出任何其他方陣或額外光格。"
)
TAIL = "電影級高細節、畫面穩定流暢，無字幕、無文字、無數字、無浮水印。"

SHOTS = {
    # S1 celebration: last cell of the 4x4 ground grid lights up, four dinos cheer
    "s1": (
        STYLE + "\n\n"
        "場景：晴朗的熱帶沙灘，白沙、椰子樹、藍天白雲，遠方是翠綠草原。"
        "沙地上鋪著一片由金黃色光線構成的十六格方陣光格（4×4、每邊四格的發光柵格平鋪在沙面上），"
        "最後一格「啪」地點亮，整片光格綻放金色星屑與光粒子，像通關慶祝。\n\n"
        "動作：伴伴開心地原地轉圈跳起、張開小爪歡呼；小三角龍蹦蹦跳跳、低頭用鼻角把一小撮白沙拋向空中；"
        "小劍龍開心甩尾巴、背板輕輕發亮；小迅猛龍興奮地繞著大家快速跑一圈、捲起細細白沙塵。" + CAST + "\n\n"
        "鏡頭：低角度緩慢推近（dolly-in），金色星屑飛舞，氣氛歡樂可愛。\n\n" + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S2 reveal: bigger 5x5 grid materializes over the plains, dinos gaze up
    "s2": (
        STYLE + "\n\n"
        "場景：同一片晴朗沙灘，地上的十六格光陣保持微亮；遠方翠綠草原的上空，"
        "緩緩浮現一片更大的金黃色二十五格方陣光格（5×5、每邊五格的發光柵格，比地上的光陣更大更亮），"
        "格子一格一格依序閃亮。\n\n"
        "動作：四隻小恐龍同時停下動作、抬頭仰望，眼睛睜得又圓又亮；小三角龍伸出前腿指向天空的大光格；"
        "小劍龍的背板輕輕顫動；小迅猛龍跳到伴伴身旁一起仰望；伴伴小嘴張成「哇」的驚喜表情。" + CAST + "\n\n"
        "鏡頭：從恐龍們仰望的臉緩緩上搖（tilt-up）到天空的大光格，充滿期待感。\n\n" + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S3 gear-up: cute preparation montage, then line up behind BanBan
    "s3": (
        STYLE + "\n\n"
        "場景：同一片沙灘，地上的十六格光陣溫柔微亮，天空的二十五格大光格遠遠閃著金光。\n\n"
        "動作：四隻小恐龍整裝待發——伴伴認真地披上一片大葉子當小披風、挺胸擺出小勇士姿勢；"
        "小三角龍原地扭身暖身伸展；小劍龍用尾巴拍打沙面打出咚咚節奏；"
        "小迅猛龍繞圈衝刺後帥帥急停、擺出「跟上我」的前爪指路姿勢；"
        "最後四隻自覺排成一路縱隊，伴伴站最前面。" + CAST + "\n\n"
        "鏡頭：橫向緩慢平移（lateral dolly）掃過排隊的四隻小恐龍，俏皮有勁。\n\n" + CONT + "\n" + ANTI + "\n" + TAIL
    ),
    # S4 march off: waddle toward the plains, BanBan waves back at camera
    "s4": (
        STYLE + "\n\n"
        "場景：沙灘上的一條小路通往遠方翠綠的草原；隊伍身後，地上的十六格光陣溫柔閃爍道別；"
        "前方草原上空的二十五格大光格閃著金光迎接。\n\n"
        "動作：四隻小恐龍搖搖擺擺列隊前進——伴伴走在最前面、高舉一面小葉子旗、昂首闊步；"
        "小迅猛龍衝到前頭又折返回來催促大家；小劍龍與小三角龍開心跟進。"
        "伴伴回頭對鏡頭揮揮小爪、露出燦爛笑容，然後蹦跳著跟上隊伍。" + CAST + "\n\n"
        "鏡頭：緩慢拉遠＋升起（dolly-out、crane-up），溫暖逆光，最後定格在遠去的小隊伍與發光的大方格。\n\n"
        + CONT + "\n" + ANTI + "\n" + TAIL
    ),
}


def flatten_white(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    return im.convert("RGB")


def build_grid2x2(out: Path, cell: int = 512) -> Path:
    """Square 2x2 grid of the four cast members (BanBan, trike, stego, raptor).

    Square aspect keeps both sides >=300px after the 896px data-uri downscale
    (the videogenerator rejects any reference side <300px).
    """
    tiles = [flatten_white(p) for p in [BANBAN_REF] + TRIO_SRC]
    sq = []
    for im in tiles:
        w = int(im.width * cell / im.height)
        im = im.resize((w, cell), Image.LANCZOS)
        c = Image.new("RGB", (cell, cell), (255, 255, 255))
        c.paste(im, ((cell - im.width) // 2, 0))
        sq.append(c)
    gap = 16
    W = cell * 2 + gap * 3
    sheet = Image.new("RGB", (W, W), (255, 255, 255))
    pos = [(gap, gap), (gap * 2 + cell, gap), (gap, gap * 2 + cell), (gap * 2 + cell, gap * 2 + cell)]
    for im, (x, y) in zip(sq, pos):
        sheet.paste(im, (x, y))
    sheet.save(out, "PNG")
    print(f"[ref] {out.name}: {sheet.size}, {out.stat().st_size} B")
    return out


def ref_configs(single: bool) -> list:
    if single:
        return [[SHEET_GRID]]
    return [[BANBAN_REF, SHEET_GRID], [SHEET_GRID]]


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


def data_uri(path: Path, maxpx: int = 896, quality: int = 88) -> str:
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
        except Exception as e:  # noqa: BLE001
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
    for paths in ref_configs(single):
        uris = [uris_by_n[p.name] for p in paths]
        if generate_once(shot, uris, len(paths)):
            return True
    return False


def main() -> int:
    args = sys.argv[1:]
    single = "--single" in args
    dry = "--dryrun" in args
    want = [w for w in args if w in SHOTS] or list(SHOTS)
    CLIPS.mkdir(exist_ok=True)
    build_grid2x2(SHEET_GRID)
    if dry:
        for shot in want:
            print(f"\n===== {shot} =====\n{SHOTS[shot]}")
        print(f"\nrefs per shot: {ref_configs(single)}")
        return 0
    uris_by_n = {}
    for p in [BANBAN_REF, SHEET_GRID]:
        uris_by_n[p.name] = data_uri(p)
        print(f"[uri] {p.name}: {len(uris_by_n[p.name])} chars")
    print(f"REFS = BanBan2star + grid2x2 sheet (single={single})", flush=True)
    ok = 0
    for shot in want:
        if generate(shot, uris_by_n, single):
            ok += 1
        time.sleep(3)
    print(f"== done: {ok}/{len(want)} ==")
    return 0 if ok == len(want) else 1


if __name__ == "__main__":
    raise SystemExit(main())
