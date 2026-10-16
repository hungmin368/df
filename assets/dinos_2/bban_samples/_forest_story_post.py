#!/usr/bin/env python3
"""Post-production for the forest adventure film:
1. cv2-verify the 9 clips, extract 2 frames each into _forest_story_frames/
2. render the spoken line 「來吧，我們一起來恐龍快找」 as a subtitle overlay
   for the tail of s9 (AI text is unreliable -> we burn our own text, per the
   game.mp4 lesson) and a matching end card (text + logo, no photos inside)
3. build a 0.3s white-flash transition (used between s6 and s7)
4. concat s1..s6 + flash + s7 + s8 + s9(sub) + endcard into
   assets/intro_forest_story_720p.mp4 (1280x720, 24fps, x264 yuv420p)
"""
import subprocess
import sys
from pathlib import Path

import cv2
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
CLIPS = HERE / "_forest_story_clips"
FRAMES = HERE / "_forest_story_frames"
OUT = HERE.parent.parent / "intro_forest_story_720p.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FONT_BOLD = "C:/Windows/Fonts/msjhbd.ttc"
FONT_REG = "C:/Windows/Fonts/msjh.ttc"
LINE = "來吧，我們一起來恐龍快找"
LOGO = HERE.parent / "game_logo.png"  # assets/dinos_2/game_logo.png

W, H = 1280, 720


def run(cmd: list) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print("FFMPEG FAILED:", " ".join(cmd[:12]), "...")
        print(r.stderr[-1500:])
        raise SystemExit(1)


def verify_clips() -> list:
    clips = [CLIPS / f"s{i}.mp4" for i in range(1, 10)]
    for c in clips:
        cap = cv2.VideoCapture(str(c))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok, _ = cap.read()
        cap.release()
        print(f"{c.name}: {w}x{h} fps={fps:.2f} frames={n} dur={n / fps:.2f}s decode={ok} "
              f"size={c.stat().st_size}B")
        if not (ok and c.stat().st_size > 500_000):
            raise SystemExit(f"clip not usable: {c}")
    return clips


def extract_frames(clips: list) -> None:
    FRAMES.mkdir(exist_ok=True)
    for i, c in enumerate(clips, start=1):
        cap = cv2.VideoCapture(str(c))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for tag, idx in (("a", int(n * 0.30)), ("b", int(n * 0.72))):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok:
                p = FRAMES / f"s{i}_{tag}_f{idx}.jpg"
                cv2.imwrite(str(p), frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
        cap.release()
    print(f"frames -> {FRAMES}")


def render_subtitle() -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 58, index=0)
    bbox = d.textbbox((0, 0), LINE, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (W - tw) // 2, int(H * 0.80)
    pad = 18
    band = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (8, 12, 8, 130))
    img.paste(band, (x - pad, y - pad), band)
    d.text((x + 2, y + 2), LINE, font=font, fill=(0, 0, 0, 190))
    d.text((x, y), LINE, font=font, fill=(255, 252, 240, 255))
    p = HERE / "_forest_story_subtitle.png"
    img.save(p)
    print(f"subtitle -> {p}")
    return p


def render_endcard() -> Path:
    img = Image.new("RGB", (W, H), (10, 20, 14))
    d = ImageDraw.Draw(img)
    for i in range(H):  # vertical gradient
        t = i / H
        d.line([(0, i), (W, i)], fill=(int(10 + 18 * t), int(22 + 28 * t), int(16 + 18 * t)))
    big = ImageFont.truetype(FONT_BOLD, 76, index=0)
    sub = ImageFont.truetype(FONT_REG, 40, index=0)
    line = LINE
    bbox = d.textbbox((0, 0), line, font=big)
    x = (W - (bbox[2] - bbox[0])) // 2
    d.text((x + 3, 292), line, font=big, fill=(0, 0, 0))
    d.text((x, 289), line, font=big, fill=(255, 246, 214))
    tip = "恐龍快找 DragonFinder"
    bbox2 = d.textbbox((0, 0), tip, font=sub)
    x2 = (W - (bbox2[2] - bbox2[0])) // 2
    d.text((x2, 402), tip, font=sub, fill=(214, 178, 106))
    if LOGO.exists():
        lg = Image.open(LOGO).convert("RGBA")
        lw = 300
        lh = int(lg.height * lw / lg.width)
        lg = lg.resize((lw, lh), Image.LANCZOS)
        img.paste(lg, ((W - lw) // 2, 470), lg)
    p = HERE / "_forest_story_endcard.png"
    img.save(p)
    print(f"endcard -> {p}")
    return p


def build_final(clips: list, sub_png: Path, endcard: Path) -> None:
    # burned subtitle on s9 tail
    s9 = CLIPS / "s9_sub.mp4"
    run([FF, "-y", "-i", str(clips[8]), "-i", str(sub_png),
         "-filter_complex", f"[0:v][1:v]overlay=0:0:enable='gte(t,2.6)',format=yuv420p",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(s9)])
    # white flash
    flash = CLIPS / "flash.mp4"
    run([FF, "-y", "-f", "lavfi", "-i", "color=c=white:s=1280x720:d=0.3:r=24",
         "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(flash)])

    inputs = []
    for c in clips[:6]:
        inputs += ["-i", str(c)]
    inputs += ["-i", str(flash)]
    for c in clips[6:8]:
        inputs += ["-i", str(c)]
    inputs += ["-i", str(s9)]
    inputs += ["-loop", "1", "-t", "3.4", "-i", str(endcard)]

    parts = []
    for i in range(11):
        extra = ""
        if i == 0:
            extra = ",fade=t=in:st=0:d=0.6"
        if i == 10:
            extra = ",fade=t=out:st=2.4:d=1.0"
        parts.append(f"[{i}:v]scale=1280:720,setsar=1,fps=24,format=yuv420p{extra}[v{i}]")
    chain = (";".join(parts)
             + ";" + "".join(f"[v{i}]" for i in range(11)) + "concat=n=11:v=1:a=0[out]")

    run([FF, "-y", *inputs, "-filter_complex", chain, "-map", "[out]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)])

    cap = cv2.VideoCapture(str(OUT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ok, _ = cap.read()
    cap.release()
    print(f"FINAL: {OUT} ({OUT.stat().st_size} B) frames={n} fps={fps:.2f} "
          f"dur={n / fps:.2f}s decode={ok}")


def main() -> int:
    clips = verify_clips()
    extract_frames(clips)
    sub_png = render_subtitle()
    endcard = render_endcard()
    build_final(clips, sub_png, endcard)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
