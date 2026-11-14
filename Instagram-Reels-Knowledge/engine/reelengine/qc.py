"""Stage 8: measure the RENDERED file against the resolved timeline (KB 32 §8). pass / warn / fail per rule."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

from . import config, ff

FAIL, WARN, PASS, INFO = "fail", "warn", "pass", "info"


def _faststart(path):
    with open(path, "rb") as f:
        pos, order = 0, []
        size = Path(path).stat().st_size
        while pos < size and len(order) < 12:
            f.seek(pos)
            hdr = f.read(16)
            if len(hdr) < 8:
                break
            n = int.from_bytes(hdr[:4], "big")
            typ = hdr[4:8].decode("latin1")
            if n == 1:
                n = int.from_bytes(hdr[8:16], "big")
            order.append(typ)
            if n < 8:
                break
            pos += n
    return "moov" in order and "mdat" in order and order.index("moov") < order.index("mdat")


def _ass_lines(ass_path):
    txt = Path(ass_path).read_text()
    head, events = [], []
    sec = None
    for line in txt.splitlines():
        if line.startswith("["):
            sec = line.strip()
        if sec == "[Events]" and line.startswith("Dialogue:"):
            events.append(line)
        elif not (sec == "[Events]" and line.startswith("Comment:")):
            head.append(line)
    return head, events


def _t(s):
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def text_boxes(ass_path, W=config.WIDTH, H=config.HEIGHT):
    """Render every Dialogue line ALONE (shifted to t=0) on black and on white; return its pixel bbox."""
    head, events = _ass_lines(ass_path)
    out = []
    with tempfile.TemporaryDirectory() as td:
        for i, line in enumerate(events):
            parts = line.split(",", 9)
            st, en = _t(parts[1]), _t(parts[2])
            dur = max(0.05, en - st)
            probe_t = min(0.5, dur * 0.6)
            single = "\n".join(head + [",".join(parts[:1] + ["0:00:00.00", "0:00:%05.2f" % min(dur, 59)] + parts[3:])])
            ap = Path(td) / f"l{i}.ass"
            ap.write_text(single + "\n")
            masks = []
            for bg, cond in (("black", lambda a: (a > 24).any(axis=2)), ("white", lambda a: (a < 231).any(axis=2))):
                png = Path(td) / f"l{i}_{bg}.png"
                ff.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        f"color=c={bg}:s={W}x{H}:r=30:d={probe_t + 0.2:.2f}", "-vf",
                        f"subtitles={ap}:fontsdir={config.FONTS_DIR},trim=start={probe_t:.3f},setpts=PTS-STARTPTS",
                        "-frames:v", "1", png])
                a = cv2.imread(str(png))
                masks.append(cond(a))
            m = masks[0] | masks[1]
            ys, xs = np.nonzero(m)
            box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
            # animation path (slide-ins, pops): union of every frame in the first 0.6 s, at half size
            span = min(dur, 0.6)
            union = np.zeros((H // 2, W // 2), bool)
            for bg, thr in (("black", lambda a: a > 24), ("white", lambda a: a < 231)):
                raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                                      f"color=c={bg}:s={W}x{H}:r=30:d={span:.2f}", "-vf",
                                      f"subtitles={ap}:fontsdir={config.FONTS_DIR},scale={W // 2}:{H // 2},format=gray",
                                      "-f", "rawvideo", "-"], capture_output=True).stdout
                fr = np.frombuffer(raw, np.uint8)
                n = fr.size // ((H // 2) * (W // 2))
                if n:
                    union |= thr(fr[: n * (H // 2) * (W // 2)].reshape(n, H // 2, W // 2)).any(axis=0)
            ys2, xs2 = np.nonzero(union)
            anim = [int(xs2.min()) * 2, int(ys2.min()) * 2, int(xs2.max()) * 2 + 1, int(ys2.max()) * 2 + 1] \
                if len(xs2) else box
            text = re.sub(r"\{[^}]*\}", "", parts[9]).replace(r"\N", " ")
            out.append({"line": i, "style": parts[3], "text": text[:60], "start": round(st, 2), "end": round(en, 2),
                        "box": box, "anim_box": anim})
    return out


def _mono8k(path, start=0.0, dur=60.0):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}",
                          "-i", str(path), "-vn", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def music_similarity(output, reference, ref_start=0.0):
    """Peak normalised cross-correlation of output audio vs the reference track (0..1)."""
    from scipy.signal import correlate
    a, b = _mono8k(output), _mono8k(reference, ref_start)
    if len(a) < 800 or len(b) < 800:
        return None
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    den = np.sqrt((a ** 2).sum() * (b ** 2).sum()) + 1e-9
    c = correlate(a, b, mode="full", method="fft")
    return round(float(np.abs(c).max() / den), 3)


def frame_diffs(path, t0, t1, boxes=(), scale=4):
    """Per-frame mean abs difference (grey, 1/scale size) in [t0, t1], with text boxes masked out
    so animated captions can't fake (or hide) a cut or a freeze."""
    import av
    out, prev = [], None
    with av.open(str(path)) as c:
        st = c.streams.video[0]
        c.seek(int(max(0.0, t0 - 0.5) / st.time_base), stream=st, backward=True)
        for f in c.decode(st):
            t = float(f.pts * f.time_base)
            if t < t0 - 1e-6:
                prev = None
                g = f.to_ndarray(format="gray")[::scale, ::scale].astype(np.int16)
                for b in boxes:
                    g[b[1] // scale:b[3] // scale + 1, b[0] // scale:b[2] // scale + 1] = 0
                prev = g
                continue
            if t > t1 + 1e-6:
                break
            g = f.to_ndarray(format="gray")[::scale, ::scale].astype(np.int16)
            for b in boxes:
                g[b[1] // scale:b[3] // scale + 1, b[0] // scale:b[2] // scale + 1] = 0
            if prev is not None:
                out.append((round(t, 4), float(np.abs(g - prev).mean())))
            prev = g
    return out


def measure_cut(path, planned, fps, boxes, win=0.3):
    d = frame_diffs(path, planned - win, planned + win, boxes)
    if not d:
        return None
    vals = np.array([v for _, v in d])
    i = int(np.argmax(vals))
    base = np.median(np.delete(vals, i)) if len(vals) > 1 else 0
    if vals[i] < max(8.0, 6 * base):
        return None                      # no visual discontinuity: cut can't be verified by pixels
    return d[i][0]


def measure_freeze(path, planned, fps, boxes, win=0.4, run_len=6, thr=0.05):
    d = frame_diffs(path, planned - win, planned + win + run_len / fps, boxes)
    for k in range(len(d) - run_len + 1):
        if all(v < thr for _, v in d[k:k + run_len]):
            return d[k][0]               # first frame identical to its predecessor = first held frame
    return None


def run(prod, version, variant="clean", evidence=True, log=print):
    build = prod.d("build")
    res = json.loads((build / f"edl.v{version}.resolved.json").read_text())
    render_edl = json.loads((build / f"edl.v{version}.{variant}.render.json").read_text())
    out = Path(render_edl["output"])
    fps, planned = res["fps"], res["total"]
    qdir = prod.d(f"build/qc_v{version}_{variant}")
    checks = []

    def chk(area, status, detail, fix=None):
        checks.append({"area": area, "status": status, "detail": detail, **({"autofix": fix} if fix else {})})

    info = ff.media_info(out)
    nb = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                             "stream=nb_read_packets", "-of", "csv=p=0", str(out)], capture_output=True,
                            text=True).stdout.strip() or 0)
    spec_ok = (info["width"], info["height"]) == (render_edl.get("width", 1080), render_edl.get("height", 1920)) \
        and abs(info["fps"] - fps) < 0.01 and info["codec"] == "h264" and info["pix_fmt"] == "yuv420p" \
        and info.get("audio_codec") == "aac" and info.get("sample_rate") == 48000 and info.get("channels") == 2
    chk("spec", PASS if spec_ok and _faststart(out) else FAIL,
        f"{info['width']}x{info['height']} {info['fps']}fps {info['codec']} {info['pix_fmt']} "
        f"{info.get('audio_codec')} {info.get('sample_rate')}Hz ch{info.get('channels')} faststart={_faststart(out)}")
    dframes = nb - res["frames"]
    chk("duration", PASS if abs(dframes) <= 1 and planned <= config.MAX_DURATION_S else FAIL,
        f"{nb} frames vs {res['frames']} planned ({dframes:+d}); {nb / fps:.2f}s ≤ {config.MAX_DURATION_S:.0f}s")

    ld = ff.ebur128(out)
    tgt = res["loudness_lufs"]
    li, tp = ld["integrated_lufs"], ld["true_peak_dbtp"]
    lok = li is not None and abs(li - tgt) <= config.LUFS_TOLERANCE
    chk("loudness", PASS if lok else FAIL, f"{li} LUFS (target {tgt}±{config.LUFS_TOLERANCE})",
        fix=None if lok else "renormalise")
    chk("true peak", PASS if tp is not None and tp <= config.TRUE_PEAK + 0.05 else FAIL, f"{tp} dBTP (≤ {config.TRUE_PEAK})",
        fix=None if tp is not None and tp <= config.TRUE_PEAK + 0.05 else "renormalise")

    blacks = [b for b in ff.blackdetect(out) if (b[1] or planned) - b[0] >= 0.1]
    chk("black frames", FAIL if blacks else PASS, f"{blacks or 'none'}")
    frz = ff.freezedetect(out, 0.5)
    planned_fr = res["freezes"]
    unplanned = [f for f in frz if not any(a - 0.25 <= f[0] and f[1] <= b + 0.25 for a, b in planned_fr)]
    chk("freezes / static spans", WARN if unplanned else PASS,
        f"planned holds {planned_fr}; other static spans ≥0.5s (check they're intentional, e.g. slow-mo of a "
        f"still subject): {[[round(a, 2), round(b, 2)] for a, b in unplanned] or 'none'}")
    sil = [s for s in ff.silencedetect(out, -45, 0.6)]
    psil = res.get("planned_silence", [])
    unp_sil = [s for s in sil if not any(a - 0.3 <= s[0] <= b for a, b in psil)]
    chk("silence", WARN if unp_sil else PASS, f"gaps >0.6s: {[[round(a, 2), round(b or planned, 2)] for a, b in sil] or 'none'}")

    first_black = any(b[0] <= 0.05 for b in ff.blackdetect(out, 0.04))
    sil0 = next((s for s in sil if s[0] <= 0.05), None)
    chk("hook", WARN if first_black or sil0 else PASS,
        f"first frame black={first_black}; audio starts {'late (' + str(sil0[1]) + 's)' if sil0 else '≤0.1s'}; "
        f"first text at {min([t['start'] for t in res['text']], default=None)}s")

    # sync: pixel-measured hard cuts + freeze onsets vs plan, with text boxes masked (see frame_diffs)
    ass = render_edl.get("ass")
    boxes = text_boxes(ass) if ass else []
    masks = [b.get("anim_box") or b["box"] for b in boxes if b["box"]]
    cuts = ff.scene_cuts(out, 0.10)
    errs = []
    for pc in res["hard_cuts"]:
        m = measure_cut(out, pc, fps, masks)
        errs.append({"planned": pc, "measured": m, "frames": None if m is None else round((m - pc) * fps, 1)})
    for pf in planned_fr:
        m = measure_freeze(out, pf[0], fps, masks)
        errs.append({"planned_freeze": pf[0], "measured": m, "frames": None if m is None else round((m - pf[0]) * fps, 1)})
    worst = max([abs(e["frames"]) for e in errs if e.get("frames") is not None], default=0)
    unverified = [e.get("planned", e.get("planned_freeze")) for e in errs if e.get("measured") is None]
    for se in res.get("sync_events", []):
        if se["marker"] == "D":
            m = [e for e in errs if abs(e.get("planned", e.get("planned_freeze", -9)) - se["time"]) < 0.01
                 and e.get("frames") is not None]
            ok = bool(m) and abs(m[0]["frames"]) <= 1
            chk("sync D (±1 frame)", PASS if ok else FAIL if m else WARN,
                f"{se['event']} planned {se['time']}s measured {m[0]['measured'] if m else 'not detectable'}")
    chk("sync cuts", PASS if worst <= 2 else WARN,
        f"worst {worst} frames over {len(errs)} events "
        f"{[(e.get('planned', e.get('planned_freeze')), e['frames']) for e in errs]}; "
        f"unverifiable (no visual change) {unverified or 'none'}")

    # text safe zone (every Dialogue line rendered alone)
    W, H = render_edl.get("width", 1080), render_edl.get("height", 1920)
    bad = []
    for b in boxes:
        if b["box"] is None:
            continue
        x0, y0, x1, y1 = b["box"]
        inside = x0 >= config.SAFE_LEFT and y0 >= config.SAFE_TOP and x1 <= W - config.SAFE_RIGHT \
            and y1 <= H - config.SAFE_BOTTOM
        b["inside_safe_zone"] = inside
        if not inside:
            bad.append(b)
    chk("text safe zone", FAIL if bad else PASS,
        f"{len(boxes)} text lines; outside: {[(b['text'][:24], b['box']) for b in bad] or 'none'}",
        fix="move_text" if bad else None)
    short = [t for t in res["text"] if t["style"] not in ("bruh", "tag") and t["end"] - t["start"] <
             max(config.MIN_TEXT_S, len(re.findall(r"\w+", t["text"])) / config.WORDS_PER_S)]
    chk("text reading time", WARN if short else PASS, f"too short: {[t['text'][:20] for t in short] or 'none'}")
    tam = [t["text"] for t in res["text"] if t.get("needs_check")]
    chk("Tamil text check", INFO if tam else PASS, f"needs your check before posting: {tam or 'none'}")

    # rights: no reference music in clean/final when it is Instagram-library audio
    if res.get("reference_audio") and variant != "syncguide":
        sim = music_similarity(out, res["reference_audio"], res.get("reference_start", 0.0))
        bad_r = res["audio_rights"] == "in_app_library" and sim is not None and sim > 0.5
        chk("rights (no library audio baked in)", FAIL if bad_r else PASS, f"similarity to reference {sim}")
    elif variant != "syncguide":
        chk("rights (no library audio baked in)", PASS if not res.get("music_in_output") or
            res["audio_rights"] != "in_app_library" else FAIL, f"music in output: {res.get('music_in_output')}, "
            f"rights path {res['audio_rights']}")

    for sid, pm in res.get("prep", {}).items():
        if pm.get("track"):
            cov = pm.get("subject_inside_crop")
            chk(f"reframe {sid}", PASS if cov is None or cov >= 0.95 else WARN, f"subject inside crop {cov}")
    if len(cuts) >= 0:
        shots = np.diff([0.0] + sorted(cuts) + [nb / fps])
        chk("pacing", INFO, f"{len(cuts)} detected cuts, {len(cuts) / max(nb / fps, 1e-3) * 10:.1f} per 10s, "
            f"median shot {float(np.median(shots)):.2f}s")

    if evidence:
        _evidence(prod, out, res, boxes, qdir, cuts)

    summary = {"version": version, "variant": variant, "file": str(out),
               "verdict": FAIL if any(c["status"] == FAIL for c in checks) else
               WARN if any(c["status"] == WARN for c in checks) else PASS,
               "checks": checks, "text_boxes": boxes, "measured_cuts": [round(c, 3) for c in cuts],
               "loudness": ld, "evidence_dir": str(qdir)}
    (build / f"qc_v{version}_{variant}.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    md = [f"# QC v{version} {variant}: **{summary['verdict'].upper()}**", "", "| Area | Status | Detail |", "|---|---|---|"]
    md += [f"| {c['area']} | {c['status']} | {str(c['detail']).replace('|', '/')} |" for c in checks]
    (build / f"qc_v{version}_{variant}.md").write_text("\n".join(md) + "\n")
    log(f"  QC v{version} {variant}: {summary['verdict'].upper()} "
        f"({sum(c['status'] == FAIL for c in checks)} fail, {sum(c['status'] == WARN for c in checks)} warn)")
    prod.mark("qc", version=version, variant=variant, verdict=summary["verdict"])
    return summary


def _evidence(prod, out, res, boxes, qdir, cuts):
    """Images for Claude's review: analyze_reel.py set + caption frames with safe zone + sync plot."""
    subprocess.run(["/usr/bin/python3", "-I", str(config.TOOLS / "analyze_reel.py"), str(out), str(qdir / "analyze")],
                   capture_output=True, text=True)
    sz = (",drawbox=x=0:y=0:w=iw:h=ih*250/1920:color=red@0.30:t=fill"
          ",drawbox=x=0:y=ih-ih*380/1920:w=iw:h=ih*380/1920:color=red@0.30:t=fill"
          ",drawbox=x=iw-iw*140/1080:y=0:w=iw*140/1080:h=ih:color=orange@0.25:t=fill")
    (qdir / "text").mkdir(exist_ok=True)
    for b in boxes[:24]:
        t = min(b["start"] + min(0.5, (b["end"] - b["start"]) * 0.6), max(0, b["end"] - 0.05))
        try:
            ff.frame_at(out, t, qdir / "text" / f"text_{b['line']:02d}_{t:.2f}s.jpg", vf="scale=540:-2" + sz)
        except ff.FFError:
            pass
    for i, x in enumerate(res.get("freezes", [])[:6]):
        try:
            ff.frame_at(out, x[0] + 0.1, qdir / f"freeze_{i}_{x[0]:.2f}s.jpg")
        except ff.FFError:
            pass
    music_json = prod.root / "audio" / "music.json"
    if music_json.exists():
        from .analysis.music import plot
        mj = json.loads(music_json.read_text())
        n = len(mj.get("energy_4hz", []))
        plot(mj, [k / 4 for k in range(n)], mj.get("energy_4hz", []), qdir / "sync_plot.png", cuts=cuts)
