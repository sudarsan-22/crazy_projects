#!/usr/bin/env python3
"""
analyze_reel.py — objective measurements for one Reel video file.

Produces VERIFIED, machine-measured facts only (no opinions):
  - container/codec/resolution/aspect/fps/duration/bitrate/audio format
  - loudness (integrated LUFS, loudness range, true peak) via ffmpeg ebur128
  - leading black frames and audio onset (silence at start)
  - detected scene changes -> cuts, cuts per 10 s, shot lengths, time to first cut
  - hook frames at 0.0-3.0 s (+ safe-zone overlay versions)
  - contact sheet with one frame per detected shot
  - transition strips (7 frames, 0.1 s apart) around each cut
  - audio-sync proxy: share of cuts landing within ±100 ms of an audio onset
  - spec checks against the knowledge base (docs 07 and 06)

Usage:
  python3 -I tools/analyze_reel.py <video> <out_dir> [--scene 0.30]

Requires ffmpeg + ffprobe on PATH. Python stdlib only.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def probe(path):
    code, out, err = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path)])
    if code != 0:
        sys.exit(f"ffprobe failed: {err.strip()}")
    return json.loads(out)


def parse_rate(r):
    try:
        n, d = r.split("/")
        return float(n) / float(d) if float(d) else None
    except Exception:
        return None


def rotation_of(vs):
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            return int(float(sd["rotation"]))
    rot = (vs.get("tags") or {}).get("rotate")
    return int(rot) if rot else 0


def loudness(path):
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                     "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else err
    def grab(pattern):
        m = re.search(pattern, summary)
        return float(m.group(1)) if m else None
    return {
        "integrated_lufs": grab(r"I:\s+(-?[\d.]+) LUFS"),
        "loudness_range_lu": grab(r"LRA:\s+(-?[\d.]+) LU"),
        "true_peak_dbfs": grab(r"Peak:\s+(-?[\d.]+) dBFS"),
    }


def leading_silence(path):
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                     "-vn", "-af", "silencedetect=noise=-45dB:d=0.15",
                     "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", err)]
    if starts and starts[0] <= 0.05:
        return ends[0] if ends else None  # None => silent throughout
    return 0.0


def leading_black(path):
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-t", "3",
                     "-i", str(path), "-an",
                     "-vf", "scale=270:-2,blackdetect=d=0.04:pix_th=0.10",
                     "-f", "null", "-"])
    m = re.search(r"black_start:(-?[\d.]+) black_end:(-?[\d.]+)", err)
    if m and float(m.group(1)) <= 0.05:
        return float(m.group(2))
    return 0.0


def scene_cuts(path, threshold):
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                     "-an", "-vf",
                     f"scale=270:-2,select='gt(scene,{threshold})',showinfo",
                     "-f", "null", "-"])
    return [float(x) for x in re.findall(r"pts_time:(-?[\d.]+)", err)]


def audio_onsets(path, jump_db=6.0, floor_db=-40.0):
    """Approximate audio onsets: 50 ms RMS windows whose level jumps by
    >= jump_db over the previous window and is above floor_db."""
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
                     "-af", "aresample=8000,asetnsamples=400,astats=metadata=1:reset=1,"
                            "ametadata=print:key=lavfi.astats.Overall.RMS_level",
                     "-f", "null", "-"])
    times, levels, cur_t = [], [], None
    for line in err.splitlines():
        mt = re.search(r"pts_time:(-?[\d.]+)", line)
        if mt:
            cur_t = float(mt.group(1))
            continue
        ml = re.search(r"RMS_level=(-?[\d.]+|-inf)", line)
        if ml and cur_t is not None:
            v = ml.group(1)
            times.append(cur_t)
            levels.append(-120.0 if v == "-inf" else float(v))
    onsets = []
    for i in range(1, len(levels)):
        if levels[i] > floor_db and levels[i] - levels[i - 1] >= jump_db:
            if not onsets or times[i] - onsets[-1] > 0.15:
                onsets.append(times[i])
    return onsets


def transition_strip(path, t, out):
    start = max(t - 0.3, 0)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}",
         "-t", "0.7", "-i", str(path), "-vf",
         "fps=10,scale=180:-2,tile=7x1:padding=3:color=white",
         "-frames:v", "1", str(out)])


def extract_frame(path, t, out, overlay=False):
    vf = "scale=540:-2"
    if overlay:  # KB doc 07 §2 safe zones, scaled to frame size
        vf += (",drawbox=x=0:y=0:w=iw:h=ih*250/1920:color=red@0.35:t=fill"
               ",drawbox=x=0:y=ih-ih*380/1920:w=iw:h=ih*380/1920:color=red@0.35:t=fill"
               ",drawbox=x=iw-iw*140/1080:y=0:w=iw*140/1080:h=ih:color=orange@0.30:t=fill")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss",
         f"{t:.3f}", "-i", str(path), "-frames:v", "1", "-vf", vf, str(out)])


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    video, out_dir = Path(args[0]), Path(args[1])
    threshold = 0.30
    if "--scene" in args:
        threshold = float(args[args.index("--scene") + 1])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "frames").mkdir(exist_ok=True)

    info = probe(video)
    vs = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not vs:
        sys.exit("No video stream found.")
    w, h = int(vs["width"]), int(vs["height"])
    rot = rotation_of(vs)
    if abs(rot) in (90, 270):
        w, h = h, w
    fps = parse_rate(vs.get("avg_frame_rate", "0/0")) or parse_rate(vs.get("r_frame_rate", "0/0"))
    duration = float(info["format"].get("duration") or vs.get("duration") or 0)
    bitrate = int(info["format"].get("bit_rate") or 0)

    m = {
        "file": video.name,
        "container": info["format"].get("format_name"),
        "video_codec": vs.get("codec_name"),
        "width": w, "height": h,
        "aspect": round(w / h, 4) if h else None,
        "fps": round(fps, 3) if fps else None,
        "duration_s": round(duration, 2),
        "total_bitrate_mbps": round(bitrate / 1e6, 2) if bitrate else None,
        "color_transfer": vs.get("color_transfer"),
        "audio_present": au is not None,
        "audio_codec": au.get("codec_name") if au else None,
        "audio_sample_rate": int(au["sample_rate"]) if au and au.get("sample_rate") else None,
        "audio_channels": au.get("channels") if au else None,
    }
    if au:
        m.update(loudness(video))
        onset = leading_silence(video)
        m["audio_onset_s"] = round(onset, 2) if onset is not None else None
    m["leading_black_s"] = leading_black(video)

    cuts = [c for c in scene_cuts(video, threshold) if 0.05 < c < duration - 0.05]
    bounds = [0.0] + cuts + [duration]
    shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:]) if b - a > 0]
    m.update({
        "scene_threshold": threshold,
        "detected_cuts": len(cuts),
        "cut_times_s": [round(c, 2) for c in cuts],
        "cuts_per_10s": round(len(cuts) / duration * 10, 2) if duration else None,
        "avg_shot_s": round(sum(shots) / len(shots), 2) if shots else None,
        "median_shot_s": sorted(shots)[len(shots) // 2] if shots else None,
        "longest_shot_s": max(shots) if shots else None,
        "first_cut_s": round(cuts[0], 2) if cuts else None,
        "cuts_in_first_3s": len([c for c in cuts if c <= 3.0]),
    })

    # Audio-sync proxy: share of cuts within ±100 ms of an audio onset
    if au:
        onsets = audio_onsets(video)
        aligned = [c for c in cuts if any(abs(c - o) <= 0.10 for o in onsets)]
        m.update({
            "audio_onsets_detected": len(onsets),
            "onset_times_s": [round(o, 2) for o in onsets][:200],
            "cuts_on_audio_onsets": f"{len(aligned)}/{len(cuts)}",
            "cut_sync_ratio": round(len(aligned) / len(cuts), 2) if cuts else None,
        })

    # Transition strips: 7 frames (0.1 s apart) around each cut, max 20
    (out_dir / "transitions").mkdir(exist_ok=True)
    for i, c in enumerate(cuts[:20]):
        transition_strip(video, c, out_dir / "transitions" / f"cut_{i:02d}_{c:.2f}s.jpg")

    # Hook frames 0.0–3.0 s (+ safe-zone overlays)
    for i, t in enumerate([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]):
        if t < duration:
            extract_frame(video, t, out_dir / "frames" / f"hook_{i:02d}_{t:.1f}s.jpg")
            extract_frame(video, t, out_dir / "frames" / f"hook_{i:02d}_{t:.1f}s_safezone.jpg", overlay=True)

    # Contact sheet: middle frame of each shot (max 36)
    mids = [(a + b) / 2 for a, b in zip(bounds, bounds[1:]) if b - a > 0][:36]
    for i, t in enumerate(mids):
        extract_frame(video, t, out_dir / "frames" / f"shot_{i:03d}.jpg")
    if mids:
        cols = 6
        rows = math.ceil(len(mids) / cols)
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-framerate", "1", "-i", str(out_dir / "frames" / "shot_%03d.jpg"),
             "-vf", f"scale=180:-2,tile={cols}x{rows}:padding=4:color=white",
             "-frames:v", "1", str(out_dir / "contact_sheet.jpg")])

    # Spec checks (KB docs 06/07). PASS / WARN / FAIL with reason.
    checks = []
    def chk(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})
    chk("Aspect 9:16", "PASS" if m["aspect"] and abs(m["aspect"] - 9 / 16) < 0.01 else "FAIL", f"{w}x{h}")
    chk("Resolution ≥1080 wide", "PASS" if w >= 1080 else ("WARN" if w >= 720 else "FAIL"), f"width {w}")
    chk("Frame rate 23–60", "PASS" if m["fps"] and 23 <= m["fps"] <= 61 else "WARN", f"{m['fps']} fps")
    chk("≤180 s (recommendation-eligible)", "PASS" if duration <= 180 else "FAIL", f"{duration:.1f} s")
    chk("Audio present", "PASS" if au else "FAIL", "muted Reels are shown less (KB 01 §4)")
    if au:
        lufs, tp = m.get("integrated_lufs"), m.get("true_peak_dbfs")
        if lufs is not None:
            chk("Loudness ≈ −14 LUFS (−16…−9)", "PASS" if -16 <= lufs <= -9 else "WARN", f"{lufs} LUFS")
        if tp is not None:
            chk("True peak ≤ −1 dBTP", "PASS" if tp <= -1.0 else "WARN", f"{tp} dBTP")
        onset = m.get("audio_onset_s")
        chk("Audio starts ≤0.5 s", "PASS" if onset is not None and onset <= 0.5 else "WARN",
            "silent throughout" if onset is None else f"onset {onset:.2f} s")
    chk("No black/fade-in at start", "PASS" if m["leading_black_s"] <= 0.1 else "WARN", f"{m['leading_black_s']:.2f} s black")
    chk("SDR (not HDR)", "PASS" if m["color_transfer"] not in ("arib-std-b67", "smpte2084") else "WARN",
        f"transfer={m['color_transfer']}")
    m["checks"] = checks

    (out_dir / "metrics.json").write_text(json.dumps(m, indent=2))

    md = [f"# Measurements — {video.name}", "",
          "_Machine-measured by tools/analyze_reel.py. Scene cuts are approximate "
          "(fast motion/flashes can add false cuts; slow dissolves can be missed)._", "",
          "| Metric | Value |", "|---|---|"]
    for k in ["container", "video_codec", "width", "height", "fps", "duration_s",
              "total_bitrate_mbps", "color_transfer", "audio_codec", "audio_sample_rate",
              "audio_channels", "integrated_lufs", "loudness_range_lu", "true_peak_dbfs",
              "audio_onset_s", "leading_black_s", "detected_cuts", "cuts_per_10s",
              "avg_shot_s", "median_shot_s", "longest_shot_s", "first_cut_s",
              "cuts_in_first_3s", "audio_onsets_detected", "cuts_on_audio_onsets",
              "cut_sync_ratio"]:
        if k in m:
            md.append(f"| {k} | {m[k]} |")
    md += ["", f"Cut times (s): {', '.join(map(str, m['cut_times_s'])) or '—'}", "",
           "| Spec check | Status | Detail |", "|---|---|---|"]
    md += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks]
    (out_dir / "metrics.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
