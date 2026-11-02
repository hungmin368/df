# -*- coding: utf-8 -*-
"""Generate the three chest tiers with Gemini using the Style A mascot as reference.

Usage:
  PYTHONIOENCODING=utf-8 python -u _gen_chests.py            # all tiers in order
  PYTHONIOENCODING=utf-8 python -u _gen_chests.py iron gold  # selected tiers

Raws -> assets/chests/_raw/<tier>_raw.png
Gold/platinum also receive the previously generated lower tier as a design-language
reference so the whole set stays one family.
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KEY = (HERE.parent / "dinos_2" / "bban_samples" / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
STYLE_REF = ROOT / "game_db" / "assets" / "dinos_2" / "DFD-000_伴伴_2star.png"
RAW = HERE / "_raw"
RAW.mkdir(exist_ok=True)

MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
]

FAMILY = (
    "A single cute chibi toy-style treasure chest, CLOSED, centered, seen from a "
    "slight three-quarter front view. Family design: chunky squashed proportions, "
    "clearly wider than tall, a rounded box body with a softly domed lid, thick "
    "rounded metal corner brackets, a prominent rounded central clasp with a tiny "
    "keyhole, two short stubby feet, big soft rounded edges, toy-like proportions. "
    "Soft organic satin material sheen with subtle highlights and fine surface "
    "texture, natural light weathering and tiny scratches, NEVER hard plastic or "
    "vinyl gloss. The rendering style must match the cute soft 3D toy look of the "
    "reference image, but do NOT copy the creature: no dinosaur, no character, no "
    "eyes, no face. Plain pure white studio background, no cast shadow, no floor, "
    "no text, no letters, no watermark, no UI, high-resolution digital art. The "
    "chest fills about 80% of a square frame with a little white margin. "
)

TIERS = {
    "iron": {
        "refs": [STYLE_REF],
        "prompt": FAMILY + (
            "RARITY: common iron chest. Antique dark slate-blue iron plates with "
            "visible round rivets, simple flat iron bands around the body, warm "
            "walnut wood side panels between the bands, and a plain rounded brass "
            "latch with a small round keyhole. One simple horizontal band only, no "
            "gems, no ornaments. Slightly worn and humble: soft edge wear, a faint "
            "scuff, a tiny bit of moss and dirt stuck near the feet. Muted cool "
            "steel-blue palette with warm brown accents. Reads plainly as the "
            "cheapest, most common chest of the set."
        ),
    },
    "gold": {
        "refs": [STYLE_REF, RAW / "iron_raw.png"],
        "prompt": FAMILY + (
            "RARITY: rare golden treasure chest, clearly richer than the plain iron "
            "chest in the second reference image. Keep the SAME chest silhouette and "
            "layout, but upgrade every part: RICH SATURATED HONEY-GOLD metal plates, "
            "clearly golden and strongly warm, NOT pale cream, NOT ivory, NOT beige; "
            "polished brass trim bands, cute elegant filigree swirls on the lid, a "
            "star-shaped amber gem set into the front clasp, small rounded star "
            "ornaments on the lid corners, deep red-brown wood panels, and a few tiny "
            "golden sparkles floating near the lid. Luxurious but still adorable and "
            "chunky. Matte satin gold with soft warm highlights and amber-shaded "
            "crevices, not mirror-chrome. Reads instantly as the middle-tier "
            "treasure."
        ),
    },
    "plat": {
        "refs": [STYLE_REF, RAW / "gold_raw.png"],
        "prompt": FAMILY + (
            "RARITY: legendary platinum treasure chest, the most precious and ornate "
            "of the set, clearly above the golden chest in the second reference "
            "image. Keep the SAME chest silhouette and layout, but make it regal: "
            "cool platinum white-gold plates with soft satin sheen, elegant silver "
            "trim, delicate wing-like filigree on the sides, a cluster of pale "
            "ice-blue crystals growing from the lid, a glowing aquamarine gem set "
            "into the front clasp, tiny pearl inlays, and a faint icy-blue rim glow "
            "with delicate sparkles. Rich detail yet cute and rounded. Reads "
            "instantly as the rarest, most valuable chest."
        ),
    },
}


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def generate(tier: str) -> bool:
    spec = TIERS[tier]
    refs = [p for p in spec["refs"] if p.exists()]
    parts = [{"text": spec["prompt"]}]
    for p in refs:
        parts.append({"inline_data": {"mime_type": "image/png", "data": b64(p)}})
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    out = RAW / f"{tier}_raw.png"
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"{tier} {model}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}", flush=True)
            continue
        except Exception as e:  # noqa: BLE001 - network failures should fall through to next model
            print(f"{tier} {model}: {type(e).__name__} {e}", flush=True)
            continue
        rparts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        img = next((p.get("inlineData", {}).get("data") for p in rparts if "inlineData" in p), None)
        if not img:
            print(f"{tier} {model}: 200 but no image: {json.dumps(data)[:300]}", flush=True)
            continue
        out.write_bytes(base64.b64decode(img))
        im = Image.open(out)
        print(f"{tier} {model}: OK -> {out.name} {im.size[0]}x{im.size[1]} {out.stat().st_size} bytes", flush=True)
        return True
    print(f"{tier}: ALL_MODELS_FAILED", flush=True)
    return False


def main() -> None:
    wanted = sys.argv[1:] or ["iron", "gold", "plat"]
    ok = True
    for tier in wanted:
        if tier not in TIERS:
            print(f"unknown tier: {tier}")
            ok = False
            continue
        ok = generate(tier) and ok
    print("GEN_DONE", "OK" if ok else "FAILED", flush=True)


if __name__ == "__main__":
    main()
