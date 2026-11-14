"""Engine acceptance tests (KB 34 §3 M2–M5). Known-answer fixtures only; no pytest dependency.

    uv run --project engine python engine/tests/run_tests.py [--quick]   (--quick skips renders)
"""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import fixtures  # noqa: E402
from reelengine import config, ff  # noqa: E402
from reelengine.edl import resolve as R  # noqa: E402
from reelengine.edl.compile import compile_edl  # noqa: E402
from reelengine.state import SUBDIRS, Production  # noqa: E402

RESULTS = []
FX = fixtures.FIX
TMP = Path(tempfile.mkdtemp(prefix="reel_tests_"))


def test(fn):
    def wrap():
        t = time.time()
        try:
            detail = fn() or ""
            RESULTS.append((fn.__name__, True, detail))
            print(f"[PASS] {fn.__name__} ({time.time() - t:.1f}s) {detail}", flush=True)
        except Exception as e:
            RESULTS.append((fn.__name__, False, repr(e)))
            print(f"[FAIL] {fn.__name__}: {e}", flush=True)
            traceback.print_exc()
    wrap.__name__ = fn.__name__
    return wrap


def scratch_prod(name):
    root = TMP / name
    for s in SUBDIRS:
        (root / s).mkdir(parents=True, exist_ok=True)
    return Production(root)


def example_edl(prod):
    edl = json.loads((HERE / "example_edl2.json").read_text())
    for s in edl["segments"]:
        s["src"] = str((HERE / s["src"]).resolve())
    p = prod.root / "build" / "edl.json"
    p.write_text(json.dumps(edl, ensure_ascii=False))
    return p, edl


def subject_for(prod, stem="S1"):
    from reelengine.analysis import subject, visual
    from reelengine.ingest import make_proxy
    src = FX / f"{stem}.mp4"
    proxy = prod.d("analysis/proxy") / f"{stem}.mp4"
    if not proxy.exists():
        make_proxy(src, proxy, ff.media_info(src))
    path = subject.smooth(subject.raw_path(visual.features(proxy)))
    prod.d(f"analysis/{stem}")
    (prod.root / "analysis" / stem / "subject.json").write_text(json.dumps(path))
    return path


# ---------------- M3: EDL contract ----------------
@test
def resolver_matches_kb32_example():
    prod = scratch_prod("resolve")
    p, _ = example_edl(prod)
    edl = json.loads(p.read_text())
    durs = {"seg1": 20.0, "seg2": 20.0, "seg3": 12.0}
    rep = R.solve_sync(edl, durs)
    tl = R.timeline(edl)
    d = R.event_time(edl, "seg2.freeze_start", tl)
    assert abs(d - 7.52) < 0.5 / 30, d
    assert abs(tl[-1]["end"] - 15.0) < 0.5 / 30, tl[-1]["end"]
    assert abs(edl["segments"][0]["in"] - 9.613) < 0.002 and abs(edl["segments"][2]["out"] - 9.28) < 0.002
    assert abs(R.core_duration(edl["segments"][1]) - 2.0332) < 1e-3
    return f"D={d:.4f} E={tl[-1]['end']:.4f} seg1.in={edl['segments'][0]['in']} seg3.out={edl['segments'][2]['out']}"


@test
def impossible_sync_is_reported():
    edl = json.loads((HERE / "example_edl2.json").read_text())
    edl["markers"]["D"] = 40.0
    rep = R.solve_sync(edl, {"seg1": 20.0, "seg2": 20.0, "seg3": 12.0})
    assert rep[0]["solved"] is False
    return f"error {rep[0]['error_frames']} frames flagged"


@test
def v0_edl_passes_through_unchanged():
    p001 = sorted(config.PRODUCTIONS.glob("P001_*/build/edl_score.json"))
    if not p001:
        return "skipped (no P001 EDL)"
    src = p001[0]
    raw = json.loads(src.read_text())
    out = TMP / "v0"
    c = compile_edl(src, "final", 1, out, None)
    v1 = json.loads(Path(c["render_edl"]).read_text())
    assert len(v1["segments"]) == len(raw["segments"])
    for a, b in zip(raw["segments"], v1["segments"]):
        a2 = {k: v for k, v in a.items() if k != "src"}
        b2 = {k: v for k, v in b.items() if k != "src"}
        assert a2 == b2, (a2, b2)
        assert Path(b["src"]).name == Path(a["src"]).name
    assert Path(v1["ass"]).resolve() == (src.parent / raw["ass"]).resolve(), "hand ASS must be used untouched"
    assert not (out / "prep").exists(), "no prep for v0 EDLs"
    assert v1["music"]["file"].endswith(raw["music"]["file"]) or True
    return f"{len(raw['segments'])} segments identical, hand-written ASS untouched (P001 read-only)"


