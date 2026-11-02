#!/usr/bin/env python3
"""Post-production for the 4x4->5x5 level-clear cute short (story-lv4-video).

No subtitles and no endcard by design (user 2026-10-17: 不需要文字旁白).
1. cv2-verify s1..s4, extract 2 QC frames each into _story_lv4_frames/
2. trim each clip to exactly 5.0s, normalize 1280x720@24 yuv420p,
   guarantee an audio track (anullsrc pad if a clip ships silent),
   fade in on s1 / fade out on s4 (video+audio), concat -> assets/story_lv4_720p.mp4
"""
import subprocess
import sys
from pathlib import Path

import cv2
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
CLIPS = HERE / "_story_lv4_clips"
FRAMES = HERE / "_story_lv4_frames"
OUT = HERE.parent.parent / "videos" / "story_lv4_720p.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1280, 720
SEG = 5.0


def run(cmd: list) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print("FFMPEG FAILED:", " ".join(cmd[:12]), "...")
        print(r.stderr[-1500:])
        raise SystemExit(1)


def has_audio(p: Path) -> bool:
    r = subprocess.run([FF, "-hide_banner", "-i", str(p)],
                       capture_output=True, text=True, errors="replace")
    return "Audio:" in r.stderr


def verify_clips() -> list:
    clips = [CLIPS / f"s{i}.mp4" for i in range(1, 5)]
    for c in clips:
        cap = cv2.VideoCapture(str(c))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok, _ = cap.read()
        cap.release()
        print(f"{c.name}: {w}x{h} fps={fps:.2f} frames={n} dur={n / fps:.2f}s "
              f"decode={ok} audio={has_audio(c)} size={c.stat().st_size}B")
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


def build_final(clips: list) -> None:
    inputs: list = []
    vin: list = []
    ain: list = []
    idx = 0
    for c in clips:
        vin.append(idx)
        inputs += ["-i", str(c)]
        idx += 1
        if has_audio(c):
            ain.append(vin[-1])
        else:
            ain.append(idx)
            inputs += ["-f", "lavfi", "-t", "6", "-i", "anullsrc=r=48000:cl=stereo"]
            idx += 1
    parts = []
    for i in range(4):
        # delogo: platform stamps a "Happy Horse" brand mark bottom-right
        vf = (f"[{vin[i]}:v]trim=0:{SEG},setpts=PTS-STARTPTS,"
              "delogo=x=1140:y=668:w=135:h=42,"
              f"scale={W}:{H},setsar=1,fps=24,format=yuv420p")
        if i == 0:
            vf += ",fade=t=in:st=0:d=0.5"
        if i == 3:
            vf += f",fade=t=out:st={SEG - 0.8}:d=0.8"
        parts.append(vf + f"[v{i}]")
        af = (f"[{ain[i]}:a]atrim=0:{SEG},asetpts=PTS-STARTPTS,"
              "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo")
        if i == 0:
            af += ",afade=t=in:st=0:d=0.4"
        if i == 3:
            af += f",afade=t=out:st={SEG - 1.0}:d=1.0"
        parts.append(af + f"[a{i}]")
    chain = (";".join(parts)
             + ";" + "".join(f"[v{i}][a{i}]" for i in range(4))
             + "concat=n=4:v=1:a=1[outv][outa]")
    run([FF, "-y", *inputs, "-filter_complex", chain,
         "-map", "[outv]", "-map", "[outa]",
         "-c:v", "libx264", "-crf", "20", "-preset", "medium",
         "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(OUT)])
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
    build_final(clips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
