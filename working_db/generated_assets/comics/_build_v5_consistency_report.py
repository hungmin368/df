# -*- coding: utf-8 -*-
"""v5 → v5.1 角色特徵一致性 before/after 報告產生器（圖片 base64 內嵌自足單檔）。"""
import base64
import io
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

COMICS = Path(__file__).parent
BAK = COMICS / "_raw" / "_v5r1_backup"
REPORTS = COMICS.parent.parent / "reports"
OUT = REPORTS / "comic_v5_consistency_report.html"

def b64(path, max_w, q=86):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

PANELS = {}
for i in range(1, 7):
    PANELS[i] = dict(
        before=b64(BAK / f"propA_ch01_v5_p{i}.png", 980),
        after=b64(COMICS / "_raw" / f"propA_ch01_v5_p{i}.png", 980),
    )
PAGE_BEFORE = b64(BAK / "propA_ch01_page1_v2_v5_r1.png", 1000)
PAGE_AFTER = b64(COMICS / "propA_ch01_page1_v2_v5.png", 1000)

NOTES = {
    1: ("方形降級圖中央裁切（角色被放大）、補給箱貼畫面下緣，構圖空間局促",
        "1792×768 真寬幅；男孩＋伴伴＋補給箱全部在下中段、上 1/3 純天空留給旁白牌；帽冠淨空"),
    2: ("男孩年齡感偏幼（5–8 歲）、臉型隨表情浮動",
        "男孩 10 歲同臉同裝鎖定；伴伴深紫翅點、雙金角、粉耳、奶油肚維持"),
    3: ("此格為薩爾塔 canonical 基準（長頸、小頭），無偏差",
        "頸長＝軀幹長、頭寬＝1/4 軀寬量化鎖定，與 P4–P6 完全同款"),
    4: ("薩爾塔優雅長頸（canonical）；其餘穩定",
        "三角色全部對齊量化特徵表；男孩 jaw-drop 表情但臉型年齡不漂"),
    5: ("薩爾塔短頸俯身近似四足、翅膜斑點偏亮桃紅；沙堡偏小不夠「氣派」",
        "長頸小頭恢復、翅點回到深紫；多塔沙堡＋小旗更醒目，呼應台詞「最氣派的沙堡」"),
    6: ("薩爾塔變短頸大頭四足、翅膜斑點偏洋紅",
        "長頸小頭＋螺旋尾靠臀；翅點深紫；男孩 10 歲；彩虹下三角色全身一致"),
}

TRAIT_ROWS = [
    ("伴伴 體色", "紫紅漸變各格濃淡不一", "亮紫身體＋深紫圓斑（頭/背/臀），6 格一致"),
    ("伴伴 角", "穩定（2 根金黃段節角）", "量化鎖定：恰好一對金黃段節角＋眉心單列小錐刺"),
    ("伴伴 翅膜", "P1/P2/P4 深紫點、P5 桃紅點、P6 洋紅點", "桃紅→橙漸變膜＋深紫圓點（never pink, never red）"),
    ("伴伴 耳/肚/爪", "穩定（粉內耳、奶油肚、金爪）", "維持一致"),
    ("薩爾塔 頸與頭身比", "P3 長頸 → P5 短頸俯身 → P6 短頸大頭，逐格漂移最嚴重", "頸長＝軀幹長、頭寬＝1/4 軀寬，4 格完全同款"),
    ("薩爾塔 背刺/耳/腹/尾", "穩定（金黃單列刺、粉耳、奶油腹、螺旋尾）", "維持一致；螺旋尾尖貼臀"),
    ("男孩 年齡與臉", "P2 偏幼 5–8 歲、其餘近 10 歲；臉型浮動", "明確 10 歲＋同臉描述（鵝蛋臉/圓下巴/深棕大眼）"),
    ("男孩 服裝", "穩定（卡其帽/米色背心/橘T/綠背包/棕短褲/棕靴）", "逐件量化鎖定，6 格一致"),
]

