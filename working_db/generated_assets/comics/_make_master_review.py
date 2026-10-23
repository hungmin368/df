# -*- coding: utf-8 -*-
"""產生 v7 角色定裝送審頁 _review_masters_v7.html（第 6 版・遊戲圖錨定＋基本六姿）。

讀取 _cast_manifest.json（_gen_cast_v7.py 寫入），按角色分區、每張卡片顯示：
流水號（大字）／動作／去背預覽（透明格底）／狀態（已去背・待生成・待去背）。
可隨時重跑；去背完成後狀態自動轉為「已去背」。
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).parent
CUT = HERE / "_raw" / "_masters"
MANIFEST = HERE / "_cast_manifest.json"
OUT = HERE / "_review_masters_v7.html"

data = json.loads(MANIFEST.read_text(encoding="utf-8"))
order = data["char_order"]
cast = data["cast"]

by_char = {c: [] for c in order}
for row in cast:
    by_char.setdefault(row["char"], []).append(row)


def card(row):
    name = row["file"]
    cut = CUT / f"{name}.png"
    src = HERE / "_raw" / "_masters" / "_src" / f"{name}.png"
    if cut.exists():
        status, img = "已去背", f'<img src="_raw/_masters/{name}.png" alt="{name}">'
        cls = "t-ok"
    elif src.exists():
        status, img = "待去背", f'<img src="_raw/_masters/_src/{name}.png" alt="{name}">'
        cls = "t-warn"
    else:
        status, img = "待生成", '<div class="ph">待產出</div>'
        cls = "t-wait"
    act = html.escape(row["action"])
    return (f'  <div class="card"><span class="sn">{row["serial"]}</span>{img}'
            f'<span class="tag {cls}">{status}</span><h3>{name}</h3><p>{act}</p></div>')


parts = ["""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>v7 角色定裝送審（第 6 版・遊戲圖錨定＋基本六姿）</title>
<style>
  body{font-family:"Microsoft JhengHei",sans-serif;background:#f4f1ea;margin:0;padding:24px;color:#333}
  h1{font-size:22px;margin:0 0 4px}
  p.sub{margin:0 0 8px;color:#777;font-size:14px}
  .gate{background:#fff3cd;border:1px solid #e0c060;border-radius:8px;padding:10px 14px;font-size:14px;color:#7a5b00;margin:14px 0 8px}
  .done{background:#e6f4e9;border:1px solid #7dbf8d;color:#2c5e3a}
  h2{font-size:18px;margin:26px 0 4px;border-left:5px solid #7a5cc7;padding-left:10px}
  p.note{font-size:13px;color:#888;margin:2px 0 12px}
  .row{display:flex;gap:14px;flex-wrap:wrap}
  .card{background:#fff;border-radius:12px;box-shadow:0 3px 10px rgba(0,0,0,.09);padding:12px;width:200px;position:relative}
  .card img{width:100%;border-radius:8px;display:block;
    background:repeating-conic-gradient(#e8e8e8 0 25%, #fff 0 50%) 0 0/16px 16px}
  .sn{position:absolute;top:8px;left:8px;z-index:2;background:#2b2b2b;color:#ffd876;
      font:bold 15px/1 Consolas,monospace;padding:4px 8px;border-radius:6px;letter-spacing:1px}
  .tag{display:inline-block;border-radius:6px;padding:2px 9px;font-size:12px;margin:8px 0 3px;color:#fff}
  .t-ok{background:#5ca86b}.t-warn{background:#d0913a}.t-wait{background:#999}
  .ph{height:130px;display:flex;align-items:center;justify-content:center;color:#bbb;font-size:13px;background:#f7f5f0;border-radius:8px}
  .card h3{font-size:12px;margin:2px 0 3px;color:#888;font-family:Consolas,monospace}
  .card p{font-size:12.5px;line-height:1.5;margin:0;color:#666}
</style>
</head>
<body>
<h1>v7 角色定裝 · 送審頁（第 6 版・遊戲圖錨定＋基本六姿）</h1>
<p class="sub">規則改版（2026-10-23）：恐龍角色一律以遊戲現有恐龍圖為造型錨；每個角色至少含 正面／左側面／右側面／背面／跑步／走路 基本六姿，其餘為劇情動作。</p>
<div class="gate done">一致性做法：同一角色所有 pose 均掛同一張造型錨生成，跨張比例／臉部／特徵以錨定圖鎖定；海洋恐龍以「快速游動／緩慢游動」替代跑步／走路。</div>
<div class="gate">待你裁決：直接用「流水號」指認——例如「038 重做」「019 換動作」。我會重出該流水號（造型以錨定圖重鎖）再送審；全部滿意回覆「可以」即進入背景與合成階段。</div>
"""]
for char in order:
    rows = by_char.get(char, [])
    if not rows:
        continue
    desc = next((r.get("desc") for r in rows if r.get("desc")), "")
    n_ok = sum(1 for r in rows if (CUT / f"{r['file']}.png").exists())
    parts.append(f'<h2>{html.escape(char)}（{len(rows)} 張・已去背 {n_ok}）</h2>')
    parts.append(f'<p class="note">{html.escape(desc)}</p>')
    parts.append('<div class="row">')
    parts.extend(card(r) for r in rows)
    parts.append('</div>')
parts.append("</body>\n</html>\n")
OUT.write_text("\n".join(parts), encoding="utf-8")
total = len(cast)
n_cut = sum(1 for r in cast if (CUT / f"{r['file']}.png").exists())
print(f"saved {OUT} ({total} serials, {n_cut} cut)")
