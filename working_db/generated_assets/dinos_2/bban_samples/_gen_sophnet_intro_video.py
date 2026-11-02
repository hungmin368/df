#!/usr/bin/env python3
"""Generate the game intro animation "Hide-and-Seek BanBan" (gameplay-matching
hide-and-seek comedy, photoreal rainforest, baby dragon BanBan) via SophNet
videogenerator/generate + happyhorse-1.0-r2v (probe-confirmed 2026-10-16).

R2V conversion (2026-10-16): the old happyhorse-1.0-t2v flow re-invented BanBan
on every segmented call, so each cut looked like a different dragon. Every shot
now ships the same fixed character reference _intro_bban_ref.jpg (a cleaned
frame cropped from intro_bban_hide_720p.mp4, watermark removed) as a
reference_image data URI, plus an identity-binding line in the prompt.

Usage: python _gen_sophnet_intro_video.py [single|1|2|3]
  single (default) = one-shot 5s cut: search -> busted -> sneeze -> net pose
  1 / 2 / 3        = three-act storyboard: find / busted / net + logo gap
Design doc: report/bban_intro_video_prompts_report.html
Cost: 720P = ~Y0.9/sec x 5s = ~Y4.5 per run.
"""
import base64
import io
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
KEY = (HERE / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/generate"
MODEL = "happyhorse-1.0-r2v"
REF = HERE / "_intro_bban_ref.jpg"

# Identity binding: the reference image is the single source of truth for
# BanBan's look; the prose card below only reinforces it.
REFBIND = (
    "參考圖中的寶寶小龍就是「伴伴」本尊：請嚴格重現參考圖的外觀——"
    "紫紅色細緻鱗片、奶油白肚皮、頭頂兩支金橘色分節大彎角、背脊小金刺、"
    "粉色內耳與粉紅翼膜、金黃琥珀色大圓眼、橘色爪子；體型、花色與五官比例"
    "必須與參考圖完全一致，不得更換顏色或造型。"
)

# BanBan film spec card (keep in EVERY prompt): chubby baby dragon, amethyst-purple
# (#AF48DB) fine scales + dark purple spots, creamy white belly (#F8EBEF), two
# golden-orange (#E9901D) segmented curved horns + small nose horn, golden back
# spines, orange claws, pink inner ears + pink wing membranes (#CD305C), big round
# golden-amber eyes (#F7A007) with white highlights, tiny white fangs + pink tongue.
# NOTE: an earlier draft wrote BanBan as "翠綠色/green" - wrong; he is purple.
# Realism recipe: Detective-Pikachu-style live-action CG creature - photoreal
# materials, satin sheen (never plastic/vinyl gloss), contact shadows, film DOF.
SHOTS = {
    "single": """電影級實拍質感，真實熱帶雨林，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色。

鏡頭像在森林裡「尋找什麼」，緩慢橫移掃過蕨葉叢、石堆與樹洞。蕨葉後方藏著一隻圓滾滾的寶寶小龍「伴伴」：紫紅色細緻鱗片、奶油白肚皮、頭頂兩支金橘色分節大彎角、背脊小金刺、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼。牠自以為藏得天衣無縫，但紫紅色尾巴尖和一整片粉紅翅膀露在葉子外一搖一搖，金黃眼睛還從葉縫偷看鏡頭。

被發現後牠慌張打了個大噴嚏——蕨葉全被吹飛，牠僵在原地，慢慢露出心虛的燦爛笑容（小尖牙與粉紅舌），順手撿起地上一支木柄捕蟲網擺出英雄姿勢，對鏡頭眨眼、豎起小爪比讚，尾巴開心地擺動。

寫實皮膚與光影質感、與地面有真實接觸陰影、電影級高細節、畫面穩定流暢、無字幕、無文字、無浮水印。""",
    "1": """電影級實拍質感，真實熱帶雨林，黃昏金色光束穿過樹冠，蕨葉、苔蘚岩石與落葉泥土皆為實拍級真實質感，空氣中漂浮微塵與光斑，淺景深、背景柔焦，手持鏡頭。

鏡頭像在森林裡尋找什麼，緩慢橫移掃過三個可疑的藏身點：蕨葉叢後露出一根一晃一晃的紫紅色尾巴尖；大石頭旁露出一整片粉紅翼膜；樹洞裡一雙金黃琥珀色的大眼睛眨了一下又縮回去。一隻彩色蝴蝶飛過鏡頭前。鏡頭停住，彷彿發現「找到了！」。

高細節、畫面穩定流暢、無字幕、無文字。""",
    "2": """電影級特寫，真實熱帶雨林午後光。圓滾滾的寶寶小龍「伴伴」躲在一片超大的蕨葉後面：紫紅色細鱗皮膚、奶油白肚皮、頭頂兩支金橘色分節大彎角、背脊小金刺、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼。牠把爪子放在嘴邊對鏡頭「噓——」，眼睛得意地笑成彎月。

下一秒牠忍不住打了個大噴嚏，蕨葉全被吹飛；牠僵住，慢慢轉頭看向鏡頭，露出心虛的燦爛笑容（小尖牙與粉紅舌），搔搔後腦杓。手持鏡頭晃了一下，像在憋笑。

寫實皮膚與光影質感、電影級高細節、無字幕、無文字。""",
    "3": """電影級實拍質感，真實熱帶雨林，黃昏金色微光，淺景深。圓滾滾的寶寶小龍「伴伴」從地上撿起一支真實的木柄捕蟲網（紅棕色圓框、米白色網），牠有紫紅色細鱗、奶油白肚皮、金橘色分節大彎角、粉色內耳與粉紅翼膜、金黃琥珀色大圓眼。

牠得意地朝空中一揮，網子撈住一顆漂浮的發光小星籽，金光閃閃、細微光塵灑落。牠舉著網子轉向鏡頭，單手叉腰、眨眼、豎起小爪比讚，尾巴開心地擺動。鏡頭緩慢拉遠，畫面中央留出乾淨空間。

寫實光影質感、電影級高細節、無字幕、無文字。""",
}


def call(method: str, url: str, payload: dict | None = None) -> dict:
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_urls(obj) -> list[str]:
    urls: list[str] = []
    if isinstance(obj, str):
        if obj.startswith("http"):
            urls.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            urls.extend(find_urls(v))
    elif isinstance(obj, list):
        for v in obj:
            urls.extend(find_urls(v))
    return urls


def data_uri(path: Path, maxpx: int = 768, quality: int = 86) -> str:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if max(w, h) > maxpx:
        s = maxpx / max(w, h)
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> int:
    shot = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in SHOTS else "single"
    name = (
        "intro_bban_hide_720p.mp4" if shot == "single"
        else f"intro_bban_hide_s{shot}_720p.mp4"
    )
    out = HERE.parent.parent / name
    content = [{"type": "text", "text": REFBIND + "\n\n" + SHOTS[shot]}]
    content.append(
        {"type": "image_url", "image_url": data_uri(REF), "role": "reference_image"}
    )
    body = {
        "model": MODEL,
        "content": content,
        "parameters": {"duration": 5, "resolution": "720P", "ratio": "16:9"},
    }
    print(f"== submit (shot={shot} -> {name}, model={MODEL}, ref={REF.name}) ==")
    sub = call("POST", BASE, body)
    print(json.dumps(sub, ensure_ascii=False, indent=2)[:1500])
    if sub.get("status") != 0 or not sub.get("result"):
        print("SUBMIT FAILED")
        return 1
    task_id = sub["result"].get("task_id") or sub["result"].get("id")
    if not task_id:
        print("no task_id in result")
        return 1
    print("task_id =", task_id)

    last_status = None
    for i in range(240):  # up to 20 min
        time.sleep(5)
        poll = call("GET", f"{BASE}/{task_id}")
        result = poll.get("result") or {}
        status = str(
            result.get("status")
            or result.get("task_status")
            or result.get("state")
            or poll.get("status")
        )
        if status != last_status:
            print(f"[poll {i}] status={status} full={json.dumps(poll, ensure_ascii=False)[:1200]}")
            last_status = status
        else:
            print(f"[poll {i}] status={status}")
        if status.upper() in ("SUCCESS", "SUCCEEDED", "COMPLETED", "DONE", "FINISHED"):
            urls = [u for u in find_urls(result) if ".mp4" in u or "video" in u.lower()]
            if not urls:
                urls = find_urls(result)
            if not urls:
                print("SUCCESS but no URL found in result")
                return 1
            url = urls[0]
            print("video url =", url)
            subprocess.run(
                ["curl", "-sL", "-A", "Mozilla/5.0", "-o", str(out), url], check=True
            )
            size = out.stat().st_size
            print(f"saved {out} ({size} bytes)")
            return 0 if size > 100_000 else 1
        if status.upper() in ("FAIL", "FAILED", "ERROR"):
            print("GENERATION FAILED")
            return 1
    print("TIMEOUT")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
