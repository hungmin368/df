# -*- coding: utf-8 -*-
"""Backend comparison on the SAME spec row (id 260): SophNet ImageGenerator vs Gemini.

Usage: PYTHONIOENCODING=utf-8 python _gen_compare_backends.py
- Gemini  : certified dual-reference recipe straight from _gen_trial5.generate().
- SophNet : identical Style A prompt with reference-image wording rewritten to pure
            text (its API only accepts http image URLs, not local files), plus the
            Chinese negative prompt. Async task endpoint {BASE}/imagegenerator/task
            (the sync /image-edit rejects prompt-only bodies with 10012).
Raws -> assets/dinos_2/compare/{sophnet,gemini}_260_raw.png (rerun skips existing).
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import _gen_trial5 as G
import _gen_sophnet_styleA_stegosaurus as SN

ROOT = HERE.parents[2]
OUT_DIR = ROOT / "assets" / "dinos_2" / "compare"
SPEC_ID = 260
TASK_BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"
SOPHNET_MODELS = ["Qwen-Image-Plus", "qwen-image", "Z-Image-Turbo"]
SOPHNET_KEY = (HERE / "_sophnet_key.txt").read_text(encoding="utf-8").strip()
SEED = 20286236
NEGATIVE = ("塑膠感, 硬塑料光澤, 乙烯基玩具感, 強反光, 模糊, 低解析度, 變形, 多餘的肢體, "
            "多隻動物, 文字, 數字, 浮水印, 簽名, 邊框, 背景雜物")


def sophnet_prompt(prompt: str) -> str:
    out = (prompt
           .replace("You are given two reference images. IMAGE 1 is a baby dragon "
                    "figurine: use it ONLY as the exact style guide (Style A) - ",
                    "Style guide (Style A): ")
           .replace("IMAGE 2 is a scientific reconstruction of the dinosaur: copy its "
                    "ANATOMY and species-defining features only, not its rendering "
                    "style or colors. ", "")
           .replace("Anatomy from IMAGE 2:", "Anatomy (scientific reconstruction):")
           .replace("Keep the same lighting, materials, proportions and overall "
                    "cuteness as IMAGE 1.",
                    "Follow the Style A description above exactly."))
    assert "IMAGE 1" not in out and "IMAGE 2" not in out, "reference wording survived"
    return out


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def gen_sophnet(prompt: str, out: Path) -> str | None:
    param_ladder = [
        {"size": "1328*1328", "seed": SEED, "watermark": False},
        {"size": "1024*1024"},
        None,
    ]
    for model in SOPHNET_MODELS:
        for params in param_ladder:
            body = {"model": model,
                    "input": {"prompt": prompt, "negative_prompt": NEGATIVE}}
            if params:
                body["parameters"] = params
            try:
                created = SN.call("POST", TASK_BASE, body)
            except urllib.error.HTTPError as e:
                print(f"  {model} create(params={bool(params)}): HTTP {e.code} "
                      f"{e.read().decode('utf-8', 'replace')[:200]}")
                continue
            out_obj = created.get("output") or created.get("result") or {}
            task_id = SN.pick(out_obj, "taskId", "task_id", "id")
            if not task_id:
                print(f"  {model} create: {json.dumps(created, ensure_ascii=False)[:250]}")
                continue
            print(f"  {model}: task {task_id} (params={bool(params)})")
            deadline = time.time() + 600
            succeeded = False
            while time.time() < deadline:
                time.sleep(5)
                try:
                    st = SN.call("GET", f"{TASK_BASE}/{task_id}")
                except urllib.error.HTTPError as e:
                    print(f"    poll HTTP {e.code} "
                          f"{e.read().decode('utf-8', 'replace')[:160]}")
                    continue
                res = st.get("output") or st.get("result") or {}
                url = SN.extract_url(res) or SN.extract_url(st)
                state = SN.task_state(res).upper()
                if url:
                    data = download(url)
                    out.write_bytes(data)
                    print(f"    {SN.task_state(res)} -> {out.name} ({len(data)} bytes)")
                    succeeded = True
                    break
                if any(s in state for s in ("FAIL", "ERROR", "CANCEL")):
                    print(f"    task failed: {state} "
                          f"{json.dumps(st, ensure_ascii=False)[:200]}")
                    break
                print(f"    poll: {state or '...'}")
            if succeeded:
                return model
    return None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    specs = {r["id"]: r for r in json.loads(
        (HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]}
    row = specs[SPEC_ID]
    print(f"spec row {SPEC_ID}: {row['stars']}★ {row['name']} "
          f"color={row['color_zh']} fun={row['fun_zh']}({row['fun_kind']}) acc={row['acc_zh']}")

    gem_out = OUT_DIR / f"gemini_{SPEC_ID}_raw.png"
    if gem_out.exists():
        print("gemini raw exists, skip")
    else:
        png, model = G.generate(row)
        if not png:
            print("GEMINI_FAILED")
            sys.exit(1)
        gem_out.write_bytes(png)
        print(f"gemini OK via {model} -> {gem_out.name} ({len(png)} bytes)")

    sn_out = OUT_DIR / f"sophnet_{SPEC_ID}_raw.png"
    if sn_out.exists():
        print("sophnet raw exists, skip")
    else:
        prompt = sophnet_prompt(G.build_prompt(row))
        (OUT_DIR / "_sophnet_prompt.txt").write_text(prompt, encoding="utf-8")
        used = gen_sophnet(prompt, sn_out)
        if not used:
            print("SOPHNET_FAILED")
            sys.exit(1)
    print("done")
    sys.exit(0)


if __name__ == "__main__":
    main()