BUBBLE_ROWS = [
    ("P1", "旁白牌置中央上空（x0.32–0.54），背後純天空、零角色接觸"),
    ("P2", "對話泡貼右上；尾尖落伴伴眉心雙眼之間——眼鼻口全部淨空"),
    ("P3", "對話泡貼右側；尾尖指薩爾塔下頜——五官淨空"),
    ("P4", "「喂——」爆裂泡壓男孩下半身、直尾入口下方；「項鍊～」泡壓右下角、尾指薩爾塔嘴——無遮臉"),
    ("P5", "泡塞左下角蓋腿蓋沙（臉在 y0.38–0.60 淨空）；尾短直上指男孩嘴"),
    ("P6", "爆裂泡左上尾指躍空伴伴嘴；「分你一半！」右上尾指男孩嘴；銘牌壓下半身——無遮臉"),
]

def table_rows(rows):
    return "\n".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)

def bubble_rows(rows):
    return "\n".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rows)

panel_blocks = []
for i in range(1, 7):
    nb, na = NOTES[i]
    panel_blocks.append(f"""
<section class="panel" id="p{i}">
  <h3>P{i}</h3>
  <div class="pair">
    <figure><figcaption>v5（第 8 輪交付）</figcaption><img src="{PANELS[i]['before']}" loading="lazy"></figure>
    <figure><figcaption>v5.1（本輪重跑）</figcaption><img src="{PANELS[i]['after']}" loading="lazy"></figure>
  </div>
  <ul class="note">
    <li><b>修正前</b>：{nb}</li>
    <li><b>修正後</b>：{na}</li>
  </ul>
</section>""")

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>v5 漫畫角色特徵一致性修正報告（before/after）</title>
<style>
  :root {{ --ink:#201a14; --paper:#fffdf8; --navy:#1e2a58; --gold:#ffd678; --red:#ce3c34; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
         font-family:"Microsoft JhengHei","PingFang TC",sans-serif; line-height:1.75; }}
  header {{ background:var(--navy); color:#f5efdf; padding:28px 20px 20px; text-align:center; }}
  header h1 {{ margin:0 0 6px; font-size:26px; color:var(--gold); letter-spacing:1px; }}
  header p {{ margin:2px 0; font-size:14px; opacity:.85; }}
  main {{ max-width:1060px; margin:0 auto; padding:20px 16px 60px; }}
  h2 {{ border-left:6px solid var(--red); padding-left:10px; margin:38px 0 14px; font-size:21px; }}
  h3 {{ margin:22px 0 8px; font-size:18px; color:var(--navy); }}
  .card {{ background:#fff; border:1px solid #e5ddcc; border-radius:10px; padding:14px 16px; margin:12px 0; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  figure {{ margin:0; }}
  figure img {{ width:100%; border:1px solid #cfc7b4; border-radius:6px; display:block; background:#eee; }}
  figcaption {{ font-size:13px; color:#6b6152; margin:4px 2px; }}
  .note {{ margin:10px 0 0; padding-left:20px; font-size:14.5px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14.5px; background:#fff; }}
  th, td {{ border:1px solid #ddd3bf; padding:8px 10px; vertical-align:top; text-align:left; }}
  th {{ background:#f7f0dd; white-space:nowrap; }}
  .ok {{ color:#1c7a3d; font-weight:bold; }}
  .tag {{ display:inline-block; background:var(--red); color:#fff; border-radius:4px;
         font-size:12px; padding:1px 8px; margin-left:8px; vertical-align:middle; }}
  footer {{ text-align:center; font-size:13px; color:#8a8172; margin-top:40px; }}
  @media (max-width:760px) {{ .pair {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>《彩虹羅盤與失落的探險隊》第 1 話<span class="tag">角色特徵一致性修正</span></h1>
  <p>v5 油畫版（第 8 輪交付）→ v5.1（本輪重跑）　before / after 對照</p>
  <p>2026-10-22・SophNet Wan2.6-T2I・方案A漫畫試刊</p>
</header>
<main>

<h2>摘要</h2>
<div class="card">
  <p><b>使用者回饋</b>：「登場角色的體型特徵外貌要固定，我看到在不同格有差異」。</p>
  <p><b>根因</b>：角色鎖定（LOCK）為質性描述（"long-necked"、"magenta spots"），Wan 對質性詞的數值詮釋逐格浮動；
  三處最明顯：薩爾塔頸長與頭身比逐格漂移、伴伴翅膜斑點色在 P5/P6 偏桃紅/洋紅、男孩年齡感在 P2 偏幼。</p>
  <p><b>修法（v5.1）</b>：① LOCK 升級為<b>量化 CHARACTER SHEET</b>（角數、刺列數、翅點顏色禁令、頸長＝軀幹長、
  頭寬＝1/4 軀寬、男孩明確 10 歲＋逐件服裝清單）並<b>置於提示詞末尾</b>加權重；
  ② 全六格固定 <code>seed=7</code>；③ 補上分鏡缺漏（P5 沙堡）；④ 依新構圖重校全部對話泡、仍守「零遮臉」硬規則；
  ⑤ 修掉組版 bug（P2 斜格紙色角溢出蓋住 P1 左下角）。</p>
  <p><b>結果</b>：<span class="ok">六格三角色特徵跨格一致；對話框（含尾尖）零臉部重疊；整頁驗收通過。</span></p>
</div>

<h2>整頁 before / after</h2>
<div class="pair">
  <figure><figcaption>v5 整頁（commit 7236005 交付版）</figcaption><img src="{PAGE_BEFORE}"></figure>
  <figure><figcaption>v5.1 整頁（本輪交付）</figcaption><img src="{PAGE_AFTER}"></figure>
</div>

<h2>逐格 before / after</h2>
{''.join(panel_blocks)}

<h2>特徵鎖定對照表</h2>
<table>
  <tr><th>特徵</th><th>v5 狀況（偏差）</th><th>v5.1 狀況（量化鎖定後）</th></tr>
  {table_rows(TRAIT_ROWS)}
</table>

<h2>對話框避臉驗證（硬規則）</h2>
<table>
  <tr><th>格子</th><th>驗證結果</th></tr>
  {bubble_rows(BUBBLE_ROWS)}
</table>
<p class="ok">結論：六格全部通過——没有任何對話框或尾尖重疊任何角色的臉。</p>

<h2>成本與備註</h2>
<div class="card">
  <ul>
    <li>本輪生成 10 格（6 格全跑＋P5 補沙堡＋P1 三次構圖修正），Wan2.6-T2I 約 NT$0.5/格，合計約 NT$5。</li>
    <li>尺寸參數（1792×768 等）佈署間歇性回 400 20011 NO_AVAILABLE_DEPLOYMENT，腳本自動降級（size→size+seed→裸 input）；
        20011 為佈署未配置錯誤，應未計費。</li>
    <li>P1 前三度為方形降級圖（中央裁切可用但帽冠會被旁白牌切到），第四度以「下中段構圖＋上 1/3 純天空」提示拿到 1792×768 真寬幅。</li>
    <li>旁白銘牌位置依 prefix 覆寫（CAPTIONS_BY_PREFIX），不影響 v3 組版。</li>
    <li>半成品與除錯裁圖（z_*.png）不交付；r1 原始六格備份於 <code>_raw/_v5r1_backup/</code>（gitignore）。</li>
  </ul>
</div>

</main>
<footer>恐龍快找 DragonFinder・故事試刊彩虹羅盤篇・2026-10-22</footer>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"saved {OUT} ({OUT.stat().st_size/1024/1024:.1f} MB)")
