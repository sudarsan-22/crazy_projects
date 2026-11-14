"""edl/2 → edl/1 compiler. tools/reel_render.py stays the renderer (unchanged); v2 features that it lacks
(smooth ramps, subject-tracked crops) are pre-rendered here as LOSSLESS FFV1 intermediates (KB 32 §7)."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from .. import __version__, config, ff
from ..analysis.subject import crop_x_expr
from . import resolve as R
from . import text as T
from .schema import EDL

V2_KEYS = {"schema", "markers", "sync", "components", "text", "audio_rights", "reference_audio", "cover_at",
           "caption"}


def resolve_path(base, p):
    q = Path(p)
    if q.is_absolute():
        return q
    for cand in (base / q, config.KB / q):
        if cand.exists():
            return cand.resolve()
    return (base / q).resolve()


# ---------- SFX metadata (peak offsets, KB 30 §3.8) ----------
def sfx_meta(path):
    path = Path(path)
    side = path.parent / "sfx.json"
    meta = json.loads(side.read_text()) if side.exists() else {}
    key = path.name
    st = path.stat()
    if key not in meta or meta[key].get("mtime") != int(st.st_mtime):
        y, sr = sf.read(str(path), dtype="float32", always_2d=True)
        env = np.abs(y).mean(axis=1)
        win = max(1, int(sr * 0.005))
        env = np.convolve(env, np.ones(win) / win, mode="same")
        meta[key] = {"duration": round(len(y) / sr, 4), "peak_ms": int(round(1000 * int(np.argmax(env)) / sr)),
                     "mtime": int(st.st_mtime)}
        if path.parent == config.SFX_DIR:
            side.write_text(json.dumps(meta, indent=1))
    return meta[key]


# ---------- macros: signatures S1–S6 (KB 16 §1, 32 §6.2) ----------
def _seg_at(tl, t):
    for x in tl:
        if x["start"] - 1e-6 <= t < x["end"] - 1e-6:
            return x
    return tl[-1]


def expand_macros(edl, tl):
    log = []
    for c in edl.get("components", []):
        m, at = c["macro"], c.get("at")
        if m == "S1_name_card":
            t0 = R.event_time(edl, at, tl)
            dur = float(c.get("dur", 1.2))
            edl.setdefault("text", []).append({"style": "card", "text": c["text"], "start": t0, "dur": dur,
                                               "anim": "slide_in", **({"pos": c["pos"]} if c.get("pos") else {})})
            if c.get("sub"):
                edl["text"].append({"style": "sub", "text": c["sub"], "start": t0 + 0.25, "end": t0 + dur,
                                    "anim": "fade"})
            edl.setdefault("sfx", []).append({"file": c.get("sfx", "assets/sfx/impact_hit.wav"), "at": t0,
                                              "align": "peak", "gain_db": c.get("gain_db", -6)})
            log.append(f"S1 name card '{c['text']}' at {t0:.2f}s")
        elif m == "S3_bruh_sting":
            t0 = R.event_time(edl, at, tl)
            x = _seg_at(tl, t0)
            seg = edl["segments"][x["index"]]
            local = round(t0 - x["start"], 3)
            if local < x["core"] - 0.05:
                seg.setdefault("punches", []).append({"at": local, "scale": c.get("scale", 1.12), "dur": 0.27})
                seg.setdefault("shakes", []).append({"at": local, "dur": 0.13, "px": c.get("px", 14)})
            if c.get("text", "BRUH"):
                edl.setdefault("text", []).append({"style": "bruh", "text": c.get("text", "BRUH"), "start": t0,
                                                   "dur": 0.7, "anim": "stamp"})
            edl.setdefault("sfx", []).append({"file": c.get("sfx", "assets/sfx/punch.wav"), "at": t0,
                                              "align": "peak", "gain_db": c.get("gain_db", -6)})
            log.append(f"S3 bruh sting at {t0:.2f}s in {x['id']} (local {local}s)")
        elif m == "S4_episode_tag":
            edl.setdefault("text", []).append({"style": "tag", "text": c["text"], "start": 0.0,
                                               "end": R.total(edl), "anim": "fade"})
            log.append(f"S4 tag '{c['text']}'")
        elif m in ("S5_two_tone", "S2_bgm_switch"):
            t0 = R.event_time(edl, at, tl)
            before, after = c.get("before", "moviemode"), c.get("after", "reality")
            for x in tl:
                edl["segments"][x["index"]]["grade"] = before if x["start"] < t0 - 1e-3 else after
            if m == "S2_bgm_switch":
                d = sfx_meta(resolve_path(config.KB, c.get("sfx", "assets/sfx/scratch_stop.wav")))
                edl.setdefault("sfx", []).append({"file": c.get("sfx", "assets/sfx/scratch_stop.wav"), "at": t0,
                                                  "align": "end", "gain_db": c.get("gain_db", -8)})
                edl.setdefault("planned_silence", []).append([round(t0 - c.get("silence", 0.4), 3), round(t0, 3)])
            log.append(f"{m} at {t0:.2f}s ({before} → {after})")
        elif m == "S6_captions":
            pass                     # style only: text items default to the S6 caption style
        else:
            raise R.EDLError(f"unknown macro '{m}'")
    return log


# ---------- prep intermediates for ramp / track ----------
def _needs_prep(seg, info):
    track = seg.get("fit") == "track" and info["width"] / info["height"] > 9 / 16 + 0.01
    return isinstance(seg.get("speed"), dict) or track, track


def prep_segment(seg, src, info, out_dir, edl, subject_path=None):
    W, H, FPS = edl.get("width", 1080), edl.get("height", 1920), edl.get("fps", 30)
    ramp = isinstance(seg.get("speed"), dict)
    _, track = _needs_prep(seg, info)
    t0, t1 = float(seg["in"]), float(seg["out"])
    L = t1 - t0
    key = hashlib.sha1(json.dumps([str(src), src.stat().st_size, int(src.stat().st_mtime), t0, t1, seg.get("speed"),
                                   seg.get("fit"), seg.get("track"), seg.get("interpolate"), W, H, FPS,
                                   edl.get("tonemap", "mobius"), __version__,
                                   (subject_path or {}).get("cx", [])[:3]], default=str).encode()).hexdigest()[:16]
    out = out_dir / f"prep_{seg['id']}_{key}.mkv"
    meta = {"prep": str(out), "ramp": ramp, "track": track}
    v = ["trim=start=0:end=%.4f" % L, "setpts=PTS-STARTPTS"]
    if info.get("hdr"):
        v.append(ff.tonemap_chain(edl.get("tonemap", "mobius")))
    if track and subject_path:
        frac = (info["height"] * 9 / 16) / info["width"]
        xexpr = crop_x_expr(subject_path, t0, t1, frac)
        v.append(f"crop=w='trunc(ih*9/16/2)*2':h=ih:x='{xexpr}':y=0")
        ts_, cx = np.array(subject_path["t"]), np.array(subject_path["raw_cx"])
        sel = (ts_ >= t0) & (ts_ <= t1)
        cam = np.array(subject_path["cx"])[sel]
        left = np.clip(cam - frac / 2, 0, 1 - frac)
        inside = (cx[sel] >= left) & (cx[sel] <= left + frac)
        meta["subject_inside_crop"] = round(float(inside.mean()), 3) if inside.size else None
    if ramp:
        lo = min(seg["speed"]["ramp"])
        if seg.get("interpolate") and lo < 1:
            v.append(f"minterpolate=fps={FPS / lo:.3f}:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
        v.append(f"setpts='{R.ramp_setpts(seg)}'")
    v += [f"fps={FPS}", f"scale={W}:{H}:force_original_aspect_ratio=increase",
          f"crop={W}:{H}:(iw-{W})*{seg.get('focus_x', 0.5)}:(ih-{H})*{seg.get('focus_y', 0.5)}",
          "setsar=1", "format=yuv420p"]
    if not out.exists():
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t0:.4f}", "-t", f"{L + 0.05:.4f}",
               "-i", src, "-map", "0:v:0", "-vf", ",".join(v)]
        if not ramp and info.get("has_audio"):
            cmd += ["-map", "0:a:0", "-af", f"atrim=0:{L:.4f},asetpts=PTS-STARTPTS", "-c:a", "pcm_s16le", "-ar", "48000"]
        cmd += ["-c:v", "ffv1", "-level", "3", "-g", "1", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-colorspace", "bt709", out]
        ff.run(cmd)
    meta["duration"] = ff.media_info(out)["duration"]
    return meta


# ---------- main entry ----------
def compile_edl(edl_path, variant="clean", version=1, out_dir=None, analysis_dir=None):
    """Return dict with paths of the edl/1 file, ASS, resolved timeline, and a report."""
    edl_path = Path(edl_path).resolve()
    raw = json.loads(edl_path.read_text())
    EDL.model_validate(raw)                      # schema check (raises with readable messages)
    edl = copy.deepcopy(raw)
    base = edl_path.parent
    out_dir = Path(out_dir or base)
    out_dir.mkdir(parents=True, exist_ok=True)
    R.seg_ids(edl)
    infos = {}
    for s in edl["segments"]:
        src = resolve_path(base, s["src"])
        if not src.exists():
            raise R.EDLError(f"{s['id']}: source not found: {src}")
        infos[s["id"]] = (src, ff.media_info(src))
    problems = []
    for s in edl["segments"]:
        d = infos[s["id"]][1]["duration"]
        if not 0 <= float(s["in"]) < float(s["out"]) <= d + 0.05:
            problems.append(f"{s['id']}: in/out {s['in']}–{s['out']} outside source 0–{d:.2f}s")
    sync = R.solve_sync(edl, {k: v[1]["duration"] for k, v in infos.items()}) if edl.get("sync") else []
    tl = R.timeline(edl)
    macro_log = expand_macros(edl, tl)
    tl = R.timeline(edl)
    total = tl[-1]["end"]
    fps = edl.get("fps", 30)

    # ASS
    hand = None
    if edl.get("ass"):
        hand = resolve_path(base, edl["ass"]).read_text()
    ass_path = None
    if hand and not edl.get("text"):
        ass_path, text_items = resolve_path(base, edl["ass"]), []      # v0: hand-written ASS used untouched
    else:
        ass_text, text_items = T.build(edl, tl, total, hand)
        if text_items or hand:
            ass_path = out_dir / f"text.v{version}.ass"
            ass_path.write_text(ass_text)

    # segments → edl/1
    prep_dir = out_dir / "prep"
    segs1, prep_meta = [], {}
    for s in edl["segments"]:
        src, info = infos[s["id"]]
        need, track = _needs_prep(s, info)
        s1 = {k: v for k, v in s.items() if k not in ("id", "track")}
        if need:
            prep_dir.mkdir(exist_ok=True)
            sp = None
            if track:
                tp = resolve_path(base, s["track"]) if s.get("track") else (
                    Path(analysis_dir) / src.stem / "subject.json" if analysis_dir else None)
                if tp and Path(tp).exists():
                    sp = json.loads(Path(tp).read_text())
                else:
                    problems.append(f"{s['id']}: fit=track but no subject path found ({tp}); centre crop used")
            pm = prep_segment(s, src, info, prep_dir, edl, sp)
            prep_meta[s["id"]] = pm
            s1.update({"src": pm["prep"], "in": 0.0, "out": round(pm["duration"] - 0.001, 4), "fit": "crop",
                       "focus_x": 0.5, "focus_y": 0.5})
            s1.pop("reframe", None)
            s1.pop("interpolate", None)
            if pm["ramp"]:
                s1["speed"] = 1.0
                s1["audio"] = "mute"
        else:
            s1["src"] = str(src)
            if s1.get("fit") == "track":
                s1["fit"] = "crop"
        segs1.append(s1)

    # SFX with alignment
    sfx1, sfx_resolved = [], []
    for x in edl.get("sfx", []):
        f = resolve_path(base, x["file"])
        at = R.event_time(edl, x["at"], tl)
        meta = sfx_meta(f)
        start = at - (meta["peak_ms"] / 1000 if x.get("align") == "peak" else
                      meta["duration"] if x.get("align") == "end" else 0.0)
        start = max(0.0, start)
        sfx1.append({"file": str(f), "at": round(start, 4), "gain_db": x.get("gain_db", -8)})
        sfx_resolved.append({"file": f.name, "event": round(at, 3), "start": round(start, 3), "align": x.get("align")})

    rights = edl.get("audio_rights", "in_app_library")
    lufs = edl.get("loudness_lufs") or (config.LUFS_CLEAN if rights == "in_app_library" else config.LUFS_BAKED)
    v1 = {k: v for k, v in edl.items() if k not in V2_KEYS and k not in ("segments", "sfx", "ass", "music",
                                                                         "planned_silence", "output")}
    v1.update({"segments": segs1, "sfx": sfx1, "loudness_lufs": lufs})
    if ass_path:
        v1["ass"] = str(ass_path)
    ref = edl.get("reference_audio") or (edl.get("music") if rights == "in_app_library" else None)
    music = None
    if variant == "syncguide" and ref:
        music = {"file": str(resolve_path(base, ref["file"])), "start": ref.get("start", 0.0),
                 "gain_db": ref.get("gain_db", -4), "duck": ref.get("duck", True)}
    elif variant == "final" and edl.get("music") and rights != "in_app_library":
        mu = edl["music"]
        music = {"file": str(resolve_path(base, mu["file"])), "start": mu.get("start", 0.0),
                 "gain_db": mu.get("gain_db", -4), "duck": mu.get("duck", True)}
    if music:
        v1["music"] = music
    v1["output"] = str((out_dir.parent / "renders" / f"v{version}_{variant}.mp4").resolve())

    # cuts that QC can verify (hard cuts only); muted segments are planned silence
    cuts = [round(x["start"], 4) for x in tl[1:] if not x["transition_in"]]
    for x, s1 in zip(tl, segs1):
        if s1.get("audio") == "mute":
            edl.setdefault("planned_silence", []).append([round(x["start"], 3), round(x["end"], 3)])
    resolved = {
        "version": version, "variant": variant, "fps": fps, "total": round(total, 4),
        "frames": int(round(total * fps)), "loudness_lufs": lufs, "audio_rights": rights,
        "markers": edl.get("markers", {}), "timeline": [{k: (round(v, 4) if isinstance(v, float) else v)
                                                       for k, v in x.items()} for x in tl],
        "hard_cuts": cuts, "freezes": [[round(x["freeze_start"], 4), round(x["end"], 4)] for x in tl if x["freeze"] > 0],
        "sync": sync, "sync_events": [{"event": c["event"], "marker": c["marker"],
                                       "time": round(R.event_time(edl, c["event"], tl), 4)} for c in edl.get("sync", [])],
        "text": text_items, "sfx": sfx_resolved, "macros": macro_log, "prep": prep_meta,
        "planned_silence": edl.get("planned_silence", []), "problems": problems,
        "reference_audio": (str(resolve_path(base, ref["file"])) if ref else None),
        "reference_start": (ref or {}).get("start", 0.0), "music_in_output": bool(music),
        "cover_at": R.event_time(edl, edl["cover_at"], tl) if edl.get("cover_at") is not None else None,
        "caption": edl.get("caption"), "edl": str(edl_path),
    }
    v1_path = out_dir / f"edl.v{version}.{variant}.render.json"
    v1_path.write_text(json.dumps(v1, indent=1, ensure_ascii=False))
    res_path = out_dir / f"edl.v{version}.resolved.json"
    res_path.write_text(json.dumps(resolved, indent=1, ensure_ascii=False))
    return {"render_edl": v1_path, "resolved": res_path, "ass": ass_path, "report": resolved}
