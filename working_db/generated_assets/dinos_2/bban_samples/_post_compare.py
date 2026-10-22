# -*- coding: utf-8 -*-
"""Post-chain for backend-comparison raws: reuses _post_trial5.py verbatim.

Inputs : assets/dinos_2/compare/{sophnet,gemini}_260_raw.png
Outputs: assets/dinos_2/compare/{sophnet,gemini}.webp + _post_report.json
(same gates: bbox_cov 50-60% solved to 55%, ratio 1:1.2-1.2:1, margins, halo...)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _post_trial5 as P

CMP = Path(__file__).resolve().parents[2] / "dinos_2" / "compare"
P.RAW = CMP
P.OUT = CMP


def main():
    P.OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for raw in sorted(P.RAW.glob("*_raw.png")):
        print(f"[{raw.name}]")
        r = P.process(raw)
        report.append(r)
        flags = " ".join(k for k, v in r["checks"].items() if not v) or "all-ok"
        print(f"  -> {r['out']} {r['kb']}KB bbox_cov={r['bbox_cov_pct']}% "
              f"ratio={r['ratio']} cov={r['coverage']}% [{flags}]")
    (P.OUT / "_post_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in report if r["pass"])
    print(f"\npost-chain: {ok}/{len(report)} passed all gates")
    sys.exit(0 if ok == len(report) else 1)


if __name__ == "__main__":
    main()
