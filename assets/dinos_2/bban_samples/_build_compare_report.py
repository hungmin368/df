# -*- coding: utf-8 -*-
"""Build styleA_backend_compare_report.html (self-contained, zh-TW).

Reads: assets/dinos_2/compare/_post_report.json (4 tiles), _gen_specs.json row 260,
       _sophnet_prompt.txt, raw PNGs (for thumbnails), trial/260.webp (reference).
Writes: styleA_backend_compare_report.html in repo root.
"""
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).parent
ROOT = HERE.parents[2]
CMP = ROOT / "assets" / "dinos_2" / "compare"
OUT_HTML = ROOT / "styleA_backend_compare_report.html"

GEMINI_PROMPT_HEADER = "雙參考（IMAGE 1 伴伴風格圖＋IMAGE 2 還原圖）＋以下文字"

# per-backend qualitative notes (filled after visual inspection, zh-TW)
NOTES = {
    ("gemini", 1): "白底純淨、風格A 緞面質感到位；坐地開腿吃食物、小戰斧、微動效線、臉側與尾端髒污全部到位；"
                   "唯本抽尾巴向左平伸，剪影 1.23 微超標（0.03），其餘 10 閘全過。",
    ("gemini", 2): "同樣白底棚拍、緞面質感；尾捲收緊後剪影 1.16，11 閘全過。吃食物動作與戰斧清晰，"
                   "可直接作為合格 512 tile。",
    ("sophnet", 1): "要素大多有命中（吃餅乾、戰斧、金甲、臉側與尾端髒污、閃電動效線），剪影 1.07 一次過；"
                    "但背景變深綠桌面場景（無視純白棚拍指令），整體偏實體公仔攝影質感、臉部擬人化（人耳＋人臉頰），"
                    "去背後白暈 0.167 未過。",
    ("sophnet", 2): "換種子重抽仍為深綠背景（2/2 無視白底指令）；「骨甲紋」被演譯成骷髏印花、頭上多出龍角（解剖漂移）；"
                    "halo 0.1465 壓線過閘，但風格A 緞面質感與白底棚拍兩項明顯未命中，tile 風格與現行資產家族不一致。",
}
COST = {"gemini": "≈US$0.04／張", "sophnet": "≈¥0.25／張（Z-Image-Turbo 費率；qwen-image 以實際帳單為準）"}
MODEL = {"gemini": "gemini-2.5-flash-image", "sophnet": "qwen-image（SophNet 任務端點）"}
INPUT_FMT = {
    "gemini": "雙參考圖 inline base64（風格＋解剖）＋文字提示",
    "sophnet": "純文字提示＋中文負向詞（API 不收本機圖檔）",
}

CHECKS_ZH = [
    ("size", "尺寸 512"), ("rgba", "RGBA"), ("bbox_ok", "本體存在"),
    ("bbox_cov_50_60", "佔圖 50–60%"), ("ratio_1p2", "剪影 ≤1.2"),
    ("cov_opaque", "不透明覆蓋"), ("margins_4pct", "四邊邊距"),
    ("bottom_4_6pct", "底部貼齊"), ("body_ok", "單體完整"),
    ("no_halo", "無白暈"), ("size_kb", "檔重 ≤50KB"),
]


