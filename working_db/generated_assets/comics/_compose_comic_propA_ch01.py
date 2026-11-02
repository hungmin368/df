# -*- coding: utf-8 -*-
"""合成方案A第1話漫畫頁：分格邊框＋標題列＋中文對話泡／旁白框"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
RAW = HERE / "_raw"
OUT = HERE / "propA_ch01_page1.png"

FONT_BD = "C:/Windows/Fonts/msjhbd.ttc"
FONT_RG = "C:/Windows/Fonts/msjh.ttc"

INK = (58, 44, 26)
PAPER = (255, 253, 248)
GOLD = (255, 217, 138)
CREAM = (255, 248, 230)

PW = 880            # 每格目標寬
GUT = 22            # 溝槽
BORDER = 6
TITLE_H = 130
FOOT_H = 56

BUBBLES = {
    2: [dict(x=(0.035, 0.42), y=(0.04, None), tail=(0.28, 0.47),
             text="薩爾塔龍寶寶：／亮晶晶的寶物！")],
    3: [dict(x=(0.38, 0.965), y=(0.035, None), tail=(0.64, 0.30),
             text="小探險家：喂——／那是我們先發現的！"),
        dict(x=(0.035, 0.36), y=(0.035, None), tail=(0.28, 0.30),
             text="薩爾塔龍寶寶：／最漂亮的項鍊～")],
    4: [dict(x=(0.46, 0.965), y=(0.035, None), tail=(0.53, 0.32),
             text="小探險家：寶貝一定藏在／最氣派的沙堡裡！")],
    5: [dict(x=(0.055, 0.40), y=(0.04, None), tail=(0.38, 0.52),
             text="伴伴：／耶——挖到了！"),
        dict(x=(0.64, 0.95), y=(0.04, None), tail=(0.83, 0.50),
             text="分你一半！")],
}
CAPTIONS = {
    1: "傳說中，第一支尋龍探險隊的補給箱，／就沉睡在這片金沙灘——",
    5: "碎片背面刻著——隊規第一條：／「永遠，把恐龍當朋友。」",
}
# 修補：模型偶發自畫的空對話泡（第3格）——以相鄰晴空貼圖蓋掉（src/dst 為面板比例矩形）
PATCHES = {
    2: [dict(src=(0.655, 0.095, 0.795, 0.265), dst=(0.485, 0.095, 0.625, 0.265))],
}

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(text, f, max_w, draw):
    lines = []
    for seg in text.split("／"):
        cur = ""
        for ch in seg:
            if draw.textlength(cur + ch, font=f) <= max_w or not cur:
                cur += ch
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
    return lines

def load_panels():
    ims = []
    for i in range(1, 7):
        p = RAW / f"propA_ch01_p{i}.png"
        if not p.exists():
            sys.exit(f"MISSING: {p}")
        ims.append(Image.open(p).convert("RGB"))
    return ims

def row_heights(ims):
    hs = []
    for a, b in ((0, 1), (2, 3), (4, 5)):
        pair = ims[a:a + 2]
        hs.append(min(round(im.height * PW / im.width) for im in pair))
    return hs

def fit_row(im, row_h):
    w = round(im.width * row_h / im.height)
    im = im.resize((w, row_h), Image.LANCZOS)
    if w > PW:
        x0 = (w - PW) // 2
        im = im.crop((x0, 0, x0 + PW, row_h))
    elif w < PW:
        canvas = Image.new("RGB", (PW, row_h), PAPER)
        canvas.paste(im, ((PW - w) // 2, 0))
        im = canvas
    return im

def draw_bubble(panel, spec):
    d = ImageDraw.Draw(panel, "RGBA")
    w, h = panel.size
    f = font(FONT_BD, 27)
    probe = ImageDraw.Draw(panel)
    x0f, x1f = spec["x"]
    max_w = int((x1f - x0f) * w) - 44
    lines = wrap(spec["text"], f, max_w, probe)
    line_h = 38
    bw = max(int(probe.textlength(ln, font=f)) for ln in lines) + 44
    bh = len(lines) * line_h + 30
    bx = int(x0f * w)
    by = int(spec["y"][0] * h)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=24, fill=(255, 255, 255, 244), outline=INK, width=3)
    tx, ty = int(spec["tail"][0] * w), int(spec["tail"][1] * h)
    cx = bx + bw // 2
    if ty > by + bh:
        ay = by + bh
        tri = [(cx - 16, ay - 2), (cx + 16, ay - 2), (tx, ty)]
    else:
        ay = by
        tri = [(cx - 16, ay + 2), (cx + 16, ay + 2), (tx, ty)]
    d.polygon(tri, fill=(255, 255, 255, 244))
    d.line([tri[0], tri[1]], fill=INK, width=3)
    d.line([tri[0], tri[2]], fill=INK, width=3)
    d.line([tri[1], tri[2]], fill=INK, width=3)
    y = by + 15
    for ln in lines:
        d.text((bx + 22, y), ln, font=f, fill=INK)
        y += line_h

def draw_caption(panel, text):
    d = ImageDraw.Draw(panel, "RGBA")
    w, h = panel.size
    f = font(FONT_RG, 28)
    probe = ImageDraw.Draw(panel)
    pad = 40
    lines = wrap(text, f, w - pad * 2 - 40, probe)
    line_h = 40
    bh = len(lines) * line_h + 26
    y0 = h - bh - 26
    d.rounded_rectangle((pad - 10, y0, w - pad + 10, h - 26), radius=12,
                        fill=(255, 248, 230, 236), outline=(201, 161, 90), width=3)
    y = y0 + 13
    for ln in lines:
        d.text((pad + 12, y), ln, font=f, fill=INK)
        y += line_h

def main():
    ims = load_panels()
    hs = row_heights(ims)
    page_w = PW * 2 + GUT * 3
    page_h = TITLE_H + FOOT_H + sum(h + BORDER * 2 for h in hs) + GUT * 4
    page = Image.new("RGB", (page_w, page_h), PAPER)
    d = ImageDraw.Draw(page)
    # 標題列
    for y in range(TITLE_H):
        t = y / TITLE_H
        c = (int(38 + 24 * t), int(50 + 22 * t), int(90 + 30 * t))
        d.line([(0, y), (page_w, y)], fill=c)
    f_t = font(FONT_BD, 52)
    f_s = font(FONT_RG, 27)
    title = "彩虹羅盤與失落的探險隊"
    sub = "第 1 話・沙灘上的第一片彩虹"
    tw = d.textlength(title, font=f_t)
    sw = d.textlength(sub, font=f_s)
    d.text(((page_w - tw) / 2, 14), title, font=f_t, fill=GOLD)
    d.text(((page_w - sw) / 2, 78), sub, font=f_s, fill=(235, 226, 205))
    tag = "試刊 vol.0"
    d.text((page_w - d.textlength(tag, font=f_s) - 24, 22), tag, font=f_s, fill=(190, 200, 235))
    # 分格
    y = TITLE_H + GUT
    idx = 0
    for r in range(3):
        row_h = hs[r]
        for c in range(2):
            im = fit_row(ims[idx], row_h)
            x = GUT + c * (PW + GUT)
            if idx in PATCHES:
                w, h = im.size
                for p in PATCHES[idx]:
                    sx0, sy0, sx1, sy1 = p["src"]
                    dx0, dy0, dx1, dy1 = p["dst"]
                    patch = im.crop((int(sx0 * w), int(sy0 * h), int(sx1 * w), int(sy1 * h)))
                    patch = patch.resize((int((dx1 - dx0) * w), int((dy1 - dy0) * h)), Image.LANCZOS)
                    patch = patch.filter(ImageFilter.GaussianBlur(1.2))
                    im.paste(patch, (int(dx0 * w), int(dy0 * h)))
            if idx in BUBBLES:
                for spec in BUBBLES[idx]:
                    draw_bubble(im, spec)
            if idx in CAPTIONS:
                draw_caption(im, CAPTIONS[idx])
            d.rounded_rectangle((x - BORDER, y - BORDER, x + PW + BORDER, y + row_h + BORDER),
                                radius=10, outline=INK, width=BORDER)
            page.paste(im, (x, y))
            idx += 1
        y += row_h + BORDER * 2 + GUT
    # 頁尾
    f_f = font(FONT_RG, 22)
    foot = "恐龍快找 DragonFinder・故事試刊彩虹羅盤篇 · 2026-10-22"
    d.text(((page_w - d.textlength(foot, font=f_f)) / 2, page_h - FOOT_H + 14), foot, font=f_f, fill=(163, 148, 131))
    page.save(OUT)
    print(f"saved {OUT} {page.size[0]}x{page.size[1]}")

if __name__ == "__main__":
    main()
