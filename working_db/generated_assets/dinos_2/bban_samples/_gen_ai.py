#!/usr/bin/env python
"""Generate BanBan-style dino samples via pollinations.ai + rembg + PIL post."""
import pathlib
import subprocess
import sys
import time

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


def gen(name: str, prompt: str, seed: int) -> bool:
    import urllib.parse
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?width=768&height=768&nologo=true&model=flux&seed={seed}")
    for attempt in range(4):
        out = HERE / f"{name}.png"
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "180", "-o", str(out), "-w", "%{http_code}", url],
            capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200" and out.exists() and out.stat().st_size > 20000:
            print(f"[gen] {name} ok ({out.stat().st_size // 1024} KB)", flush=True)
            return True
        print(f"[gen] {name} attempt {attempt + 1}: http {code}, "
              f"{out.stat().st_size if out.exists() else 0} B", flush=True)
        if out.exists():
            out.unlink()
        time.sleep(50)
    return False


def main() -> int:
    ok = True
    for name, (prompt, seed) in SPECIES.items():
        if not gen(name, prompt + STYLE, seed):
            ok = False
        time.sleep(15)
    print("GEN_DONE ok=" + str(ok), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
