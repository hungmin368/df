#!/usr/bin/env python3
"""Decisive probe: can happyhorse r2v (reference-to-video) take our kid photos
via data-URI reference_image? If yes, shot S1 is generated for real (~Y4.5);
if the server cannot download a data URI, we fall through to the image-edit
hosting chain (also probed here) and report clearly.

Runs model happyhorse-1.0-r2v, then happyhorse-1.1-r2v (same content shape),
then probes image-edit data-URI support as a hosting fallback.
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
VB = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/generate"
IB = "https://www.sophnet.com/api/open-apis/projects/easyllms/image-edit"
OUT_DIR = Path(r"C:\tmp")
PHOTO1 = Path(
    r"C:\Users\hungm\AppData\Roaming\@sophclaw\desktop\attachments"
    r"\6ef208b4-49cc-4184-affa-aa38b043fb7e\image.png"
)

S1_PROMPT = """電影級實拍質感（真人電影），真實熱帶雨林深處的空地，黃昏金色光束穿過高大樹冠，實拍級蕨葉、苔蘚岩石與落葉泥土，空氣中漂浮微塵與光斑，淺景深、背景柔焦、手持鏡頭微晃，溫暖電影調色，畫面穩定流暢。

前景的巨大蕨葉後面躲著兩個亞洲小男孩，屏住呼吸偷偷往外看：哥哥 A寶（九歲、短黑髮、無眼鏡、淺藍色短袖T恤、卡其短褲），弟弟 B寶（七歲、短黑髮、透明圓框眼鏡、橘色短袖T恤）。

前方空地中央，一顆米白色帶紫色圓斑的巨大恐龍蛋立在苔蘚上微微透光；一隻巨大寫實的暴龍低著頭、張開長滿利牙的大嘴，慢慢逼近這顆蛋準備一口吞下。

鏡頭穿過前景蕨葉緩慢向前推近（dolly-in），電影級高細節，無字幕、無文字、無浮水印。"""


def call(method: str, url: str, payload: dict | None = None, timeout: int = 120) -> tuple:
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
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"raw": "unparseable"}
    except Exception as e:  # noqa: BLE001
        return "ERR", {"raw": str(e)}


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
    raw = buf.getvalue()
    uri = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
    print(f"[uri] {path.name}: jpeg {len(raw)} bytes -> data URI {len(uri)} chars, {im.size}")
    return uri


def submit_and_wait(model: str, content: list, out_name: str) -> str:
    """Returns 'success' | 'failed' | 'shape-error'."""
    body = {
        "model": model,
        "content": content,
        "parameters": {"duration": 5, "resolution": "720P", "ratio": "16:9"},
    }
    st, sub = call("POST", VB, body)
    print(f"[{model}] submit -> {st} | {json.dumps(sub, ensure_ascii=False)[:400]}")
    if not (isinstance(sub, dict) and sub.get("status") == 0 and sub.get("result")):
        print(f"[{model}] NOT ACCEPTED (shape/params)")
        return "shape-error"
    task_id = sub["result"].get("task_id") or sub["result"].get("id")
    print(f"[{model}] task_id = {task_id}")
    last = None
    for i in range(120):  # up to ~16 min
        time.sleep(8)
        pst, poll = call("GET", f"{VB}/{task_id}")
        result = poll.get("result") or {}
        status = str(result.get("status") or "").lower()
        if status != last:
            print(f"[{model}] [poll {i}] status={status} full={json.dumps(poll, ensure_ascii=False)[:600]}")
            last = status
        if status in ("succeeded", "success", "completed", "done", "finished"):
            urls = [u for u in find_urls(result) if ".mp4" in u or "video" in u.lower()] or find_urls(result)
            if not urls:
                print(f"[{model}] success but no URL")
                return "failed"
            out = OUT_DIR / out_name
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", str(out), urls[0]], check=True)
            print(f"[{model}] saved {out} ({out.stat().st_size} bytes)")
            return "success"
        if status in ("failed", "fail", "error"):
            err = result.get("error") or {}
            print(f"[{model}] FAILED: {json.dumps(err, ensure_ascii=False)[:400]}")
            return "failed"
    print(f"[{model}] TIMEOUT")
    return "failed"


def main() -> int:
    uri = data_uri(PHOTO1)
    ref_item = {"type": "image_url", "image_url": uri, "role": "reference_image"}

    for model in ("happyhorse-1.0-r2v", "happyhorse-1.1-r2v"):
        content = [{"type": "text", "text": S1_PROMPT}, ref_item]
        verdict = submit_and_wait(model, content, f"r2v_s1_{model.replace('.', '_')}.mp4")
        print(f"== {model}: {verdict} ==")
        if verdict == "success":
            print("R2V DATA-URI PATH WORKS")
            return 0

    # Fallback discovery: does image-edit accept a data URI input (hosting chain)?
    print("== probing image-edit data-URI input ==")
    st, body = call("POST", IB, {
        "model": "Z-Image-Turbo",
        "input": {
            "prompt": "Keep the two Asian boys exactly as they are, just return the same image.",
            "images": [uri],
        },
        "parameters": {"size": "1328*1328", "watermark": False},
    })
    print(f"[image-edit] {st} | {json.dumps(body, ensure_ascii=False)[:600]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
