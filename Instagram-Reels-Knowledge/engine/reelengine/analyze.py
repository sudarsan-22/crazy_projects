"""Stage 2: run every analysis adapter per source clip → productions/P###/analysis/<clip>/*.json."""
import json
import time

from . import ff
from .analysis import scenes, sounds, subject, visual
from .state import Production


def _dump(path, obj):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False))


def analyze(prod: Production, speech=True, model="large-v3-turbo", language=None, only=None, log=print):
    sources = json.loads((prod.root / "source" / "sources.json").read_text())
    summary = {}
    for s in sources:
        if s["kind"] != "video" or not s.get("proxy"):
            continue
        stem = s["file"].rsplit(".", 1)[0]
        if only and stem not in only:
            continue
        out = prod.d(f"analysis/{stem}")
        proxy = prod.root / s["proxy"]
        t0 = time.time()
        timings = {}

        t = time.time()
        sh = scenes.shots(proxy)
        _dump(out / "scenes.json", sh)
        timings["scenes"] = round(time.time() - t, 1)

        t = time.time()
        vis = visual.features(proxy)
        _dump(out / "visual.json", vis)
        timings["visual"] = round(time.time() - t, 1)

        path = subject.smooth(subject.raw_path(vis))
        path["source_w"], path["source_h"] = s["info"]["width"], s["info"]["height"]
        _dump(out / "subject.json", path)

        sp = None
        if speech and s.get("wav16"):
            t = time.time()
            try:
                from .analysis import speech as speech_mod
                sp = speech_mod.transcribe(prod.root / s["wav16"], model=model, language=language)
            except ImportError as e:
                sp = {"error": f"speech model unavailable: {e}", "segments": []}
            _dump(out / "speech.json", sp)
            timings["speech"] = round(time.time() - t, 1)
        if s.get("wav48"):
            _dump(out / "sounds.json", sounds.events(prod.root / s["wav48"], sp))

        # contact sheet: one frame per shot (max 12) for Claude's review
        mids = [(a + b) / 2 for a, b in sh][:12] or [s["info"]["duration"] / 2]
        sheet(proxy, mids, out / "shots_sheet.jpg")
        timings["total"] = round(time.time() - t0, 1)
        summary[stem] = {"duration": s["info"]["duration"], "shots": len(sh),
                         "subject_coverage": path["coverage"], "subject_sources": path["sources"],
                         "speech_seconds": (sp or {}).get("speech_seconds"), "language": (sp or {}).get("language"),
                         "timings_s": timings}
        log(f"  {stem}: {len(sh)} shots, subject coverage {path['coverage']:.0%}, "
            f"speech {(sp or {}).get('speech_seconds')} s, {timings['total']} s")
    _dump(prod.d("analysis") / "summary.json", summary)
    prod.mark("analyzed", clips=len(summary), model=model if speech else None)
    return summary


def sheet(video, times, out, cols=4, width=270, labels=None):
    """Tile frames at `times` into one JPG with time labels (OpenCV, no extra deps)."""
    import tempfile
    from pathlib import Path

    import cv2
    import numpy as np
    tiles = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(times):
            p = Path(td) / f"{i}.jpg"
            try:
                ff.frame_at(video, t, p, vf=f"scale={width}:-2")
                img = cv2.imread(str(p))
            except ff.FFError:
                img = None
            if img is None:
                continue
            lab = labels[i] if labels else f"{t:.1f}s"
            cv2.rectangle(img, (0, 0), (img.shape[1], 26), (0, 0, 0), -1)
            cv2.putText(img, lab[:34], (5, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            tiles.append(img)
    if not tiles:
        return None
    h = max(t.shape[0] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiles]
    while len(tiles) % cols:
        tiles.append(np.full_like(tiles[0], 255))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
    return out
