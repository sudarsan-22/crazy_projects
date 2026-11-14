"""Loudness envelope + non-speech sound events (laughs, shouts, thumps, revs) from a source WAV."""
import numpy as np
import soundfile as sf


def envelope(wav, hop_s=0.05):
    y, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    y = y.mean(axis=1)
    hop = int(sr * hop_s)
    n = len(y) // hop
    if n == 0:
        return np.array([]), np.array([])
    frames = y[: n * hop].reshape(n, hop)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    t = (np.arange(n) + 0.5) * hop_s
    return t, db


def events(wav, speech=None, min_gap=0.5, jump_db=12.0, floor_db=-35.0):
    t, db = envelope(wav)
    if len(t) == 0:
        return {"hop_s": 0.05, "median_db": None, "peaks": [], "envelope_10hz": []}
    med = float(np.median(db))
    spans = [(s["start"], s["end"]) for s in (speech or {}).get("segments", [])]

    def in_speech(x):
        return any(a - 0.1 <= x <= b + 0.1 for a, b in spans)
    peaks = []
    for i in range(1, len(db) - 1):
        if db[i] >= db[i - 1] and db[i] >= db[i + 1] and db[i] > floor_db and db[i] - med >= jump_db:
            if peaks and t[i] - peaks[-1]["t"] < min_gap:
                if db[i] > peaks[-1]["db"]:
                    peaks[-1] = {"t": round(float(t[i]), 2), "db": round(float(db[i]), 1)}
                continue
            peaks.append({"t": round(float(t[i]), 2), "db": round(float(db[i]), 1)})
    for p in peaks:
        p["above_median_db"] = round(p["db"] - med, 1)
        p["in_speech"] = in_speech(p["t"])
    env10 = [round(float(x), 1) for x in db[::2]]
    return {"hop_s": 0.05, "median_db": round(med, 1), "peaks": peaks, "envelope_10hz": env10}
