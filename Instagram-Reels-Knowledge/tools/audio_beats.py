#!/usr/bin/env python3
"""
audio_beats.py — approximate tempo, beat grid, strong hits and the "drop"
for an audio (or video) file, to plan beat-synced edits.

Method (stdlib only + ffmpeg):
  1. ffmpeg astats -> RMS level (dB) every 10 ms
  2. onset strength = positive change in level (half-wave rectified)
  3. tempo = autocorrelation peak of onset strength in 60–180 BPM
  4. beat phase = offset maximising onset strength on the grid
  5. strong hits = largest onset peaks; drop = largest 1 s energy jump

Usage:
  python3 -I tools/audio_beats.py <audio_or_video> [--fps 30] [--start S] [--dur S]

Output: tempo, frames per beat at the given fps, beat times (s + frame),
strong hits, candidate drop, and a coarse energy curve (every 0.5 s).
All values are ESTIMATES — confirm by ear before final cuts.
"""
import re
import subprocess
import sys

HOP = 0.01  # 10 ms


def levels(path, start=None, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-vn", "-af",
            "aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,asetnsamples=480,"
            "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level",
            "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    vals = []
    for line in err.splitlines():
        m = re.search(r"RMS_level=(-?[\d.]+|-inf|nan)", line)
        if m:
            v = m.group(1)
            vals.append(-100.0 if v in ("-inf", "nan") else max(float(v), -100.0))
    return vals


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    path = a[0]
    fps = float(a[a.index("--fps") + 1]) if "--fps" in a else 30.0
    start = float(a[a.index("--start") + 1]) if "--start" in a else None
    dur = float(a[a.index("--dur") + 1]) if "--dur" in a else None
    lv = levels(path, start, dur)
    if len(lv) < 300:
        sys.exit("Audio too short or unreadable (need >= 3 s).")
    n = len(lv)
    onset = [0.0] + [max(0.0, lv[i] - lv[i - 1]) for i in range(1, n)]
    # Smooth with a 5-tap triangle so onsets split across windows still align
    k = [1, 2, 3, 2, 1]
    sm = [sum(k[j] * onset[i + j - 2] for j in range(5) if 0 <= i + j - 2 < n) / 9 for i in range(n)]
    mean = sum(sm) / n
    o = [x - mean for x in sm]

    # Tempo via autocorrelation (60–180 BPM => lag 0.333–1.0 s)
    best_lag, best_val, scores = None, float("-inf"), {}
    for lag in range(int(0.333 / HOP), int(1.0 / HOP) + 1):
        s = sum(o[i] * o[i + lag] for i in range(n - lag)) / (n - lag)
        scores[lag] = s
        if s > best_val:
            best_lag, best_val = lag, s
    # Prefer a faster tempo when half the lag is nearly as strong (octave check)
    half = round(best_lag / 2)
    if half in scores and scores[half] > 0.8 * best_val:
        best_lag = half
    # Parabolic interpolation around the peak for sub-window precision
    frac = 0.0
    if best_lag - 1 in scores and best_lag + 1 in scores:
        y0, y1, y2 = scores[best_lag - 1], scores[best_lag], scores[best_lag + 1]
        den = y0 - 2 * y1 + y2
        if den != 0:
            frac = max(-0.5, min(0.5, 0.5 * (y0 - y2) / den))
    period = (best_lag + frac) * HOP
    bpm = 60.0 / period

    # Phase: offset with maximum summed onset on the grid
    best_off, best_sum = 0, float("-inf")
    steps = int(n * HOP / period)
    for off in range(int(round(period / HOP))):
        s = 0.0
        for k in range(steps + 1):
            i = int(round(off + k * period / HOP))
            if i >= n:
                break
            s += sm[i]
        if s > best_sum:
            best_off, best_sum = off, s
    beats = []
    t = best_off * HOP
    while t < n * HOP:
        beats.append(t)
        t += period

    # Strong hits: local maxima of onset, top 12, min 0.25 s apart
    peaks = sorted(((onset[i], i) for i in range(1, n - 1)
                    if onset[i] >= onset[i - 1] and onset[i] >= onset[i + 1] and onset[i] > 3.0),
                   reverse=True)
    hits = []
    for val, i in peaks:
        if all(abs(i - j) * HOP >= 0.25 for _, j in hits):
            hits.append((val, i))
        if len(hits) == 12:
            break
    hits.sort(key=lambda x: x[1])

    # Drop: largest rise of 1 s mean level vs the previous 1 s
    w = int(1.0 / HOP)
    best_drop, best_rise = None, float("-inf")
    for i in range(w, n - w):
        rise = sum(lv[i:i + w]) / w - sum(lv[i - w:i]) / w
        if rise > best_rise:
            best_rise, best_drop = rise, i
    off = start or 0.0

    def fmt(t):
        return f"{t + off:7.2f}s  (frame {round((t + off) * fps):5d} @ {fps:g}fps)"

    print(f"File: {path}")
    print(f"Analysed: {n * HOP:.1f} s" + (f" from {off:.2f} s" if off else ""))
    print(f"Estimated tempo: {bpm:.1f} BPM · beat = {period:.3f} s = {period * fps:.2f} frames @ {fps:g} fps")
    print("  (tempo may be half/double the musical feel — confirm by ear)")
    print("\nBeat grid (first 32):")
    for k, t in enumerate(beats[:32]):
        print(f"  beat {k + 1:2d}: {fmt(t)}")
    print("\nStrongest hits (candidate cut / impact points):")
    for val, i in hits:
        print(f"  {fmt(i * HOP)}  strength {val:.1f} dB")
    if best_drop is not None:
        print(f"\nCandidate drop (largest 1 s energy rise, +{best_rise:.1f} dB): {fmt(best_drop * HOP)}")
    print("\nEnergy curve (mean dB per 0.5 s):")
    step = int(0.5 / HOP)
    for i in range(0, n - step + 1, step):
        m = sum(lv[i:i + step]) / step
        bar = "#" * max(0, int((m + 60) / 2))
        print(f"  {i * HOP + off:6.1f}s {m:6.1f} dB {bar}")


if __name__ == "__main__":
    main()
