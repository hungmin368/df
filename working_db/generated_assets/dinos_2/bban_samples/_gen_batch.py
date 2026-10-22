# -*- coding: utf-8 -*-
"""Phase 2 batch: generate the remaining 134 Style A dinos with Gemini dual references.

Usage:
  PYTHONIOENCODING=utf-8 python -u _gen_batch.py --dryrun          # build all prompts, no API
  PYTHONIOENCODING=utf-8 python -u _gen_batch.py --ids 3,9,109     # smoke subset
  PYTHONIOENCODING=utf-8 python -u _gen_batch.py                   # full remaining queue

Methods (from _gen_specs.json):
  P0: recon = target's own science reconstruction -> IMAGE 2, en name from recon filename.
  P1: recon = same-family proxy reconstruction -> IMAGE 2, en name from _name_en.json.
  P2: no recon; IMAGE 2 = existing game asset assets/dinos/<id>.webp (READ-ONLY),
      en name = descriptor from _name_en.json, IMAGE-2 clause swapped.

Raws -> assets/dinos_2/batch/_raw/<id>_<En>_raw.png
State -> assets/dinos_2/batch/_gen_state.json (rerun-safe; raw-exists == done)
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import _gen_trial5 as G  # noqa: E402

ROOT = HERE.parents[3]
BATCH = HERE.parent / "batch"
RAW = BATCH / "_raw"
STATE = BATCH / "_gen_state.json"
DONE_IDS = {1, 101, 202, 260, 325}
NAME_EN = json.loads((HERE / "_name_en.json").read_text(encoding="utf-8"))
SLEEP_BETWEEN = 3.0
BACKOFFS = [0, 20, 45, 90, 180, 300]
QUOTA_ABORT = 3

IMG2_CLAUSE_P0P1 = ("IMAGE 2 is a scientific reconstruction of the dinosaur: copy its ANATOMY and "
                    "species-defining features only, not its rendering style or colors. ")
IMG2_CLAUSE_P2 = ("IMAGE 2 is the creature's existing game artwork: copy its ANATOMY and "
                  "species-defining features only (body shape, limbs, wings, membranes, horns, "
                  "fins, tail), not its rendering style or colors. ")

# Per-id prompt patches for rows that keep failing the same gate across rounds.
# Each value: list of (old_substr, new_substr) replacements applied in order.
PROMPT_PATCHES = {
    9: [
        ("rolling on its back, belly up, playful",
         "rolling playfully into a tight snail-like spiral curl seen from the "
         "side, the body looped into a round coil with the tail and neck tucked "
         "inside, the coiled figure nearly as tall as it is wide like a cinnamon "
         "roll standing upright, compact and rounded"),
    ],
}

# Corrective direction is set from the AUTHORITATIVE r4 gate measurement per id
# (11 of 15 were previously backwards, which is why that retry round never
# converged). SQUAT = measured too TALL/narrow (ratio<0.833) -> must be widened;
# WIDE = measured too WIDE (ratio>1.2) -> must be compacted toward square.
SQUAT_IDS = {31, 35, 65, 250, 303}
WIDE_IDS = {17, 39, 49, 85, 117, 218, 252, 264, 288}
# id 9 is a sleeping snail-coil that came out too tall; the lizard-horizontal
# SQUAT note would fight the curl, so it gets a dedicated flatten-the-coil note.
COIL_IDS = {9}
SQUARE_TAIL = (" The final cropped silhouette MUST fit inside a SQUARE: total "
               "width and total height nearly equal, aspect ratio strictly "
               "between 1:1.2 and 1.2:1 - measure it before finishing.")
SQUAT_NOTE = ("Correction for this attempt: the previous image came out far too "
              "tall and narrow. Rebuild the pose HORIZONTALLY like a lizard: the "
              "spine runs level from hips to shoulders close to the ground, the "
              "tail stretches straight BACKWARD just above the ground instead of "
              "hanging down, the neck extends FORWARD low, and both legs are "
              "bent in a wide crouched stance; the whole creature reads long and "
              "low, clearly wider than it is tall, inside a square frame."
              + SQUARE_TAIL)
WIDE_NOTE = ("Correction for this attempt: the previous image came out far too "
             "wide and stretched. Gather the body compactly: coil the tail in a "
             "tight spiral against the hip, lift the head slightly, tuck the "
             "limbs closer under the body, seen from a slight three-quarter "
             "angle; the overall silhouette must be nearly square, not sprawled "
             "sideways." + SQUARE_TAIL)
COIL_NOTE = ("Correction for this attempt: the sleeping curl came out too tall "
             "and narrow. Flatten the coiled body so it spreads clearly WIDER "
             "than it is tall - loop the tail and neck out sideways into a broad, "
             "low spiral resting flat on the ground like a cinnamon roll lying on "
             "its side, the whole curled silhouette reading wider than tall."
             + SQUARE_TAIL)

# Round-9 overrides: ids whose single-direction note demonstrably over- or
# under-shot in round 8 (measured both too-tall under one note and too-wide under
# the other), or whose anatomy needs a pose-specific fix rather than a generic
# directional push. An override REPLACES the SQUAT/WIDE/COIL note for that id.
NEUTRAL_SQUARE = ("Correction for this attempt: previous tries kept landing "
                  "outside a square frame - some too tall, some too wide. Keep "
                  "the species, the pose intent and the identity, but compose the "
                  "whole figure to FIT A SQUARE. Pull the far-reaching extremes "
                  "(tail tip, snout, crest, outstretched limbs, wings or props) "
                  "inward so nothing pokes far out, and balance width against "
                  "height so total width and total height are nearly equal, "
                  "ideally width:height about 1:1 to 1.1:1 and strictly inside "
                  "1:1.2 to 1.2:1. Use a compact three-quarter view. Measure the "
                  "bounding box before finishing.")
JUMP_WIDE = ("Correction for this attempt: the previous images came out far too "
             "tall and upright because of the leaping pose. Do NOT show the "
             "animal airborne or standing tall. Instead catch the moment of "
             "LANDING in a wide, low crouch: body dropped close to the ground, "
             "both legs bent and splayed out to the sides, the long arms and "
             "claws spread outward horizontally, neck and tail held out to the "
             "sides rather than raised. The whole figure reads clearly WIDER than "
             "it is tall, fitting a square frame (aspect ratio strictly between "
             "1:1.2 and 1.2:1, ideally wider than tall). Measure the bounding box "
             "before finishing.")
SAUROPOD_GATHER = ("Correction for this attempt: the previous images came out "
                   "far too wide, stretched end-to-end because the long neck and "
                   "tail spread sideways in opposite directions. Gather the animal "
                   "compactly: curve the long neck back and upward in a loose S so "
                   "the head sits near the shoulders, coil the tail in against the "
                   "body, and turn the whole creature to a three-quarter view "
                   "facing slightly toward the viewer, so it reads as a compact "
                   "rounded figure nearly as tall as it is wide (aspect ratio "
                   "strictly between 1:1.2 and 1.2:1). Never stretch neck and tail "
                   "out horizontally. Measure the bounding box before finishing.")
MILD_WIDEN = ("Correction for this attempt: the figure keeps coming out just "
              "slightly too tall and narrow. Widen it MODESTLY - not the extreme "
              "flat sprawl. Keep the natural pose but take a somewhat wider "
              "stance, hold the tail and neck out a bit more horizontally, and "
              "drop the shoulders slightly, so the silhouette becomes just a "
              "little wider than it is tall, about 1.05 to 1.15 times as wide as "
              "it is tall, strictly inside the 1:1.2 to 1.2:1 limit. Measure the "
              "bounding box before finishing.")
NOTE_OVERRIDE = {
    31: NEUTRAL_SQUARE, 35: NEUTRAL_SQUARE,
    117: NEUTRAL_SQUARE, 250: NEUTRAL_SQUARE,
    65: JUMP_WIDE,
    252: SAUROPOD_GATHER,
    39: MILD_WIDEN, 288: MILD_WIDEN,
}


def apply_patches(sid, prompt):
    for old, new in PROMPT_PATCHES.get(sid, []):
        assert old in prompt, f"patch anchor missing for id {sid}: {old[:60]}"
        prompt = prompt.replace(old, new)
    if sid in NOTE_OVERRIDE:
        return prompt + "\n" + NOTE_OVERRIDE[sid]
    if sid in SQUAT_IDS:
        prompt += "\n" + SQUAT_NOTE
    if sid in WIDE_IDS:
        prompt += "\n" + WIDE_NOTE
    if sid in COIL_IDS:
        prompt += "\n" + COIL_NOTE
    return prompt


def load_specs():
    rows = json.loads((HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]
    return {r["id"]: r for r in rows}


def simple_en(sid, row):
    if row["recon"]:
        return row["recon"].split("_")[1].replace(" ", "_")
    words = [w for w in re.findall(r"[A-Za-z]+", NAME_EN[str(sid)])
             if w.lower() not in ("a", "an", "the", "matching", "its", "of", "in")]
    w = (words[0] if words else "creature").capitalize()
    return re.sub(r"[^A-Za-z0-9]+", "", w)[:24] or "creature"


def prompt_for(sid, row):
    """Return (prompt, row2) - row2 only feeds build_prompt (recon blanked)."""
    method = row["method"]
    if row["recon"] and not method.startswith("P1"):
        return G.build_prompt(row), row           # P0: verbatim trial path
    row2 = dict(row)
    row2["recon"] = ""
    row2["name"] = re.sub(r"^(a|an) ", "", NAME_EN[str(sid)], flags=re.IGNORECASE)
    prompt = G.build_prompt(row2)
    if method == "P2":
        assert IMG2_CLAUSE_P0P1 in prompt
        prompt = prompt.replace(IMG2_CLAUSE_P0P1, IMG2_CLAUSE_P2)
    else:
        assert IMG2_CLAUSE_P0P1 in prompt
    return prompt, row2


def anatomy_src(row):
    if row["recon"]:
        return G.RECON_DIR / row["recon"], "image/jpeg"
    p = ROOT / "game_db" / row["img"]
    if not p.exists():
        raise FileNotFoundError(p)
    return p, "image/jpeg"


def request_image(prompt, style_b64, anatomy_b64, model):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent")
    body = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": style_b64}},
            {"inline_data": {"mime_type": "image/jpeg", "data": anatomy_b64}},
        ]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": G.KEY},
        method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p.get("inlineData", {}).get("data") for p in parts
                if "inlineData" in p), None)
    return base64.b64decode(img) if img else None


def gen_one(row, prompt, style_b64):
    """Model ladder x backoff ladder. Returns (png|None, model|None, err)."""
    anatomy_path, _ = anatomy_src(row)
    anatomy_b64, _ = G.as_b64(anatomy_path, HERE / "_ref_batch_anatomy.jpg", "image/jpeg")
    last_err = ""
    for model in G.MODELS:
        hard_fail = False
        for wait in BACKOFFS:
            if wait:
                print(f"    backoff {wait}s on {model} ...", flush=True)
                time.sleep(wait)
            try:
                png = request_image(prompt, style_b64, anatomy_b64, model)
            except urllib.error.HTTPError as e:
                last_err = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:160]}"
                print(f"    {model}: {last_err}", flush=True)
                if e.code in (429, 500, 503):
                    continue
                hard_fail = True
                break
            except Exception as e:  # URLError, timeout
                last_err = f"{type(e).__name__}: {e}"
                print(f"    {model}: {last_err}", flush=True)
                continue
            if png:
                return png, model, ""
            last_err = "200 but no image part (likely safety block)"
            print(f"    {model}: {last_err}", flush=True)
            hard_fail = True
            break
        if not hard_fail and last_err.startswith("HTTP 429"):
            pass  # exhausted backoffs on quota -> treat as ladder fallthrough
    return None, None, last_err


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, STATE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated spec ids (default: all remaining)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dryrun", action="store_true")
    args = ap.parse_args()

    specs = load_specs()
    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
    else:
        ids = [r["id"] for r in specs.values() if r["id"] not in DONE_IDS]
    ids = sorted(ids)
    if args.limit:
        ids = ids[:args.limit]

    if args.dryrun:
        bad = []
        for sid in ids:
            row = specs[sid]
            try:
                prompt, row2 = prompt_for(sid, row)
                prompt = apply_patches(sid, prompt)
                simple_en(sid, row)
                anatomy_src(row)
                if row["stars"] == 5 and row.get("fun_kind") == "action":
                    bad.append((sid, "5★ with action fun"))
            except Exception as e:
                bad.append((sid, repr(e)))
        print(f"dryrun: {len(ids) - len(bad)}/{len(ids)} rows build OK")
        for sid, why in bad:
            print(f"  BAD id {sid}: {why}")
        for sid, label in ((3, "P0"), (9, "P1"), (109, "P2")):
            row = specs[sid]
            prompt, _ = prompt_for(sid, row)
            prompt = apply_patches(sid, prompt)
            print(f"\n===== sample {label} id {sid} {row['name']} "
                  f"({len(prompt)} chars) =====\n{prompt}")
        sys.exit(1 if bad else 0)

    BATCH.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    state = load_state()
    style_b64, _ = G.as_b64(G.STYLE_SRC, HERE / "_ref_banban_2star.png", "image/png")

    print(f"queue: {len(ids)} rows; state has {sum(1 for v in state.values() if v.get('status') == 'done')} done",
          flush=True)
    results = []
    quota_fail_streak = 0
    for n, sid in enumerate(ids, 1):
        row = specs[sid]
        out = RAW / f"{sid}_{simple_en(sid, row)}_raw.png"
        if out.exists():
            state[str(sid)] = {"status": "done", "model": state.get(str(sid), {}).get("model", "cached"),
                               "raw": out.name, "attempts": state.get(str(sid), {}).get("attempts", 1),
                               "ts": time.time()}
            save_state(state)
            print(f"[{n}/{len(ids)}] id {sid} ({row['stars']}★ {row['name']}) skip (raw exists)", flush=True)
            results.append((sid, "cached"))
            continue
        prompt, _ = prompt_for(sid, row)
        prompt = apply_patches(sid, prompt)
        print(f"[{n}/{len(ids)}] id {sid} ({row['stars']}★ {row['name']} / {row['method']}) "
              f"color={row['color_zh']} pose={row['pose_zh']}", flush=True)
        png, model, err = gen_one(row, prompt, style_b64)
        attempts = state.get(str(sid), {}).get("attempts", 0) + 1
        if png:
            out.write_bytes(png)
            state[str(sid)] = {"status": "done", "model": model, "raw": out.name,
                               "attempts": attempts, "err": "", "ts": time.time()}
            print(f"    OK via {model} -> {out.name} ({len(png) // 1024}KB)", flush=True)
            results.append((sid, "ok"))
            quota_fail_streak = 0
        else:
            state[str(sid)] = {"status": "failed", "model": None, "raw": None,
                               "attempts": attempts, "err": err, "ts": time.time()}
            print(f"    FAILED: {err}", flush=True)
            results.append((sid, "failed"))
            if "HTTP 429" in err:
                quota_fail_streak += 1
                if quota_fail_streak >= QUOTA_ABORT:
                    save_state(state)
                    print(f"\nABORT: {quota_fail_streak} consecutive quota failures "
                          f"(daily limit?) - rerun later to resume", flush=True)
                    sys.exit(2)
        save_state(state)
        time.sleep(SLEEP_BETWEEN)

    ok = sum(1 for _, s in results if s in ("ok", "cached"))
    print(f"\ngen done: {ok}/{len(results)} raws present in {RAW}", flush=True)
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
