# Extract the 5 named dinos from the 1024x1024 spec sheet (baked checkerboard
# bg, no alpha) into individual transparent PNGs named after their labels.
# Background = neutral (white/gray) pixels >=140, which also absorbs the soft
# shadows; label glyphs all measure <250px, and each dino is one connected
# comp of 44k-106k px, so keep comps >=250 and fill interior holes (teeth,
# eye whites) per comp. A filled hole that contains fg pixels of a DIFFERENT
# comp is a label-glyph pocket leaning on the dino (glyph strokes bridging two
# spines) and is unfilled again; eye whites only contain same-comp pixels.
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

SRC = r'C:\Users\hungm\AppData\Roaming\@sophclaw\desktop\attachments\d522123a-9457-4d16-ae4c-f54aad99c903\image.png'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# centroid anchors (full-image coords) to map comps to names
NAMES = {
    (190, 200): '小盜龍_Microraptor_001_1星',
    (760, 200): '迅猛龍_Velociraptor_041_2星',
    (465, 390): '劍龍_Stegosaurus_081_3星',
    (250, 760): '雷克斯暴龍_Tyrannosaurus_Rex_121_4星',
    (724, 695): '阿根廷龍_Argentinosaurus_161_1星',
}
# full-image rect (x0, y0, x1, y1) to subtract from a dino's mask: the trex
# crown spike is AA-glued to the stego label's first glyph (劍, x413-424,
# y543-557); cutting above y560 at x>=405 removes only the glued strokes and
# a ~3px sliver of spike tip (stego label chars beyond x431 are separate comps)
CUTS = {
    (250, 760): (405, 0, 485, 560),
}

a = np.array(Image.open(SRC).convert('RGB')).astype(int)
h, w = a.shape[:2]
mx = a.max(axis=2)
mn = a.min(axis=2)
fg = ~((mx - mn < 12) & (mn >= 140))

lab, n = ndimage.label(fg, structure=np.ones((3, 3)))
big = [i for i in range(1, n + 1) if int((lab == i).sum()) >= 250]
print(f'{len(big)} dino comps')

debug = Image.open(SRC).convert('RGB')
draw = ImageDraw.Draw(debug)
sheet_cells = []
kept = 0
for i in big:
    cy, cx = ndimage.center_of_mass(lab == i)
    best = min(NAMES, key=lambda k: (k[0]-cx)**2 + (k[1]-cy)**2)
    name = NAMES[best]
    mask = ndimage.binary_fill_holes(lab == i)
    holes = mask & ~(lab == i)
    foreign = holes & (lab != i) & (lab != 0)
    if foreign.any():
        hl, _ = ndimage.label(holes, structure=np.ones((3, 3)))
        bad = np.unique(hl[foreign])
        bad = bad[bad != 0]
        mask = mask & ~np.isin(hl, bad)
    cut = CUTS.get(best)
    if cut:
        cx0, cy0, cx1, cy1 = cut
        mask[cy0:cy1, cx0:cx1] = False
    ys, xs = np.where(mask)
    x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
    pad = 6
    x0 = max(0, x0-pad); y0 = max(0, y0-pad)
    x1 = min(w, x1+pad); y1 = min(h, y1+pad)
    sub_rgb = a[y0:y1, x0:x1].astype(np.uint8)
    sub_mask = mask[y0:y1, x0:x1]
    alpha = Image.fromarray((sub_mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.fromarray(sub_rgb).convert('RGBA')
    out.putalpha(alpha)
    out.save(os.path.join(OUT_DIR, name + '.png'))
    kept += 1
    print(f'{name}.png size={out.size} centroid=({cx:.0f},{cy:.0f})')
    draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=3)
    bgc = Image.new('RGBA', out.size, (255, 0, 255, 255))
    bgc.alpha_composite(out)
    sheet_cells.append(bgc.convert('RGB'))

assert kept == 5, f'expected 5 dinos, kept {kept}'
debug.save(os.path.join(OUT_DIR, '_extract_debug_boxes.png'))
cw = max(c.width for c in sheet_cells)
ch = max(c.height for c in sheet_cells)
cols = 3
rows = (len(sheet_cells)+cols-1)//cols
sheet = Image.new('RGB', (cols*cw, rows*ch), (30, 30, 30))
for idx, cell in enumerate(sheet_cells):
    sheet.paste(cell, ((idx % cols)*cw, (idx//cols)*ch))
sheet.save(os.path.join(OUT_DIR, '_extract_debug_sheet.png'))
print('debug images written')
