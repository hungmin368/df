# -*- coding: utf-8 -*-
"""v7 試刊驗收報告：方法A（角色定裝＋去背合成）三階段成果、六格驗收與限制。
圖片全部內嵌（base64），報告可單檔攜出。輸出 working_db/reports/comic_v7_master_composite_report.html
"""
import base64
import io
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
MASTERS = HERE / "_raw" / "_masters"
BGS = HERE / "_raw" / "_bgs"
PAGE = HERE / "propA_ch01_page1_v7.png"
OUT = HERE.parents[1] / "reports" / "comic_v7_master_composite_report.html"

COLS = [(24, 906), (920, 1802)]
ROWS = [(148, 782), (794, 1428), (1440, 2074)]


def b64(im, max_w, q=84):
    im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def b64_file(path, max_w, q=84, flatten=False):
    im = Image.open(path)
    if flatten:
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    return b64(im, max_w, q)


PIPELINE = [
    ("Phase 1 定裝", "24 角色 × 基本六姿＋篇章嘉賓 19 隻",
     "298 張 src → rembg 去背 298/298；逐角色一致性 QC 全數 PASS，Rainer 以 001 重錨 6 張", "10-22～24"),
    ("Phase 2 背景", "4 張 4:3 空景（日出灘／沙面微距／大沙堡／夕陽海面）",
     "gemini-2.5-flash-image 一次成功、鏈式風格參考；無角色、無文字", "10-24"),
    ("Phase 3 合成", "1 頁 6 格、1826×2236",
     "cover-crop＋縮放／翻轉／底部錨定＋軟陰影＋暖金統一色調＋氣泡／銘牌", "10-24"),
    ("驗收", "送審頁 3 份",
     "定裝 298 卡、QC 24 帶 298 格、背景 4 卡；全部 0 破圖，成品逐格目視", "10-24"),
]

PANELS = [
    ("P1", "bg_beach_wide", "007 雷恩站姿、025 伴伴站姿",
     "旁白：傳說中，第一支尋龍探險隊的補給箱，／就沉睡在這片金沙灘——",
     "身高 0.52／0.28；旁白框在左上空景，不遮臉"),
    ("P2", "bg_sand_close", "026 伴伴嗅聞、008 雷恩蹲姿（水平翻轉）",
     "（嗅嗅……）／亮晶晶的味道！",
     "身高 0.40／0.44；泡尾落在伴伴頭頂，零重疊"),
    ("P3", "bg_beach_wide（翻轉）", "036 薩爾塔 p01、007 雷恩、025 伴伴",
     "薩爾塔：撿到～／最漂亮的項鍊！／雷恩：喂——那是我們／先發現的！",
     "身高 0.52／0.44／0.22；彩虹珠鍊＋碎墜補畫在胸口"),
    ("P4", "bg_sand_close", "008 雷恩蹲姿",
     "寶貝一定藏在／最氣派的沙堡裡！",
     "身高 0.58；沙上圓圈改畫在人物下層、右下沙面"),
    ("P5", "bg_sandcastle", "009 雷恩跪姿、027 伴伴歡呼、046 薩爾塔 p11（翻轉）",
     "分你一半！",
     "身高 0.36／0.30／0.50；沙堡在後，泡尾指薩爾塔"),
    ("P6", "bg_sunset_glow", "010 雷恩側身",
     "銘牌：碎片背面刻著——隊規第一條：／「永遠，把恐龍當朋友。」",
     "身高 0.86；彩虹碎片落在掌心，銘牌只壓腿部"),
]

CAST = [
    ("001", "cg_man_p01", "雷恩臉孔基準", "全 18 姿共用同一張臉/服裝鎖定"),
    ("007", "cg_man_stand", "雷恩・站姿", "P1/P3"),
    ("008", "cg_man_crouch", "雷恩・蹲姿", "P2（翻轉）/P4"),
    ("009", "cg_man_kneel", "雷恩・跪姿", "P5"),
    ("010", "cg_man_side", "雷恩・側身", "P6"),
    ("025", "cg_da_stand", "伴伴・站姿", "P1/P3"),
    ("026", "cg_da_sniff", "伴伴・嗅聞", "P2"),
    ("027", "cg_da_cheer", "伴伴・歡呼", "P5"),
    ("036", "cg_db_p01", "薩爾塔龍・正面", "P3"),
    ("046", "cg_db_p11", "薩爾塔龍・盤坐", "P5"),
]

