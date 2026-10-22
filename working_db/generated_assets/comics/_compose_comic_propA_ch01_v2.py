# -*- coding: utf-8 -*-
"""方案A第1話 v2 漫畫頁合成：少年漫畫風動態版面（斜格、平行四邊形格、滿版跨格、出血格）

版面（畫布 1826×2236）：
- 斜切標題帶（平行四邊形）＋紅色試刊徽章
- P1 全寬橫幅格（自動裁掉模型自畫黑框）
- P2 逆時針斜格 ｜ P3 平行四邊形格（左緣斜切）
- P4 全幅出血跨格（左右貼頁緣）＝震驚高潮
- P5 順時針斜格 ｜ P6 右下雙出血格＝結尾
- 少年風對話泡：圓角泡（粗框尖尾）＋爆裂泡（鋸齒），文字一律後製
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
RAW = HERE / "_raw"

PREFIX = "v2"
SUFFIX = ""
_args = sys.argv[1:]
_i = 0
while _i < len(_args):
    if _args[_i] == "--prefix":
        PREFIX = _args[_i + 1]
        _i += 2
    elif _args[_i] == "--suffix":
        SUFFIX = _args[_i + 1]
        _i += 2
    else:
        _i += 1
OUT = HERE / f"propA_ch01_page1_v2{SUFFIX}.png"

FONT_BD = "C:/Windows/Fonts/msjhbd.ttc"
FONT_RG = "C:/Windows/Fonts/msjh.ttc"

INK = (32, 26, 20)
PAPER = (255, 252, 246)
NAVY = (30, 42, 88)
NAVY_D = (22, 31, 66)
GOLD = (255, 214, 120)
CREAM = (255, 248, 230)
RED = (206, 60, 52)

PW, PH = 1826, 2236

# 版面幾何：(x0, y0, x1, y1)
P1 = (24, 148, 1802, 640)
P2 = (24, 664, 788, 1184)
P3 = (820, 652, 1802, 1184)   # 平行四邊形：左上角內縮 64px
P3_SLANT = 64
P4 = (0, 1208, 1826, 1610)    # 全幅出血
P5 = (24, 1638, 894, 2148)
P6 = (924, 1622, 1826, 2236)  # 右、下出血

BUBBLES = {
    "P2": [dict(kind="round", x=(0.40, 0.97), y0=0.05, tail=(0.72, 0.40),
                text="（嗅嗅……）／亮晶晶的味道！")],
    "P3": [dict(kind="round", x=(0.50, 0.98), y0=0.05, tail=(0.60, 0.32),
                text="撿到～／亮晶晶的寶物！")],
    "P4": [dict(kind="burst", x=(0.02, 0.34), y0=0.05, tail=(0.18, 0.36),
                text="喂——那是我們／先發現的！"),
           dict(kind="round", x=(0.42, 0.74), y0=0.10, tail=(0.55, 0.40),
                text="最漂亮的項鍊～")],
    "P5": [dict(kind="round", x=(0.42, 0.97), y0=0.05, tail=(0.50, 0.38),
                text="寶貝一定藏在／最氣派的沙堡裡！")],
    "P6": [dict(kind="burst", x=(0.02, 0.38), y0=0.05, tail=(0.20, 0.44),
                text="耶——挖到了！"),
           dict(kind="round", x=(0.68, 0.99), y0=0.20, tail=(0.65, 0.36),
                text="分你一半！")],
}
CAPTIONS = {
    "P1": dict(x=(0.03, 0.42), y0=0.06, text="傳說中，第一支尋龍探險隊的補給箱，／就沉睡在這片金沙灘——"),
    "P6": dict(x=(0.06, 0.94), y0=0.80, text="碎片背面刻著——隊規第一條：／「永遠，把恐龍當朋友。」", plaque=True),
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

def cover_crop(im, tw, th):
    s = max(tw / im.width, th / im.height)
    im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im2.width - tw) // 2
    y = (im2.height - th) // 2
    return im2.crop((x, y, x + tw, y + th))

def strip_dark_frame(im, thr=60):
    """裁掉模型自畫的黑框：逐邊掃描，整行/列逾半像素偏暗即視為框（可容忍少量亮色速線穿越）。"""
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    def dim_frac_col(x):
        return sum(1 for y in range(0, h, 3) if px[x, y] < thr) / (h // 3 + 1)

    def dim_frac_row(y):
        return sum(1 for x in range(0, w, 3) if px[x, y] < thr) / (w // 3 + 1)

    left = 0
    while left < w // 3 and dim_frac_col(left) > 0.5:
        left += 1
    right = w - 1
    while right > 2 * w // 3 and dim_frac_col(right) > 0.5:
        right -= 1
    top = 0
    while top < h // 3 and dim_frac_row(top) > 0.5:
        top += 1
    bottom = h - 1
    while bottom > 2 * h // 3 and dim_frac_row(bottom) > 0.5:
        bottom -= 1
    if left < right - 10 and top < bottom - 10:
        return im.crop((left, top, right + 1, bottom + 1))
    return im

def rot_corners(w, h, angle):
    """PIL rotate(angle) 之後，原矩形四角在新影像座標系的位置（未加 expand 平移前，相對中心）。"""
    th = math.radians(angle)
    pts = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((x * math.cos(th) + y * math.sin(th), -x * math.sin(th) + y * math.cos(th)))
    return pts

def paste_tilted(page, im, box, angle, border=9):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    m = 70
    im2 = cover_crop(im, bw + 2 * m, bh + 2 * m)
    rot = im2.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=PAPER)
    cx, cy = rot.width / 2, rot.height / 2
    inner = [(cx + px, cy + py) for px, py in rot_corners(bw, bh, angle)]
    mask = Image.new("L", rot.size, 0)
    ImageDraw.Draw(mask).polygon(inner, fill=255)
    clean = Image.new("RGB", rot.size, PAPER)
    clean.paste(rot, (0, 0), mask)
    ox, oy = round((x0 + x1) / 2 - rot.width / 2), round((y0 + y1) / 2 - rot.height / 2)
    page.paste(clean, (ox, oy))
    d = ImageDraw.Draw(page)
    abs_pts = [(px + ox, py + oy) for px, py in inner]
    for i in range(4):
        d.line([abs_pts[i], abs_pts[(i + 1) % 4]], fill=INK, width=border)

def paste_parallelogram(page, im, box, slant, border=9):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    im2 = cover_crop(im, w, h)
    poly = [(slant, 0), (w, 0), (w, h), (0, h)]
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    clean = Image.new("RGB", (w, h), PAPER)
    clean.paste(im2, (0, 0), mask)
    page.paste(clean, (x0, y0))
    d = ImageDraw.Draw(page)
    abs_pts = [(x0 + px, y0 + py) for px, py in poly]
    for i in range(4):
        d.line([abs_pts[i], abs_pts[(i + 1) % 4]], fill=INK, width=border)

def draw_bubble(page, box, spec):
    d = ImageDraw.Draw(page, "RGBA")
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    f = font(FONT_BD, 27)
    probe = ImageDraw.Draw(page)
    xa, xb = spec["x"]
    max_w = int((xb - xa) * w) - 52
    lines = wrap(spec["text"], f, max_w, probe)
    line_h = 38
    tw = max(int(probe.textlength(ln, font=f)) for ln in lines)
    th = len(lines) * line_h
    cx = x0 + int((xa + xb) / 2 * w)
    tx, ty = x0 + spec["tail"][0] * w, y0 + spec["tail"][1] * h
    pad_x, pad_y = 30, 22
    if spec["kind"] == "burst":
        rx, ry = tw / 2 + pad_x + 14, th / 2 + pad_y + 12
        by = y0 + spec["y0"] * h + ry
        pts = []
        n = 16
        for i in range(n * 2):
            ang = math.pi * i / n
            r_x = rx if i % 2 == 0 else rx * 0.74
            r_y = ry if i % 2 == 0 else ry * 0.68
            pts.append((cx + r_x * math.cos(ang), by + r_y * math.sin(ang)))
        d.polygon(pts, fill=(255, 255, 255, 246))
        for i in range(len(pts)):
            d.line([pts[i], pts[(i + 1) % len(pts)]], fill=INK, width=5)
        d.polygon([(cx - 15, by + ry - 4), (cx + 15, by + ry - 4), (tx, ty)], fill=(255, 255, 255, 246))
        d.line([(cx - 15, by + ry - 4), (tx, ty)], fill=INK, width=5)
        d.line([(cx + 15, by + ry - 4), (tx, ty)], fill=INK, width=5)
        yy = by - th / 2 + 6
        for ln in lines:
            d.text((cx - probe.textlength(ln, font=f) / 2, yy), ln, font=f, fill=INK)
            yy += line_h
    else:
        bw2 = tw + pad_x * 2
        bh2 = th + pad_y * 2 + 10
        bx = x0 + int(xa * w)
        by = y0 + spec["y0"] * h
        d.rounded_rectangle((bx, by, bx + bw2, by + bh2), radius=22, fill=(255, 255, 255, 246), outline=INK, width=5)
        sx = min(max(tx, bx + 26), bx + bw2 - 26)
        top = by + bh2 - 2 if ty > by else by + 2
        d.polygon([(sx - 16, top - (2 if ty > by else -2)), (sx + 16, top - (2 if ty > by else -2)), (tx, ty)],
                  fill=(255, 255, 255, 246))
        d.line([(sx - 16, top), (tx, ty)], fill=INK, width=5)
        d.line([(sx + 16, top), (tx, ty)], fill=INK, width=5)
        d.line([(sx - 16, top), (sx + 16, top)], fill=(255, 255, 255, 255), width=6)
        yy = by + pad_y - 2
        for ln in lines:
            d.text((bx + pad_x, yy), ln, font=f, fill=INK)
            yy += line_h

def draw_caption(page, box, spec):
    d = ImageDraw.Draw(page, "RGBA")
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    xa, xb = spec["x"]
    f = font(FONT_BD, 28)
    probe = ImageDraw.Draw(page)
    max_w = int((xb - xa) * w) - 76
    lines = wrap(spec["text"], f, max_w, probe)
    line_h = 40
    tw = max(int(probe.textlength(ln, font=f)) for ln in lines)
    bw2 = int((xb - xa) * w)
    bh2 = len(lines) * line_h + 34
    bx = x0 + int(xa * w)
    by = y0 + spec["y0"] * h
    if spec.get("plaque"):
        d.rounded_rectangle((bx, by, bx + bw2, by + bh2), radius=14, fill=(255, 243, 205, 242), outline=(150, 108, 40), width=5)
        d.rounded_rectangle((bx + 8, by + 8, bx + bw2 - 8, by + bh2 - 8), radius=9, outline=(201, 161, 90), width=3)
    else:
        d.rectangle((bx, by, bx + bw2, by + bh2), fill=(255, 255, 255, 244), outline=INK, width=5)
        d.rectangle((bx, by, bx + 12, by + bh2), fill=RED)
    yy = by + 17
    for ln in lines:
        d.text((bx + 40, yy), ln, font=f, fill=INK)
        yy += line_h

def main():
    page = Image.new("RGB", (PW, PH), PAPER)
    d = ImageDraw.Draw(page)

    # 斜切標題帶
    band = [(28, 20), (PW, 20), (PW, 126), (0, 126)]
    d.polygon(band, fill=NAVY)
    d.line([(0, 126), (PW, 126)], fill=GOLD, width=5)
    d.polygon([(28, 20), (PW, 20), (PW, 30), (30, 30)], fill=NAVY_D)
    f_t = font(FONT_BD, 52)
    f_s = font(FONT_RG, 26)
    title = "彩虹羅盤與失落的探險隊"
    sub = "第 1 話・沙灘上的第一片彩虹"
    tw = d.textlength(title, font=f_t)
    d.text(((PW - tw) / 2, 24), title, font=f_t, fill=GOLD)
    sw = d.textlength(sub, font=f_s)
    d.text(((PW - sw) / 2, 86), sub, font=f_s, fill=(225, 220, 205))
    badge_c = (PW - 96, 58)
    d.ellipse((badge_c[0] - 52, badge_c[1] - 32, badge_c[0] + 52, badge_c[1] + 32), fill=RED, outline=(255, 235, 210), width=3)
    f_b = font(FONT_BD, 22)
    d.text((badge_c[0] - d.textlength("試刊", font=f_b) / 2, badge_c[1] - 26), "試刊", font=f_b, fill=(255, 245, 230))
    d.text((badge_c[0] - d.textlength("vol.0", font=f_b) / 2, badge_c[1] + 2), "vol.0", font=f_b, fill=(255, 245, 230))

    def load(n):
        im = Image.open(RAW / f"propA_ch01_{PREFIX}_p{n}.png").convert("RGB")
        return strip_dark_frame(im) if n == 1 else im

    paste_plain = cover_crop(load(1), P1[2] - P1[0], P1[3] - P1[1])
    page.paste(paste_plain, (P1[0], P1[1]))
    d.rectangle((P1[0], P1[1], P1[2], P1[3]), outline=INK, width=9)

    paste_tilted(page, load(2), P2, -2.2)
    paste_parallelogram(page, load(3), P3, P3_SLANT)
    p4 = cover_crop(load(4), P4[2] - P4[0], P4[3] - P4[1])
    page.paste(p4, (P4[0], P4[1]))
    d.line([(0, P4[1]), (PW, P4[1])], fill=INK, width=9)
    d.line([(0, P4[3]), (PW, P4[3])], fill=INK, width=9)
    paste_tilted(page, load(5), P5, 2.0)
    p6 = cover_crop(load(6), P6[2] - P6[0], P6[3] - P6[1])
    page.paste(p6, (P6[0], P6[1]))
    d.line([(P6[0], P6[1]), (P6[2], P6[1])], fill=INK, width=9)
    d.line([(P6[0], P6[1]), (P6[0], P6[3])], fill=INK, width=9)

    for key, box in (("P2", P2), ("P3", P3), ("P4", P4), ("P5", P5), ("P6", P6)):
        for spec in BUBBLES.get(key, []):
            draw_bubble(page, box, spec)
    draw_caption(page, P1, CAPTIONS["P1"])
    draw_caption(page, P6, CAPTIONS["P6"])

    f_f = font(FONT_RG, 21)
    foot = "恐龍快找 DragonFinder・故事試刊彩虹羅盤篇 · 2026-10-22"
    fw = d.textlength(foot, font=f_f)
    d.text(((24 + 894 - fw) / 2, 2172), foot, font=f_f, fill=(150, 138, 122))

    page.save(OUT)
    print(f"saved {OUT} {page.size[0]}x{page.size[1]}")

if __name__ == "__main__":
    main()
