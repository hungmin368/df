# -*- coding: utf-8 -*-
"""產生 Phase 2 背景送審頁 _review_bgs_v7.html：掃描 _raw/_bgs/ 全部底圖，
對照 _gen_bgs_v7.py 的 BGS 清單標示用途（哪幾格用哪張），供使用者裁決後才進入合成。
用法：python _make_bg_review.py（任何時候可重跑；無背景時產出「待產出」提示頁）
"""
import html
import re
from pathlib import Path

HERE = Path(__file__).parent
BG_DIR = HERE / "_raw" / "_bgs"
OUT = HERE / "_review_bgs_v7.html"

USAGE = {}
gen_src = (HERE / "_gen_bgs_v7.py").read_text(encoding="utf-8")
for m in re.finditer(r'\("((?:bg_)[a-z_]+)", [^\n]*?\n', gen_src):
    name = m.group(1)
    prompt = gen_src[m.end():]
    prompt = prompt.split('f"{STYLE}")')[0].split('"{STYLE}")')[0]
    first_line = " ".join(l.strip().strip('"') for l in prompt.splitlines()[:2])
    USAGE[name] = first_line[:150]
PANEL_USE = {"bg_beach_wide": "P1／P3", "bg_sand_close": "P2／P4",
             "bg_sandcastle": "P5", "bg_sunset_glow": "P6"}

imgs = sorted(BG_DIR.glob("*.png")) if BG_DIR.exists() else []
cards = []
for p in imgs:
    name = p.stem
    use = PANEL_USE.get(name, "—")
    desc = html.escape(USAGE.get(name, ""))
    cards.append(
        f'  <div class="card"><img src="_raw/_bgs/{name}.png" alt="{name}">'
        f'<span class="tag t-bg">背景</span><h3>{name}</h3>'
        f'<p>用途：第 {use} 格</p><p>{desc}</p></div>')
body = "\n".join(cards) if cards else '  <p class="empty">尚無背景底圖——Phase 2（_gen_bgs_v7.py）執行後重跑本腳本即可產出送審卡片。</p>'

page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>v7 背景底圖送審（Phase 2）</title>
<style>
  body{{font-family:"Microsoft JhengHei",sans-serif;background:#f4f1ea;margin:0;padding:24px;color:#333}}
  h1{{font-size:22px;margin:0 0 4px}}
  p.sub{{margin:0 0 8px;color:#777;font-size:14px}}
  .gate{{background:#fff3cd;border:1px solid #e0c060;border-radius:8px;padding:10px 14px;font-size:14px;color:#7a5b00;margin:14px 0 22px}}
  .row{{display:flex;gap:16px;flex-wrap:wrap}}
  .card{{background:#fff;border-radius:12px;box-shadow:0 3px 10px rgba(0,0,0,.09);padding:12px;width:340px}}
  .card img{{width:100%;border-radius:8px;display:block}}
  .tag{{display:inline-block;border-radius:6px;padding:2px 9px;font-size:12px;margin:8px 0 3px;color:#fff}}
  .t-bg{{background:#3a86d0}}
  .card h3{{font-size:15px;margin:2px 0 3px}}
  .card p{{font-size:12.5px;line-height:1.5;margin:2px 0;color:#666}}
  .empty{{color:#999;font-size:14px}}
</style>
</head>
<body>
<h1>v7 背景底圖 · 送審頁（Phase 2）</h1>
<p class="sub">4 張 4:3 空景（3A-CG、暖金晨光、無角色無文字）。合成器 _compose_v7.py 依「用途」欄取用。</p>
<div class="gate">待你裁決：背景可否進入合成階段？指認任何一張不滿意（構圖／光線／色調），我用 _gen_bgs_v7.py 重出該張再送審。</div>
<div class="row">
{body}
</div>
</body>
</html>
"""
OUT.write_text(page, encoding="utf-8")
print(f"saved {OUT} ({len(imgs)} bg(s))")