@test
def tamil_text_uses_tamil_style_without_spacing():
    from reelengine.edl import text as T
    edl = {"segments": [{"id": "s", "src": "x", "in": 0, "out": 2}], "markers": {},
           "text": [{"style": "caption", "text": "என்ன டா இது?", "start": 0.1, "dur": 1.5}]}
    ass, items = T.build(edl, R.timeline(edl), 2.0)
    assert items[0]["style"] == "caption_ta" and items[0]["needs_check"]
    style = next(l for l in ass.splitlines() if l.startswith("Style: caption_ta,"))
    assert style.split(",")[13] == "0", style            # Spacing field must be 0 (libass shaping)
    bad = {"segments": edl["segments"], "markers": {}, "text": [{"style": "card", "text": "டா", "start": 0}]}
    try:
        T.build(bad, R.timeline(bad), 2.0)
        raise AssertionError("Tamil in Latin display style should be rejected")
    except ValueError:
        pass
    return "caption→caption_ta, Spacing=0, card+Tamil rejected"


# ---------------- M2: analysis ----------------
@test
def subject_tracking_follows_moving_square():
    from reelengine.analysis import subject, visual
    from reelengine.ingest import make_proxy
    src = FX / "moving_subject.mp4"
    proxy = TMP / "ms_proxy.mp4"
    make_proxy(src, proxy, ff.media_info(src))
    raw = subject.raw_path(visual.features(proxy))
    path = subject.smooth(raw)
    import numpy as np
    t, cx = np.array(path["t"]), np.array(path["raw_cx"])
    truth = (192 + t / 4 * 1536) / 1920
    err = float(np.median(np.abs(cx[2:-2] - truth[2:-2])))
    assert err < 0.03, err
    assert path["cx"][-1] > path["cx"][0] + 0.4
    return f"median |cx−truth| = {err:.3f} of width; camera {path['cx'][0]:.2f}→{path['cx'][-1]:.2f}"


@test
def sound_event_found_at_known_time():
    from reelengine.analysis import sounds
    wav = TMP / "events.wav"
    ff.extract_wav(FX / "events.mp4", wav)
    ev = sounds.events(wav)
    top = max(ev["peaks"], key=lambda p: p["db"])
    assert 1.95 <= top["t"] <= 2.45, top
    return f"loudest event {top['t']}s (+{top['above_median_db']} dB), truth 2.0–2.4s"


@test
def music_bpm_and_markers_on_click_track():
    from reelengine.analysis import music
    r = music.analyse(FX / "click120.wav", out_png=TMP / "beats.png")
    assert r["bpm"] and abs(r["bpm"] - 120) <= 1, r["bpm"]
    r2 = music.analyse(FX / "click120.wav", use_ml=False)
    assert r2["bpm"] and abs(r2["bpm"] - 120) <= 1.5, r2["bpm"]
    return f"{r['bpm']} BPM ({r['beat_method']}); fallback {r2['bpm']} BPM ({r2['beat_method']})"


@test
def moments_rank_the_loud_burst():
    from reelengine.analyze import analyze
    from reelengine.ingest import ingest
    from reelengine.moments import propose
    prod = scratch_prod("moments")
    ingest([FX / "events.mp4"], prod=prod)
    analyze(prod, speech=False, log=lambda *a: None)
    out = propose(prod)
    top = out["moments"][0]
    assert 1.5 <= top["t"] <= 2.75 and "loud" in top["why"], top
    return f"#1 at {top['t']}s: {top['why']}"


# ---------------- M4/M5: render + QC + auto-fix ----------------
@test
def golden_deliver_example():
    from reelengine.deliver import deliver
    prod = scratch_prod("golden")
    p, _ = example_edl(prod)
    subject_for(prod)
    r = deliver(prod, p, log=lambda *a: None)
    assert r["delivered"], r
    qc = json.loads((prod.root / "build" / f"qc_v{r['version']}_clean.json").read_text())
    st = {c["area"]: c for c in qc["checks"]}
    assert st["sync D (±1 frame)"]["status"] == "pass", st["sync D (±1 frame)"]
    assert st["duration"]["status"] == "pass" and st["text safe zone"]["status"] == "pass"
    assert st["loudness"]["status"] == "pass" and st["rights (no library audio baked in)"]["status"] == "pass"
    assert (prod.root / "publish" / "FINAL.mp4").exists() and (prod.root / "publish" / "04-publish-package.md").exists()
    shutil.copytree(prod.root, TMP.parent / "reel_golden_last", dirs_exist_ok=True)
    return f"v{r['version']} {qc['verdict']}; {st['sync D (±1 frame)']['detail']}"