BUBBLES = [
    ("P1", "無氣泡；左上旁白框", "零重疊"),
    ("P2", "右上圓泡，尾尖指向伴伴頭頂", "零重疊"),
    ("P3", "左上爆裂泡（雷恩）＋右上圓泡（薩爾塔）", "零重疊"),
    ("P4", "左上圓泡，尾尖指雷恩頭頂", "零重疊"),
    ("P5", "上方圓泡，尾尖指薩爾塔頭頂", "零重疊"),
    ("P6", "無氣泡；底部金色銘牌壓腿部", "不遮臉"),
]

BG_USE = {"bg_beach_wide": "P1／P3（P3 水平翻轉）", "bg_sand_close": "P2／P4",
          "bg_sandcastle": "P5", "bg_sunset_glow": "P6"}


def table(rows, head, row_head=True):
    tr = "".join(
        f"<tr>{'<th>' + r[0] + '</th>' if row_head else '<td>' + r[0] + '</td>'}"
        + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    th = "".join(f"<th>{h}</th>" for h in head)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


page_im = Image.open(PAGE)
page_b64 = b64_file(PAGE, 1400)

crops = []
for i, (r, c) in enumerate((r, c) for r in ROWS for c in COLS):
    crops.append(f"<figure><img src='{b64(page_im.crop((c[0], r[0], c[1], r[1])), 440)}'>"
                 f"<figcaption>P{i + 1}</figcaption></figure>")
panels_html = "".join(crops)

bgs_html = "".join(
    f"<figure class='bg'><img src='{b64_file(BGS / f'{n}.png', 380)}'>"
    f"<figcaption>{n}｜{BG_USE[n]}</figcaption></figure>" for n in BG_USE)

cast_html = "".join(
    f"<div class='cast'><span class='serial'>{s}</span>"
    f"<img src='{b64_file(MASTERS / f'{f}.png', 130, flatten=True)}'>"
    f"<b>{name}</b><small>{use}</small></div>" for s, f, name, use in CAST)

html = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<title>v7 試刊驗收報告・方法A 定裝＋去背合成</title>
<style>
body{{font-family:'Microsoft JhengHei',sans-serif;max-width:1080px;margin:0 auto;padding:28px;background:#faf7f0;color:#2c2620}}
h1{{font-size:26px;border-bottom:4px solid #c33;padding-bottom:8px;margin-bottom:6px}}
p.sub{{color:#6b6156;font-size:14px;margin:0 0 6px}}
h2{{font-size:20px;margin-top:34px;color:#7a2820}}
h3{{font-size:16px;margin:18px 0 6px}}
img{{max-width:100%;border:3px solid #2c2620;box-sizing:border-box;background:#fff}}
figure{{margin:14px 0}}figcaption{{font-size:13px;color:#6b6156;margin-top:4px}}
table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px}}
th,td{{border:1px solid #b9ad9c;padding:7px 9px;text-align:left;vertical-align:top}}
thead th{{background:#3a2f24;color:#fff}}
tbody th{{background:#efe7d8;white-space:nowrap}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.grid figure{{margin:0}}
.grid figcaption{{text-align:center;font-weight:bold}}
.bgs{{display:flex;gap:12px;flex-wrap:wrap}}
.bgs figure{{width:calc(25% - 9px);margin:0}}
.castrow{{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}}
.cast{{width:118px;text-align:center;font-size:12px;background:#fff;border:1px solid #d8cdbb;border-radius:8px;padding:6px 4px;position:relative}}
.cast img{{border:none;height:88px;width:auto}}
.cast b{{display:block;font-size:12px;line-height:1.35}}
.cast small{{color:#8a7f70;font-size:11px}}
.serial{{position:absolute;top:4px;left:4px;background:#c33;color:#fff;border-radius:4px;font-size:10px;padding:1px 5px}}
.note{{background:#fff8e0;border-left:5px solid #e0a400;padding:10px 14px;font-size:14px}}
.ok{{background:#eef8ea;border-left:5px solid #4a9e3f;padding:10px 14px;font-size:14px}}
code{{background:#efe7d8;padding:1px 5px;border-radius:4px;font-size:12.5px}}
ul{{font-size:14px;line-height:1.7}}
</style></head><body>
<h1>《彩虹羅盤與失落的探險隊》v7 試刊驗收報告</h1>
<p class="sub">方法A：角色定裝＋去背合成｜第 1 話第 1 頁（6 格）｜2026-10-24｜成品 1826×2236</p>
<p>本版不再讓模型「一次畫一整格」，而是把 298 張遊戲圖錨定的角色定裝去背後，
依分鏡座標貼進 4 張空景底圖，再用程式統一光線、陰影、色調並加上氣泡與旁白。
角色跨格不再漂移，畫面元素也能單獨替換重排。</p>

<h2>成品整頁</h2>
<figure><img src='{page_b64}'><figcaption>propA_ch01_page1_v7.png｜2×3 直排、6 格</figcaption></figure>

<h2>六格分格檢視</h2>
<div class="grid">{panels_html}</div>

<h2>三階段製程與驗收</h2>
{table(PIPELINE, ("階段", "產出", "做法與驗證", "日期"))}

<h2>六格設定與驗收結果</h2>
{table(PANELS, ("格", "背景", "使用定裝（流水號）", "對白／旁白", "配置與驗收"))}

<h2>角色一致性舉證（本篇使用張）</h2>
<p>雷恩所有姿勢共用同一張臉孔基準 001（cg_man_p01）；伴伴以遊戲圖 DFD-000 錨定；
薩爾塔龍以遊戲圖 9.webp 錨定並保留螺旋盤卷尾。以下流水號可直接對照
<code>_review_masters_v7.html</code> 與 <code>_qc_consistency.html</code>。</p>
<div class="castrow">{cast_html}</div>

<h2>Phase 2 背景底圖</h2>
<div class="bgs">{bgs_html}</div>

<h2>氣泡避臉驗證</h2>
{table(BUBBLES, ("格", "氣泡位置", "臉部重疊"))}
<p class="ok">六格氣泡（含尾尖）與旁白／銘牌皆未覆蓋任何角色臉部；P6 銘牌只壓雷恩腿部。</p>

<h2>已知限制</h2>
<ul>
<li>每個姿勢是固定定裝，表情不會隨對白變化；情緒靠姿勢、鏡頭與文字承擔。</li>
<li>角色與背景仍來自不同渲染，靠程式暖金調與接觸陰影拉近；近看仍可分辨 CG 角色與寫實沙灘。</li>
<li>背景構圖固定，跨格重複使用只能靠翻轉／裁切變化（P3 已水平翻轉 beach_wide）。</li>
<li>沙堡頂端生成了一面紅色小三角旗（提示詞原為無旗木桿），保留為畫面細節。</li>
<li>目前只完成第 1 話第 1 頁；其餘頁面需新增分鏡座標與必要的新背景。</li>
</ul>

<h2>重跑方式</h2>
<ul>
<li>背景：<code>python _gen_bgs_v7.py</code>（已存在則跳過）</li>
<li>資產檢查：<code>python _compose_v7.py --check</code></li>
<li>合成：<code>python _compose_v7.py</code> → <code>propA_ch01_page1_v7.png</code></li>
<li>送審頁：<code>python _make_master_review.py</code>、<code>python _make_qc_sheet.py</code>、<code>python _make_bg_review.py</code></li>
</ul>
</body></html>"""

OUT.write_text(html, encoding="utf-8")
print(f"saved {OUT} ({OUT.stat().st_size} bytes)")
