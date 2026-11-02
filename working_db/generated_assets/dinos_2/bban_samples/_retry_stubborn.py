# -*- coding: utf-8 -*-
"""Round 29 retry driver: force the 15 ratio-stubborn ids to converge.

Why a dedicated driver instead of _gen_batch + _post_batch rounds: these ids are
stochastic on the ratio gate (the corrective note lands in-window only ~half the
time), so a single-candidate-per-round loop needs many rounds. This driver fires
up to K candidates per id and KEEPS THE FIRST that passes all 11 gates, stopping
early - far higher cumulative convergence for the same wall-clock.

Reuses the proven primitives: _gen_batch.gen_one (model ladder + backoff) and
_post_trial5.process (the 11-gate chain). Corrective direction per id comes from
_gen_batch's freshly-fixed SQUAT_IDS/WIDE_IDS/COIL_IDS (r4 measurements).

Resume-safe: _retry_state.json records per-id outcome; passing tiles are appended
to _post_report.json immediately so a crash never loses work. Single-instance via
_retry.lock (lesson from the id-13 race-orphan).

Usage: PYTHONIOENCODING=utf-8 python -u _retry_stubborn.py [--k 6] [--ids 9,17]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import _gen_trial5 as G          # noqa: E402
import _gen_batch as GB          # noqa: E402
import _post_trial5 as P         # noqa: E402

BATCH = HERE.parent / "batch"
RAW = BATCH / "_raw"
REJ = RAW / "_rejected"
REPORT = BATCH / "_post_report.json"
HIST = BATCH / "_gate_history.json"
STATE = BATCH / "_retry_state.json"
LOCK = BATCH / "_retry.lock"

STUB = [9, 17, 31, 35, 39, 49, 65, 85, 117, 218, 250, 252, 264, 288, 303]
SLEEP = 3.0


def _load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _save(path, obj):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def acquire_lock():
    if LOCK.exists():
        try:
            old = int(LOCK.read_text().strip())
        except Exception:
            old = -1
        # refuse if another live process holds it (best-effort liveness on Windows)
        alive = False
        if old > 0:
            try:
                os.kill(old, 0)
                alive = True
            except OSError:
                alive = False
        if alive:
            print(f"ABORT: _retry.lock held by live PID {old}", flush=True)
            sys.exit(3)
        print(f"stale lock (PID {old} dead) - taking over", flush=True)
    LOCK.write_text(str(os.getpid()))


def release_lock():
    try:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


def direction(sid):
    if sid in GB.SQUAT_IDS:
        return "SQUAT"
    if sid in GB.WIDE_IDS:
        return "WIDE"
    if sid in GB.COIL_IDS:
        return "COIL"
    return "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=6, help="max candidates per id")
    ap.add_argument("--ids", help="comma-separated subset (default: all 15)")
    ap.add_argument("--round", type=int, default=0)
    args = ap.parse_args()

    ids = [int(x) for x in args.ids.split(",")] if args.ids else list(STUB)
    ids = sorted(set(ids))

    acquire_lock()
    try:
        run(ids, args.k, args.round)
    finally:
        release_lock()


def run(ids, K, rnd_arg):
    RAW.mkdir(parents=True, exist_ok=True)
    REJ.mkdir(parents=True, exist_ok=True)
    P.RAW = RAW
    P.OUT = BATCH

    specs = GB.load_specs()
    finals = _load(REPORT, [])
    passed_ids = {x["id"] for x in finals if "id" in x}
    state = _load(STATE, {})
    hist = _load(HIST, [])
    rnd = rnd_arg or (max((h["round"] for h in hist), default=0) + 1)

    style_b64, _ = G.as_b64(G.STYLE_SRC, HERE / "_ref_banban_2star.png", "image/png")

    todo = []
    for sid in ids:
        if state.get(str(sid), {}).get("status") == "pass" or sid in passed_ids:
            print(f"id {sid}: already passed - skip", flush=True)
            continue
        todo.append(sid)
    print(f"round {rnd}: retrying {len(todo)} ids, up to {K} candidates each "
          f"({K * len(todo)} img max ~${0.04 * K * len(todo):.2f})", flush=True)

    round_pass, round_fail = [], []
    for sid in todo:
        row = specs[sid]
        en = GB.simple_en(sid, row)
        prompt, _ = GB.prompt_for(sid, row)
        prompt = GB.apply_patches(sid, prompt)
        d = direction(sid)
        print(f"\n=== id {sid} ({row['stars']}* {row['name']}) dir={d} ===", flush=True)

        won = None
        for a in range(1, K + 1):
            raw = RAW / f"{sid}_{en}_raw.png"
            t0 = time.time()
            png, model, err = GB.gen_one(row, prompt, style_b64)
            if not png:
                print(f"  [{a}/{K}] GEN FAIL: {err}", flush=True)
                state[str(sid)] = {"status": "genfail", "attempts": a, "err": err,
                                   "dir": d, "ts": time.time()}
                _save(STATE, state)
                time.sleep(SLEEP)
                continue
            raw.write_bytes(png)
            r = P.process(raw)
            r["id"] = sid
            flags = [k for k, v in r["checks"].items() if not v]
            tag = "PASS" if r["pass"] else "FAIL " + ",".join(flags)
            print(f"  [{a}/{K}] ratio={r['ratio']} bbox={r['bbox_cov_pct']}% "
                  f"halo={r['halo']} {tag} via {model} ({time.time() - t0:.0f}s)",
                  flush=True)
            if r["pass"]:
                won = {"attempt": a, "ratio": r["ratio"], "model": model}
                finals.append(r)
                _save(REPORT, finals)
                state[str(sid)] = {"status": "pass", "attempts": a, "ratio": r["ratio"],
                                   "dir": d, "model": model, "raw": raw.name,
                                   "ts": time.time()}
                _save(STATE, state)
                break
            # archive the losing candidate + remove its bad tile
            dst = REJ / f"r{rnd}_a{a}_{raw.name}"
            n = 2
            while dst.exists():
                dst = REJ / f"r{rnd}_a{a}_{n}_{raw.name}"
                n += 1
            raw.rename(dst)
            outp = BATCH / f"{sid}.webp"
            if outp.exists():
                outp.unlink()
            state[str(sid)] = {"status": "trying", "attempts": a, "ratio": r["ratio"],
                               "dir": d, "last_flags": flags, "archived": dst.name,
                               "ts": time.time()}
            _save(STATE, state)
            time.sleep(SLEEP)

        if won:
            round_pass.append(sid)
            print(f"  -> id {sid} CONVERGED on attempt {won['attempt']} "
                  f"(ratio {won['ratio']})", flush=True)
        else:
            round_fail.append({"id": sid, "dir": d,
                               "ratio": state.get(str(sid), {}).get("ratio"),
                               "flags": state.get(str(sid), {}).get("last_flags", []),
                               "attempts": state.get(str(sid), {}).get("attempts", 0)})
            state[str(sid)] = {**state.get(str(sid), {}), "status": "exhausted"}
            _save(STATE, state)
            print(f"  -> id {sid} EXHAUSTED {K} candidates, still failing", flush=True)

    hist.append({"round": rnd, "ts": time.time(), "driver": "retry_stubborn",
                 "k": K, "attempted": len(todo),
                 "passed": round_pass, "failed": round_fail})
    _save(HIST, hist)

    print(f"\n==== round {rnd} summary ====", flush=True)
    print(f"converged : {len(round_pass)}/{len(todo)} -> {round_pass}", flush=True)
    print(f"exhausted : {len(round_fail)} -> {[f['id'] for f in round_fail]}", flush=True)
    print(f"total passing tiles in report: {len(finals)}", flush=True)
    sys.exit(0 if not round_fail else 1)


if __name__ == "__main__":
    main()
