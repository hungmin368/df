# -*- coding: utf-8 -*-
"""寫實人類風格變體選擇報告（自足單檔：圖片全 base64 內嵌）

素材：_raw/kidstyle_{film,photo,gamecg,paint}_p2_sophnet.png（SophNet 產出）
      ＋ _raw/propA_ch01_v4_p2.png（遭否決的 v4 混搭版，供對照）。
輸出：working_db/reports/kid_style_variants_report.html
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"
REPORT = HERE.parent.parent / "reports" / "kid_style_variants_report.html"

PANEL_W = 760
JPEG_Q = 85

DATE = "2026-10-22"
BACKEND = "SophNet ImageGenerator・Wan2.6-T2I（任務端點純文生圖）"


def to_data_uri(path: Path) -> str:
    im = Image.open(path).convert("RGB")
    if im.width > PANEL_W:
        im = im.resize((PANEL_W, round(im.height * PANEL_W / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


VARIANTS = [
    ("film", "電影實拍",
     "意圖：35mm 電影攝影機單格、菲林顆粒、好萊塢 CG 合成。實測觀察：暖金色電影調光、"
     "淺景深有到位，但男孩仍偏 3D 動畫電影感，並非真正的底片實拍質感。"),
    ("photo", "攝影寫真",
     "意圖：85mm 人像鏡頭雜誌級攝影。實測觀察：四者中最有「照片感」——奶油散景、真實陰影、"
     "膚質與布料細節貼近攝影；恐龍如收藏玩具立在沙灘上。"),
    ("gamecg", "3A 遊戲 CG",
     "意圖：遊戲過場動畫、PBR 高階 CG 人類。實測觀察：Pixar 級 3D 動畫 CG 質感，皮膚與毛髮"
     "細緻、比例可愛化；男孩與玩具風恐龍共用同一套打光，風格最統一。"),
    ("paint", "寫實油畫插畫",
     "意圖：電影海報級傳統油畫插畫。實測觀察：全畫面可見油畫筆觸（天空寬筆、鱗片高光手繪感），"
     "男孩寫實但帶手繪溫度；與遊戲的 3D 玩具風反差最大。"),
]


def main() -> None:
    cards = []
    for vid, name, desc in VARIANTS:
        path = RAW / f"kidstyle_{vid}_p2_sophnet.png"
        if not path.exists():
            sys.exit(f"missing image: {path}")
        cards.append(f"""
    <section class="card">
      <h2>變體 {vid}：{name}</h2>
      <img src="{to_data_uri(path)}" alt="{name}">
      <p class="desc">{desc}</p>
    </section>""")

    v4 = RAW / "propA_ch01_v4_p2.png"
    v4_html = ""
    if v4.exists():
        v4_html = f"""
    <section class="card rejected">
      <h2>對照 A：v4 混搭寫實（已否決，Gemini 產出）</h2>
      <img src="{to_data_uri(v4)}" alt="v4">
      <p class="desc">前一版嘗試：真人男孩＋3D 玩具恐龍的直接混搭。您已表示不喜歡，
      列於此僅供與下方四個新選項對照。</p>
    </section>"""

    edit2509 = RAW / "kidstyle_film_p2_sophnet_edit2509.png"
    edit_html = ""
    if edit2509.exists():
        edit_html = f"""
    <section class="card rejected">
      <h2>對照 B：Qwen-Image-Edit-2509 編輯模型（非寫實，僅供後端對照）</h2>
      <img src="{to_data_uri(edit2509)}" alt="edit2509">
      <p class="desc">同一格、同一「電影實拍」提示詞改用編輯模型（帶伴伴參考圖）的輸出：
      恐龍鎖定成功，但「100% 實拍」指令被完全無視，整格被統一成 3D 卡通風——
      人類寫實化失敗，因此四個變體改以純文生圖模型 Wan2.6-T2I 產出。</p>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>寫實人類風格變體選擇報告</title>
<style>
  body {{ font-family: "Microsoft JhengHei", "PingFang TC", sans-serif; margin: 0;
         background: #1a1d24; color: #e8e8ea; }}
  .wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 60px; }}
  h1 {{ font-size: 26px; border-bottom: 2px solid #7c5cff; padding-bottom: 10px; }}
  .meta {{ color: #9aa0ab; font-size: 13px; margin-bottom: 24px; line-height: 1.7; }}
  .card {{ background: #232732; border-radius: 12px; padding: 20px; margin: 26px 0; }}
  .card.rejected {{ opacity: .75; border: 1px dashed #a33; }}
  .card img {{ width: 100%; border-radius: 8px; display: block; }}
  .desc {{ line-height: 1.8; font-size: 14px; }}
  .note {{ background: #2a2f3d; border-left: 4px solid #7c5cff; padding: 12px 16px;
           border-radius: 6px; font-size: 14px; line-height: 1.8; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>寫實人類風格變體選擇報告</h1>
  <p class="meta">日期：{DATE}｜分鏡：提案A 第一章 P2（沙灘上的第一片彩虹・發現彩虹水晶）
  ｜後端：{BACKEND}<br>
  背景：v4 混搭寫實版遭否決後，以「同一格分鏡 × 四種真人渲染流派」重新試產供挑選。
  恐龍全程維持角色鎖定（紫身＋紫點、金黃角刺、粉紫→暖橘漸層翅膜、爬蟲臉條款），
  四個變體的恐龍設計均一致命中。</p>
  {v4_html}{edit_html}{"".join(cards)}
  <div class="note">
    <b>下一步</b>：請從上方四個變體中挑選一個（或指出想混搭／調整的方向）。選定後將以該風格
    重新產出全部六格並組版整頁。若四者都不滿意，也可以指明問題點（例如「男孩再年輕一點」、
    「背景再卡通一點」），我會帶著修正重試。
  </div>
</div>
</body>
</html>
"""
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(html, encoding="utf-8")
    print(f"OK -> {REPORT} ({REPORT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
