#!/usr/bin/env python
"""Generate BanBan-style dino samples with the Leonardo.Ai REST API.

Get a key at https://app.leonardo.ai/api-access (API access is a separate
subscription from the web app). Then run:

    LEONARDO_API_KEY=... python _gen_leonardo.py            # all species below
    LEONARDO_API_KEY=... python _gen_leonardo.py ai_21_triceratops
    python _gen_leonardo.py --list-models                   # pick a modelId

Outputs leo_<name>.png next to this script. Feed them to _post_ai.py
(same rembg -> 512 master -> 200x200 webp flow) once style is approved.
"""
import json
import os
import pathlib
import sys
import time
import urllib.request

API = "https://cloud.leonardo.ai/api/rest/v1"
DEFAULT_MODEL = os.environ.get("LEONARDO_MODEL_ID", "6b645e3a-d64f-4341-a6d8-7a3690fbf042")
HERE = pathlib.Path(__file__).resolve().parent

STYLE = (", smooth glossy vibrant purple vinyl skin, no fur, "
         "big round amber orange eyes with white sparkle highlights, "
         "cream colored belly, tiny fangs happy smile, "
         "chibi 3D vinyl toy render, soft studio lighting, "
         "plain white background, centered full body")

SPECIES = {
    "ai_21_triceratops": (
        "chibi 3D render of a baby triceratops dinosaur with a large round bony "
        "frill behind its head, pink inner frill, three golden horns two above "
        "the eyes pointing upward and one on the nose, chubby quadruped standing "
        "on four short legs", 21),
    "ai_11_stegosaurus": (
        "chibi 3D render of a baby stegosaurus dinosaur with two rows of golden "
        "diamond-shaped plates along its arched back and four golden spikes on "
        "its tail tip, small head with golden cheeks, chubby quadruped standing "
        "on four short legs", 11),
    "ai_260_trex": (
        "chibi 3D render of a baby tyrannosaurus rex with a huge head and strong "
        "jaws, two small golden horns above its eyes, two tiny arms with golden "
        "claws, two strong hind legs, long thick balancing tail, standing upright", 260),
    "ai_300_ptero": (
        "chibi 3D render of a baby pterodactyl with huge pink bat-like wings "
        "spread wide, long golden beak, golden crest sweeping back from its "
        "head, small purple body with tiny feet, standing pose", 300),
}


def api(method: str, path: str, payload: dict | None = None) -> dict:
    key = os.environ.get("LEONARDO_API_KEY", "").strip()
    if not key:
        sys.exit("LEONARDO_API_KEY is not set. Create a key at "
                 "https://app.leonardo.ai/api-access and export it first.")
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"authorization": f"Bearer {key}",
                 "content-type": "application/json",
                 "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def generate(prompt: str, seed: int) -> list[str]:
    job = api("POST", "/generations", {
        "prompt": prompt,
        "modelId": DEFAULT_MODEL,
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "seed": seed,
    })
    gid = job["sdGenerationJob"]["generationId"]
    print(f"[gen] queued {gid}", flush=True)
    for _ in range(72):
        time.sleep(5)
        g = api("GET", f"/generations/{gid}")["generations_by_pk"]
        if g["status"] == "COMPLETE":
            return [im["url"] for im in g["generated_images"]]
        if g["status"] == "FAILED":
            raise RuntimeError(f"generation {gid} FAILED")
    raise TimeoutError(f"generation {gid} still not COMPLETE")


def download(url: str, out: pathlib.Path) -> None:
    with urllib.request.urlopen(url, timeout=120) as r, open(out, "wb") as f:
        f.write(r.read())


def main() -> int:
    args = sys.argv[1:]
    if "--list-models" in args:
        for m in api("GET", "/platformModels")["custom_models"]:
            print(f"{m['id']}  {m['name']}")
        return 0
    targets = args or list(SPECIES)
    for name in targets:
        prompt, seed = SPECIES[name]
        urls = generate(prompt + STYLE, seed)
        out = HERE / f"leo_{name.removeprefix('ai_')}.png"
        download(urls[0], out)
        print(f"[gen] {name} -> {out.name} ({out.stat().st_size // 1024} KB)", flush=True)
        time.sleep(5)
    print("LEO_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
