"""Speech segments + word timings with faster-whisper (bundled Silero VAD). Tamil output = DRAFT only (KB 30 §2.5)."""
import time

_MODELS = {}


def load16(path):
    """16 kHz mono float32 array (ingest already writes *_16k.wav; resample anything else via ffmpeg)."""
    import numpy as np
    import soundfile as sf
    y, sr = sf.read(str(path), dtype="float32", always_2d=True)
    if sr != 16000:
        import subprocess
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar",
                              "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.float32).copy()
    return y.mean(axis=1)


def transcribe(wav16, model="large-v3-turbo", language=None, beam_size=5):
    from faster_whisper import WhisperModel
    if model not in _MODELS:
        _MODELS[model] = WhisperModel(model, device="cpu", compute_type="int8")
    t0 = time.time()
    # Pass a decoded array: faster-whisper 1.2.1's own decoder calls av.open(metadata_errors=...),
    # which PyAV 19 removed (found in the T2 smoke test, 2026-11-07).
    audio = load16(wav16)
    segs, info = _MODELS[model].transcribe(audio, language=language, vad_filter=True,
                                            word_timestamps=True, beam_size=beam_size,
                                            condition_on_previous_text=False)
    out = []
    for s in segs:
        words = [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                  "p": round(w.probability, 3)} for w in (s.words or [])]
        out.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
                    "avg_logprob": round(s.avg_logprob, 3), "no_speech_prob": round(s.no_speech_prob, 3),
                    "words": words})
    speech_s = sum(s["end"] - s["start"] for s in out)
    return {"model": model, "language": info.language, "language_probability": round(info.language_probability, 3),
            "duration": round(info.duration, 3), "speech_seconds": round(speech_s, 2),
            "segments": out, "low_confidence_words": sum(1 for s in out for w in s["words"] if w["p"] < 0.5),
            "wall_s": round(time.time() - t0, 1),
            "note": "Machine transcript. Tamil/Tanglish accuracy is limited: use for timing; captions need a human check."}
