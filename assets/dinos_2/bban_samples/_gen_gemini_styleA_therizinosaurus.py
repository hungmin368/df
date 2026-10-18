import base64
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
KEY = (HERE / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
STYLE_SRC = HERE.parent / "DFD-000_伴伴_2star.png"
ANATOMY_SRC = Path(r"C:\MY_AI_JOBS\恐龍圖片\鐮刀龍_Therizinosaurus_no18_★★★★★.jpg")
STYLE_REF = HERE / "_ref_banban_2star.png"
ANATOMY_REF = HERE / "_ref_therizinosaurus_photo.jpg"
OUT = HERE / "gemini_styleA_therizinosaurus.png"
MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
]

PROMPT = (
    "You are given two reference images. IMAGE 1 is a baby dragon figurine: use it "
    "ONLY as the exact style guide (Style A) - cute chibi glossy 3D vinyl-toy render, "
    "big round golden-amber eyes with white specular highlights, cheerful open smile "
    "showing tiny white fangs and a pink tongue, creamy white belly, subtle fine scale "
    "texture, plain pure white studio background, high-resolution digital art. "
    "IMAGE 2 is a scientific reconstruction of Therizinosaurus: copy its ANATOMY and "
    "defining features, not its rendering style. "
    "Create a baby Therizinosaurus in Style A. THE most prominent feature of the whole "
    "design: each hand carries three gigantic curved SCYTHE CLAWS, each claw as long "
    "as the dinosaur's own head, gleaming bright yellow-orange, unmistakably oversized "
    "like samurai-sword claws. It proudly holds one arm high showing off the scythe "
    "claws; the other hand rests at its belly. "
    "Also keep from IMAGE 2: a small cute head on a long graceful neck, a round "
    "pot-bellied body, a long thick tail with a fluffy feathered tip, sturdy "
    "two-legged stance. "
    "Color: deep emerald green body matching the reconstruction, with a warm "
    "red-orange throat patch down the neck, creamy white belly. "
    "Expression: cheerful open smile with tiny white fangs. "
    "Keep the same lighting, materials, proportions and overall cuteness as IMAGE 1. "
    "Single full-body creature only, centered, plain white background."
)


def as_ref(src: Path, dst: Path) -> str:
    im = Image.open(src)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    im.thumbnail((1024, 1024), Image.LANCZOS)
    im.save(dst)
    return base64.b64encode(dst.read_bytes()).decode("ascii")


style_b64 = as_ref(STYLE_SRC, STYLE_REF)
anatomy_b64 = as_ref(ANATOMY_SRC, ANATOMY_REF)
print(f"refs: style {STYLE_REF.name}, anatomy {ANATOMY_REF.name}")

for model in MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": "image/png", "data": style_b64}},
                {"inline_data": {"mime_type": "image/jpeg", "data": anatomy_b64}},
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
