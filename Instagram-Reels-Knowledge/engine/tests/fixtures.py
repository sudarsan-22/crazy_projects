"""Synthetic fixtures with KNOWN ground truth (same approach that validated tools/analyze_reel.py).

    uv run --project engine python engine/tests/fixtures.py   # builds engine/tests/fixtures/*
"""
import json
import subprocess
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixtures"

TRUTH = {
    # 3 shots at 30 fps: cuts exactly at 2.000 s (frame 60) and 3.500 s (frame 105); 6.0 s long
    "cuts.mp4": {"cuts": [2.0, 3.5], "duration": 6.0},
    # variable frame rate: jittered timestamps, ~30 fps average
    "vfr.mp4": {"vfr": True, "frames": 120},
    # 120 BPM click track, first click at 0.0 s, 20 s long; downbeat accent every 4th beat
    "click120.wav": {"bpm": 120.0, "beat_period": 0.5, "first_beat": 0.0, "duration": 20.0},
    # landscape clip with a bright square moving left -> right (subject-tracking ground truth)
    "moving_subject.mp4": {"x_start": 0.1, "x_end": 0.9, "duration": 4.0},
    # vertical clip with speech-like tone bursts and a loud 'laugh' burst at 2.0-2.4 s
    "events.mp4": {"loud_burst": [2.0, 2.4], "duration": 5.0},
}


def ff(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def build():
    FIX.mkdir(parents=True, exist_ok=True)
    ff("-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30:duration=2",
       "-f", "lavfi", "-i", "mandelbrot=size=1080x1920:rate=30",
       "-f", "lavfi", "-i", "smptehdbars=size=1080x1920:rate=30:duration=2.5",
       "-f", "lavfi", "-i", "sine=frequency=330:duration=6",
       "-filter_complex", "[1:v]trim=duration=1.5,setpts=PTS-STARTPTS[m];[0:v][m][2:v]concat=n=3:v=1:a=0,format=yuv420p[v]",
       "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-shortest",
       FIX / "cuts.mp4")
    ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=4",
       "-vf", "settb=1/90000,setpts='(N/30+0.012*sin(N*1.7))/TB'", "-fps_mode", "passthrough",
       "-video_track_timescale", "90000", "-c:v", "libx264", "-crf", "23", FIX / "vfr.mp4")
    # click: 1 kHz 15 ms clicks every 0.5 s, downbeats (every 2 s) louder
    ff("-f", "lavfi", "-i",
       "aevalsrc='(if(lt(mod(t,0.5),0.015),0.5,0)+if(lt(mod(t,2),0.015),0.4,0))*sin(2*PI*1000*t)':s=48000:d=20",
       "-ac", "2", FIX / "click120.wav")
    # white square whose centre moves from x=192 (0.1) to x=1728 (0.9) over 4 s
    ff("-f", "lavfi", "-i", "color=c=0x202830:size=1920x1080:rate=30:duration=4",
       "-f", "lavfi", "-i", "color=c=white:size=240x240:rate=30:duration=4",
       "-filter_complex", "[0:v][1:v]overlay=x='192+t/4*(1536)-120':y=420,format=yuv420p[v]",
       "-map", "[v]", "-c:v", "libx264", "-crf", "20", FIX / "moving_subject.mp4")
    ff("-f", "lavfi", "-i", "color=c=0x334455:size=1080x1920:rate=30:duration=5",
       "-f", "lavfi", "-i",
       "aevalsrc='0.05*sin(2*PI*220*t)*lt(mod(t,0.6),0.35)+0.9*between(t,2.0,2.4)*sin(2*PI*600*t)*(0.6+0.4*sin(2*PI*9*t))':s=48000:d=5",
       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-ac", "2", FIX / "events.mp4")
    # long sources for the KB 32 §6.1 EDL example: S1 landscape 60 fps 20 s (moving subject + tone),
    # S2 vertical 30 fps 12 s. A visible frame counter makes freezes/cuts checkable by eye.
    if not (FIX / "S1.mp4").exists():
        ff("-f", "lavfi", "-i", "color=c=0x2a3340:size=1920x1080:rate=60:duration=20",
           "-f", "lavfi", "-i", "color=c=0xf0c040:size=260x260:rate=60:duration=20",
           "-f", "lavfi", "-i", "sine=frequency=220:duration=20",
           "-filter_complex", "[0:v][1:v]overlay=x='960+700*sin(2*PI*t/10)-130':y=410,"
           "drawtext=font='DejaVu Sans':text='S1 %{eif\\:t\\:d}.%{eif\\:mod(n\\,60)\\:d}':x=40:y=40:fontsize=60:fontcolor=white,format=yuv420p[v]",
           "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", FIX / "S1.mp4")
    if not (FIX / "S2.mp4").exists():
        ff("-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30:duration=12",
           "-f", "lavfi", "-i", "sine=frequency=440:duration=12",
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", FIX / "S2.mp4")
    (FIX / "truth.json").write_text(json.dumps(TRUTH, indent=2))
    return FIX


if __name__ == "__main__":
    print("fixtures in", build())
