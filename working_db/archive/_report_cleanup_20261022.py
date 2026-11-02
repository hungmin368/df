# -*- coding: utf-8 -*-
"""One-off report consolidation for 2026-10-22.

Merges same-topic HTML reports into single self-contained pages while
preserving each source report's own CSS by scoping every selector to a
per-source section id. Source scripts are kept in IIFEs after the sections.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT, "working_db", "reports")

GROUPS = [
    {
        "out": "styleA_spec_report.html",
        "title": "風格A 規格、前置審查與雙後端比較",
        "subtitle": "整併自《批量生產規格書（定案版）》《生成規格表（139 筆）》《批量替換前置審查》《雙後端比較報告》",
        "note": "本報告是風格A 的規格與決策總集；最終 134 張批量成果見 <a href=\"styleA_phase2_report.html\">styleA_phase2_report.html</a>。",
        "sources": [
            ("styleA_batch_spec_report.html", "2026-10-16"),
            ("styleA_gen_specs_report.html", "2026-10-16"),
            ("styleA_swap_audit_report.html", "2026-10-16"),
            ("styleA_backend_compare_report.html", "2026-10-16"),
        ],
    },
    {
        "out": "intro_video_report.html",
        "title": "開場影片設計與交付（捉迷藏版）",
        "subtitle": "整併自《開場影片提示詞設計》與《伴伴開場動畫（捉迷藏版）交付驗證》",
        "note": "早期「蛋孵化・擬真森林」版本已被捉迷藏版取代；最終成品規格與提示詞以本報告為準。",
        "sources": [
            ("bban_intro_video_prompts_report.html", "2026-10-16"),
            ("bban_intro_video_delivery_report.html", "2026-10-16"),
        ],
    },
    {
        "out": "image_generation_tools_report.html",
        "title": "圖像生成工具調查與指揮力評估",
        "subtitle": "整併自《圖像生成 MCP 工具調查報告》與《圖片生成工具指揮力評估報告》",
        "note": "現行實戰管線與提示詞配方見 <code>working_db/docs/Imagegen_usage.md</code>。",
        "sources": [
            ("image_gen_mcp_report.html", "2026-10-15"),
            ("image_gen_tools_report.html", "2026-10-15"),
        ],
    },
    {
        "out": "ios_release_report.html",
        "title": "iOS 上架前置與收費方案",
        "subtitle": "整併自《Apple iOS App Store 上架前置報告》與《iOS 收費方案報告》",
        "note": "App Store Connect 中繼資料、隱私標籤、年齡分級與收費決策集中於本報告。",
        "sources": [
            ("apple_ios_store_prep_report.html", "2026-10-18"),
            ("ios_monetization_report.html", "2026-10-18"),
        ],
    },
    {
        "out": "publishing_plan_report.html",
        "title": "上架平台評估與任務清單",
        "subtitle": "整併自《上架平台評估報告》與《上架任務清單（第一／第二梯隊）》",
        "note": "2026-09-24 的舊版上架準備報告（尋龍高手名稱、單檔打包時代）已淘汰；最新 iOS 狀態見 <a href=\"ios_release_report.html\">ios_release_report.html</a>。",
        "sources": [
            ("game_publish_platforms_report.html", "2026-10-17"),
            ("publish_task_checklist_report.html", "2026-10-17"),
        ],
    },
    {
        "out": "backend_design_report.html",
        "title": "後端與龍塔留言設計",
        "subtitle": "整併自《後端實作報告：分數驗證與內購》與《龍塔關卡攻略留言 — 實現做法評估報告》",
        "note": "本報告為設計參考，後端尚未實作；目前遊戲仍以離線 localStorage 進度為主。",
        "sources": [
            ("backend_implementation_report.html", "2026-10-14"),
            ("dragon_tower_comments_report.html", "2026-10-13"),
        ],
    },
    {
        "out": "buddy_system_report.html",
        "title": "隨行系統驗證（自動排除與進階秘訣）",
        "subtitle": "整併自《隨行羈絆自動排除驗證報告》與《隨行閒聊進階秘訣驗證報告》",
        "note": "兩份報告皆為 2026-10-13 的實機驗證紀錄。",
        "sources": [
            ("buddy_auto_exclude_report.html", "2026-10-13"),
            ("buddy_tips_report.html", "2026-10-13"),
        ],
    },
    {
        "out": "tutorial_report.html",
        "title": "教學流程驗證（4×4 與固定盤面）",
        "subtitle": "整併自《4×4 教學步驟報告》與《第一次教學固定盤面驗證報告》",
        "note": "歷史驗證紀錄。現行教學已於 2026-10-21 改為「點擊畫面推進」，程式碼為最終準據。",
        "sources": [
            ("tutorial_4x4_report.html", "2026-10-13"),
            ("tutorial_fixed_board_report.html", "2026-10-14"),
        ],
    },
]

SHELL_CSS = """
:root{
  --page-bg:#0b1020; --panel:#111a2e; --line:rgba(148,163,184,.24);
  --text:#e8eefc; --muted:#9fb0d0; --accent:#7dd3fc; --accent2:#c084fc;
}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#172554 0%,transparent 60%),var(--page-bg);
  color:var(--text);font-family:"Microsoft JhengHei","PingFang TC","Noto Sans TC",sans-serif;line-height:1.7}
