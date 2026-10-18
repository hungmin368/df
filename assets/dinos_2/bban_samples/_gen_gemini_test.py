import base64
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

HERE = Path(__file__).parent
KEY = (HERE / "_gemini_key.txt").read_text(encoding="utf-8").strip()
REF = HERE / "v4_trex_s10201_512.png"
OUT = HERE / "gemini_test_parasaurolophus.png"

MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-lite-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image",
    "gemini-3-pro-image-preview",
    "nano-banana-pro-preview",
]

PROMPT = (
    "Using the dinosaur in the reference image as an exact style guide, create a "
    "Parasaurolophus in the same family style: cute glossy 3D vinyl-toy render, "
    "big round golden eyes, cheerful open smile with tiny white teeth, creamy white "
    "belly, small yellow-orange claws, subtle fine scale texture, dynamic lively pose, "
    "plain pure white studio background, high-resolution digital art. "
    "The Parasaurolophus has a long backward-curving hollow head crest in vibrant "
    "yellow-orange, and its entire body is vivid teal cyan. "
    "Keep the same lighting, materials, proportions and overall cuteness as the "
    "reference. Single full-body creature only, centered."
)

img_b64 = base64.b64encode(REF.read_bytes()).decode("ascii")

for model in MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}},
            ]
        }],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"{model}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}")
        continue
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts if "inlineData" in p), None)
    if not img:
        print(f"{model}: 200 but no image part: {json.dumps(data)[:300]}")
        continue
    OUT.write_bytes(base64.b64decode(img))
    print(f"{model}: OK -> {OUT.name} ({OUT.stat().st_size} bytes)")
    sys.exit(0)

print("ALL_MODELS_FAILED")
sys.exit(1)
