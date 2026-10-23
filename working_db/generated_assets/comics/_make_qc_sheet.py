# -*- coding: utf-8 -*-
"""產生逐角色一致性檢查頁 _qc_consistency.html（用戶規則③：比例／臉部／特徵跨張一致）。

每角色一列：基本六姿（含海洋替代姿）優先並排、同高縮放，其次劇情動作與既有劇照，
供逐列目視比對。已去背者用去背圖，否則用原始生成圖。可隨時重跑。
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).parent
CUT = HERE / "_raw" / "_masters"
SRC = CUT / "_src"
MANIFEST = HERE / "_cast_manifest.json"
OUT = HERE / "_qc_consistency.html"

data = json.loads(MANIFEST.read_text(encoding="utf-8"))

by_char = {}
for row in data["cast"]:
    by_char.setdefault(row["char"], []).append(row)

parts = ["""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>QC 一致性檢查（逐角色並排）</title>
<style>
  body{font-family:"Microsoft JhengHei",sans-serif;background:#222;color:#ddd;margin:0;padding:20px}
  h1{font-size:20px;margin:0 0 4px}
  p.sub{color:#999;font-size:13px;margin:0 0 16px}
  .strip{background:#2c2c2c;border-radius:12px;padding:12px 14px;margin:0 0 18px;overflow-x:auto}
  .strip h2{font-size:16px;color:#ffd876;margin:0 0 8px}
  .strip h2 small{color:#888;font-weight:normal;margin-left:8px}
  .cells{display:flex;gap:8px;align-items:flex-end}
  .cell{flex:0 0 auto;text-align:center}
  .cell img{height:230px;display:block;border-radius:8px;
    background:repeating-conic-gradient(#3a3a3a 0 25%, #2e2e2e 0 50%) 0 0/18px 18px}
  .cell .sn{font:bold 13px/1 Consolas,monospace;color:#ffd876;background:#111;
    display:inline-block;padding:3px 7px;border-radius:5px;margin-bottom:4px}
  .cell .lb{font-size:11.5px;color:#aaa;margin-top:4px;max-width:150px}
  .cell.miss img{background:#4a2b2b}
  .cell.miss::after{content:"缺";color:#e66;font-size:12px}
</style>
</head>
<body>
<h1>QC 一致性檢查 · 逐角色並排</h1>
<p class="sub">同一列＝同一角色全部定裝（基本六姿在前）。檢查：體型比例、臉部長相、特徵（角／斑紋／配件）是否跨張一致；不一致者以流水號回報重做。</p>
"""]
for char, rows in by_char.items():
    desc = next((r.get("desc") for r in rows if r.get("desc")), "")
    cells = []
    n_have = 0
    for r in rows:
        cut = CUT / f"{r['file']}.png"
        src = SRC / f"{r['file']}.png"
        if cut.exists():
            img, have = f"_raw/_masters/{r['file']}.png", True
        elif src.exists():
            img, have = f"_raw/_masters/_src/{r['file']}.png", True
        else:
            img, have = "", False
        if have:
            n_have += 1
        cls = "cell" if have else "cell miss"
        cell = f'<div class="{cls}"><span class="sn">{r["serial"]}</span>'
        cell += f'<img src="{img}" alt="{r["file"]}">' if have else '<img src="data:," alt="">'
        cell += f'<div class="lb">{html.escape(r["action"])}</div></div>'
        cells.append(cell)
    parts.append(f'<div class="strip"><h2>{html.escape(char)}'
                 f'<small>{n_have}/{len(rows)} 張</small></h2>'
                 f'<div class="cells">{"".join(cells)}</div>'
                 f'<p style="color:#777;font-size:12px;margin:8px 0 0">{html.escape(desc)}</p></div>')
parts.append("</body>\n</html>\n")
OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"saved {OUT} ({len(by_char)} chars)")
