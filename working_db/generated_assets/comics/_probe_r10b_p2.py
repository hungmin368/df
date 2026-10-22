# -*- coding: utf-8 -*-
"""第10輪探針B：帶參考圖的請求 180s 逾時——改測 Qwen-Image-Edit / Edit-2509（編輯模型吃 images）
與單參考圖 Qwen-Image；建立逾時加長到 480s。"""
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator"
RAW = HERE / "_raw"

REF_BANBAN = "https://hungmin368.github.io/df/game_db/assets/dinos_2/DFD-000_%E4%BC%B4%E4%BC%B4_2star.png"
REF_SALTA = "https://hungmin368.github.io/df/game_db/assets/dinos/9.webp"

STYLE = ("Premium illustrated storybook panel painted in rich traditional oil-paint style: the human boy "
         "is painted realistically in expressive oil-paint with visible brush strokes; the baby "
         "dragons are rendered as glossy 3D-toy art popping vividly against the painted scenery; the "
         "beach, sea and sky are painted realistically with painterly waves, clouds and warm sunlight. "
         "Absolutely NO text, NO speech bubbles, NO letters, NO watermark, NO panel borders. ")

SCENE_P2 = (
    "Close-up discovery beat. ONLY TWO characters appear in this panel - the boy and the purple baby "
    "dragon - absolutely no other dragons, no sauropod, no other characters, no photobombers anywhere "
    "in the frame. The purple baby dragon presses its nose deep into the sand sniffing intensely, eyes "
    "squeezed then popping wide in surprise; a corner of a RAINBOW-COLORED HEXAGONAL crystal shard - a "
    "broken piece of a compass, NOT a round dial, NOT a needle - peeks out of the sand right in front "
    "of its nose with bright sparkle effects. A realistic human boy, EXACTLY 10 years old, with a "
    "khaki safari hat, cream sleeveless explorer vest over an orange T-shirt, brown shorts, white socks, "
    "sturdy brown boots and a small green backpack crouches just behind the dragon, leaning in with wide "
    "shining eyes. Warm morning light, exaggerated manga expressions.")

EDIT_LOCK = (
    "Reproduce BOTH reference characters EXACTLY as they appear in the reference images - identical "
    "species design, body proportions, face shape, colors, horns/spikes/ears, belly, claws; only pose, "
    "expression and camera angle may change. The purple dragon is reference image 1; do not invent any "
    "other dragon. Render them as glossy 3D-toy art over the painted scenery.")

NEGATIVE = ("文字, 數字, 浮水印, 簽名, 對話泡泡, 漫畫分格邊框, 模糊, 低解析度, 變形, 多餘的肢體, "
            "拟人化恐龙, 恐龙人脸, 塑膠感, 硬塑料光澤, 多餘的角")

HDRS = {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

PROMPT_EDIT = f"{STYLE} {SCENE_P2} {EDIT_LOCK}"


def call(method, url, payload=None, timeout=480):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HDRS, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_task_id(res):
    for holder in (res.get("output"), res.get("result"), res):
        if isinstance(holder, dict):
            for k in ("taskId", "task_id", "id"):
                if holder.get(k):
                    return holder[k]
    return None


def extract_url(res):
    out = res.get("output") if isinstance(res, dict) else None
    if isinstance(out, dict):
        results = out.get("results")
        if isinstance(results, list) and results:
            r0 = results[0]
            if isinstance(r0, dict):
                for k in ("url", "imageUrl", "image_url", "imgUrl"):
                    if r0.get(k):
                        return r0[k]
            if isinstance(r0, str) and r0.startswith("http"):
                return r0
    for k in ("url", "imageUrl", "image_url"):
        if isinstance(res, dict) and res.get(k):
            return res[k]
    return None


def run(tag, bodies):
    for body in bodies:
        try:
            res = call("POST", f"{BASE}/task", body)
        except Exception as e:
            detail = ""
            if isinstance(e, urllib.error.HTTPError):
                try:
                    detail = e.read().decode("utf-8", "replace")
                except Exception:
                    detail = ""
            print(f"{tag}: CREATE_ERR {e} {detail}", flush=True)
            continue
        task_id = find_task_id(res)
        if not task_id:
            print(f"{tag}: NO_TASK_ID {json.dumps(res)[:300]}", flush=True)
            continue
        print(f"{tag}: task {task_id}", flush=True)
        deadline = time.time() + 600
        while time.time() < deadline:
            time.sleep(5)
            try:
                st = call("GET", f"{BASE}/task/{task_id}", timeout=60)
            except Exception as e:
                print(f"{tag}: poll err {e}", flush=True)
                continue
            s = st.get("output", {}).get("taskStatus") or st.get("taskStatus")
            if s in ("SUCCESS", "FINISHED", "COMPLETED"):
                url = extract_url(st)
                if not url:
                    print(f"{tag}: NO_URL {json.dumps(st)[:300]}", flush=True)
                    break
                out = RAW / f"_probe_r10_{tag}.png"
                req = urllib.request.Request(url, headers=HDRS)
                with urllib.request.urlopen(req, timeout=180) as r, open(out, "wb") as f:
                    f.write(r.read())
                print(f"{tag}: OK {out.name} {out.stat().st_size}", flush=True)
                return
            if s in ("FAILED", "CANCELED", "CANCELLED"):
                print(f"{tag}: TASK_FAILED {json.dumps(st)[:400]}", flush=True)
                break
        else:
            print(f"{tag}: POLL_TIMEOUT", flush=True)


# 候選1：Qwen-Image-Edit（編輯模型，裸 input）
run("qwenedit", [
    {"model": "Qwen-Image-Edit",
     "input": {"prompt": PROMPT_EDIT, "negative_prompt": NEGATIVE,
               "images": [REF_BANBAN, REF_SALTA]}},
])
# 候選2：Edit-2509（已知吃 images；先前棄用因整格卡通化，本輪驗證油畫鎖定是否改善）
run("edit2509", [
    {"model": "Edit-2509",
     "input": {"prompt": PROMPT_EDIT, "negative_prompt": NEGATIVE,
               "images": [REF_BANBAN, REF_SALTA]}},
])
# 候選3：Qwen-Image T2I＋單參考（減少伺服器抓圖負擔）
run("qwen_1ref", [
    {"model": "Qwen-Image",
     "input": {"prompt": PROMPT_EDIT, "negative_prompt": NEGATIVE,
               "images": [REF_BANBAN]}},
])
print("PROBE_B_DONE", flush=True)
