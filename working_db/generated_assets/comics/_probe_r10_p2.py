# -*- coding: utf-8 -*-
"""第10輪探針：Wan2.6-Edit（參考圖鎖恐龍）vs Qwen-Image（純文生圖）誰能固定臉型體型。"""
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
         "is painted realistically in expressive oil-paint with visible brush strokes; the two baby "
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

TEXT_LOCK = (
    "CHARACTER SHEET (binding, identical in every panel): the purple baby dragon = vivid purple chubby "
    "body with darker purple round spots, EXACTLY ONE pair of thick golden-yellow segmented horns plus "
    "ONE single row of small golden cone spikes along neck/back/tail, very large round golden-amber eyes, "
    "large purple bat wings with magenta-pink-to-orange gradient membranes carrying ROUND DARK-PURPLE "
    "spots, ONE pair of big pink inner ears, cream-ivory belly plates, chunky golden claws, round snout "
    "with nostrils, tiny white fangs, NO human face/ears/cheeks. The boy = EXACTLY 10 years old, same "
    "oval face with rounded chin, short dark-brown hair with straight bangs under a khaki safari hat, "
    "big dark-brown eyes, khaki safari hat, cream sleeveless vest over orange T-shirt, brown shorts, "
    "white socks, sturdy brown boots, small green backpack.")

NEGATIVE = ("文字, 數字, 浮水印, 簽名, 對話泡泡, 漫畫分格邊框, 模糊, 低解析度, 變形, 多餘的肢體, "
            "拟人化恐龙, 恐龙人脸, 塑膠感, 硬塑料光澤, 多餘的角")

HDRS = {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def call(method, url, payload=None, timeout=180):
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
    out = RAW / f"_probe_r10_{tag}.png"
    task_id = None
    for body in bodies:
        try:
            created = call("POST", f"{BASE}/task", body)
        except urllib.error.HTTPError as e:
            print(f"{tag}: HTTP {e.code} {e.read().decode('utf-8','replace')[:150]}", flush=True)
            continue
        except Exception as e:
            print(f"{tag}: net {type(e).__name__}", flush=True)
            continue
        tid = find_task_id(created)
        if tid:
            task_id = tid
            print(f"{tag}: task {tid} body_keys={list(body.get('input',{}).keys())}", flush=True)
            break
        print(f"{tag}: {json.dumps(created, ensure_ascii=False)[:180]}", flush=True)
    if not task_id:
        print(f"{tag}: CREATE_FAILED", flush=True)
        return
    deadline = time.time() + 420
    while time.time() < deadline:
        time.sleep(5)
        try:
            st = call("GET", f"{BASE}/task/{task_id}", timeout=60)
        except Exception:
            continue
        url = extract_url(st)
        if url:
            urllib.request.urlretrieve(url, out)
            print(f"{tag}: OK {out.name} {out.stat().st_size}", flush=True)
            return
        res = st.get("output") or st.get("result") or {}
        state = str(res.get("taskStatus") or res.get("status") or "").upper()
        if any(s in state for s in ("FAIL", "ERROR", "CANCEL")):
            print(f"{tag}: TASK_FAILED {json.dumps(res, ensure_ascii=False)[:200]}", flush=True)
            return
    print(f"{tag}: POLL_TIMEOUT", flush=True)


PROMPT_EDIT = f"{STYLE} {SCENE_P2} {EDIT_LOCK}"
PROMPT_TEXT = f"{STYLE} {SCENE_P2} {TEXT_LOCK}"

run("wanedit", [
    {"model": "Wan2.6-Edit",
     "input": {"prompt": PROMPT_EDIT, "negative_prompt": NEGATIVE,
               "images": [REF_BANBAN, REF_SALTA]}},
    {"model": "Wan2.6-Edit",
     "input": {"prompt": PROMPT_EDIT, "images": [REF_BANBAN, REF_SALTA]}},
])
run("qwen", [
    {"model": "Qwen-Image",
     "input": {"prompt": PROMPT_TEXT, "negative_prompt": NEGATIVE,
               "parameters": {"size": "1536*1024", "seed": 7}}},
    {"model": "Qwen-Image",
     "input": {"prompt": PROMPT_TEXT, "negative_prompt": NEGATIVE,
               "parameters": {"size": "1536*1024"}}},
    {"model": "Qwen-Image",
     "input": {"prompt": PROMPT_TEXT, "negative_prompt": NEGATIVE}},
])
run("qwen_ref", [
    {"model": "Qwen-Image",
     "input": {"prompt": PROMPT_EDIT, "negative_prompt": NEGATIVE,
               "images": [REF_BANBAN, REF_SALTA]}},
])
print("PROBE_DONE", flush=True)
