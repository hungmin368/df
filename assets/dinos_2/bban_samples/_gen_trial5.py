# -*- coding: utf-8 -*-
"""Phase 1 trial: generate 5 Style A dinos (one per star tier) with dual references.

Usage: PYTHONIOENCODING=utf-8 python _gen_trial5.py
Reads specs from _gen_specs.json (ids 1, 101, 202, 260, 325 - spec verbatim).
Raw PNGs -> assets/dinos_2/trial/_raw/<id>_<en>_raw.png (post-chain runs separately).
Skips a row when its raw PNG already exists (rerun-safe, saves budget).
"""
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
KEY = (HERE / "_gemini_key2.txt").read_text(encoding="utf-8").strip()
STYLE_SRC = HERE.parent / "DFD-000_伴伴_2star.png"
RECON_DIR = Path(r"C:\MY_AI_JOBS\恐龍圖片")
TRIAL_DIR = ROOT / "assets" / "dinos_2" / "trial"
RAW_DIR = TRIAL_DIR / "_raw"
SPEC_IDS = [1, 101, 202, 260, 325]
MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image",
    "gemini-nano-banana-2.1",
]

ANATOMY = {
    "Diplodocus": "a very long graceful neck and an extremely long whip-like tail, "
                  "tiny head, tall columnar legs, gentle back without plates or horns",
    "Pachycephalosaurus": "a thick bony DOME on top of the skull surrounded by small "
                          "bony bumps and short spikes at the rim, short little arms, "
                          "bipedal stance, long stiff balanced tail",
    "Spinosaurus": "a tall SAIL on its back formed by long spines (copy the sail shape "
                   "from IMAGE 2), a long narrow crocodile-like snout, strong arms with "
                   "big claws, compact legs",
    "Tyrannosaurus rex": "a massive skull with strong jaws and heavy brows, tiny "
                         "two-fingered arms, powerful long legs, thick heavy tail for "
                         "balance",
    "Dilong": "a small slender early tyrannosaur covered in filament-like protofeathers "
              "along the head, neck, back and tail, long low snout, agile legs",
}

STYLE_CLAUSE = (
    "You are given two reference images. IMAGE 1 is a baby dragon figurine: use it "
    "ONLY as the exact style guide (Style A) - cute chibi 3D toy-style render with a "
    "soft organic satin skin sheen: subtle soft highlights and visible fine scale or "
    "feather texture. Absolutely NO hard plastic or vinyl gloss, never glass-smooth; "
    "the skin looks naturally weathered and alive. Big round golden-amber eyes with "
    "white specular highlights, cheerful open smile showing tiny white fangs and a "
    "pink tongue, creamy white belly, bright yellow-orange claws (and small "
    "yellow-orange horn/nail accents where the species has any), pink inner ears, "
    "high-resolution digital art. "
    "IMAGE 2 is a scientific reconstruction of the dinosaur: copy its ANATOMY and "
    "species-defining features only, not its rendering style or colors. "
)

TIER_CLAUSE = {
    1: "Tier 1 (plain rookie): no accessory at all, no skin pattern; weathering is "
       "only {stains}. ",
    2: "Tier 2 (scout): give it exactly one simple small accessory: {acc}. No skin "
       "pattern. Weathering: {stains}. ",
    3: "Tier 3 (warrior): skin pattern/tattoo: {pattern}. Light leather gear: {acc}. "
       "Weathering: {stains}. ",
    4: "Tier 4 (gold-armored): skin pattern/tattoo: {pattern}. Gold-trimmed gear or "
       "weapon: {acc}. Add subtle motion effect lines for energy. Weathering: {stains}. ",
    5: "Tier 5 (legendary hero): skin pattern/tattoo: {pattern}. Golden crown on the "
       "head, flowing hero cape, legendary weapon: {acc}. Use this heroic signature "
       "pose: {pose}. Add a subtle golden particle glow around the body. Weathering: "
       "{stains}. ",
}

COMPOSITION = (
    "Composition rules: single creature only, whole body fully visible and uncut, "
    "centered horizontally, positioned so the lowest body part sits about 5% above "
    "the bottom edge of the frame, generous empty margins of at least 4% on every "
    "side, plain pure white studio background, no text, no logo, no watermark, no "
    "drop shadow. SILHOUETTE ENVELOPE (highest priority): fit the ENTIRE creature - "
    "head, neck, tail, limbs, props and any floating effects - inside an imaginary "
    "SQUARE box: overall width and overall height must be nearly equal, ratio "
    "strictly between 1:1.2 and 1.2:1. Prefer a squat wide stance over an upright "
    "narrow one; curl the tail and lower the head rather than letting anything "
    "stretch outside the square envelope. A narrow-tall silhouette (much taller "
    "than wide) is forbidden: if in doubt, make the creature squatter and wider. "
)


