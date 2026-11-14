"""Stage 4: analyse a reference audio (timing only) and keep the machine-readable audio record (KB 31 §4)."""
import json
import shutil
from pathlib import Path

from .analysis import music
from .state import Production, now


def analyse_reference(prod: Production, ref, start=0.0, dur=None, rights="in_app_library", name=None, role=None,
                      evidence=None, use_ml=True, log=print):
    ref = Path(ref).resolve()
    adir = prod.d("audio")
    if ref.parent != adir:
        dst = adir / ref.name
        if not dst.exists():
            shutil.copy2(ref, dst)          # reference copy: timing only, never uploaded (KB 31 §5)
        ref = dst
    res = music.analyse(ref, start=start, dur=dur, out_png=adir / "beats_plot.png", use_ml=use_ml)
    res["rights_path"] = rights
    (adir / "music.json").write_text(json.dumps(res, indent=1))
    rec_path = adir / "audio_candidates.json"
    recs = json.loads(rec_path.read_text()) if rec_path.exists() else []
    rec = {"audio_key": f"aud_{now()[:10]}_{(name or ref.stem)[:24].replace(' ', '_').lower()}",
           "title": name or ref.stem, "role": role, "rights_path": rights,
           "observations": evidence or [],
           "trend_stage": "unknown" if not evidence else None,
           "reference_audio": {"path": str(ref.relative_to(prod.root)), "origin": "provided", "use": "timing_only",
                               "start": start},
           "analysis": {"bpm": res["bpm"], "beat_method": res["beat_method"], "markers": res["markers"]},
           "in_app_start": start, "selected": True}
    recs = [dict(r, selected=False) for r in recs if r.get("audio_key") != rec["audio_key"]] + [rec]
    rec_path.write_text(json.dumps(recs, indent=1, ensure_ascii=False))
    prod.mark("audio", reference=ref.name, bpm=res["bpm"], method=res["beat_method"])
    log(f"  {ref.name}: {res['bpm']} BPM ({res['beat_method']}), markers {res['markers']}, "
        f"{len(res['downbeats'])} downbeats")
    return res
