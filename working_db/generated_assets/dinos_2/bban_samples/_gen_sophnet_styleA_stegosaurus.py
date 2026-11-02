import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
KEY = (HERE / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator"
OUT = HERE / "sophnet_styleA_stegosaurus.png"
SEED = 231

# model names per the console's own call example (lowercase) + skill screenshot
MODELS = ["qwen-image", "Qwen-Image", "Qwen-Image-Plus", "Z-Image-Turbo"]

# schema per https://sophnet.com/docs/component/vision_model.html:
# body = {model, input{prompt/images/negative_prompt}, parameters{size/seed/watermark}}
# poll = GET {BASE}/task/{taskId}; result carries output.results[]
PROMPT = (
    "Cute chibi 3D toy-style render of a baby Stegosaurus, soft organic satin skin "
    "sheen with subtle soft highlights and visible fine scale texture, big round "
    "golden-amber eyes with white specular highlights, cheerful open smile showing "
    "tiny white fangs and a pink tongue, creamy white belly. Rich indigo-blue body "
    "like lapis lazuli. Two straight rows of large upright kite-shaped plates "
    "running along the back from neck to tail, warm amber-orange plates with "
    "golden edges, every plate fully visible. Four long sharp yellow-orange tail "
    "spikes at the tip of a raised muscular tail. Small low head on a short neck, "
    "big rounded bulky body, sturdy four-legged stance. Natural weathering: subtle "
    "dirt smudges, small mud patches, tiny grass or leaf fragments on the legs, "
    "belly and tail. One simple woven grass armband with a small star charm around "
    "the front left leg, not covering any back plate. Action: joyful playful leap "
    "mid-air, front legs tucked up, tail swung high, delighted open-mouth laugh. "
    "Plain pure white studio background, soft even lighting, high-resolution "
    "digital art, single full-body creature only, centered. No text, no watermark."
)

NEGATIVE = (
    "塑膠感, 硬塑料光澤, 乙烯基玩具感, 強反光, 模糊, 低解析度, 變形, 多餘的肢體, "
    "多隻動物, 文字, 數字, 浮水印, 簽名, 邊框, 背景雜物"
)


def call(method: str, url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, "", []):
            return d[k]
    return None


def extract_url(res: dict):
    out = res.get("output")
    if isinstance(out, dict):
        # format B (sync image services, per console python example):
        # output.choices[0].message.content[{image|url}]
        choices = out.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        u = pick(part, "image", "url", "imageUrl", "image_url")
                        if u:
                            return u
        # format A (task poll): output.results[]
        results = out.get("results")
        if isinstance(results, list) and results:
            r0 = results[0]
            if isinstance(r0, dict):
                u = pick(r0, "url", "imageUrl", "image_url", "imgUrl")
                if u:
                    return u
            elif isinstance(r0, str) and r0.startswith("http"):
                return r0
    u = pick(res, "url", "imageUrl", "image_url")
    if u:
        return u
    imgs = res.get("images")
    if isinstance(imgs, list) and imgs:
        i0 = imgs[0]
        if isinstance(i0, dict):
            return pick(i0, "url", "imageUrl", "image_url")
        if isinstance(i0, str) and i0.startswith("http"):
            return i0
    return None


def task_state(res: dict) -> str:
    return str(pick(res, "status", "state", "taskStatus") or "").upper()


def main() -> None:
    shapes = [
        {"prompt": PROMPT, "negative_prompt": NEGATIVE},
        {"prompt": PROMPT},
    ]
    param_shapes = [
        {"size": "1328*1328", "seed": SEED},
        {"size": "1328*1328"},
        {"size": "1024*1024", "seed": SEED},
        {"size": "1024*1024"},
        None,
    ]
    created = None
    used_model = None
    for model in MODELS:
        for shape in shapes:
            for params in param_shapes:
                body = {"model": model, "input": shape}
                if params:
                    body["parameters"] = params
                try:
                    created = call("POST", f"{BASE}/task", body)
                except urllib.error.HTTPError as e:
                    msg = e.read().decode("utf-8", "replace")[:200]
                    print(f"{model} {list(shape.keys())} params={bool(params)}: HTTP {e.code} {msg}")
                    created = None
                    continue
                err = created.get("error") or {}
                if created.get("result") and not err:
                    used_model = model
                    print("task created:", model, list(shape.keys()),
                          "with-params" if params else "no-params")
                    break
                print(f"{model}: {json.dumps(created, ensure_ascii=False)[:250]}")
                created = None
            if created:
                break
        if created:
            break
    if not created:
        print("TASK_CREATE_FAILED")
        sys.exit(1)

    result = created.get("result") or {}
    task_id = pick(result, "id", "taskId", "task_id") or pick(created, "id", "taskId", "task_id")
    if not task_id:
        print("NO_TASK_ID_IN_RESPONSE:", json.dumps(created, ensure_ascii=False)[:300])
        sys.exit(1)
    print("task_id:", task_id)

    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(5)
        try:
            st = call("GET", f"{BASE}/task/{task_id}")
        except urllib.error.HTTPError as e:
            print("poll HTTP", e.code, e.read().decode("utf-8", "replace")[:200])
            continue
        res = st.get("result") or {}
        url = extract_url(res)
        print("poll:", str(st.get("status")), task_state(res),
              json.dumps(res, ensure_ascii=False)[:250])
        if url:
            urllib.request.urlretrieve(url, OUT)
            print("OK ->", OUT.name, OUT.stat().st_size, "bytes (model:", used_model, ")")
            return
        if any(s in task_state(res) for s in ("FAIL", "ERROR", "CANCEL")):
            print("TASK_FAILED")
            sys.exit(1)
    print("POLL_TIMEOUT")
    sys.exit(1)


if __name__ == "__main__":
    main()
