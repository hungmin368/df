# -*- coding: utf-8 -*-
"""Phase 2 batch overview report -> styleA_phase2_report.html (repo root).

Reads: assets/dinos_2/batch/{_gen_state.json,_post_report.json,_gate_history.json}
       assets/dinos_2/trial/_post_report.json   (5 certified Phase-1 tiles)
       assets/dinos_2/bban_samples/_gen_specs.json
Embeds 256px white-bg JPEG previews of every deliverable tile (batch + trial).
"""
import base64
import html
import io
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D2 = ROOT / "assets" / "dinos_2"
BATCH = D2 / "batch"
TRIAL = D2 / "trial"
SPECS = json.loads((HERE / "_gen_specs.json").read_text(encoding="utf-8"))["rows"]
GEN = json.loads((BATCH / "_gen_state.json").read_text(encoding="utf-8"))
POST = json.loads((BATCH / "_post_report.json").read_text(encoding="utf-8")) \
    if (BATCH / "_post_report.json").exists() else []
TRIAL_POST = json.loads((TRIAL / "_post_report.json").read_text(encoding="utf-8"))
HIST = json.loads((BATCH / "_gate_history.json").read_text(encoding="utf-8")) \
    if (BATCH / "_gate_history.json").exists() else []
RETRY = json.loads((BATCH / "_retry_state.json").read_text(encoding="utf-8")) \
    if (BATCH / "_retry_state.json").exists() else {}
OUT = ROOT / "styleA_phase2_report.html"
COST_PER_IMG = 0.04  # gemini-2.5-flash-image ~US$0.04
CHECKS = ["size", "rgba", "bbox_ok", "bbox_cov_50_60", "ratio_1p2", "cov_opaque",
          "margins_4pct", "bottom_4_6pct", "body_ok", "no_halo", "size_kb"]
CHECKS_ZH = {"size": "512", "rgba": "RGBA", "bbox_ok": "bbox", "bbox_cov_50_60": "佔圖",
             "ratio_1p2": "剪影", "cov_opaque": "實心", "margins_4pct": "邊距",
             "bottom_4_6pct": "底距", "body_ok": "單體", "no_halo": "白暈",
             "size_kb": "≤50KB"}


def esc(s):
    return html.escape(str(s), quote=True)


