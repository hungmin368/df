# -*- coding: utf-8 -*-
"""Phase 1: build the trial review report (contact sheet + gates + specs).

Usage: PYTHONIOENCODING=utf-8 python _build_trial_report.py
Input : assets/dinos_2/trial/<id>.webp, _raw/*.png, _post_report.json,
        bban_samples/_gen_specs.json
Output: styleA_trial5_report.html (repo root)
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
TRIAL = Path(r"C:\MY_AI_JOBS\dragonfinder\assets\dinos_2\trial")
SPEC_IDS = [1, 101, 202, 260, 325]
OUT = ROOT / "styleA_trial5_report.html"


def b64_webp(p: Path) -> str:
    return "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def b64_thumb(p: Path, box=(256, 256)) -> str:
    im = Image.open(p).convert("RGB")
    im.thumbnail(box)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def variant_b64(p: Path, mode: str, px=150) -> str:
    im = Image.open(p).convert("RGBA")
    a = im.getchannel("A")
    if mode == "silhouette":
        body = Image.new("RGBA", im.size, (17, 12, 33, 255))
        body.putalpha(a.point(lambda v: 255 if v > 8 else 0))
        im = body
    elif mode == "gray":
        g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
        g.putalpha(a)
        im = g
    im.thumbnail((px, px))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def aspect_ratio(p: Path) -> float:
    import numpy as np
    a = np.asarray(Image.open(p).convert("RGBA"))[..., 3]
    ys, xs = np.where(a > 12)
    w = xs.max() - xs.min() + 1
    h = ys.max() - ys.min() + 1
    return w / h


def ar_span(ar: float) -> str:
    color = "#6ee7b7" if ar <= 1.2 else "#fca5a5"
    return f'<b style="color:{color}">{ar:.2f}:1</b>'


def main():
    specs = {r["id"]: r for r in json.loads(
        (HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]}
    post = {int(r["out"].split(".")[0]): r for r in json.loads(
        (TRIAL / "_post_report.json").read_text(encoding="utf-8"))}

    cards = []
    sheet_cells = []
    for sid in SPEC_IDS:
        r = specs[sid]
        g = post[sid]
        tile = TRIAL / f"{sid}.webp"
        raw = TRIAL / "_raw" / g["raw"]
        stain_txt = "、".join(s["zh"] for s in r["stains"])
        pose_txt = r["pose_zh"] if r["pose_pool"] == "general" else f"{r['pose_zh']}（英雄姿勢池）"
        checks = "".join(
            f'<span class="ck {"ok" if v else "bad"}">{k} {"✔" if v else "✘"}</span>'
            for k, v in g["checks"].items())
        ar = g.get("ratio") or aspect_ratio(tile)
        if r.get("body_compact"):
            variant = ("收攏體態（尾緊捲・頭微抬・長高比 ≤1.2）"
                       if r.get("body_note_en", "").startswith("compact gathered")
                       else "收攏體態（頸平低前伸・收尾・頭低側・長高比 ≤1.2）")
            body_txt = f'<b style="color:#fbbf24">{variant}</b>'
        else:
            body_txt = "標準"
        fun_kind_zh = {"action": "動作", "mood": "情緒"}[r.get("fun_kind", "mood")]
        pose_disp = pose_txt
        if r.get("fun_kind") == "action" and r["stars"] != 5:
            pose_disp = f'{pose_txt} → <b style="color:#f0abfc">{r["fun_zh"]}</b>（趣味動作取代）'
        cards.append(f"""
  <div class="card">
    <div class="imgs">
      <figure><img src="{b64_webp(tile)}"><figcaption>512×512 WebP 成品（{g['kb']}KB）</figcaption></figure>
      <figure><img src="{b64_thumb(raw)}"><figcaption>生成原圖（縮圖）</figcaption></figure>
    </div>
    <h2><span class="st s{r['stars']}">{r['stars']}★</span> {r['name']} <span class="id">id {sid} · {r['method']} · seed {r['seed']}</span></h2>
    <table class="spec">
      <tr><th>還原圖</th><td>{r['recon']}</td></tr>
      <tr><th>體色</th><td>{r['color_zh']}（{r['color_en']}）</td></tr>
      <tr><th>花紋</th><td>{r['pattern_zh']}</td></tr>
      <tr><th>表情</th><td>{r['expr_zh']}</td></tr>
      <tr><th>姿勢</th><td>{pose_disp}</td></tr>
      <tr><th>趣味要素</th><td><b style="color:#f0abfc">{r['fun_zh']}</b>（{fun_kind_zh}）</td></tr>
      <tr><th>體態</th><td>{body_txt}</td></tr>
      <tr><th>長高比</th><td>{ar_span(ar)}（門檻 ≤1.2:1）</td></tr>
      <tr><th>本體佔圖</th><td>{g['bbox_cov_pct']}%（門檻 50–60%）</td></tr>
      <tr><th>配件</th><td>{r['acc_zh']}</td></tr>
      <tr><th>星級要素</th><td>{r['tier_extra']}</td></tr>
      <tr><th>污漬/沾黏</th><td>{stain_txt}</td></tr>
    </table>
    <div class="gates">{checks}</div>
    <p class="meta">不透明覆蓋率 {g['coverage']}%｜下緣 {g['bottom_pct']}%｜邊距 {g['margins_pct']}%｜主體分量 {g['main_pct']}%｜白邊暈染 {g['halo']}</p>
  </div>""")
        sheet_cells.append(f"""
    <div class="cell">
      <img src="{b64_webp(tile)}" class="big"><img src="{variant_b64(tile, 'gray')}"><img src="{variant_b64(tile, 'silhouette')}">
      <div class="lbl">{r['stars']}★ {r['name']}</div>
    </div>""")

    v1 = TRIAL / "_raw" / "_rejected" / "202_wide.webp"
    v2 = TRIAL / "_raw" / "_rejected" / "v2_202.webp"
    v1_raw = TRIAL / "_raw" / "_rejected" / "202_Spinosaurus_wide_raw.png"
    if v1.exists() and v2.exists():
        g202 = post[202]
        rev_card = f"""
  <div class="card" style="border-color:rgba(251,191,36,.45)">
    <h2>修訂歷程：id 202 棘龍（v1 → v2 → r24 重產×5 → 現行） <span class="id">審核回饋驅動：剪影包絡與佔圖規則逐步收緊</span></h2>
    <div class="imgs">
      <figure><img src="{b64_webp(v1)}"><figcaption>v1 初版　長高比 <b style="color:#fca5a5">{aspect_ratio(v1):.2f}:1</b>（長扁・超標）</figcaption></figure>
      <figure><img src="{b64_webp(v2)}"><figcaption>v2 收攏體態　長高比 {ar_span(aspect_ratio(v2))}・佔圖 58.5%（比例過但佔圖舊尺規）</figcaption></figure>
      <figure><img src="{b64_webp(TRIAL / '202.webp')}"><figcaption>現行（r24 新尺規）　長高比 {ar_span(g202['ratio'])}・佔圖 {g202['bbox_cov_pct']}%・趣味=踢腿</figcaption></figure>
      <figure><img src="{b64_thumb(v1_raw)}"><figcaption>v1 原圖</figcaption></figure>
    </div>
    <p class="meta">現行規則（全量適用 Phase 2）：剪影長高比介於 1:1.2–1.2:1（細長型分兩類收攏：蜥腳/原蜥腳「頸平低」、棘龍科/鱷/海爬「尾緊捲＋頭微抬＋四分之三視角」）｜本體佔圖 50–60%（55% 求解）｜趣味隨機要素（動作類取代姿勢、情緒類修飾演出）。r24 中間失敗成品（v3fail×3・v4fail×3・v5fail×2・v6fail×2・v7fail×1・v8fail×1）已歸檔於 _raw/_rejected/。</p>
  </div>"""
        cards.insert(SPEC_IDS.index(202) + 1, rev_card)

    npass = sum(1 for sid in SPEC_IDS if post[sid]["pass"])
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>風格A 試產報告（Phase 1・5 星級）</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Microsoft JhengHei","PingFang TC",sans-serif; background:#141021; color:#f3eefc;
         line-height:1.6; padding:28px 14px 60px; }}
  .wrap {{ max-width:1180px; margin:0 auto; }}
  h1 {{ text-align:center; font-size:25px; margin-bottom:4px;
       background:linear-gradient(90deg,#c084fc,#6ee7b7,#fbbf24); -webkit-background-clip:text;
       background-clip:text; color:transparent; }}
  .sub {{ text-align:center; color:#b9a6d9; font-size:13.5px; margin-bottom:20px; }}
  .banner {{ background:rgba(110,231,183,.08); border:1px solid rgba(110,231,183,.35); border-radius:12px;
            padding:14px 18px; margin-bottom:22px; font-size:14px; }}
  .banner b {{ color:#6ee7b7; }}
  .card {{ background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.10); border-radius:14px;
          padding:18px 20px; margin-bottom:20px; }}
  .imgs {{ display:flex; gap:22px; flex-wrap:wrap; margin-bottom:12px; }}
  figure {{ text-align:center; }}
  figure img {{ width:280px; height:280px; object-fit:contain; background:
    repeating-conic-gradient(#241d38 0% 25%, #1b1530 0% 50%) 0 0/24px 24px; border-radius:12px;
    border:1px solid rgba(255,255,255,.12); }}
  figcaption {{ font-size:12px; color:#b9a6d9; margin-top:6px; }}
  h2 {{ font-size:19px; margin-bottom:10px; }}
  .id {{ font-size:12px; color:#8b76ad; font-weight:400; margin-left:8px; }}
  .st {{ display:inline-block; font-size:13px; font-weight:800; border:1px solid; border-radius:999px; padding:0 10px; margin-right:6px; }}
  .s1 {{ color:#66bb6a; border-color:#66bb6a; }} .s2 {{ color:#42a5f5; border-color:#42a5f5; }}
  .s3 {{ color:#ffb300; border-color:#ffb300; }} .s4 {{ color:#ff7043; border-color:#ff7043; }}
  .s5 {{ color:#ab47bc; border-color:#ab47bc; }}
  table.spec {{ border-collapse:collapse; font-size:13px; width:100%; }}
  table.spec th {{ text-align:left; color:#e9d5ff; background:rgba(192,132,252,.12); padding:5px 10px;
                  border:1px solid rgba(255,255,255,.10); width:110px; white-space:nowrap; }}
  table.spec td {{ padding:5px 10px; border:1px solid rgba(255,255,255,.10); }}
  .gates {{ margin-top:10px; display:flex; flex-wrap:wrap; gap:6px; }}
  .ck {{ font-size:11.5px; border:1px solid; border-radius:999px; padding:1px 9px; }}
  .ck.ok {{ color:#6ee7b7; border-color:rgba(110,231,183,.5); }}
  .ck.bad {{ color:#fca5a5; border-color:rgba(252,165,165,.6); }}
  .meta {{ font-size:12px; color:#8b76ad; margin-top:8px; }}
  .sheet {{ display:flex; gap:14px; flex-wrap:wrap; }}
  .cell {{ text-align:center; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10);
          border-radius:10px; padding:10px 8px 8px; }}
  .cell img {{ width:118px; height:118px; object-fit:contain; margin:2px;
             background:repeating-conic-gradient(#241d38 0% 25%, #1b1530 0% 50%) 0 0/18px 18px;
             border-radius:8px; }}
  .lbl {{ font-size:12.5px; margin-top:6px; }}
  .foot {{ text-align:center; color:#8b76ad; font-size:12px; margin-top:16px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>風格A 試產報告（Phase 1・5 星級各 1 張）</h1>
  <div class="sub">Gemini 2.5 flash image・雙參考（伴伴風格A + 還原圖解剖）・種子化規格原樣執行｜2026-10-16</div>
  <div class="banner">
    審核重點：① 風格A 是否一致（緞面光澤、金琥珀眼、家族配色）　② 各星級階梯是否拉開（1★素體 → 5★傳說全套）
    ③ 皮膚是否<b>無塑膠感</b>且有污漬/沾黏　④ 物種辨識度　⑤ 遊戲規格門檻（{npass}/5 全過）
    ⑥ 全體剪影長高比 ≤1.2:1　⑦ 本體佔圖 50–60%　⑧ 趣味隨機要素（動作類取代姿勢/情緒類修飾演出）。<br>
    通過後即進 Phase 2：按星級切 6 批量產 139 張（每張 ≈US$0.04）。
  </div>
  <div class="card">
    <h2>總覽：150px 縮圖 / 轉灰 / 剪影（對應遊戲內圖鑑未收集與剪影猜謎）</h2>
    <div class="sheet">{''.join(sheet_cells)}
    </div>
  </div>
  {''.join(cards)}
  <div class="foot">Phase 1 試產｜累計 23 張生成 ≈US$0.92（r23 初版 5＋202 修訂 1＋r24 重產 5＋3＋3＋2＋2＋1＋1）｜規格表：styleA_gen_specs_report.html（139 筆・種子化）</div>
</div>
</body>
</html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"written: {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
