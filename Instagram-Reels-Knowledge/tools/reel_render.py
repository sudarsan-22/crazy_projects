#!/usr/bin/env python3
"""
reel_render.py — render a finished Reel from a JSON edit decision list (EDL)
with a single video encode from the ORIGINAL clips (originals are never modified).

Usage:  python3 -I tools/reel_render.py <edl.json> [--draft]

EDL (paths relative to the EDL file; assets/ also resolved from the KB root):
{
  "output": "../renders/v1.mp4",
  "fps": 30, "width": 1080, "height": 1920, "crf": 17,
  "loudness_lufs": -16,                       # -16 when music is added in-app, -14 if baked in
  "segments": [
    {"src": "../source/clip.mp4", "in": 1.20, "out": 3.80,
     "speed": 1.0,                            # 0.5 = half speed; >1 faster
     "interpolate": false,                    # minterpolate for slow-mo beyond source fps
     "fit": "crop",                           # crop (fill) | blur (fit + blurred background)
     "focus_x": 0.5, "focus_y": 0.5,          # crop focus (0..1)
     "grade": "moviemode",                    # moviemode | reality | none | raw ffmpeg filter string
     "zoom": [1.0, 1.06],                     # linear zoom over the segment
     "punches": [{"at": 0.6, "scale": 1.12, "dur": 0.5}],
     "shakes":  [{"at": 0.6, "dur": 0.13, "px": 14}],
     "freeze_end": 0.0,                       # hold last frame (seconds)
     "audio": "keep", "gain_db": 0,           # keep | mute
     "transition_in": {"type": "fade", "dur": 0.25}   # xfade type into THIS segment (omit = hard cut)
    }
  ],
  "ass": "text.ass",                          # optional animated text (libass)
  "sfx": [{"file": "assets/sfx/whoosh_short.wav", "at": 2.4, "gain_db": -8}],
  "music": {"file": "ref.wav", "start": 0.0, "gain_db": -4, "duck": true}   # optional; licensed/royalty-free or sync-guide only
}
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KB = Path(__file__).resolve().parent.parent
GRADES = {
    "moviemode": "eq=contrast=1.08:saturation=1.08:gamma=0.97,"
                 "colorbalance=rs=-0.05:bs=0.06:rh=0.06:bh=-0.04,vignette=PI/5,noise=alls=4:allf=t",
    "reality": "eq=contrast=0.97:saturation=0.95,colortemperature=temperature=7000",
    "cozy": "eq=contrast=1.06:saturation=1.12:gamma=1.02,"
            "colorbalance=rm=0.03:bm=-0.02:rh=0.04:bh=-0.03,vignette=PI/6,noise=alls=3:allf=t",
    # cozy + shadow lift for dark close-ups of dark subjects (keeps OLED/highlights intact)
    "cozy_lift": "eq=contrast=1.02:saturation=1.12:gamma=1.22,curves=all='0/0.02 0.5/0.52 1/1',"
                 "colorbalance=rm=0.03:bm=-0.02:rh=0.04:bh=-0.03,vignette=PI/7,noise=alls=3:allf=t",
    "none": "",
}
HDR_TRC = {"arib-std-b67", "smpte2084"}
TONEMAPS = {
    # mobius keeps more brightness/detail on dark iPhone HLG footage (chosen for P001); hable = more contrast
    "mobius": "tonemap=tonemap=mobius:param=0.3:desat=0",
    "hable": "tonemap=tonemap=hable:desat=0",
    "reinhard": "tonemap=tonemap=reinhard:param=0.5:desat=0",
}


def tonemap_chain(kind):
    return ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
            f"{TONEMAPS.get(kind, TONEMAPS['mobius'])},zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def resolve(base, p):
    q = Path(p)
    if q.is_absolute():
        return q
    for cand in (base / q, KB / q):
        if cand.exists():
            return cand.resolve()
    return (base / q).resolve()


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
                          "-show_format", str(path)], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"Cannot read {path}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def atempo_chain(speed):
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0"); s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5"); s /= 0.5
    parts.append(f"atempo={s:.6f}")
    return ",".join(parts)


def esc(path):  # escape a path for use inside a filtergraph
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def build(edl, base, draft=False):
    W, H, FPS = edl.get("width", 1080), edl.get("height", 1920), edl.get("fps", 30)
    inputs, chains, durations = [], [], []

    def add_input(args):
        inputs.extend(args)
        return sum(1 for a in inputs if a == "-i") - 1

    for k, seg in enumerate(edl["segments"]):
        src = resolve(base, seg["src"])
        info = probe(src)
        vs = next(s for s in info["streams"] if s["codec_type"] == "video")
        has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
        t0, t1 = float(seg["in"]), float(seg["out"])
        # Input-level accurate seek: decode only the needed range (fast on long 4K HEVC files)
        idx = add_input(["-ss", f"{t0:.4f}", "-t", f"{t1 - t0 + 0.05:.4f}", "-i", str(src)])
        speed = float(seg.get("speed", 1.0))
        freeze = float(seg.get("freeze_end", 0.0))
        D = (t1 - t0) / speed + freeze
        durations.append(D)
        t0, t1 = 0.0, t1 - t0   # timestamps now start at 0 for this input

        v = [f"trim=start={t0}:end={t1}", "setpts=PTS-STARTPTS"]
        if vs.get("color_transfer") in HDR_TRC:
            v.append(tonemap_chain(edl.get("tonemap", "mobius")))
        rf = seg.get("reframe")   # [x, y, s]: crop a region (fraction s of width & height) BEFORE scaling
        if rf:
            x, y, s = rf
            v.append(f"crop=trunc(iw*{s}/2)*2:trunc(ih*{s}/2)*2:iw*{x}:ih*{y}")
        if seg.get("interpolate") and speed < 1:
            v.append(f"minterpolate=fps={FPS / speed:.3f}:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
        if speed != 1.0:
            v.append(f"setpts=PTS/{speed}")
        v.append(f"fps={FPS}")
        fx, fy = seg.get("focus_x", 0.5), seg.get("focus_y", 0.5)
        if seg.get("fit", "crop") == "blur":
            v_pre = ",".join(v)
            chains.append(
                f"[{idx}:v]{v_pre},split=2[bg{k}][fg{k}];"
                f"[bg{k}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.08[bgb{k}];"
                f"[fg{k}]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs{k}];"
                f"[bgb{k}][fgs{k}]overlay=(W-w)/2:(H-h)/2[fit{k}]")
            v = []
            head = f"[fit{k}]"
        else:
            v.append(f"scale={W}:{H}:force_original_aspect_ratio=increase")
            v.append(f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy}")
            head = f"[{idx}:v]"
        g = seg.get("grade", "none")
        g = GRADES.get(g, g)
        if g:
            v.append(g)
        # Zoom / punch / shake (frame-evaluated scale + crop)
        z0, z1 = seg.get("zoom", [1.0, 1.0])
        punches, shakes = seg.get("punches", []), seg.get("shakes", [])
        if z0 != 1.0 or z1 != 1.0 or punches or shakes:
            dur_core = (t1 - t0) / speed
            z = f"({z0}+({z1}-{z0})*min(t/{dur_core:.4f},1))"
            for p in punches:
                a, s, d = p["at"], p["scale"], p.get("dur", 0.4)
                z += f"+({s}-1)*min(max((t-{a})/0.1,0),1)*between(t,{a},{a + d})"
            sx = sy = "0"
            for sh in shakes:
                a, d, px = sh["at"], sh.get("dur", 0.13), sh.get("px", 12)
                z = f"max({z},{1 + 2.2 * px / W:.4f}*between(t,{a},{a + d}))"
                sx += f"+{px}*sin(n*2.7)*between(t,{a},{a + d})"
                sy += f"+{px}*cos(n*3.1)*between(t,{a},{a + d})"
            v.append(f"scale=w='2*trunc({W}*({z})/2)':h='2*trunc({H}*({z})/2)':eval=frame")
            v.append(f"crop={W}:{H}:x='(iw-{W})/2+({sx})':y='(ih-{H})/2+({sy})'")
        if freeze > 0:
            v.append(f"tpad=stop_mode=clone:stop_duration={freeze}")
        v += ["setsar=1", "format=yuv420p", "settb=AVTB"]
        chains.append(f"{head}{','.join(v)}[v{k}]")

        if seg.get("audio", "keep") == "keep" and has_audio and 0.25 <= speed <= 4:
            a = [f"atrim=start={t0}:end={t1}", "asetpts=PTS-STARTPTS"]
            if speed != 1.0:
                a.append(atempo_chain(speed))
            a += ["aresample=48000", "aformat=sample_fmts=fltp:channel_layouts=stereo",
                  f"volume={seg.get('gain_db', 0)}dB", f"apad=whole_dur={D:.4f}", f"atrim=duration={D:.4f}"]
            chains.append(f"[{idx}:a]{','.join(a)}[a{k}]")
        else:
            chains.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={D:.4f},"
                          f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{k}]")

    # Join segments: hard cuts (concat) or xfade/acrossfade
    vacc, aacc, total = "[v0]", "[a0]", durations[0]
    for k in range(1, len(durations)):
        tr = edl["segments"][k].get("transition_in")
        if tr:
            d = float(tr.get("dur", 0.25))
            chains.append(f"{vacc}[v{k}]xfade=transition={tr.get('type', 'fade')}:duration={d}:offset={total - d:.4f}[vx{k}]")
            chains.append(f"{aacc}[a{k}]acrossfade=d={d}[ax{k}]")
            total += durations[k] - d
        else:
            chains.append(f"{vacc}{aacc}[v{k}][a{k}]concat=n=2:v=1:a=1[vx{k}][ax{k}]")
            total += durations[k]
        vacc, aacc = f"[vx{k}]", f"[ax{k}]"

    if edl.get("ass"):
        chains.append(f"{vacc}ass='{esc(resolve(base, edl['ass']))}',format=yuv420p[vout]")
    else:
        chains.append(f"{vacc}format=yuv420p[vout]")

    mix = [aacc]
    for j, s in enumerate(edl.get("sfx", [])):
        si = add_input(["-i", str(resolve(base, s["file"]))])
        ms = int(round(float(s["at"]) * 1000))
        chains.append(f"[{si}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                      f"volume={s.get('gain_db', -6)}dB,adelay={ms}|{ms},"
                      f"apad=whole_dur={total:.4f},atrim=duration={total:.4f}[sfx{j}]")
        mix.append(f"[sfx{j}]")
    music = edl.get("music")
    if music:
        mi = add_input(["-ss", str(music.get("start", 0)), "-i", str(resolve(base, music["file"]))])
        chains.append(f"[{mi}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                      f"volume={music.get('gain_db', -4)}dB,apad=whole_dur={total:.4f},atrim=duration={total:.4f}[mus]")
        if music.get("duck", True):
            chains.append(f"{aacc}asplit=2[key][nat]")
            mix[0] = "[nat]"
            chains.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[musd]")
            mix.append("[musd]")
        else:
            mix.append("[mus]")
    if len(mix) > 1:
        chains.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest,"
                      f"atrim=duration={total:.4f}[aout]")
    else:
        chains.append(f"{mix[0]}anull[aout]")
    return inputs, ";".join(chains), total


def render_intermediates(edl, base, workdir):
    """Memory-safe mode: render each segment alone to a near-lossless 1080x1920 intermediate
    (one heavy 4K/HDR decoder at a time), then return an equivalent EDL of simple segments."""
    W, H, FPS = edl.get("width", 1080), edl.get("height", 1920), edl.get("fps", 30)
    new_segs = []
    for k, seg in enumerate(edl["segments"]):
        one = {k2: v for k2, v in edl.items() if k2 not in ("segments", "ass", "sfx", "music")}
        s = {k2: v for k2, v in seg.items() if k2 != "transition_in"}
        s["src"] = str(resolve(base, seg["src"]))
        one["segments"] = [s]
        inputs, graph, total = build(one, base)
        mid = workdir / f"seg{k:02d}.mkv"
        r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "8"] + inputs +
                           ["-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "8", "-pix_fmt", "yuv420p",
                            "-r", str(FPS), "-c:a", "pcm_s24le", "-ar", "48000", str(mid)],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"Segment {k} failed:\n" + r.stderr[-3000:])
        print(f"  segment {k + 1}/{len(edl['segments'])} rendered ({total:.2f} s)", flush=True)
        ns = {"src": str(mid), "in": 0.0, "out": round(total, 4), "audio": "keep", "fit": "crop", "grade": "none"}
        if "transition_in" in seg:
            ns["transition_in"] = seg["transition_in"]
        new_segs.append(ns)
    flat = dict(edl)
    flat["segments"] = new_segs
    return flat


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    edl_path = Path(sys.argv[1]).resolve()
    draft = "--draft" in sys.argv
    onepass = "--onepass" in sys.argv     # old behaviour: everything in one filtergraph (needs lots of RAM for 4K/HDR)
    edl = json.loads(edl_path.read_text())
    base = edl_path.parent
    out = resolve(base, edl["output"])
    out.parent.mkdir(parents=True, exist_ok=True)
    seg_dir = Path(tempfile.mkdtemp(prefix="reel_segs_"))
    try:
        if not onepass:
            edl = render_intermediates(edl, base, seg_dir)
        inputs, graph, total = build(edl, base, draft)
        _final(edl, base, out, inputs, graph, total, draft)
    finally:
        for f in seg_dir.glob("*"):
            f.unlink()
        seg_dir.rmdir()


def _final(edl, base, out, inputs, graph, total, draft):
    FPS, crf = edl.get("fps", 30), edl.get("crf", 17)
    target = edl.get("loudness_lufs", -16)
    preset = "veryfast" if draft else "slow"

    with tempfile.TemporaryDirectory() as td:
        vtmp, atmp = Path(td) / "v.mp4", Path(td) / "a.wav"
        cmd1 = (["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + inputs +
                ["-filter_complex", graph,
                 "-map", "[vout]", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                 "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(vtmp),
                 "-map", "[aout]", "-c:a", "pcm_s24le", "-ar", "48000", str(atmp)])
        (base / "render_cmd.txt").write_text(" ".join(f"'{c}'" if " " in c or ";" in c else c for c in cmd1) + "\n")
        r = subprocess.run(cmd1, capture_output=True, text=True)
        if r.returncode:
            sys.exit("Render failed:\n" + r.stderr[-3000:])
        # Two-pass loudness normalisation (video stream is copied, not re-encoded)
        m = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(atmp), "-af",
                            f"loudnorm=I={target if target is not None else -16}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        js = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
        # TP -1.5 leaves margin for AAC encoding overshoot (measured -0.9 dBTP with -1.0 in P001 draft)
        ln = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
              f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
        if target is None or float(js["input_i"]) < -60:   # no normalisation requested / silent track
            ln = "alimiter=limit=0.84:level=false"
        r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(vtmp), "-i", str(atmp),
                            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", ln, "-c:a", "aac", "-b:a", "320k",
                            "-ar", "48000", "-t", f"{total:.4f}", "-movflags", "+faststart", str(out)],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("Mux failed:\n" + r.stderr[-2000:])
    print(f"Rendered {out} ({total:.2f} s planned) · loudness target {target if target is not None else 'none (peak-limited)'} LUFS · preset {preset}")


if __name__ == "__main__":
    main()