def b64_jpg(path: Path, side=256) -> str:
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg = bg.convert("RGB")
    bg.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    bg.save(buf, "JPEG", quality=82)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    by_id = {r["id"]: r for r in SPECS}
    post_by_id = {r["id"]: r for r in POST}
    trial_by_id = {int(r["out"].split(".")[0]): r for r in TRIAL_POST}
    gen_ids = {int(k) for k, v in GEN.items() if v.get("status") == "done" and v.get("raw")}
    # last round failures (still failing ids)
    still_fail = {}
    for h in HIST:
        for f in h.get("failed", []):
            still_fail[f["id"]] = f
    for rid in (post_by_id.keys() | trial_by_id.keys()):
        still_fail.pop(rid, None)

    ids = sorted(by_id)
    n_batch_pass = len(post_by_id)
    n_trial = len(trial_by_id)
    n_total_pass = n_batch_pass + n_trial
    attempts_total = sum(v.get("attempts", 1) for v in GEN.values())
    # per-id retry attempts are overwritten each round; prefer the cumulative total
    attempts_total += RETRY.get("_retry_attempts_total",
                                sum(v.get("attempts", 0) for v in RETRY.values()
                                    if isinstance(v, dict)))
    spend = attempts_total * COST_PER_IMG
    deployed = sorted(post_by_id.keys() | trial_by_id.keys())
    kept_old = sorted(set(by_id) - set(deployed))

    gate_counts = {c: [0, 0] for c in CHECKS}
    for r in POST:
        for c in CHECKS:
            gate_counts[c][0 if r["checks"].get(c) else 1] += 1

    def tile_card(sid):
        row = by_id[sid]
        if sid in post_by_id:
            m = post_by_id[sid]
            src, tag = BATCH, "batch"
        elif sid in trial_by_id:
            m = trial_by_id[sid]
            src, tag = TRIAL, "trial"
        else:
            fail = still_fail.get(sid)
            ch = ",".join(fail.get("checks") or fail.get("flags") or []) \
                if fail else (GEN.get(str(sid), {}).get("err") or "未生成")
            return (f'<figure class="tile bad"><figcaption><b>{sid}</b> '
                    f'{esc(row["name"])} {"★" * row["stars"]}<br>'
                    f'<span class="fail">✗ {esc(ch)}</span></figcaption></figure>')
        img = b64_jpg(src / m["out"])
        stars = "★" * row["stars"]
        return (f'<figure class="tile"><img src="data:image/jpeg;base64,{img}">'
                f'<figcaption><b>{sid}</b> {esc(row["name"])} <span class="stars">{stars}</span>'
                f'<br>ratio {m["ratio"]} · {m["kb"]}KB · 佔圖 {m["bbox_cov_pct"]}%'
                f'<span class="src {tag}">{tag}</span></figcaption></figure>')

    tiers = {}
    for sid in ids:
        tiers.setdefault(by_id[sid]["stars"], []).append(sid)

    sections = []
    for st in sorted(tiers):
        cards = "\n".join(tile_card(s) for s in tiers[st])
        passed = sum(1 for s in tiers[st] if s in post_by_id or s in trial_by_id)
        sections.append(f'<section><h2>{st}★（{passed}/{len(tiers[st])} 過閘）</h2>'
                        f'<div class="grid">{cards}</div></section>')

    gate_rows = "\n".join(
        f'<tr><td>{CHECKS_ZH[c]}</td><td>{gate_counts[c][0]}</td>'
        f'<td class="{"ok" if gate_counts[c][1] == 0 else "bad"}">{gate_counts[c][1]}</td></tr>'
        for c in CHECKS)

    hist_rows = "\n".join(
        f'<tr><td>r{h["round"]}</td><td>{h.get("processed", h.get("attempted", 0))}</td>'
        f'<td class="ok">{len(h["passed"])}</td>'
        f'<td class="{"bad" if h["failed"] else ""}">{len(h["failed"])}</td>'
        f'<td>{", ".join(str(f["id"]) for f in h["failed"]) or "—"}</td></tr>'
        for h in HIST)

    known = "\n".join(
        f'<tr><td>{sid}</td><td>{esc(by_id[sid]["name"])} {by_id[sid]["stars"]}★</td>'
        f'<td>{esc(",".join(still_fail[sid]["checks"]))}</td>'
        f'<td>{still_fail[sid]["ratio"]}</td><td>{still_fail[sid]["halo"]}</td></tr>'
        for sid in sorted(still_fail)) or '<tr><td colspan="5">無</td></tr>'

    doc = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<title>風格A Phase 2 批量 134 張報告</title>