.page-head{max-width:1220px;margin:0 auto;padding:44px 20px 10px}
.kicker{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0 0 8px}
.page-head h1{margin:0 0 10px;font-size:30px;line-height:1.3;background:linear-gradient(90deg,#7dd3fc,#c084fc,#fbbf24);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.page-head .subtitle{margin:0 0 8px;color:#cbd5e1;font-size:14.5px}
.page-head .note{margin:0 0 14px;color:#fbbf24;font-size:13.5px}
.page-head .meta{margin:0;color:var(--muted);font-size:12.5px}
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px;margin:20px 0 6px}
.toc a{display:block;padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.04);
  color:#dbeafe;text-decoration:none;font-size:13px}
.toc a:hover{border-color:var(--accent);background:rgba(125,211,252,.10)}
main{max-width:1220px;margin:0 auto;padding:8px 20px 50px}
.src-block{margin:26px 0;border:1px solid var(--line);border-radius:16px;background:#0f172a;
  box-shadow:0 18px 50px rgba(0,0,0,.28);scroll-margin-top:14px}
.src{border-radius:0 0 15px 15px;overflow:hidden}
.src-meta{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:8px;align-items:center;
  padding:9px 14px;background:#101a30;border-bottom:1px solid var(--line);color:#cbd5e1;font-size:12px;
  border-radius:15px 15px 0 0}
.src-badge{display:inline-block;padding:2px 8px;border-radius:999px;background:rgba(125,211,252,.16);
  color:#bae6fd;font-weight:700;letter-spacing:.04em}
.src-meta code{color:#fde68a;background:rgba(0,0,0,.35);padding:1px 6px;border-radius:4px}
.foot{max-width:1220px;margin:0 auto;padding:0 20px 50px;color:var(--muted);font-size:12px;text-align:center}
@media print{.toc{display:none}.src{break-inside:auto;box-shadow:none}.src-meta{position:static}}
"""


def read_text(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def extract_report(path):
    s = read_text(path)
    title_m = re.search(r"<title[^>]*>(.*?)</title>", s, re.S | re.I)
    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else os.path.basename(path)
    styles = re.findall(r"<style[^>]*>(.*?)</style>", s, re.S | re.I)
    body_m = re.search(r"<body[^>]*>(.*?)</body>", s, re.S | re.I)
    body = body_m.group(1) if body_m else s
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", body, re.S | re.I)
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S | re.I)
    return {"title": title, "styles": styles, "body": body, "scripts": scripts}


def split_selectors(prelude):
    out, buf, depth = [], [], 0
    for ch in prelude:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def scope_css(css, scope):
    """Prefix all normal selectors with *scope*; keep at-rules sane."""
    out = []
    i, n = 0, len(css)
    while i < n:
        if css[i].isspace():
            out.append(css[i])
            i += 1
            continue
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(css[i:j])
            i = j
            continue
        j = i
        while j < n and css[j] not in "{};":
            j += 1
        if j >= n:
            out.append(css[i:])
            break
        prelude = css[i:j].strip()
        if css[j] == ";":
            out.append(css[i:j + 1])
            i = j + 1
            continue
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        block = css[j + 1:k - 1]
        low = prelude.lower()
        if low.startswith(("@media", "@supports", "@container", "@layer")):
            out.append(prelude + "{" + scope_css(block, scope) + "}")
        elif low.startswith(("@keyframes", "@-webkit-keyframes", "@font-face", "@page")):
            out.append(prelude + "{" + block + "}")
        elif low.startswith(("@import", "@charset", "@namespace")):
            out.append(prelude + ";")
        else:
            scoped = []
            for sel in split_selectors(prelude):
                sel = sel.strip()
                if not sel:
                    continue
                sl = sel.lower()
                if sl in ("html",):
                    continue
                if sl in ("body",) or sl.startswith("body:") or sl.startswith("body.") or sl.startswith("body["):
                    scoped.append(scope + sel[4:])
                elif sl == ":root":
                    scoped.append(scope)
                elif sl == "*":
                    scoped.append(scope + " *")
                else:
                    scoped.append(scope + " " + sel)
            if scoped:
                out.append(", ".join(scoped) + "{" + block + "}")
        i = k
    return "".join(out)


def build_group(group):
    sections, scoped_css, scripts, toc, used = [], [], [], [], set()
    for idx, (fname, date) in enumerate(group["sources"], 1):
        path = os.path.join(SRC_DIR, fname)
        if not os.path.exists(path):
            print("MISSING SOURCE:", fname)
            continue
        rep = extract_report(path)
        used.add(fname)
        sid = "src-%d" % idx
        scope = "#%s-body" % sid
        toc.append((sid, "%d. %s" % (idx, rep["title"])))
        for css in rep["styles"]:
            scoped_css.append(scope_css(css, scope))
        body = rep["body"]
        sections.append(
            '<div class="src-block" id="%s">\n'
            '<div class="src-meta"><span class="src-badge">來源 %d</span>'
            '<span>原報告：<code>%s</code></span><span>原日期：%s</span></div>\n'
            '<section class="src" id="%s-body">\n%s\n</section>\n</div>\n'
            % (sid, idx, fname, date, sid, body)
        )
        for sc in rep["scripts"]:
            sc = sc.strip()
            if sc:
                scripts.append("(function(){\n%s\n})();" % sc)
        # Keep images and tables inside the section from breaking the layout.
        scoped_css.append(
            "%s img{max-width:100%%;height:auto}\n%s table{max-width:100%%}\n"
            "%s header code,%s .hero code,%s .meta code{color:#7c2d12;background:#fef3c7}\n"
            % (scope, scope, scope, scope, scope)
        )

    toc_html = "\n".join('<a href="#%s">%s</a>' % (sid, t) for sid, t in toc)
    script_html = "\n".join("<script>\n%s\n</script>" % s for s in scripts)
    return """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s — 恐龍快找 DragonFinder</title>
<style>
%s
%s
</style>
</head>
<body>
<header class="page-head">
  <p class="kicker">DragonFinder Report Library</p>
  <h1>%s</h1>
  <p class="subtitle">%s</p>
  <p class="note">%s</p>
  <p class="meta">整併日期：2026-10-22 ・ 來源 %d 份 ・ 本報告保留原始內容與圖表，僅整併版面。</p>
  <nav class="toc">
%s
  </nav>
</header>
<main>
%s
</main>
<div class="foot">恐龍快找 DragonFinder ・ 報告整併（2026-10-22）</div>
%s
</body>
</html>
""" % (
        group["title"], SHELL_CSS, "\n".join(scoped_css), group["title"],
        group["subtitle"], group["note"], len(used), toc_html,
        "\n".join(sections), script_html,
    )


def main():
    for group in GROUPS:
        html = build_group(group)
        out_path = os.path.join(SRC_DIR, group["out"])
        io.open(out_path, "w", encoding="utf-8", newline="\n").write(html)
        print("WROTE %-42s %8d bytes  (%d sources)" % (group["out"], len(html.encode("utf-8")), len(group["sources"])))


if __name__ == "__main__":
    main()
