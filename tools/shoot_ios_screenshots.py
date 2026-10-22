#!/usr/bin/env python3
"""Shoot App Store review screenshots at Apple's exact pixel sizes via system Chrome."""
import os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://localhost:8917/game_db/index.html'
OUT = str(ROOT / 'working_db' / 'store' / 'ios' / 'screenshots')
DEVICES = [
    ('iphone-6_9', 440, 956, 3),    # -> 1320x2868
    ('iphone-6_5', 414, 896, 3),    # -> 1242x2688
    ('ipad-13',   1032, 1376, 2),   # -> 2064x2752
]

CLEANUP = """
document.body.classList.remove('splash-on','intro-video-on');
const iv=document.getElementById('intro-video'); if(iv) iv.style.display='none';
const sp=document.getElementById('splash'); if(sp) sp.style.display='none';
const st=document.getElementById('story-stage'); if(st) st.classList.remove('show');
"""

SHOTS = {
    '01-menu': CLEANUP,
    '02-game': CLEANUP + """
hide('ov-menu'); newRun(6);
""",
    '03-dex': CLEANUP + """
dexGot=new Set(allMonsWithCompanion().map(p=>p.id));
renderDexFull(); show('ov-dexfull');
""",
    '04-capture': CLEANUP + """
hide('ov-menu'); newRun(6);
const ms=allMonsWithCompanion();
const m=ms.find(x=>x.stars===4)||ms.find(x=>x.stars===3)||ms[1];
nmQueue.length=0; nmQueue.push(m); showNextNewMon();
""",
}

def prep_cells(page):
    page.wait_for_selector('#board .cell', timeout=15000)
    page.wait_for_timeout(400)
    idxs = [2, 5, 9, 12, 16, 21, 24, 29, 33]
    page.evaluate(
        "const cs=document.querySelectorAll('#board .cell');"
        + "".join(f"cs[{i}]&&cs[{i}].click();" for i in idxs)
    )
    page.wait_for_timeout(300)

def prep_dex(page):
    page.wait_for_selector('#dexfull-grid img', timeout=15000)
    page.evaluate("document.querySelectorAll('#dexfull-grid img').forEach(im=>{im.loading='eager';})")
    page.wait_for_timeout(2500)

def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        for name, w, h, dsf in DEVICES:
            ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
            page = ctx.new_page()
            page.route('**/sw.js', lambda r: r.abort())
            page.add_init_script("try{localStorage.setItem('dinodoku-story','{\"intro\":1,\"4\":1,\"5\":1}');}catch(e){}")
            page.goto(BASE, wait_until='load')
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(1200)
            for shot, script in SHOTS.items():
                page.evaluate(script)
                page.wait_for_timeout(1200)
                if shot == '02-game':
                    prep_cells(page)
                if shot == '03-dex':
                    prep_dex(page)
                if shot == '04-capture':
                    page.wait_for_timeout(600)
                fdir = os.path.join(OUT, name)
                os.makedirs(fdir, exist_ok=True)
                fpath = os.path.join(fdir, shot + '.jpg')
                page.screenshot(path=fpath, type='jpeg', quality=92)
                print(shot, name, fpath)
                if shot != '01-menu':
                    page.evaluate("location.reload()")
                    page.wait_for_timeout(1500)
            ctx.close()
        browser.close()
    print('[OK]')

if __name__ == '__main__':
    main()
