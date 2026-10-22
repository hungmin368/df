# -*- coding: utf-8 -*-
"""方案A第1話 v5：寫實油畫插畫風（用戶 2026-10-22 選定 paint 變體）— SophNet 版

- 後端：Wan2.6-T2I 任務端點（Gemini 額度耗盡；Edit-2509 會把整格卡通化，不適用）。
- 風格：男孩與場景為傳統油畫寫實（可見筆觸），兩隻恐龍維持 3D 玩具光澤跳出畫面。
- 角色鎖定：無參考圖可餵（Edit 模型會毀風格）→ 伴伴／薩爾塔皆改文字鎖定
  （2026-10-22 四變體測試已驗證 Wan 文字鎖定 4/4 命中）。
- 尺寸：先試 ratio 對應 size 參數，被拒（500 20031）即降級裸 input（方形，構圖指令
  已要求角色置於中央水平帶，配合組版 cover_crop 中央裁切）。

輸出：_raw/propA_ch01_v5_p{1..6}.png
"""
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
RAW.mkdir(exist_ok=True)

MODEL = "Wan2.6-T2I"
RATIO_SIZE = {"21:9": "1792*768", "16:9": "1664*936", "3:2": "1536*1024"}

KID = ("a realistic human boy painted in rich traditional media: oil-paint skin with visible brushwork "
       "texture, realistic human proportions and anatomy, naturally imperfect features, warm painterly "
       "light on his khaki safari hat, cream sleeveless vest, orange T-shirt, brown shorts, sturdy "
       "little boots and small green backpack")

STYLE = ("Premium illustrated storybook panel painted in rich traditional oil-paint style: the human boy "
         "is painted realistically in expressive oil-paint with visible brush strokes; the two baby "
         "dragons are rendered as glossy 3D-toy art popping vividly against the painted scenery; the "
         "beach, sea and sky are painted realistically with painterly waves, clouds and warm sunlight. "
         "Dynamic manga composition, high detail. "
         "Absolutely NO text, NO speech bubbles, NO letters, NO sound-effect lettering, NO watermark, "
         "NO panel borders. ")

LOCK = (
    "CHARACTER LOCK (strict, from text descriptions): "
    "Dragon A = a chubby VIVID PURPLE baby dragon with slightly darker purple round spots on "
    "head/back/haunches, very large round GOLDEN-AMBER eyes with big white specular highlights, TWO thick "
    "golden-yellow segmented horns on the head plus smaller golden cone spikes along the neck, back and "
    "tail, large purple bat-style wings whose membranes gradient from magenta-pink at the leading edge to "
    "warm orange at the trailing edge, dotted with round magenta spots, big PINK inner ears, cream-ivory "
    "belly plates, chunky golden-yellow claws, and a cheerful open smile showing tiny white fangs and a "
    "pink tongue; a reptile with a round snout and nostrils - NO human face, NO human ears, NO cheeks. "
    "Keep Dragon A exactly this design in every panel - identical colors, markings, proportions and face; "
    "only pose and expression may change. "
    "Dragon B = a chubby SLATE-GRAY baby long-necked sauropod dinosaur whose tail curls into a tight "
    "spiral resting against its hip, big round golden-amber eyes with white highlights, small "
    "golden-yellow cone spikes on the head and along the neck ridge and back, one big PINK inner ear, a "
    "soft cream-tan underside, tiny golden claws and a gentle smile; when Dragon B stands or holds "
    "something the spiral tail stays visible against its hip. "
    "Keep Dragon B exactly this design in every panel. Never recolor or redesign either dragon."
)

