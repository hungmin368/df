#!/usr/bin/env python3
"""Extract evenly-spaced frames from the intro video for visual verification."""
import sys
from pathlib import Path

import cv2

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VIDEO = Path(__file__).resolve().parent.parent.parent / "videos" / "intro_bban_hatch_720p.mp4"
OUTDIR = Path(__file__).resolve().parent / "_intro_frames"
N = 8

OUTDIR.mkdir(exist_ok=True)
cap = cv2.VideoCapture(str(VIDEO))
if not cap.isOpened():
    print("cannot open", VIDEO)
    sys.exit(1)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"frames={total} fps={fps:.2f} size={w}x{h} duration={total/fps:.2f}s")
for i in range(N):
    idx = int(total * (i + 0.5) / N)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if ok:
        out = OUTDIR / f"frame_{i:02d}_f{idx}.jpg"
        cv2.imwrite(str(out), frame)
        print("wrote", out.name)
cap.release()
