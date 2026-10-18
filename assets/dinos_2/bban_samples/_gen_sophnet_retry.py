# -*- coding: utf-8 -*-
"""SophNet retry (Round 26): two mitigations for the anthropomorphic-baby-face issue.

Variant A : hardened TEXT-ONLY prompt -> task endpoint (anti-anthro negatives +
            explicit reptilian-face positives).
Variant B : /image-edit with images=[Style-A reference on GitHub Pages] +
            transform prompt (does edit mode honor the reference style?).
Raws -> assets/dinos_2/compare/{sophA,sophB}_260_raw.png (rerun skips existing).
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import _gen_trial5 as G
import _gen_sophnet_styleA_stegosaurus as SN
import _gen_compare_backends as C

ROOT = HERE.parents[2]
OUT_DIR = ROOT / "assets" / "dinos_2" / "compare"
SPEC_ID = 260
STYLE_URL = ("https://hungmin368.github.io/df/assets/dinos_2/"
             "DFD-000_%E4%BC%B4%E4%BC%B4_2star.png")
IMAGE_EDIT_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/image-edit"
SEED_A, SEED_B = 555001, 555002

REPTILE_FACE = ("The face must be fully reptilian: a reptile snout with nostrils "
                "at the tip, a reptile mouth with tiny white fangs and a pink "
                "tongue, small reptilian ear openings on the sides of the head. "
                "Strictly NO human face, NO human ears, NO human cheeks, no "
                "humanoid features. ")
NEG_EXTRA = ", 拟人化, 人脸, 人类耳朵, 婴儿脸, 儿童"


def hardened_prompt(prompt: str, en_name: str) -> str:
    out = prompt.replace(
        f"Create a baby {en_name} in Style A.",
        f"Create a baby {en_name} in Style A. " + REPTILE_FACE)
    assert "fully reptilian" in out
    return out


def hard_negative() -> str:
    return C.NEGATIVE + NEG_EXTRA


def gen_edit(prompt: str, out: Path) -> bool:
    """Sync /image-edit with the Style-A reference image as edit source."""
    body = {"model": "qwen-image",
            "input": {"prompt": prompt, "images": [STYLE_URL],
                      "negative_prompt": hard_negative()},
            "parameters": {"size": "1328*1328", "seed": SEED_B,
                           "watermark": False}}
    try:
        res = SN.call("POST", IMAGE_EDIT_URL, body)
    except urllib.error.HTTPError as e:
        print(f"  edit HTTP {e.code} {e.read().decode('utf-8', 'replace')[:250]}")
        res = None
    if res:
        url = SN.extract_url(res)
        if url:
            data = C.download(url)
            out.write_bytes(data)
            print(f"  edit OK -> {out.name} ({len(data)} bytes)")
            return True
        print(f"  edit no url: {json.dumps(res, ensure_ascii=False)[:300]}")
    # fallback: task endpoint also accepts input.images
    body2 = {"model": "qwen-image",
             "input": {"prompt": prompt, "images": [STYLE_URL],
                       "negative_prompt": hard_negative()},
             "parameters": {"size": "1328*1328", "seed": SEED_B,
                            "watermark": False}}
    try:
        created = SN.call("POST", C.TASK_BASE, body2)
    except urllib.error.HTTPError as e:
        print(f"  task-with-images HTTP {e.code} "
              f"{e.read().decode('utf-8', 'replace')[:250]}")
        return False
    out_obj = created.get("output") or created.get("result") or {}
    task_id = SN.pick(out_obj, "taskId", "task_id", "id")
    if not task_id:
        print(f"  task-with-images create: {json.dumps(created, ensure_ascii=False)[:250]}")
        return False
    print(f"  task-with-images: {task_id}")
    import time
    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(5)
        try:
            st = SN.call("GET", f"{C.TASK_BASE}/{task_id}")
        except urllib.error.HTTPError as e:
            print(f"    poll HTTP {e.code}")
            continue
        o = st.get("output") or st.get("result") or {}
        url = SN.extract_url(o) or SN.extract_url(st)
        state = SN.task_state(o).upper()
        if url:
            out.write_bytes(C.download(url))
            print(f"    OK -> {out.name}")
            return True
        if any(s in state for s in ("FAIL", "ERROR", "CANCEL")):
            print(f"    task failed: {state}")
            return False
        print(f"    poll: {state or '...'}")
    return False


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    specs = {r["id"]: r for r in json.loads(
        (HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]}
    row = specs[SPEC_ID]
    en_name = row["recon"].split("_")[1] if row["recon"] else row["name"]
    base = C.sophnet_prompt(G.build_prompt(row))
    hard = hardened_prompt(base, en_name)
    C.NEGATIVE = hard_negative()

    a_out = OUT_DIR / f"sophA_{SPEC_ID}_raw.png"
    if a_out.exists():
        print("sophA raw exists, skip")
    else:
        print("[Variant A] hardened text-only, task endpoint")
        used = C.gen_sophnet(hard, a_out)
        if not used:
            print("VARIANT_A_FAILED")
            sys.exit(1)

    b_out = OUT_DIR / f"sophB_{SPEC_ID}_raw.png"
    if b_out.exists():
        print("sophB raw exists, skip")
    else:
        print("[Variant B] /image-edit with Style-A reference URL")
        edit_prompt = ("Repaint the character in the reference image into a baby "
                       f"{en_name} in the EXACT same art style, rendering, "
                       "lighting and plain pure white background. " + REPTILE_FACE
                       + f"Anatomy (scientific reconstruction): "
                         f"a massive skull with strong jaws and heavy brows, tiny "
                         f"two-fingered arms, powerful long legs, thick heavy tail "
                         f"for balance. Body color: the entire body is "
                         f"{row['color_en']} with {row['pattern_en']}. "
                         f"Expression: {row['expr_en']}. Pose: {row['fun_en']}. "
                         f"Gear: {row['acc_en']}. Weathering: "
                         f"{'; '.join(s['en'] for s in row['stains'])}. "
                         "Single full-body creature, whole body visible, "
                         "silhouette close to square (1:1 to 1.2:1), centered, "
                         "no text, no watermark.")
        (OUT_DIR / "_sophB_edit_prompt.txt").write_text(edit_prompt, encoding="utf-8")
        if not gen_edit(edit_prompt, b_out):
            print("VARIANT_B_FAILED")
            sys.exit(1)
    print("done")
    sys.exit(0)


if __name__ == "__main__":
    main()