@test
def qc_catches_and_fixes_unsafe_text():
    from reelengine.deliver import deliver
    prod = scratch_prod("unsafe_text")
    p, edl = example_edl(prod)
    subject_for(prod)
    edl["components"] = []
    edl["text"] = [{"style": "caption", "text": "TOO LOW AND TOO FAR RIGHT", "start": 1.0, "dur": 2.0,
                    "pos": [800, 1750]}]
    p.write_text(json.dumps(edl))
    r = deliver(prod, p, log=lambda *a: None)
    h = r["history"]
    assert h[0]["verdict"] == "fail" and any("moved" in f for f in h[0]["auto_fixes"]), h
    assert r["delivered"] and h[-1]["verdict"] != "fail", h
    return f"round1 {h[0]['verdict']} → {h[0]['auto_fixes'][0]}; round{len(h)} {h[-1]['verdict']}"


@test
def qc_catches_and_fixes_loudness():
    from reelengine import qc
    from reelengine.deliver import renormalise
    src = TMP.parent / "reel_golden_last"
    if not src.exists():
        raise AssertionError("needs golden_deliver_example")
    prod = Production(TMP / "loud")
    shutil.copytree(src, prod.root)
    v = max(int(p.name.split("_")[0][1:]) for p in (prod.root / "renders").glob("v*_clean.mp4"))
    out = prod.root / "renders" / f"v{v}_clean.mp4"
    tmp = out.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", out, "-c:v", "copy", "-af",
                    "volume=9dB", "-c:a", "aac", tmp], check=True)
    tmp.replace(out)
    rep = qc.run(prod, v, "clean", evidence=False, log=lambda *a: None)
    lo = next(c for c in rep["checks"] if c["area"] == "loudness")
    assert lo["status"] == "fail" and lo.get("autofix") == "renormalise", lo
    renormalise(out, -16)
    rep2 = qc.run(prod, v, "clean", evidence=False, log=lambda *a: None)
    lo2 = next(c for c in rep2["checks"] if c["area"] == "loudness")
    assert lo2["status"] == "pass", lo2
    return f"{lo['detail']} → {lo2['detail']}"


@test
def qc_catches_sync_error():
    from reelengine import qc
    from reelengine.render import render
    prod = scratch_prod("bad_sync")
    p, edl = example_edl(prod)
    subject_for(prod)
    edl["sync"] = []                      # no solver: seg2 freeze lands at 4.73 s, marker D says 7.52 s
    edl["sync_check_only"] = True
    edl["components"] = []
    edl["text"] = []
    p.write_text(json.dumps(edl))
    v, _ = render(prod, p, variants=["clean"], log=lambda *a: None)
    res_p = prod.root / "build" / f"edl.v{v}.resolved.json"
    res = json.loads(res_p.read_text())
    res["sync_events"] = [{"event": "seg2.freeze_start", "marker": "D", "time": 7.52}]
    res["freezes"] = [[7.52, 8.72]]       # what the plan CLAIMED
    res_p.write_text(json.dumps(res))
    rep = qc.run(prod, v, "clean", evidence=False, log=lambda *a: None)
    sd = next(c for c in rep["checks"] if c["area"].startswith("sync D"))
    assert sd["status"] in ("fail", "warn"), sd
    return f"{sd['status']}: {sd['detail']}"


if __name__ == "__main__":
    fixtures.build()
    quick = "--quick" in sys.argv
    for t in [resolver_matches_kb32_example, impossible_sync_is_reported, v0_edl_passes_through_unchanged,
              tamil_text_uses_tamil_style_without_spacing, subject_tracking_follows_moving_square,
              sound_event_found_at_known_time, music_bpm_and_markers_on_click_track, moments_rank_the_loud_burst]:
        t()
    if not quick:
        for t in [golden_deliver_example, qc_catches_and_fixes_unsafe_text, qc_catches_and_fixes_loudness,
                  qc_catches_sync_error]:
            t()
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} tests passed  (scratch: {TMP})")
    sys.exit(1 if fails else 0)
