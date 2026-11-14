"""Install smoke tests (KB doc 33 §8). Every check prints PASS/FAIL with the measured value.

    uv run --project engine python engine/tests/smoke.py [--t2]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import fixtures  # noqa: E402
from reelengine import config  # noqa: E402

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)


def t1():
    import numpy, cv2, av, scenedetect, librosa, soundfile, pyloudnorm, pydantic  # noqa: F401
    vers = {m.__name__: m.__version__ for m in (numpy, cv2, av, scenedetect, librosa, pydantic)}
    check("python 3.12", sys.version_info[:2] == (3, 12), sys.version.split()[0])
    check("core imports", True, json.dumps(vers))
    check("OpenCV YuNet API", hasattr(cv2, "FaceDetectorYN"), "cv2.FaceDetectorYN")
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    need = ["xfade", "ass", "subtitles", "drawtext", "loudnorm", "scdet", "zscale", "minterpolate"]
    have = [n for n in need if any(line.split()[1:2] == [n] for line in out.splitlines() if line.strip())]
    check("ffmpeg filters", len(have) == len(need), f"{len(have)}/{len(need)} {sorted(set(need) - set(have)) or ''}")

    fx = fixtures.build()
    truth = json.loads((fx / "truth.json").read_text())

    # PySceneDetect 0.7 + OpenCV 5
    from scenedetect import detect, AdaptiveDetector
    scenes = detect(str(fx / "cuts.mp4"), AdaptiveDetector())
    cuts = [s[0].seconds for s in scenes[1:]]
    want = truth["cuts.mp4"]["cuts"]
    ok = len(cuts) == len(want) and all(abs(a - b) <= 1 / 30 + 1e-6 for a, b in zip(cuts, want))
    check("PySceneDetect AdaptiveDetector (±1 frame)", ok, f"found {[round(c, 3) for c in cuts]} want {want}")
    scenes_av = detect(str(fx / "cuts.mp4"), AdaptiveDetector(), backend="pyav")
    cuts_av = [s[0].seconds for s in scenes_av[1:]]
    check("PySceneDetect pyav backend", len(cuts_av) == len(want), f"{[round(c, 3) for c in cuts_av]}")

    # PyAV on VFR
    with av.open(str(fx / "vfr.mp4")) as c:
        ts = [float(f.pts * f.time_base) for f in c.decode(video=0)]
    mono = all(b > a for a, b in zip(ts, ts[1:]))
    cnt = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(fx / "vfr.mp4")],
                         capture_output=True, text=True).stdout.strip()
    check("PyAV VFR decode", mono and len(ts) == int(cnt), f"{len(ts)} frames (ffprobe {cnt}), monotonic={mono}")

    # librosa tempo on click track
    # hop 256 @ 22.05 kHz (11.6 ms). At the default hop 512 the autocorrelation lag grid can't express
    # 120 BPM exactly (117.45 / 123.05), so the engine uses hop 256 + BPM from beat intervals.
    y, sr = librosa.load(str(fx / "click120.wav"), sr=22050)
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
    tempo = float(numpy.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr, hop_length=256))[0])
    _, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=256, units="time")
    bpm_iv = 60 / float(numpy.median(numpy.diff(beats)))
    ph = numpy.abs(((beats - truth["click120.wav"]["first_beat"]) + 0.25) % 0.5 - 0.25)
    check("librosa tempo 120±1", abs(tempo - 120) <= 1 and abs(bpm_iv - 120) <= 1,
          f"tempo() {tempo:.2f} BPM, beat-interval {bpm_iv:.2f} BPM, median beat error {numpy.median(ph) * 1000:.0f} ms")

    # YuNet face detector loads and runs
    if config.YUNET.exists():
        det = cv2.FaceDetectorYN.create(str(config.YUNET), "", (320, 320))
        img = numpy.zeros((320, 320, 3), numpy.uint8)
        _, faces = det.detect(img)
        check("YuNet model runs", True, f"faces on blank image: {0 if faces is None else len(faces)}")
    else:
        check("YuNet model present", False, str(config.YUNET))

    # ASS render with fontsdir: Anton, Poppins, Noto Sans Tamil
    with tempfile.TemporaryDirectory() as td:
        ass = Path(td) / "t.ass"
        ass.write_text(
            "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n"
            "Style: A,Anton,150,&H0000C4FF,&H0,&H0,&H0,0,0,0,0,100,100,0,0,1,6,0,5,0,0,0,1\n"
            "Style: P,Poppins ExtraBold,90,&H00FFFFFF,&H0,&H0,&H0,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1\n"
            "Style: T,Noto Sans Tamil Black,90,&H00FFFFFF,&H0,&H0,&H0,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1\n"
            "Style: M,Montserrat ExtraBold,80,&H00FFFFFF,&H0,&H0,&H0,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:01.00,A,,0,0,0,,{\\pos(540,600)}MASS HERO\n"
            "Dialogue: 0,0:00:00.00,0:00:01.00,P,,0,0,0,,{\\pos(540,850)}Poppins Bold\n"
            "Dialogue: 0,0:00:00.00,0:00:01.00,M,,0,0,0,,{\\pos(540,1050)}Montserrat XB\n"
            "Dialogue: 0,0:00:00.00,0:00:01.00,T,,0,0,0,,{\\pos(540,1250)}என்ன டா இது?\n")
        png = HERE / "fixtures" / "font_check.png"
        p = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "color=c=0x223344:s=1080x1920:d=1",
                            "-vf", f"subtitles={ass}:fontsdir={config.FONTS_DIR}", "-frames:v", "1", str(png)],
                           capture_output=True, text=True)
        fallback = [ln for ln in p.stderr.splitlines() if "fontselect" in ln and "Using default" in ln]
        check("ASS fonts resolve (no fallback)", p.returncode == 0 and not fallback,
              f"{png.name} written; fallbacks: {fallback or 'none'}")


def t2():
    import numpy
    fx = fixtures.FIX
    import torch, torchaudio  # noqa: F401
    check("torch CPU build", not torch.cuda.is_available() and "+cpu" in torch.__version__,
          f"torch {torch.__version__}, torchaudio {torchaudio.__version__}")
    from beat_this.inference import File2Beats
    f2b = File2Beats(checkpoint_path="final0", device="cpu", dbn=False)
    beats, downbeats = f2b(str(fx / "click120.wav"))
    period = float(numpy.median(numpy.diff(beats)))
    phase = numpy.abs(((numpy.asarray(beats) + 0.25) % 0.5) - 0.25)
    check("Beat This! beats ±20 ms", abs(60 / period - 120) <= 1 and numpy.median(phase) <= 0.02,
          f"{60 / period:.2f} BPM, median beat error {numpy.median(phase) * 1000:.1f} ms, "
          f"{len(beats)} beats, {len(downbeats)} downbeats")
    from reelengine.analysis.speech import transcribe
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "e16.wav"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(fx / "events.mp4"), "-ac", "1",
                        "-ar", "16000", str(wav)], check=True)
        r = transcribe(wav, model="small")
    check("faster-whisper runs (small, int8, array input)", "segments" in r,
          f"lang={r['language']} p={r['language_probability']}, {len(r['segments'])} segments on tone-only audio, "
          f"{r['wall_s']} s")


if __name__ == "__main__":
    t1()
    if "--t2" in sys.argv:
        t2()
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} checks passed")
    sys.exit(1 if fails else 0)
