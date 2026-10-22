#!/usr/bin/env python3
"""Build iOS app icons (AppIcon.appiconset, no alpha) and launch splash from app_icon.png.

Run from the repository root so the relative paths below resolve.
"""
import json, os
from PIL import Image

SRC = os.path.join('working_db', 'generated_assets', 'icons', 'app_icon.png')
LOGO = os.path.join('game_db', 'assets', 'dinos_2', 'game_logo.png')
BG = (253, 253, 249)
OUT = os.path.join('working_db', 'generated_assets', 'icons')
APPICONSET = os.path.join(OUT, 'AppIcon.appiconset')

src = Image.open(SRC).convert('RGBA')
bbox = src.split()[3].getbbox()
art = src.crop(bbox)
print(f'source art bbox={bbox} -> {art.size}')

def flatten(art_img, box_px, canvas_px):
    im = Image.new('RGB', (canvas_px, canvas_px), BG)
    scaled = art_img.copy()
    scaled.thumbnail((box_px, box_px), Image.LANCZOS)
    im.paste(scaled, ((canvas_px - scaled.width) // 2, (canvas_px - scaled.height) // 2), scaled)
    return im

master = flatten(art, round(1024 * 0.78), 1024)
master.save(os.path.join(OUT, 'icon-1024-ios.png'), optimize=True)
print('icon-1024-ios.png', master.size, master.mode)

SIZES = [
    ('iphone', '20x20', '2x', 40), ('iphone', '20x20', '3x', 60),
    ('iphone', '29x29', '1x', 29), ('iphone', '29x29', '2x', 58), ('iphone', '29x29', '3x', 87),
    ('iphone', '40x40', '2x', 80), ('iphone', '40x40', '3x', 120),
    ('iphone', '60x60', '2x', 120), ('iphone', '60x60', '3x', 180),
    ('ipad', '20x20', '1x', 20), ('ipad', '20x20', '2x', 40),
    ('ipad', '29x29', '1x', 29), ('ipad', '29x29', '2x', 58),
    ('ipad', '40x40', '1x', 40), ('ipad', '40x40', '2x', 80),
    ('ipad', '76x76', '1x', 76), ('ipad', '76x76', '2x', 152),
    ('ipad', '83.5x83.5', '2x', 167),
    ('ios-marketing', '1024x1024', '1x', 1024),
]

os.makedirs(APPICONSET, exist_ok=True)
images, written = [], set()
for idiom, size, scale, px in SIZES:
    fname = f'icon-{px}.png' if idiom == 'ios-marketing' else f'icon-{size}@{scale}.png'
    if fname not in written:
        if px == 1024:
            img = master
        else:
            img = master.resize((px, px), Image.LANCZOS)
        img.save(os.path.join(APPICONSET, fname), optimize=True)
        written.add(fname)
    images.append({'idiom': idiom, 'size': size, 'scale': scale, 'filename': fname})

with open(os.path.join(APPICONSET, 'Contents.json'), 'w', encoding='utf-8') as f:
    json.dump({'images': images, 'info': {'author': 'xcode', 'version': 1}}, f, indent=2)
print(f'AppIcon.appiconset: {len(images)} entries, {len(written)} files')

logo = Image.open(LOGO).convert('RGBA')
lw = round(2732 * 0.7)
lh = round(logo.height * lw / logo.width)
splash = Image.new('RGB', (2732, 2732), BG)
lg = logo.resize((lw, lh), Image.LANCZOS)
splash.paste(lg, ((2732 - lw) // 2, (2732 - lh) // 2), lg)
splash.save(os.path.join(OUT, 'splash-2732.png'), optimize=True)
print('splash-2732.png', splash.size, splash.mode)
print('[OK]')
