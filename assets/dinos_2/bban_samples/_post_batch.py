# -*- coding: utf-8 -*-
"""Phase 2 batch post-chain: reuse _post_trial5's 11-gate chain over batch raws.

Usage: PYTHONIOENCODING=utf-8 python -u _post_batch.py [--round N]
Inputs : assets/dinos_2/batch/_raw/<id>_*_raw.png   (already-passed raws skipped)
Outputs: assets/dinos_2/batch/<id>.webp             (512x512 RGBA, q90)
         assets/dinos_2/batch/_post_report.json     (all passing tiles, rewritten incrementally)
         assets/dinos_2/batch/_gate_history.json    (append-only per-round results)
Failed tiles: raw moved to _raw/_rejected/r<N>_<name>, bad webp deleted.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import _post_trial5 as P  # noqa: E402

BATCH = HERE.parent / "batch"
RAW = BATCH / "_raw"
REJ = RAW / "_rejected"
REPORT = BATCH / "_post_report.json"
HIST = BATCH / "_gate_history.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, default=0)
    args = ap.parse_args()

    P.RAW = RAW
    P.OUT = BATCH
    BATCH.mkdir(parents=True, exist_ok=True)

    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    rnd = args.round or (max((h["round"] for h in hist), default=0) + 1)

    finals = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else []
    passed_names = {x["raw"] for x in finals}
    raws = sorted((p for p in RAW.glob("*_raw.png") if p.name not in passed_names),
                  key=lambda p: int(p.name.split("_")[0]))
    print(f"round {rnd}: {len(raws)} raws to process "
          f"({len(passed_names)} already passed)", flush=True)

    n_pass = 0
    fails = []
    for i, raw in enumerate(raws, 1):
        t0 = time.time()
        r = P.process(raw)
        r["id"] = int(raw.name.split("_")[0])
        flags = [k for k, v in r["checks"].items() if not v]
        print(f"[{i}/{len(raws)}] id {r['id']}: {r['kb']}KB ratio={r['ratio']} "
              f"bbox={r['bbox_cov_pct']}% halo={r['halo']} "
              f"{'all-ok' if r['pass'] else 'FAIL ' + ','.join(flags)}"
              f" ({time.time() - t0:.0f}s)", flush=True)
        if r["pass"]:
            finals.append(r)
            n_pass += 1
        else:
            REJ.mkdir(parents=True, exist_ok=True)
            dst = REJ / f"r{rnd}_{raw.name}"
            n = 2
            while dst.exists():
                dst = REJ / f"r{rnd}_{n}_{raw.name}"
                n += 1
            raw.rename(dst)
            outp = P.OUT / r["out"]
            if outp.exists():
                outp.unlink()
            r["archived"] = dst.name
            fails.append(r)
        REPORT.write_text(json.dumps(finals, ensure_ascii=False, indent=1), encoding="utf-8")

    hist.append({"round": rnd, "ts": time.time(), "processed": len(raws),
                 "passed": [r["id"] for r in finals[-n_pass:]] if n_pass else [],
                 "failed": [{"id": r["id"],
                             "checks": [k for k, v in r["checks"].items() if not v],
                             "ratio": r["ratio"], "halo": r["halo"],
                             "archived": r.get("archived", "")} for r in fails]})
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nround {rnd}: +{n_pass} passed, {len(fails)} failed "
          f"(total passing: {len(finals)})", flush=True)
    for r in fails:
        print(f"  REJECT id {r['id']} -> {r.get('archived')}", flush=True)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
