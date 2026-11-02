# -*- coding: utf-8 -*-
"""v6 攝影寫真版一致性報告：v5.1 油畫版 vs v6 攝影寫真版 before/after＋特徵對照表。"""
import base64
import io
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
RAW = HERE / "_raw"
OUT = HERE.parents[1] / "reports" / "comic_v6_photo_report.html"

def b64(path, max_w, q=80):
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

PAGE_V5 = HERE / "propA_ch01_page1_v2_v5.png"
PAGE_V6 = HERE / "propA_ch01_page1_v2_v6.png"

TRAIT_ROWS = [
    ("男孩臉型/年齡", "每格浮動，5–10 歲搖擺", "六格同一位寫實男孩（85mm 人像攝影語義鎖定）"),
    ("龍A 頭身比例", "P1/P5 寫實修長吻 vs P2/P4/P6 Q版大頭", "六格一致：Q版大頭、圓吻、雙金角"),
    ("龍A 翅膀斑點/配色", "深紫↔桃紅↔洋紅漂移", "六格一致：紫身、金角、粉橙翼、深紫斑"),
    ("龍B 體態", "長頸↔短頸俯身↔四足 逐格漂移", "六格一致：石板藍長頸、橙刺、粉耳、無翼"),
    ("龍B 翅膀", "—（v5 無翅膀問題）", "P3 初版誤加蝠翼 → 重跑移除，全格無翼"),
    ("生成模型", "SophNet Wan2.6-T2I（純文字）", "Gemini gemini-2.5-flash-image＋參考圖內嵌＋P1 連鎖參考"),
]

BUBBLE_ROWS = [
    ("P2", "泡貼左上天空，尾垂落雙角間", "零重疊"),
    ("P3", "泡貼右上天空，尾垂直指龍A嘴", "零重疊"),
    ("P4", "爆裂泡壓男孩膝、直尾入口；項鍊泡壓右下沙地", "零重疊"),
    ("P5", "泡壓左下沙地，尾斜上指男孩嘴", "零重疊"),
    ("P6", "爆裂泡貼左上天空；分你一半泡貼右側；銘牌壓下半身", "零重疊"),
]

def table(rows, head):
    tr = "".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return f"<table><thead><tr><th>{head[0]}</th><th>{head[1]}</th><th>{head[2]}</th></tr></thead><tbody>{tr}</tbody></table>"

panels_v6 = "".join(
    f"<figure><img src='{b64(RAW / f'propA_ch01_v6_p{n}.png', 560)}'><figcaption>v6 P{n}</figcaption></figure>"
    for n in range(1, 7))

html = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<title>v6 攝影寫真版一致性報告</title>
<style>
body{{font-family:'Microsoft JhengHei',sans-serif;max-width:1060px;margin:0 auto;padding:28px;background:#faf7f0;color:#2c2620}}
h1{{font-size:26px;border-bottom:4px solid #c33;padding-bottom:8px}}
h2{{font-size:20px;margin-top:34px;color:#7a2820}}
img{{max-width:100%;border:3px solid #2c2620;box-sizing:border-box}}
figure{{margin:14px 0}}figcaption{{font-size:13px;color:#6b6156;margin-top:4px}}
table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}}
th,td{{border:1px solid #b9ad9c;padding:8px 10px;text-align:left;vertical-align:top}}
thead th{{background:#3a2f24;color:#fff}}
tbody th{{background:#efe7d8;white-space:nowrap}}
.note{{background:#fff8e0;border-left:5px solid #e0a400;padding:10px 14px;font-size:14px}}
</style></head><body>
<h1>方案A 第1話漫畫試刊：v6 攝影寫真版（跨格一致性報告）</h1>
<p>日期：2026-10-22｜生成：Gemini gemini-2.5-flash-image＋伴伴2star／薩爾塔9.webp 參考圖每格內嵌，
P1 完成圖作為第三張連鎖參考餵給 P2–P6。風格依用戶指定「變體 photo：攝影寫真」
（85mm 人像鏡、真實男孩、恐龍＝收藏級玩具立於真實沙灘）。</p>

<h2>整頁 before（v5.1 油畫版）→ after（v6 攝影寫真版）</h2>
<figure><img src='{b64(PAGE_V5, 900)}'><figcaption>v5.1 油畫版整頁（before）</figcaption></figure>
<figure><img src='{b64(PAGE_V6, 900)}'><figcaption>v6 攝影寫真版整頁（after）</figcaption></figure>

<h2>跨格特徵對照（before → after）</h2>
{table(TRAIT_ROWS, ("特徵", "v5.1 油畫版（before）", "v6 攝影寫真版（after）"))}

<h2>v6 六格分格圖</h2>
{panels_v6}

<h2>氣泡避臉驗證（v6 組版）</h2>
{table(BUBBLE_ROWS, ("格", "氣泡位置", "臉部重疊"))}
<p class="note">結論：v6 六格男孩與兩隻恐龍的臉型、體型、配色跨格一致；對話泡（含尾尖）與旁白銘牌
零臉部重疊。龍B（薩爾塔）初版誤加蝠翼、P1 初版頭部被横幅裁切，皆已重跑修正。</p>
</body></html>"""

OUT.write_text(html, encoding="utf-8")
print(f"saved {OUT} ({OUT.stat().st_size} bytes)")