def as_b64(src: Path, dst: Path, mime: str) -> str:
    im = Image.open(src)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    im.thumbnail((1024, 1024), Image.LANCZOS)
    im.save(dst)
    return base64.b64encode(dst.read_bytes()).decode("ascii"), mime


def stains_text(row):
    parts = []
    for s in row["stains"]:
        en = s["en"]
        parts.append(en)
    return "; ".join(parts) if parts else "a light dusting of fine dirt"


def build_prompt(row):
    en_name = row["recon"].split("_")[1] if row["recon"] else row["name"]
    anatomy = ANATOMY.get(en_name, "overall body plan exactly as shown in IMAGE 2")
    pattern = row["pattern_en"] if row["pattern_zh"] != "無" else "none"
    pose = row["pose_en"]
    fun_en = row.get("fun_en", "")
    if row.get("fun_kind") == "action" and row["stars"] != 5:
        pose = fun_en
    acc = row["acc_en"]
    tier = TIER_CLAUSE[row["stars"]].format(
        acc=acc, pattern=pattern, pose=pose, stains=stains_text(row))
    if row["stars"] != 5:
        pose_clause = f"Pose/action: {pose}. "
    else:
        pose_clause = ""
    mood = ""
    if row.get("fun_kind") == "mood":
        mood = f"Acting note: perform everything {fun_en}. "
    compact = ""
    if row.get("body_compact"):
        compact = ("Silhouette rule (important): " + row["body_note_en"]
                   + ". Execute the requested pose inside this compact envelope. ")
    return (
        STYLE_CLAUSE
        + f"Create a baby {en_name} in Style A. Anatomy from IMAGE 2: {anatomy}. "
        + f"Body color: the entire body is {row['color_en']} "
        + (f"with {pattern}" if pattern != "none" else "with clean unpatterned skin")
        + ". "
        + f"Expression: {row['expr_en']}. "
        + pose_clause
        + mood
        + compact
        + tier
        + COMPOSITION
        + "Keep the same lighting, materials, proportions and overall cuteness as "
          "IMAGE 1."
    )


def generate(row):
    style_b64, _ = as_b64(STYLE_SRC, HERE / "_ref_banban_2star.png", "image/png")
    recon_path = RECON_DIR / row["recon"]
    anatomy_b64, anatomy_mime = as_b64(recon_path, HERE / "_ref_trial_anatomy.jpg", "image/jpeg")
    prompt = build_prompt(row)
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        body = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": style_b64}},
                    {"inline_data": {"mime_type": anatomy_mime, "data": anatomy_b64}},
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
            print(f"  {model}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:200]}")
            continue
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        img = next((p.get("inlineData", {}).get("data") for p in parts if "inlineData" in p), None)
        if not img:
            print(f"  {model}: 200 but no image part: {json.dumps(data)[:200]}")
            continue
        return base64.b64decode(img), model
    return None, None


def main():
    specs = {r["id"]: r for r in json.loads(
        (HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    style_b64_cache = None
    results = []
    for sid in SPEC_IDS:
        row = specs[sid]
        en_name = row["recon"].split("_")[1] if row["recon"] else row["name"]
        safe_en = en_name.replace(" ", "_")
        out = RAW_DIR / f"{sid}_{safe_en}_raw.png"
        print(f"[{row['stars']}★ id {sid} {row['name']} / {en_name}] "
              f"color={row['color_zh']} pose={row['pose_zh']} acc={row['acc_zh']}")
        if out.exists():
            print(f"  skip (exists): {out.name}")
            results.append((sid, True, "cached"))
            continue
        png, model = generate(row)
        if png:
            out.write_bytes(png)
            print(f"  OK via {model} -> {out.name} ({len(png)} bytes)")
            results.append((sid, True, model))
        else:
            print("  FAILED all models")
            results.append((sid, False, None))
        time.sleep(2)
    ok = sum(1 for _, s, _ in results if s)
    print(f"\ndone: {ok}/{len(results)} raw images in {RAW_DIR}")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
