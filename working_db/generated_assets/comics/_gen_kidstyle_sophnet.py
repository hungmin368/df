# -*- coding: utf-8 -*-
"""寫實人類風格變體試產（SophNet ImageGenerator 版；Gemini 額度耗盡時的替代線）

同一格 P2 分鏡 × 四種真人渲染流派。2026-10-22 探針實況：舊同步路由 /image-edit 已死
（20204）；任務端點上 qwen-image 系全 20011 未部署、Qwen-Image-Edit/Z-Image-Turbo-Edit
不在型錄（20030）；可用者＝Qwen-Image-Edit-2509（編輯模型，必帶 input.images，恐龍用
遊戲原圖公網 URL 鎖定）與 Wan2.6-T2I（純文生圖，恐龍靠文字描述鎖定）。

輸出：_raw/kidstyle_{film,photo,gamecg,paint}_p2_sophnet.png
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator"
RAW = HERE / "_raw"
RAW.mkdir(exist_ok=True)

MODELS = [
    ("Wan2.6-T2I", False),             # 純文生圖：風格彈性大，攝影流派指令有機會生效
    ("Qwen-Image-Edit-2509", True),    # 編輯模型：帶參考圖鎖恐龍，但實測會把畫面統一 3D 卡通化
]
REF_URL = "https://hungmin368.github.io/df/game_db/assets/dinos_2/DFD-000_%E4%BC%B4%E4%BC%B4_2star.png"

DRAGON_REF = (
    "Reproduce the purple baby dragon from the reference image EXACTLY - identical design, colors (vivid purple "
    "body with darker purple round spots, golden-yellow segmented horns and cone spikes, purple bat wings with "
    "magenta-to-orange gradient membranes dotted with magenta spots, big pink inner ears, cream-ivory belly, "
    "golden claws), proportions and face; only pose and expression may change. It is a reptile: round snout with "
    "nostrils, tiny white fangs, NO human face, NO human ears, NO cheeks on the dragon."
)

DRAGON_DESC = (
    "A cute chibi 3D toy-style baby dragon with soft satin skin sheen: vivid purple body with darker purple round "
    "spots, golden-yellow segmented horns and cone spikes, small purple bat wings with magenta-to-orange gradient "
    "membranes dotted with magenta spots, big pink inner ears, cream-ivory belly, golden claws, big round "
    "golden-amber eyes with white specular highlights. It is a reptile: round snout with nostrils, tiny white "
    "fangs, NO human face, NO human ears, NO cheeks."
)

SCENE = (
    "Close-up discovery beat on a realistic tropical beach. The purple baby dragon "
    "presses its nose deep into the sand sniffing intensely, eyes popping wide in surprise; a corner of a "
    "RAINBOW-COLORED hexagonal crystal shard peeks out of the sand right in front of its nose with bright "
    "sparkle effects. {kid} crouches just behind, leaning in close with curious wide eyes and an amazed "
    "open-mouth smile. Warm morning light."
)

VARIANTS = {
    "film": dict(
        kid=("a REAL 10-year-old East Asian boy actor on a live-action film set: a fully photorealistic human "
             "being - natural skin with visible pores, fine peach fuzz, a few subtle freckles, slightly messy "
             "realistic short dark-brown hair, natural facial asymmetry, real hands; wearing a khaki safari hat, "
             "cream sleeveless vest over an orange T-shirt, brown shorts, sturdy little boots and a small green "
             "backpack with real fabric weave and worn edges"),
        style=("A single frame from a big-budget live-action adventure film shot on a 35mm cinema camera: the "
               "human boy is 100% photorealistic live-action footage with natural film grain, cinematic "
               "teal-and-warm color grading, soft anamorphic bokeh; the cartoon baby dragon is seamlessly "
               "composited into the live-action plate like a Hollywood CG creature with lighting and contact "
               "shadows matching the plate; real photographed beach location. ")),
    "photo": dict(
        kid=("a real 10-year-old East Asian boy photographed with an 85mm portrait lens: tack-sharp pore-level "
             "skin detail, visible skin texture and tiny blemishes, natural catchlights in dark-brown eyes, "
             "realistic wind-touched short dark-brown hair; wearing a khaki safari hat, cream sleeveless vest "
             "over an orange T-shirt, brown shorts, sturdy little boots and a small green backpack - every "
             "fabric fiber visible"),
        style=("High-end editorial photography composite at magazine quality: the human boy is a real photograph "
               "- DSLR sharpness, natural sunlight, true-to-life colors, shallow depth of field with creamy "
               "bokeh; the cartoon baby dragon stands on the photographed sand like a real physical collectible "
               "toy come to life with studio-grade lighting and contact shadows; location-photography beach. ")),
    "gamecg": dict(
        kid=("a realistic CG human child character at AAA video-game cinematic quality: physically-based skin "
             "shading with subtle subsurface scattering, individually groomed hair strands, realistic cloth "
             "weave on a khaki safari hat, cream sleeveless vest, orange T-shirt, brown shorts, sturdy little "
             "boots and small green backpack, expressive realistic child face"),
        style=("A cinematic still from a AAA video-game cutscene: the human child is a fully realistic high-end "
               "CG character rendered with physically-based rendering, ray-traced soft shadows and volumetric "
               "lighting; the baby dragon keeps its stylized toy-game-art look beside him, both sharing one "
               "unified cinematic lighting rig over a hyper-real CG beach. ")),
    "paint": dict(
        kid=("a realistic human boy painted in rich traditional media: oil-paint skin with visible brushwork "
             "texture, realistic human proportions and anatomy, naturally imperfect features, warm painterly "
             "light on his khaki safari hat, cream sleeveless vest, orange T-shirt, brown shorts, sturdy "
             "little boots and small green backpack"),
        style=("Premium illustrated movie-poster art: the human boy is painted realistically in expressive "
               "traditional oil-paint style with visible brush strokes; the cartoon baby dragon is rendered as "
               "glossy 3D-toy art popping against the painted background; painted realistic beach scenery with "
               "painterly waves and clouds. ")),
}

NEGATIVE = ("文字, 數字, 浮水印, 簽名, 對話泡泡, 漫畫分格邊框, 模糊, 低解析度, 變形, 多餘的肢體, "
            "拟人化恐龙, 恐龙人脸, 恐龙长出人类耳朵, 塑膠感, 硬塑料光澤")

HDRS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {KEY}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


def call(method: str, url: str, payload: dict | None = None, timeout: int = 180) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HDRS, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, "", []):
            return d[k]
    return None


def find_task_id(res: dict):
    # 實測 2026-10-22：create/poll 都包在 "output"；舊文件版才有 "result" 包裝
    for holder in (res.get("output"), res.get("result"), res):
        if isinstance(holder, dict):
            tid = pick(holder, "taskId", "task_id", "id")
            if tid:
                return tid
    return None


def extract_url(res: dict):
    out = res.get("output") if isinstance(res, dict) else None
    if isinstance(out, dict):
        results = out.get("results")
        if isinstance(results, list) and results:
            r0 = results[0]
            if isinstance(r0, dict):
                return pick(r0, "url", "imageUrl", "image_url", "imgUrl")
            if isinstance(r0, str) and r0.startswith("http"):
                return r0
        choices = out.get("choices")
        if isinstance(choices, list) and choices:
            for part in (choices[0].get("message") or {}).get("content") or []:
                if isinstance(part, dict):
                    u = pick(part, "image", "url", "imageUrl", "image_url")
                    if u:
                        return u
    return pick(res, "url", "imageUrl", "image_url")


def gen(vid: str, v: dict) -> bool:
    out = RAW / f"kidstyle_{vid}_p2_sophnet.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"{vid}: exists, skip")
        return True

    task_id = None
    used_model = None
    for model, is_edit in MODELS:
        dragon = DRAGON_REF if is_edit else DRAGON_DESC
        prompt = f"{v['style']} {dragon} {SCENE.format(kid=v['kid'])}"
        prompt += " No text, no speech bubbles, no letters, no watermark, no panel borders."

        inp = {"prompt": prompt, "negative_prompt": NEGATIVE}
        if is_edit:
            inp["images"] = [REF_URL]
        # 逐步降級：完整參數 → 只有 size → 裸 input → 再退掉 negative_prompt
        #（實測 Edit-2509 帶 parameters 會 500/20031，裸 input 才建立成功）
        body_shapes = [
            {"model": model, "input": dict(inp)},
        ]
        if is_edit:
            body_shapes.append({"model": model, "input": {"prompt": prompt, "images": [REF_URL]}})
        else:
            body_shapes.append({"model": model, "input": {"prompt": prompt}})

        for attempt in range(2):
            for body in body_shapes:
                try:
                    created = call("POST", f"{BASE}/task", body)
                except urllib.error.HTTPError as e:
                    msg = e.read().decode("utf-8", "replace")[:160]
                    print(f"{vid}/{model}: HTTP {e.code} {msg}")
                    continue
                except (urllib.error.URLError, TimeoutError, OSError) as e:
                    print(f"{vid}/{model}: net {type(e).__name__} (attempt {attempt + 1})")
                    time.sleep(10)
                    continue
                tid = find_task_id(created)
                if tid and not created.get("error"):
                    task_id = tid
                    used_model = model
                    print(f"{vid}: task {tid} created on {model}")
                    break
                print(f"{vid}/{model}: {json.dumps(created, ensure_ascii=False)[:200]}")
            if task_id:
                break
        if task_id:
            break
    if not task_id:
        print(f"{vid}: TASK_CREATE_FAILED")
        return False

    deadline = time.time() + 420
    while time.time() < deadline:
        time.sleep(5)
        try:
            st = call("GET", f"{BASE}/task/{task_id}", timeout=60)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"{vid}: poll net {type(e).__name__}")
            continue
        res = st.get("output") or st.get("result") or {}
        state = str(pick(res, "taskStatus", "status", "state") or "").upper()
        url = extract_url(st)
        if url:
            urllib.request.urlretrieve(url, out)
            print(f"{vid}: OK {out.name} {out.stat().st_size} bytes (model {used_model})")
            return True
        if any(s in state for s in ("FAIL", "ERROR", "CANCEL")):
            print(f"{vid}: TASK_FAILED {json.dumps(res, ensure_ascii=False)[:200]}")
            return False
    print(f"{vid}: POLL_TIMEOUT")
    return False


if __name__ == "__main__":
    only = sys.argv[1:]
    ok = True
    for vid, v in VARIANTS.items():
        if only and vid not in only:
            continue
        if not gen(vid, v):
            ok = False
    print("DONE_OK" if ok else "DONE_PARTIAL")
