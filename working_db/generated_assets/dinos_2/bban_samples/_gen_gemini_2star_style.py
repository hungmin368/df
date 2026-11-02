import base64
import io
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
KEY = (HERE / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
SRC = ROOT / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_2star.png"
REF = HERE / "_ref_banban_2star.png"
OUT = HERE / "gemini_carnotaurus_red.png"

MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
]

PROMPT = (
    "Using the baby dragon in the reference image as an exact style guide, create a "
    "Carnotaurus in the same family style: cute chibi glossy 3D render, big round "
    "golden-amber eyes, cheerful open smile showing tiny white fangs, creamy white "
    "belly, small yellow-orange claws, subtle fine scale texture, plain pure white "
    "studio background, high-resolution digital art. "
    "Keep the family identity (golden eyes, bright yellow-orange horns and claws, "
    "cream belly, pink inner ears) but give this species its own instantly "
    "recognizable color: the entire body is vibrant crimson red. "
    "Carnotaurus anatomy: two short bull horns in bright yellow-orange right above "
    "the eyes, a short blunt crocodile-like snout, tiny stubby arms, thick muscular "
    "tail. No wings, no back spikes. "
    "Action: full-speed charging dash, body leaning forward, one hind foot lifted "
    "mid-stride, tail streaming behind for balance, mouth open in an excited happy "
    "roar. "
    "Keep the same lighting, materials, proportions and overall cuteness as the "
    "reference. Single full-body creature only, centered."
)

# flatten the transparent mascot onto white and cap at 1024 px
im = Image.open(SRC).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
bg.alpha_composite(im)
bg = bg.convert("RGB")
bg.thumbnail((1024, 1024), Image.LANCZOS)
bg.save(REF)
print(f"reference: {REF.name} {bg.size[0]}x{bg.size[1]}")

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
        with urllib.request.urlopen(req, timeout=180) as resp:
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
