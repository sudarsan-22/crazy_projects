"""Music analysis of a REFERENCE audio (timing only, never uploaded; KB 31 §5).

Beats/downbeats: Beat This! (MIT) when installed, else librosa (hop 256). Energy, onsets, sections: librosa.
Markers follow KB 24 §3: H hook start, B build, D drop, S switch (planned by Claude), E end/loop.
All times are relative to the analysed start point (= video 0.0 s = in-app audio start point).
"""
import tempfile
from pathlib import Path

import cv2
import numpy as np

from .. import ff

SR, HOP = 22050, 256


def _beats_beat_this(wav):
    from beat_this.inference import File2Beats
    f2b = File2Beats(checkpoint_path="final0", device="cpu", dbn=False)
    b, d = f2b(str(wav))
    return np.asarray(b, float), np.asarray(d, float), "beat_this final0"


def _beats_librosa(y):
    import librosa
    oenv = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    _, b = librosa.beat.beat_track(onset_envelope=oenv, sr=SR, hop_length=HOP, units="time")
    b = np.asarray(b, float)
    # no downbeat model: assume 4/4 and choose the phase whose beats carry the most low-end energy
    if len(b) >= 8:
        rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
        idx = np.clip((b * SR / HOP).astype(int), 0, len(rms) - 1)
        phase = int(np.argmax([rms[idx[k::4]].mean() for k in range(4)]))
        d = b[phase::4]
    else:
        d = b[:1]
    return b, d, "librosa beat_track (hop 256)"


def analyse(src, start=0.0, dur=None, out_png=None, use_ml=True):
    import librosa
    with tempfile.TemporaryDirectory() as td:
        wav = ff.extract_wav(src, Path(td) / "ref.wav", 44100, mono=False, start=start, dur=dur)
        y, _ = librosa.load(str(wav), sr=SR, mono=True)
        method = None
        if use_ml:
            try:
                beats, downs, method = _beats_beat_this(wav)
            except Exception as e:      # missing torch/model → documented fallback
                method = f"fallback ({type(e).__name__})"
        if method is None or method.startswith("fallback"):
            beats, downs, m2 = _beats_librosa(y)
            method = m2 if method is None else f"{m2} [{method}]"
    length = len(y) / SR
    bpm = 60.0 / float(np.median(np.diff(beats))) if len(beats) > 2 else None
    oenv = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    tempo_lr = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=SR, hop_length=HOP))[0])
    ambiguous = bool(bpm and (abs(bpm / tempo_lr - 2) < 0.08 or abs(bpm / tempo_lr - 0.5) < 0.04))

    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    rdb = 20 * np.log10(rms + 1e-6)
    tt = librosa.times_like(rms, sr=SR, hop_length=HOP)
    k = max(1, int(0.25 * SR / HOP))
    energy = np.convolve(rdb, np.ones(k) / k, mode="same")
    k1 = max(1, int(1.0 * SR / HOP))
    e1 = np.convolve(rdb, np.ones(k1) / k1, mode="same")
    rise = np.zeros_like(e1)
    rise[k1:] = e1[k1:] - e1[:-k1]
    drop_t = float(tt[int(np.argmax(rise))]) if len(rise) else 0.0
    snap = downs if len(downs) else beats
    if len(snap):
        j = int(np.argmin(np.abs(snap - drop_t)))
        if abs(snap[j] - drop_t) <= 0.6:
            drop_t = float(snap[j])

    y_p = librosa.effects.percussive(y)
    on_env = librosa.onset.onset_strength(y=y_p, sr=SR, hop_length=HOP)
    onsets = librosa.onset.onset_detect(onset_envelope=on_env, sr=SR, hop_length=HOP, backtrack=True, units="time")
    strength = on_env[np.clip((np.asarray(onsets) * SR / HOP).astype(int), 0, len(on_env) - 1)] if len(onsets) else []
    accents = sorted(zip(onsets, strength), key=lambda x: -x[1])[:16]

    try:
        mf = librosa.feature.mfcc(y=y, sr=SR, hop_length=HOP * 4, n_mfcc=13)
        nseg = int(np.clip(length // 8, 2, 8))
        bnd = librosa.segment.agglomerative(mf, nseg)
        sections = [round(float(x), 2) for x in librosa.frames_to_time(bnd, sr=SR, hop_length=HOP * 4)]
    except Exception:
        sections = []

    markers = {"H": round(float(downs[0]) if len(downs) else 0.0, 3), "D": round(drop_t, 3),
               "E": round(float(snap[snap <= length - 0.05][-1]) if len(snap) and (snap <= length - 0.05).any()
                          else length, 3)}
    builds = [s for s in sections if s < drop_t - 1.0]
    if builds:
        markers["B"] = builds[-1]
    res = {"source": str(src), "start": start, "duration": round(length, 3), "beat_method": method,
           "bpm": round(bpm, 2) if bpm else None, "librosa_tempo": round(tempo_lr, 2), "tempo_ambiguous": ambiguous,
           "beats": [round(float(b), 3) for b in beats], "downbeats": [round(float(d), 3) for d in downs],
           "accents": [{"t": round(float(a), 3), "strength": round(float(s), 2)} for a, s in accents],
           "sections": sections, "markers": markers,
           "energy_4hz": [round(float(e), 1) for e in energy[:: max(1, int(SR / HOP / 4))]],
           "note": "Estimates. Confirm by ear before final cuts (KB 24)."}
    if out_png:
        plot(res, tt, energy, out_png)
    return res


def plot(res, tt, energy, out_png, cuts=None, W=1800, H=420):
    """Sync plot: energy curve, beat ticks, downbeats (thick), markers (labelled), measured cuts (red)."""
    img = np.full((H, W, 3), 255, np.uint8)
    L = max(res["duration"], 1e-3)
    X = lambda t: int(20 + (W - 40) * t / L)  # noqa: E731
    e = np.asarray(energy, float)
    if len(e):
        lo, hi = np.percentile(e, 2), e.max() + 1e-6
        pts = np.array([[X(t), int(H - 60 - (H - 120) * (v - lo) / (hi - lo))] for t, v in zip(tt, np.clip(e, lo, hi))])
        cv2.polylines(img, [pts.reshape(-1, 1, 2)], False, (180, 120, 40), 2)
    for b in res["beats"]:
        cv2.line(img, (X(b), H - 50), (X(b), H - 35), (120, 120, 120), 1)
    for d in res["downbeats"]:
        cv2.line(img, (X(d), H - 55), (X(d), H - 25), (0, 0, 0), 2)
    for k, t in res["markers"].items():
        cv2.line(img, (X(t), 10), (X(t), H - 60), (0, 160, 0), 2)
        cv2.putText(img, k, (X(t) + 4, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 120, 0), 2)
    for c in cuts or []:
        cv2.line(img, (X(c), 40), (X(c), H - 20), (0, 0, 255), 1)
    for s in range(0, int(L) + 1):
        cv2.putText(img, f"{s}", (X(s) - 5, H - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (90, 90, 90), 1)
    cv2.putText(img, f"{res.get('bpm')} BPM  ({res['beat_method']})", (W - 520, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (60, 60, 60), 1)
    cv2.imwrite(str(out_png), img)