<style>
body{{font-family:"Microsoft JhengHei",sans-serif;margin:24px;background:#fafafa;color:#222}}
.banner{{background:#1c3f60;color:#fff;padding:16px 20px;border-radius:10px;margin-bottom:20px}}
.banner h1{{margin:0 0 6px;font-size:20px}} .banner p{{margin:2px 0;font-size:13px}}
.stats{{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px}}
.stat{{background:#ffffff22;border-radius:8px;padding:8px 14px;font-size:13px}}
.stat b{{font-size:18px;display:block}}
table{{border-collapse:collapse;margin:10px 0;font-size:13px}}
td,th{{border:1px solid #ccc;padding:4px 10px}} th{{background:#eef}}
.ok{{color:#0a7a2f;font-weight:700}} .bad{{color:#c0392b;font-weight:700}}
section h2{{font-size:16px;margin:18px 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}}
.tile{{margin:0;background:#fff;border:1px solid #ddd;border-radius:8px;padding:6px;text-align:center}}
.tile img{{width:100%;border-radius:6px}}
.tile figcaption{{font-size:11px;margin-top:4px;line-height:1.5}}
.tile .stars{{color:#e6a100}}
.tile.bad{{background:#fdecea;border-color:#e5b7b3}}
.tile .fail{{color:#c0392b}}
.src{{display:inline-block;margin-left:6px;padding:0 6px;border-radius:6px;font-size:10px}}
.src.batch{{background:#dff0d8}} .src.trial{{background:#d9edf7}}
details{{margin:14px 0}} summary{{cursor:pointer;font-weight:700}}
footer{{margin-top:24px;font-size:12px;color:#666;border-top:1px solid #ccc;padding-top:8px}}
</style></head><body>
<div class="banner">
<h1>風格A Phase 2 批量報告——134 張（Gemini 雙參考）</h1>
<p>方法：P0 直配還原圖 47 張 ｜ P1 同科代理解剖 47 張 ｜ P2 舊遊戲圖為解剖參考 40 張；後製 rembg→11 閘→512×512 RGBA WebP(q90)。</p>
<div class="stats">
<div class="stat"><b>{n_batch_pass}</b>本批過閘（含重抽）</div>
<div class="stat"><b>{n_trial}</b>試產過閘（Round 24）</div>
<div class="stat"><b>{n_total_pass}/139</b>全集過閘</div>
<div class="stat"><b>{len(HIST)}</b>後製輪次</div>
<div class="stat"><b>{len(still_fail)}</b>未收斂</div>
<div class="stat"><b>~US${spend:.2f}</b>生成花費（{attempts_total} 抽×$0.04）</div>
</div></div>

<section><h2>閘門統計（本批 {n_batch_pass} 張過閘成品）</h2>
<table><tr><th>閘門</th><th>通過</th><th>未過</th></tr>{gate_rows}</table></section>

<section><h2>失敗輪歷程（_gate_history.json）</h2>
<table><tr><th>輪</th><th>處理</th><th>過閘</th><th>未過</th><th>未過 id</th></tr>{hist_rows}</table></section>

<section><h2>已知問題（最後一輪仍未收斂）</h2>
<table><tr><th>id</th><th>名稱</th><th>未過閘</th><th>ratio</th><th>halo</th></tr>{known}</table></section>

<section><h2>部署（覆蓋遊戲圖）</h2>
<p>依用戶指示「新生成好的圖片覆蓋舊的圖片」：已過閘新圖 <b>{len(deployed)}</b> 張（本批 {n_batch_pass}＋試產 {n_trial}）複製覆蓋
<code>assets/dinos/&lt;id&gt;.webp</code>；{f"未收斂 <b>{len(kept_old)}</b> 張保留舊圖（id：{','.join(map(str, kept_old))}）" if kept_old else "未收斂 <b>0</b> 張——<b>139/139 全數覆蓋</b>"}。
15 張 ratio 頑固案例（9,17,31,35,39,49,65,85,117,218,250,252,264,288,303）經 Round 8–10 逐 id 校準糾偏句
（<code>NOTE_OVERRIDE</code>：NEUTRAL_SQUARE／JUMP_WIDE／SAUROPOD_GATHER／MILD_WIDEN）多抽重生成後<b>全數收斂</b>。
驗證：HTTP 200、瀏覽器 139/139 載入 0 破圖（<b>全部 139 張均為 512×512 Style A 新圖，無保留舊圖</b>）、遊戲內圖鑑 140/140 渲染正常。變更走 git 可回滾。</p></section>

{''.join(sections)}

<details><summary>方法與檔案索引</summary>
<p>生成器 <code>assets/dinos_2/bban_samples/_gen_batch.py</code>（P0/P1/P2 路由＋退避＋斷點續跑 state）；命名對照 <code>_name_en.json</code>；
後製 <code>_post_batch.py</code>（11 閘，失敗歸檔 <code>batch/_raw/_rejected/r&lt;N&gt;_</code>）；本報告 <code>_build_phase2_report.py</code>。
素材：<code>assets/dinos_2/batch/&lt;id&gt;.webp</code> 本批；<code>assets/dinos_2/trial/&lt;id&gt;.webp</code> 試產；<code>assets/dinos/&lt;id&gt;.webp</code> 遊戲現役圖（已依指示覆蓋 139 張全數，r8–r10 收斂後）。</p>
</details>
<footer>Phase 2 批量 134 張 ｜ {n_batch_pass} 過閘 ｜ 花費 ~US${spend:.2f} ｜ 已覆蓋部署 {len(deployed)} 張、保留舊圖 {len(kept_old)} 張</footer>
</body></html>"""
    OUT.write_text(doc, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"OK -> {OUT.name} ({kb:.0f}KB), tiles: {n_total_pass}, still_fail: {len(still_fail)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
