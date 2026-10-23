# -*- coding: utf-8 -*-
"""v7-Phase3：方法A 漫畫頁合成器——背景底圖 × 去背定裝貼圖 × 對話泡後製。

輸入：_raw/_bgs/bg_*.png（Phase 2 產物）＋ _raw/_masters/cg_*.png（Phase 1 定裝，已去背）
輸出：propA_ch01_page1_v7.png（1826×2236，2×3 格直排版）
每格：cover_crop 背景 → 依 PANELS 規格貼上定裝（縮放/水平翻轉/底部錨定/軟陰影）
      → extras（薩爾塔項鍊光點、P4 沙上圓圈、P6 掌心碎片光）→ 對話泡／旁白銘牌。
氣泡位置為預估值，首跑後依實際構圖校準（比照 v5/v6 慣例：泡與尾不可蓋臉）。
用法：python _compose_v7.py [--suffix _x] [--check]
  --check  不合成，只驗證 PANELS 引用的定裝與背景檔案是否齊全（Phase 2 完成前背景不存在屬預期）
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
BGS = HERE / "_raw" / "_bgs"
MASTERS = HERE / "_raw" / "_masters"

SUFFIX = ""
CHECK = False
_args = sys.argv[1:]
_i = 0
while _i < len(_args):
    if _args[_i] == "--suffix":
        SUFFIX = _args[_i + 1]
        _i += 2
    elif _args[_i] == "--check":
        CHECK = True
        _i += 1
    else:
        _i += 1
OUT = HERE / f"propA_ch01_page1_v7{SUFFIX}.png"

FONT_BD = "C:/Windows/Fonts/msjhbd.ttc"
FONT_RG = "C:/Windows/Fonts/msjh.ttc"

INK = (32, 26, 20)
PAPER = (255, 252, 246)
NAVY = (30, 42, 88)
GOLD = (255, 214, 120)
RED = (206, 60, 52)

PW, PH = 1826, 2236
# 版面幾何（直排 2×3，餘白對齊 v6 慣例）
COLS = [(24, 906), (920, 1802)]
ROWS = [(148, 782), (794, 1428), (1440, 2074)]

# 定裝貼圖規格：(主檔, 目標高佔格高, 中心 x, 底部 y, 是否翻轉)
PANELS = {
    "P1": dict(bg="bg_beach_wide", actors=[("cg_man_stand", 0.52, 0.32, 0.98, False),
                                           ("cg_da_stand", 0.28, 0.52, 0.98, False)],
               extras=[], bubbles=[],
               caption=dict(x=(0.03, 0.55), y0=0.05,
                            text="傳說中，第一支尋龍探險隊的補給箱，／就沉睡在這片金沙灘——")),
    "P2": dict(bg="bg_sand_close", actors=[("cg_da_sniff", 0.40, 0.40, 0.99, False),
                                           ("cg_man_crouch", 0.44, 0.80, 0.99, True)],
               extras=[], bubbles=[dict(kind="round", x=(0.55, 0.99), y0=0.05, tail=(0.38, 0.60),
                                        text="（嗅嗅……）／亮晶晶的味道！")]),
    "P3": dict(bg="bg_beach_wide", flip_bg=True,
               actors=[("cg_db_p01", 0.52, 0.70, 1.03, False),
                       ("cg_man_stand", 0.44, 0.17, 0.97, False),
                       ("cg_da_stand", 0.22, 0.38, 0.98, False)],
               extras=[dict(kind="necklace", cx=0.70, cy=0.785, w=0.085, h=0.026)],
               bubbles=[dict(kind="round", x=(0.55, 0.99), y0=0.04, tail=(0.70, 0.52),
                             text="撿到～／最漂亮的項鍊！"),
                        dict(kind="burst", x=(0.02, 0.36), y0=0.04, tail=(0.19, 0.45),
                             text="喂——那是我們／先發現的！")]),
    "P4": dict(bg="bg_sand_close", actors=[("cg_man_crouch", 0.58, 0.44, 0.99, False)],
               extras=[dict(kind="circle", cx=0.68, cy=0.86, rx=0.22, ry=0.075)],
               extras_under=True,
               bubbles=[dict(kind="round", x=(0.06, 0.60), y0=0.04, tail=(0.45, 0.40),
                             text="寶貝一定藏在／最氣派的沙堡裡！")]),
    "P5": dict(bg="bg_sandcastle",
               actors=[("cg_man_kneel", 0.36, 0.19, 1.00, False),
                       ("cg_da_cheer", 0.30, 0.46, 1.00, False),
                       ("cg_db_p11", 0.50, 0.79, 1.03, True)],
               extras=[], bubbles=[dict(kind="round", x=(0.42, 0.96), y0=0.05, tail=(0.72, 0.60),
                                        text="分你一半！")]),
    "P6": dict(bg="bg_sunset_glow", actors=[("cg_man_side", 0.86, 0.50, 1.00, False)],
               extras=[dict(kind="shard", cx=0.365, cy=0.373, s=0.028, glow=1.7)],
               bubbles=[],
               caption=dict(x=(0.06, 0.94), y0=0.82, plaque=True,
                            text="碎片背面刻著——隊規第一條：／「永遠，把恐龍當朋友。」")),
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


def cover_crop(im, tw, th, vy=0.5, flip=False):
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    s = max(tw / im.width, th / im.height)
    im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im2.width - tw) // 2
    y = int((im2.height - th) * vy)
    return im2.crop((x, y, x + tw, y + th))


def paste_actor(panel, name, h_frac, cx_frac, by_frac, flip):
    im = Image.open(MASTERS / f"{name}.png").convert("RGBA")
    th = round(panel.height * h_frac)
    s = th / im.height
    im = im.resize((max(1, round(im.width * s)), th), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    cx = round(panel.width * cx_frac)
    by = round(panel.height * by_frac)
    px, py = cx - im.width // 2, by - im.height
    # 接觸陰影：腳底軟橢圓（光自左上，投影略偏右下）
    sh = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((px + im.width * 0.22, by - im.height * 0.045,
                                px + im.width * 0.99, by + im.height * 0.02), fill=(40, 28, 16, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    panel.alpha_composite(sh)
    panel.alpha_composite(im, (px, py))


def warm_grade(panel):
    """全格統一暖金調：輕微暖色覆蓋＋左上暖光，讓去背角色與寫實背景同一光場。"""
    w, h = panel.size
    ov = Image.new("RGBA", (w, h), (255, 186, 96, 16))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((-w * 0.55, -h * 0.65, w * 0.85, h * 0.70), fill=48)
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    light = Image.new("RGBA", (w, h), (255, 226, 168, 255))
    light.putalpha(glow)
    return Image.alpha_composite(Image.alpha_composite(panel, ov), light)


def draw_shard(d, cx, cy, s, rainbow=True, glow=2.6):
    for i, a in enumerate((70, 45)):
        rr = s * (glow - i * 0.9)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 216, 130, a))
    top = (cx, cy - s * 1.05)
    right = (cx + s * 0.62, cy - s * 0.12)
    bot = (cx + s * 0.18, cy + s)
    left = (cx - s * 0.58, cy - s * 0.05)
    cols = [(255, 236, 190), (255, 168, 176), (255, 214, 120), (150, 226, 210), (150, 176, 255)] \
        if rainbow else [(255, 238, 170)] * 5
    d.polygon([top, right, (cx, cy + s * 0.25)], fill=cols[0] + (245,))
    d.polygon([right, bot, (cx, cy + s * 0.25)], fill=cols[1] + (240,))
    d.polygon([top, (cx, cy + s * 0.25), left], fill=cols[2] + (240,))
    d.polygon([left, (cx, cy + s * 0.25), bot], fill=cols[3] + (240,))
    d.polygon([top, right, bot, left], outline=(255, 252, 235, 255), width=max(1, round(s * 0.10)))
    d.ellipse((cx - s * 0.16, cy - s * 0.60, cx + s * 0.10, cy - s * 0.30), fill=(255, 255, 250, 230))


def draw_extras(panel, extras):
    d = ImageDraw.Draw(panel, "RGBA")
    w, h = panel.size
    for e in extras:
        if e["kind"] == "glow":
            cx, cy, r = w * e["cx"], h * e["cy"], min(w, h) * e["r"]
            for i, a in enumerate((70, 50, 30)):
                rr = r * (1.6 - i * 0.4)
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=e["color"] + (a,))
            d.ellipse((cx - r * 0.35, cy - r * 0.5, cx + r * 0.35, cy + r * 0.5),
                      fill=(255, 246, 210, 235), outline=(180, 130, 60, 255), width=3)
        elif e["kind"] == "circle":
            d.ellipse((w * (e["cx"] - e["rx"]), h * (e["cy"] - e["ry"]),
                       w * (e["cx"] + e["rx"]), h * (e["cy"] + e["ry"])),
                      outline=(120, 86, 48, 220), width=6)
        elif e["kind"] == "shard":
            draw_shard(d, w * e["cx"], h * e["cy"], min(w, h) * e["s"], glow=e.get("glow", 2.6))
        elif e["kind"] == "necklace":
            cx, cy, nw, nh = w * e["cx"], h * e["cy"], w * e["w"], h * e["h"]
            colors = [(255, 120, 120), (255, 186, 92), (255, 232, 130), (146, 224, 156),
                      (130, 200, 255), (170, 150, 255)]
            n = 11
            for i in range(n):
                t = i / (n - 1)
                x = cx - nw / 2 + nw * t
                y = cy + nh * math.sin(math.pi * t)
                r = max(3.5, nw * 0.042)
                d.ellipse((x - r, y - r, x + r, y + r), fill=colors[i % len(colors)] + (245,),
                          outline=(90, 66, 30, 210), width=1)
            pd = (cx, cy + nh + nh * 0.55)
            for i, a in enumerate((80, 50)):
                rr = nh * (0.95 - i * 0.4)
                d.ellipse((pd[0] - rr, pd[1] - rr, pd[0] + rr, pd[1] + rr), fill=(255, 224, 140, a))
            draw_shard(d, pd[0], pd[1], nh * 0.55, glow=1.4)


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
        d.rounded_rectangle((bx, by, bx + bw2, by + bh2), radius=22, fill=(255, 255, 255, 246),
                            outline=INK, width=5)
        sx = min(max(tx, bx + 26), bx + bw2 - 26)
        top = by + bh2 - 2 if ty > by else by + 2
        d.polygon([(sx - 16, top - (2 if ty > by else -2)), (sx + 16, top - (2 if ty > by else -2)),
                   (tx, ty)], fill=(255, 255, 255, 246))
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
    bw2 = int((xb - xa) * w)
    bh2 = len(lines) * line_h + 34
    bx = x0 + int(xa * w)
    by = y0 + spec["y0"] * h
    if spec.get("plaque"):
        d.rounded_rectangle((bx, by, bx + bw2, by + bh2), radius=14, fill=(255, 243, 205, 242),
                            outline=(150, 108, 40), width=5)
        d.rounded_rectangle((bx + 8, by + 8, bx + bw2 - 8, by + bh2 - 8), radius=9,
                            outline=(201, 161, 90), width=3)
    else:
        d.rectangle((bx, by, bx + bw2, by + bh2), fill=(255, 255, 255, 244), outline=INK, width=5)
        d.rectangle((bx, by, bx + 12, by + bh2), fill=RED)
    yy = by + 17
    for ln in lines:
        d.text((bx + 40, yy), ln, font=f, fill=INK)
        yy += line_h


def check_assets():
    missing = []
    need_bg = []
    for key, spec in PANELS.items():
        if not (BGS / f"{spec['bg']}.png").exists():
            need_bg.append(f"{key}:{spec['bg']}")
        for name, *_ in spec["actors"]:
            if not (MASTERS / f"{name}.png").exists():
                missing.append(f"{key}:{name}")
    for f in (FONT_BD, FONT_RG):
        if not Path(f).exists():
            missing.append(f"font:{f}")
    print(f"定裝/字型缺漏: {missing or '無'}")
    print(f"尚待 Phase 2 產出背景: {need_bg or '無'}")
    return not missing


def main():
    page = Image.new("RGB", (PW, PH), PAPER)
    d = ImageDraw.Draw(page)
    band = [(28, 20), (PW, 20), (PW, 126), (0, 126)]
    d.polygon(band, fill=NAVY)
    d.line([(0, 126), (PW, 126)], fill=GOLD, width=5)
    f_t = font(FONT_BD, 52)
    f_s = font(FONT_RG, 26)
    title = "彩虹羅盤與失落的探險隊"
    sub = "第 1 話・沙灘上的第一片彩虹"
    d.text(((PW - d.textlength(title, font=f_t)) / 2, 24), title, font=f_t, fill=GOLD)
    d.text(((PW - d.textlength(sub, font=f_s)) / 2, 86), sub, font=f_s, fill=(225, 220, 205))
    badge_c = (PW - 96, 58)
    d.ellipse((badge_c[0] - 52, badge_c[1] - 32, badge_c[0] + 52, badge_c[1] + 32),
              fill=RED, outline=(255, 235, 210), width=3)
    f_b = font(FONT_BD, 22)
    d.text((badge_c[0] - d.textlength("試刊", font=f_b) / 2, badge_c[1] - 26), "試刊", font=f_b,
           fill=(255, 245, 230))
    d.text((badge_c[0] - d.textlength("v7", font=f_b) / 2, badge_c[1] + 2), "v7", font=f_b,
           fill=(255, 245, 230))

    order = ["P1", "P2", "P3", "P4", "P5", "P6"]
    for i, key in enumerate(order):
        spec = PANELS[key]
        col, row = COLS[i % 2], ROWS[i // 2]
        box = (col[0], row[0], col[1], row[1])
        tw, th = box[2] - box[0], box[3] - box[1]
        bg = Image.open(BGS / f"{spec['bg']}.png").convert("RGB")
        panel = cover_crop(bg, tw, th, flip=spec.get("flip_bg", False)).convert("RGBA")
        if spec.get("extras_under"):
            draw_extras(panel, spec["extras"])
        for name, hf, cx, by, fl in spec["actors"]:
            paste_actor(panel, name, hf, cx, by, fl)
        if not spec.get("extras_under"):
            draw_extras(panel, spec["extras"])
        panel = warm_grade(panel)
        page.paste(panel.convert("RGB"), (box[0], box[1]))
        d.rectangle(box, outline=INK, width=9)
        for b in spec["bubbles"]:
            draw_bubble(page, box, b)
        if spec.get("caption"):
            draw_caption(page, box, spec["caption"])

    f_f = font(FONT_RG, 21)
    foot = "恐龍快找 DragonFinder・故事試刊 彩虹羅盤篇 · 2026-10-23"
    d.text((30, PH - 52), foot, font=f_f, fill=(150, 138, 122))

    page.save(OUT)
    print(f"saved {OUT} {page.size[0]}x{page.size[1]}")


if __name__ == "__main__":
    if CHECK:
        raise SystemExit(0 if check_assets() else 1)
    main()