PANELS = [
    dict(id=1, ratio="21:9", prompt=(
        f"Ultra-wide establishing shot of a golden tropical beach at bright morning. {KID} walks along the "
        f"shoreline toward an old shipwrecked wooden supply crate half-buried in the sand, reinforced with "
        f"iron straps and faded rainbow paint, a faint mysterious glint on its lid. Dragon A trots happily "
        f"beside the kid, tail up. Turquoise waves, palm trees, seabirds. Three-quarter back view, strong "
        f"sense of adventure. Keep both characters and the crate fully inside the central horizontal band "
        f"of the frame.")),
    dict(id=2, ratio="3:2", prompt=(
        f"Close-up discovery beat. ONLY TWO characters appear in this panel - the boy and Dragon A - "
        f"absolutely no other dragons, no other characters, no photobombers anywhere in the frame. "
        f"Dragon A presses its nose deep into the sand sniffing intensely, eyes squeezed then popping wide "
        f"in surprise; a corner of a RAINBOW-COLORED HEXAGONAL crystal shard - a broken piece of a compass, "
        f"NOT a round compass dial, NOT a needle - peeks out of the sand right in front of its nose with "
        f"bright sparkle effects. {KID} crouches just behind Dragon A, leaning in with wide shining eyes. "
        f"Exaggerated manga expressions, warm morning light.")),
    dict(id=3, ratio="16:9", prompt=(
        f"Dramatic low-angle beat on the beach. ONLY ONE character appears in this panel - Dragon B "
        f"completely alone, no other dragons, no other characters, no boy, nothing else alive in the frame. "
        f"Dragon B is a LONG-NECKED sauropod baby: its long slender neck is stretched UPWARD and held high "
        f"with the small head raised high above its back, not short, not tucked down. It stands proudly on "
        f"a driftwood log, holding the RAINBOW-COLORED HEXAGONAL crystal shard up between its tiny front "
        f"paws like a trophy, chin raised, smug delighted smile, its spiral-coiled tail visible against its "
        f"hip. Sunbeams and sparkle effects around the shard, sand dunes and turquoise sea behind, "
        f"shonen-style heroic framing.")),
    dict(id=4, ratio="21:9", prompt=(
        f"Full-throttle shonen comedy shock wide shot. Dragon B now wears the rainbow crystal shard as a "
        f"necklace strung on seaweed, posing proudly with a wink. {KID} does an exaggerated anime jaw-drop "
        f"shock pose, arms flailing, giant sweat drop flying; Dragon A beside him freezes mid-gasp with "
        f"wings popped up, jaw dropped. Dramatic RADIAL SPEED LINES burst across the background from the "
        f"center, exaggerated expressions, peak comedy energy. Keep all three characters fully inside the "
        f"central horizontal band of the frame.")),
    dict(id=5, ratio="16:9", prompt=(
        f"Determination beat. {KID} kneels drawing a big circle-and-arrow plan in the sand with a stick, "
        f"confident grin, pointing at a BIG impressive sandcastle nearby; Dragon A leans in on one side "
        f"with a pumped fist, Dragon B leans in from the other side, both fired up with tiny flame-like "
        f"determination sparks in their eyes; the faint glow of a rainbow crystal tip pokes out of a sand "
        f"mound beside the sandcastle. Warm mid-morning light, dynamic shonen framing.")),
    dict(id=6, ratio="3:2", prompt=(
        f"Triumphant shonen finale. {KID} hoists a blazing HEXAGONAL rainbow crystal shard - a broken "
        f"piece of the rainbow compass, NOT a round compass, no dial, no needle - high overhead in both "
        f"hands, classic hero pose, rainbow light rays bursting from it. Dragon A - the VIVID PURPLE baby "
        f"dragon with purple body, golden horns and magenta-to-orange gradient wing membranes exactly as "
        f"described in the character lock - leaps mid-air beside the kid cheering with both golden claws "
        f"raised. Dragon B - the SLATE-GRAY sauropod baby with spiral-coiled tail exactly as described in "
        f"the character lock - bounces joyfully on the sand wearing its seaweed necklace. All three "
        f"characters clearly visible. A big vivid rainbow arcs across the golden sunset sky above the sea, "
        f"sparkles everywhere, maximum joyful energy.")),
]

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


def gen(p) -> bool:
    pid = p["id"]
    out = RAW / f"propA_ch01_v5_p{pid}.png"
    if out.exists() and out.stat().st_size > 10000:
        print(f"p{pid}: exists, skip")
        return True
    prompt = f"{STYLE} {LOCK} {p['prompt']}"
    size = RATIO_SIZE.get(p["ratio"])
    inp = {"prompt": prompt, "negative_prompt": NEGATIVE}
    # 先試帶 size 參數（21:9/16:9/3:2），被拒即降級裸 input（方形輸出）
    body_shapes = [{"model": MODEL, "input": dict(inp), "parameters": {"size": size}}] if size else []
    body_shapes.append({"model": MODEL, "input": dict(inp)})

    task_id = None
    for attempt in range(2):
        for body in body_shapes:
            try:
                created = call("POST", f"{BASE}/task", body)
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "replace")[:160]
                print(f"p{pid}: HTTP {e.code} {msg}")
                continue
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                print(f"p{pid}: net {type(e).__name__} (attempt {attempt + 1})")
                time.sleep(10)
                continue
            tid = find_task_id(created)
            if tid and not created.get("error"):
                task_id = tid
                print(f"p{pid}: task {tid} created (size={bool(body.get('parameters'))})")
                break
            print(f"p{pid}: {json.dumps(created, ensure_ascii=False)[:200]}")
        if task_id:
            break
    if not task_id:
        print(f"p{pid}: TASK_CREATE_FAILED")
        return False

    deadline = time.time() + 420
    while time.time() < deadline:
        time.sleep(5)
        try:
            st = call("GET", f"{BASE}/task/{task_id}", timeout=60)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"p{pid}: poll net {type(e).__name__}")
            continue
        res = st.get("output") or st.get("result") or {}
        state = str(pick(res, "taskStatus", "status", "state") or "").upper()
        url = extract_url(st)
        if url:
            urllib.request.urlretrieve(url, out)
            print(f"p{pid}: OK {out.name} {out.stat().st_size} bytes")
            return True
        if any(s in state for s in ("FAIL", "ERROR", "CANCEL")):
            print(f"p{pid}: TASK_FAILED {json.dumps(res, ensure_ascii=False)[:200]}")
            return False
    print(f"p{pid}: POLL_TIMEOUT")
    return False


if __name__ == "__main__":
    only = sys.argv[1:]
    ok = True
    for p in PANELS:
        if only and str(p["id"]) not in only:
            continue
        if not gen(p):
            ok = False
    print("DONE_OK" if ok else "DONE_PARTIAL")