def b64_img(path: Path, max_px: int = 340, quality: int = 80) -> str:
    im = Image.open(path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def b64_file(path: Path) -> str:
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    spec = {r["id"]: r for r in json.loads(
        (HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]}[260]
    report = json.loads((CMP / "_post_report.json").read_text(encoding="utf-8"))
    by_raw = {r["raw"].split("_raw.")[0]: r for r in report}
    soph_prompt = (CMP / "_sophnet_prompt.txt").read_text(encoding="utf-8")

    sys.path.insert(0, str(HERE))
    import _gen_trial5 as G
    gem_prompt = G.build_prompt(spec)

    import _gen_sophnet_retry as R
    b_edit_prompt = (CMP / "_sophB_edit_prompt.txt").read_text(encoding="utf-8")
    RETRY_APPENDIX = ("Variant A 追加正向條款：\n" + R.REPTILE_FACE
                      + "\n\nVariant A 追加負向詞：" + R.NEG_EXTRA.lstrip(", ")
                      + "\n\nVariant B /image-edit 重繪提示詞全文：\n" + b_edit_prompt)

    rolls = [("gemini", 1, "gemini"), ("gemini", 2, "gem2"),
             ("sophnet", 1, "sophnet"), ("sophnet", 2, "soph2")]

    EXP_META = {
        "sophA": {
            "title": "SophNet 重試・Variant A（純文字強化）",
            "meta": "qwen-image｜任務端點｜seed 555001",
            "input": "強化版純文字提示（爬蟲臉正向條款）＋抗擬人負向詞",
        },
        "sophB": {
            "title": "SophNet 重試・Variant B（風格參考圖編輯）",
            "meta": "qwen-image｜/image-edit 編輯模式（images=伴伴2星圖 Pages URL）",
            "input": "參考圖 URL＋重繪提示詞＋抗擬人負向詞",
        },
    }
    exp_notes = {
        "sophA": "爬蟲臉條款見效——吻部、鼻尖鼻孔、恐龍嘴與尖牙全部到位，擬人臉消失，剪影 0.95、11 閘全過。"
                 "但深綠桌面背景依舊（純文字下 3/3 無視白底），公仔實拍質感未變；頭上仍有一隻粉紅大外耳——"
                 "根因確認：Style A 家族特徵「pink inner ears」在無參考圖時被字面化成外耳"
                 "（Gemini 有伴伴圖參考故詮釋正確），提示詞工程可解（不適用物種應移除該句）。",
        "sophB": "編輯模式確實繼承參考圖的白底與棚拍感——halo 0.037 全場最乾淨、11 閘全過；戰斧、髒污、骨甲紋也到位。"
                 "但「baby T-rex」被演成『人類嬰兒身體＋恐龍頭』的變裝概念，擬人化反而比純文字更重——"
                 "edit 模式放大的是參考圖的『嬰兒感』，不是只繼承風格。",
    }

    def card_html(title: str, meta: str, input_fmt: str, m: dict, note: str) -> str:
        badges = "".join(
            f'<span class="badge {"ok" if m["checks"][k] else "bad"}">{zh}</span>'
            for k, zh in CHECKS_ZH)
        thumb = b64_img(CMP / m["raw"])
        tile = b64_file(CMP / m["out"])
        return f"""
<section class="card">
  <h2>{title}
      <small>{esc(meta)}</small></h2>
  <div class="duo">
    <figure><img src="{thumb}" alt="raw"><figcaption>raw（{esc(input_fmt)}）</figcaption></figure>
    <figure><img src="{tile}" alt="tile"><figcaption>512 tile（{m['out']}，{m['kb']}KB）</figcaption></figure>
  </div>
  <div class="badges">{badges}</div>
  <table class="metrics">
    <tr><th>剪影長高比</th><td>{m['ratio']}{' ✅' if m['checks']['ratio_1p2'] else ' ❌（限 0.833–1.2）'}</td>
        <th>本體佔圖</th><td>{m['bbox_cov_pct']}%</td></tr>
    <tr><th>不透明覆蓋</th><td>{m['coverage']}%</td><th>白暈比</th><td>{m['halo']}</td></tr>
    <tr><th>連通元件</th><td>{m['components']}（主體 {m['main_pct']}%）</td>
        <th>最大雜點</th><td>{m['largest_stray_pct']}%</td></tr>
  </table>
  <p class="note">{esc(note)}</p>
</section>"""

    cards = []
    for backend, roll, key in rolls:
        m = by_raw[f"{key}_260"]
        cards.append(card_html(
            f"{'Gemini' if backend == 'gemini' else 'SophNet ImageGenerator'}・第 {roll} 抽",
            f"{MODEL[backend]}｜成本 {COST[backend]}",
            INPUT_FMT[backend], m, NOTES[(backend, roll)]))
    for key, em in EXP_META.items():
        m = by_raw[f"{key}_260"]
        cards.append(card_html(em["title"], em["meta"], em["input"],
                               m, exp_notes[key]))

    summary_rows = ""
    for backend, roll, key in rolls + [(None, None, "sophA"), (None, None, "sophB")]:
        m = by_raw[f"{key}_260"]
        label = (f"{'Gemini' if backend == 'gemini' else 'SophNet'} r{roll}"
                 if backend else EXP_META[key]["title"].split("・", 1)[1])
        summary_rows += (f"<tr><td>{label}</td>"
                         f"<td>{m['ratio']}</td><td>{m['bbox_cov_pct']}%</td>"
                         f"<td>{m['kb']}KB</td><td>{m['halo']}</td>"
                         f"<td class=\"{'ok' if m['pass'] else 'bad'}\">"
                         f"{'全過' if m['pass'] else '、'.join(k for k, v in m['checks'].items() if not v)}</td></tr>")
    ref_tile = b64_file(ROOT / "assets" / "dinos_2" / "trial" / "260.webp")

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>風格A 雙後端比較報告（SophNet ImageGenerator vs Gemini）</title>
<style>
body{{font-family:"Microsoft JhengHei",system-ui,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px}}
main{{max-width:1080px;margin:0 auto}}
h1{{color:#7dd3fc;text-align:center}} h2 small{{font-weight:400;font-size:.62em;color:#94a3b8}}
.banner{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:14px 18px;line-height:1.7;font-size:.95em}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px 20px;margin:18px 0}}
.duo{{display:flex;gap:18px;flex-wrap:wrap}} figure{{margin:0;text-align:center}}
figure img{{max-width:340px;border-radius:8px;background:#fff}} figcaption{{font-size:.85em;color:#94a3b8;margin-top:4px}}
.badge{{display:inline-block;border-radius:999px;padding:2px 10px;margin:2px;font-size:.8em}}
.badge.ok{{background:#052e16;color:#4ade80;border:1px solid #166534}}
.badge.bad{{background:#450a0a;color:#f87171;border:1px solid #7f1d1d}}
table{{border-collapse:collapse;width:100%;margin-top:10px;font-size:.92em}}
th,td{{border:1px solid #334155;padding:5px 10px;text-align:left}} th{{background:#0f172a;color:#93c5fd}}
td.ok{{color:#4ade80}} td.bad{{color:#f87171}}
.note{{background:#0f172a;border-left:4px solid #fbbf24;padding:8px 12px;border-radius:4px;font-size:.9em;line-height:1.6}}
details{{margin-top:10px}} summary{{cursor:pointer;color:#7dd3fc}}
pre{{white-space:pre-wrap;word-break:break-all;background:#0f172a;padding:10px;border-radius:8px;font-size:.8em;color:#cbd5e1}}
footer{{text-align:center;color:#64748b;font-size:.85em;margin-top:22px}}
</style></head><body><main>
<h1>風格A 雙後端比較報告<br><small style="font-size:.55em;color:#94a3b8">SophNet ImageGenerator vs Gemini（同一素材・同一要素要求）</small></h1>
<div class="banner">
<b>素材</b>：spec 列 id 260 霸王龍（4★・還原圖 {esc(spec['recon'])}・seed {spec['seed']}）。<br>
<b>同一組要素要求</b>：體色 {esc(spec['color_zh'])}、花紋 {esc(spec['pattern_zh'])}、表情 {esc(spec['expr_zh'])}、
趣味動作「{esc(spec['fun_zh'])}」取代姿勢（{esc(spec['pose_zh'])}）配件 {esc(spec['acc_zh'])}、
污漬（{'；'.join(s['zh'] for s in spec['stains'])}）、4★ 金甲裝備＋微動態效果線、風格A 緞面質感＋自然髒污。<br>
<b>遊戲規則閘</b>：剪影長高比 1:1.2–1.2:1、本體佔圖 50–60%（解算 55%）、512×512 RGBA WebP。<br>
<b>輸入差異（後端本質）</b>：Gemini 收雙參考圖（風格A 伴伴圖＋還原圖）；SophNet API 不收本機圖檔 → 純文字提示＋中文負向詞，
參考圖字樣改寫為純文字描述。每後端各抽 2 張（SophNet 換種子避免同圖）。
</div>
{''.join(cards)}
<section class="card"><h2>彙總對照</h2>
<table><tr><th>後端/輪次</th><th>剪影比</th><th>佔圖</th><th>檔重</th><th>白暈</th><th>未過閘</th></tr>
{summary_rows}
<tr><td>（參考）現行試產 260.webp</td><td>1.17</td><td>55.0%</td><td>38.3KB</td><td>0.0464</td>
<td class="ok">全過（r24 認證）</td></tr></table>
<figure style="margin-top:12px"><img src="{ref_tile}" style="max-width:220px" alt="ref">
<figcaption>r24 認證版（Gemini・同 spec 列）供對照</figcaption></figure>
</section>
<section class="card"><h2>結論與建議</h2>
<div class="note">
<b>1. 數據閘兩後端都能過</b>：第二抽雙方 11 閘全綠（Gemini 1.16／SophNet 1.03–1.07），剪影與佔圖規則對兩後端都可執行。<br>
<b>2. 風格A 一致性只有 Gemini 穩定命中</b>：白底棚拍、緞面質感、物種解剖三項，Gemini 2/2 命中；
SophNet qwen-image 2/2 無視純白背景、轉為實體公仔攝影風——數據閘測不到這一層，選後端必須看圖。<br>
<b>3. SophNet 重試（Variant A/B）結論</b>：純文字強化救回了爬蟲臉（擬人臉消失、0.95 全閘過），但白底 3/3 失守、
公仔實拍感不變，且「pink inner ears」家族特徵被字面化成粉紅大外耳（不適用物種應移除該句）；
參考圖編輯模式（/image-edit）繼承了白底（halo 0.037 全場最佳），卻把「baby」放大成人類嬰兒身體＋恐龍頭——擬人化反而加重。<br>
<b>4. 建議</b>：風格A 正式資產續走 Gemini 雙參考配方（每張 ≈US$0.04）。SophNet 若要再試，
最佳下一步是 Variant A 模式＋移除 pink inner ears 句＋白底指令前置加重＋多抽；
其定位仍是便宜備援／非風格A 素材線（qwen-image ≈¥0.25/張）。
</div>
</section>
<details><summary>Gemini 提示詞（{esc(GEMINI_PROMPT_HEADER)}）</summary><pre>{esc(gem_prompt)}</pre></details>
<details><summary>SophNet 提示詞（純文字改寫版＋負向詞：{esc('塑膠感, 硬塑料光澤, 乙烯基玩具感, 強反光, 模糊, 低解析度, 變形, 多餘的肢體, 多隻動物, 文字, 數字, 浮水印, 簽名, 邊框, 背景雜物')}）</summary><pre>{esc(soph_prompt)}</pre></details>
<details><summary>SophNet 重試強化（Variant A 追加條款＋Variant B 重繪提示詞全文）</summary><pre>{esc(RETRY_APPENDIX)}</pre></details>
<footer>Phase 1 附加實驗｜比較 4 張＋SophNet 重試 2 張（Gemini ×2 ≈US$0.08；SophNet ×4＋診斷 ×1）｜2026-10-16</footer>
</main></body></html>"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"OK -> {OUT_HTML.name} ({OUT_HTML.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
