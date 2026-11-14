"""Stage 3: moment PROPOSALS (KB 32 §5.1). Scores only order candidates; they are not evidence of 'funny'."""
import json

import numpy as np

from . import config
from .analyze import sheet
from .state import Production


def _norm(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return x
    lo, hi = np.percentile(x, 5), np.percentile(x, 98)
    return np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)


def score_clip(adir, duration, weights, win=0.5):
    vis = json.loads((adir / "visual.json").read_text())
    shots = json.loads((adir / "scenes.json").read_text())
    sp = json.loads((adir / "speech.json").read_text()) if (adir / "speech.json").exists() else {"segments": []}
    so = json.loads((adir / "sounds.json").read_text()) if (adir / "sounds.json").exists() else {"peaks": []}
    S = vis["samples"]
    ts = np.array([s["t"] for s in S])
    motion = _norm([s.get("motion", 0) for s in S])
    sharp = _norm(np.log1p([s.get("sharp", 0) for s in S]))
    luma = np.array([s.get("luma", 0.5) for s in S])
    face = np.array([max([f[2] * f[3] for f in s.get("faces", [])], default=0) for s in S])
    face = np.clip(face / 0.05, 0, 1)
    words = [(w["start"], w["end"]) for seg in sp.get("segments", []) for w in seg.get("words", [])]
    out = []
    n = max(1, int(np.ceil(duration / win)))
    for i in range(n):
        a, b = i * win, min((i + 1) * win, duration)
        m = (ts >= a) & (ts < b)
        if not m.any():
            continue
        f = {
            "motion": float(motion[m].max()),
            "face": float(face[m].max()),
            "speech": float(min(1.0, sum(max(0, min(b, we) - max(a, ws)) for ws, we in words) / (b - a))),
            "sound_peak": float(max([min(1, p["above_median_db"] / 24) for p in so["peaks"]
                                     if a <= p["t"] < b and not p.get("in_speech")], default=0)),
            "scene_start": float(any(a <= s0 < b for s0, _ in shots[1:])),
        }
        pen_blur = float(1 - sharp[m].mean())
        lm = float(luma[m].mean())
        pen_exp = float(max(0, 0.12 - lm) / 0.12 + max(0, lm - 0.92) / 0.08)
        sc = sum(weights[k] * v for k, v in f.items()) - weights["blur"] * pen_blur * 0.5 - weights["exposure"] * pen_exp
        out.append({"t": round(a + win / 2, 2), "score": round(sc, 3), **{k: round(v, 2) for k, v in f.items()},
                    "blur_pen": round(pen_blur, 2), "exposure_pen": round(pen_exp, 2)})
    return out


def reasons(w):
    r = []
    if w["sound_peak"] > 0.3:
        r.append("loud non-speech burst")
    if w["speech"] > 0.4:
        r.append("speech")
    if w["motion"] > 0.6:
        r.append("motion peak")
    if w["face"] > 0.3:
        r.append("face visible")
    if w["scene_start"]:
        r.append("shot start")
    if w["blur_pen"] > 0.6:
        r.append("(soft focus)")
    return ", ".join(r) or "baseline"


def propose(prod: Production, pillar="default", top=12, min_gap=1.5):
    weights = config.MOMENT_WEIGHTS.get(pillar, config.MOMENT_WEIGHTS["default"])
    sources = json.loads((prod.root / "source" / "sources.json").read_text())
    cands = []
    for s in sources:
        if s["kind"] != "video":
            continue
        stem = s["file"].rsplit(".", 1)[0]
        adir = prod.root / "analysis" / stem
        if not (adir / "visual.json").exists():
            continue
        for w in score_clip(adir, s["info"]["duration"], weights):
            cands.append({"src": s["file"], "stem": stem, **w})
    cands.sort(key=lambda c: -c["score"])
    picked = []
    for c in cands:
        if all(c["src"] != p["src"] or abs(c["t"] - p["t"]) >= min_gap for p in picked):
            dur = next(s["info"]["duration"] for s in sources if s["file"] == c["src"])
            c["window"] = [round(max(0, c["t"] - 1.0), 2), round(min(dur, c["t"] + 1.5), 2)]
            c["why"] = reasons(c)
            picked.append(c)
        if len(picked) >= top:
            break
    out = {"pillar": pillar, "weights": weights, "note": "Proposals only. Claude chooses and explains in plan/decisions.md.",
           "moments": [{"rank": i + 1, **c} for i, c in enumerate(picked)]}
    (prod.d("analysis") / "moments.json").write_text(json.dumps(out, indent=1))
    # thumbnail sheet: one frame per proposed moment, labelled rank/clip/time
    by_src = {}
    for i, c in enumerate(picked):
        by_src.setdefault(c["src"], []).append((i, c))
    frames = []
    for src, items in by_src.items():
        proxy = prod.root / next(s["proxy"] for s in sources if s["file"] == src)
        for i, c in items:
            frames.append((i, proxy, c))
    frames.sort()
    if frames:
        import tempfile
        from pathlib import Path
        import cv2
        import numpy as np
        tiles = []
        with tempfile.TemporaryDirectory() as td:
            for i, proxy, c in frames:
                o = sheet(proxy, [c["t"]], Path(td) / f"{i}.jpg", cols=1,
                          labels=[f"#{c['rank'] if 'rank' in c else i + 1} {c['stem'][:12]} {c['t']:.1f}s"])
                if o:
                    tiles.append(cv2.imread(str(o)))
        if tiles:
            h = max(t.shape[0] for t in tiles)
            w = max(t.shape[1] for t in tiles)
            tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, w - t.shape[1], cv2.BORDER_CONSTANT,
                                        value=(255, 255, 255)) for t in tiles]
            while len(tiles) % 4:
                tiles.append(np.full_like(tiles[0], 255))
            cv2.imwrite(str(prod.root / "analysis" / "moments_sheet.jpg"),
                        np.vstack([np.hstack(tiles[k:k + 4]) for k in range(0, len(tiles), 4)]))
    prod.mark("moments", proposed=len(picked), pillar=pillar)
    return out
