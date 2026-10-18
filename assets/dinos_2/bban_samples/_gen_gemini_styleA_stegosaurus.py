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
ANATOMY_SRC = Path(r"C:\MY_AI_JOBS\恐龍圖片\劍龍_Stegosaurus_no231_★★★☆☆.png")
STYLE_REF = HERE / "_ref_banban_2star.png"
ANATOMY_REF = HERE / "_ref_stegosaurus_recon.png"
OUT = HERE / "gemini_styleA_stegosaurus.png"
MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
]

PROMPT = (
    "You are given two reference images. IMAGE 1 is a baby dragon figurine: use it "
    "ONLY as the exact style guide (Style A) - cute chibi 3D toy-style render with "
    "soft organic SATIN skin sheen (subtle soft highlights, visible fine scale "
    "texture; NOT hard plastic, NOT glossy vinyl), big round golden-amber eyes with "
    "white specular highlights, cheerful open smile showing tiny white fangs and a "
    "pink tongue, creamy white belly, plain pure white studio background, "
    "high-resolution digital art. Add natural weathering: subtle dirt smudges, a "
    "few small mud patches and tiny grass/leaf fragments stuck on the legs, belly "
    "and tail (light-to-moderate amount, do not hide the body color). "
    "IMAGE 2 is a scientific reconstruction of Stegosaurus: copy its ANATOMY and "
    "defining features, not its rendering style. "
    "Create a baby Stegosaurus in Style A. Its silhouette must read instantly: a "
    "small low head on a short neck, a big rounded bulky body, TWO STRAIGHT ROWS of "
    "large upright kite-shaped plates running from the neck to the tail along the "
    "back - the plates are the star of the design, keep every plate fully visible, "
    "colored warm amber-orange with golden edges - and FOUR long sharp tail spikes "
    "(thagomizer) in bright yellow-orange at the tip of a raised muscular tail. "
    "Sturdy four-legged stance, hind legs slightly taller than the front legs. "
    "Color: rich indigo-blue body like lapis lazuli, creamy white belly. "
    "Action: joyful playful leap mid-air, front legs tucked up, tail swung high "
    "showing the thagomizer spikes, mouth open in a delighted laugh. "
    "It wears one simple woven grass armband around the front left leg (a small "
    "3-star warrior charm) that does NOT cover any back plates. "
    "Keep the same lighting, materials, proportions and overall cuteness as IMAGE 1. "
    "Single full-body creature only, centered, plain pure white background. "
    "No text, no watermark, no signature."
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
                {"inline_data": {"mime_type": "image/png", "data": anatomy_b64}},
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
