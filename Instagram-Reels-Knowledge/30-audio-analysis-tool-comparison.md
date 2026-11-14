# 30 — Audio Analysis Tool Comparison

> **Phase 3b · Technical infrastructure** · Created 2026-11-07 · **Research only. Nothing has been installed.**
> Evidence tags: ✅ Official (project docs, PyPI metadata, GitHub API) · 🟡 Reported (incl. published research) · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here
> Infrastructure set: [29 video](29-video-processing-tool-comparison.md) · **30 audio** · [31 Instagram audio research](31-instagram-audio-research-methods.md) · [32 architecture](32-automated-editing-architecture.md) · [33 setup](33-environment-setup-guide.md) · [34 integration plan](34-tool-integration-plan.md)
> Sync and mixing *craft* (marker names H/B/D/S/E, sync hierarchy, levels) is defined in [24](24-beat-sync-and-sound-design.md). This document picks the software that measures and executes it.

---

## 1. Verdict

| Job | Selected | Fallback | Rejected |
|---|---|---|---|
| Beat + **downbeat** tracking | **Beat This!** (CPJKU, MIT, CPU OK) | librosa `beat_track` · existing stdlib [tools/audio_beats.py](tools/README.md) 🧪 | madmom (dead on Py 3.12), Essentia (AGPL + NC models) |
| BPM | Median inter-beat interval from Beat This!, cross-checked with `librosa.feature.tempo` | audio_beats.py | — |
| Energy curve, drop, sections | **librosa** (RMS, onset strength, spectral contrast, segmentation) | audio_beats.py energy curve | Essentia mood/energy models (non-commercial licence) |
| Onsets (accents, SFX hit points) | **librosa** `onset_detect(backtrack=True)` + HPSS for drum hits | FFmpeg level-jump method (audio_beats.py) | — |
| Dialogue / speech detection | **faster-whisper with its built-in Silero VAD** | standalone `silero-vad` | Audacity |
| Transcription with word timing (Tamil, English, Tanglish) | **faster-whisper** (`large-v3` or `large-v3-turbo`, CPU int8) | openai-whisper (slower) · WhisperX (better alignment, heavier) | — |
| Music vs speech vs laughter / pet / engine sounds | **MediaPipe Audio Classifier (YAMNet)**, optional | Loudness + VAD heuristics | — |
| Source separation (strip background music from your footage) | **Demucs** (adefossez fork, MIT code), optional | — | **Spleeter** (Python < 3.12, TensorFlow) |
| Loudness measurement | **FFmpeg `ebur128`** (authority) + **pyloudnorm** (in-Python checks) | — | — |
| Mixing, ducking, SFX placement, loudness normalisation | **FFmpeg filtergraph** (`amix`, `sidechaincompress`, `adelay`, `afade`, two-pass `loudnorm`) 🧪 | — | Audacity (GUI-bound), pedalboard (GPL, unnecessary) |

**Principle:** analysis tools only produce **numbers and timestamps** (JSON). Every audible change is rendered by FFmpeg in the same graph as the picture, so audio and video stay sample-locked.

---

## 2. Tool cards

### 2.1 librosa: ✅ **SELECTED (core music features)**
| Field | Detail |
|---|---|
| Website | https://librosa.org · docs https://librosa.org/doc/latest/ |
| GitHub | https://github.com/librosa/librosa |
| License | **ISC** ✅ |
| Version | **1.0.0** (2026-08-11), "the first 'stable' version". **Requires Python ≥ 3.12** ✅ |
| Breaking changes in 1.0 | **`audioread` backend removed**, plus other expired deprecations ✅. This means librosa reads through `soundfile`/libsndfile only, which **can't open AAC/MP4**. The engine extracts audio to WAV with FFmpeg first (we do this anyway) |
| Install | `uv pip install librosa` → pulls numba + llvmlite (~60 MB), scipy (~35 MB), scikit-learn, soundfile, soxr, pooch, msgpack |
| Capabilities | `beat.beat_track`, `feature.tempo`, `onset.onset_strength` / `onset_detect`, `feature.rms`, spectral centroid and contrast, `effects.hpss` (harmonic/percussive split → cleaner drum onsets), chroma / MFCC + `segment` (recurrence, agglomerative) for **section boundaries** (intro / hook / drop) |
| Limitations | The beat tracker is a classic DP method: weaker on syncopated Tamil kuthu and gaana percussion and on rubato film BGM 🔵. No downbeats. Tempo has half/double ambiguity |
| Integration | `analysis/music.py`: WAV → features at 100 Hz hop → `music.json` |

### 2.2 Beat This!: ✅ **SELECTED (beats + downbeats)** *(not in your original list. Added because it beats the alternatives on licence and maintenance)*
| Field | Detail |
|---|---|
| Paper | Foscarin, Schlüter, Widmer, *"Beat This! Accurate Beat Tracking Without DBN Postprocessing"*, ISMIR 2024 ✅ |
| GitHub | https://github.com/CPJKU/beat_this |
| License | **MIT for code *and* published weights** ✅ (training data has separate licences) |
| Version | 1.1.0 (2026-04-14) |
| Install | Needs PyTorch + torchaudio (CPU build is fine) → `uv pip install beat-this`. Checkpoints auto-download (`final*` ≈ 78 MB, `small*` ≈ 8 MB) ✅ |
| Capabilities | Beat **and downbeat** times. CLI `beat_this file -o out.beats`. Python `File2Beats(checkpoint_path="final0", device="cpu")`. **Falls back to CPU automatically** ✅ |
| Limitations | Pulls in PyTorch (a large install, see [33](33-environment-setup-guide.md)). Optional `--dbn` needs madmom (we won't use it). Not tested on Tamil film music by us. Validate on 5 real tracks first |
| Integration | `analysis/music.py` calls `File2Beats` → beats and downbeats. librosa adds energy and sections on the same timeline |

### 2.3 Essentia: ❌ **NOT SELECTED** (keep as a research option)
| Field | Detail |
|---|---|
| Website | https://essentia.upf.edu · models https://essentia.upf.edu/models.html |
| GitHub | https://github.com/MTG/essentia |
| License | **AGPL-3.0** library ✅. **Pretrained models: CC BY-NC-SA 4.0 (non-commercial)**, "also available under proprietary license upon request" ✅ |
| Version / Py 3.12 | Latest `2.1b6.dev1438` (2026-05-19) ships **only cp314 Linux wheels**. The **last cp312 Linux wheel is `2.1b6.dev1389` (2025-07-24)** ✅ (PyPI file list). On this machine it would have to be pinned to an old dev build |
| Capabilities | Excellent: `RhythmExtractor2013`, TempoCNN, key, loudness, and a large model zoo (danceability, mood happy/sad/aggressive, arousal/valence, genre, voice/instrumental) |
| Why rejected | (1) The model licence is **non-commercial**, so it's unusable once brand-deal Reels start (your account goal is still open, see [13](13-my-instagram-account-analysis.md)). (2) AGPL. (3) It would mean pinning a stale build on Python 3.12. librosa + Beat This! cover what we need |

### 2.4 Audacity: ❌ **NOT SELECTED** (manual tool only)
| Field | Detail |
|---|---|
| Website | https://www.audacityteam.org · scripting https://manual.audacityteam.org/man/scripting.html |
| GitHub | https://github.com/audacity/audacity |
| License | GPL (v3 for current releases, with some components GPL-2.0-or-later) 🟡 (GitHub reports "NOASSERTION") |
| Install | `sudo apt install audacity`, or the AppImage/Flatpak (not installed here) |
| Automation | **mod-script-pipe**: a named-pipe scripting module that drives a **running Audacity GUI** from Python 🔵/🟡 (manual page returned 403 to our fetch, so this isn't re-verified) |
| Why rejected | Automation needs the GUI open, it's fragile headless, and everything it would do (noise reduction, EQ, compression, normalisation, mixing) is available as FFmpeg filters inside the render graph ([24 §7](24-beat-sync-and-sound-design.md#7-voice-clean-up-chain-your-speech-in-reels)). **Useful to you manually** for listening, spectral inspection or recording a "bruh" sting, so it's worth installing later as a desktop app, not as pipeline infrastructure |

### 2.5 Whisper family: ✅ **SELECTED: faster-whisper**
| | **faster-whisper** ✅ | openai-whisper | WhisperX (optional) |
|---|---|---|---|
| GitHub | https://github.com/SYSTRAN/faster-whisper | https://github.com/openai/whisper | https://github.com/m-bain/whisperX |
| License | MIT (code). Converted Whisper weights MIT ✅ | MIT (code + weights) ✅ | BSD-2-Clause ✅. Its diarisation models (pyannote) are **gated on Hugging Face** |
| Version | 1.2.1 (2025-10-31) | 20250625 | 3.8.6 (2026-05-25), Py 3.10–3.13 |
| Engine | CTranslate2 (**no PyTorch needed**), int8 on CPU | PyTorch | faster-whisper + wav2vec2 forced alignment |
| Built-ins | **`word_timestamps=True`**, **`vad_filter=True` (Silero VAD bundled as ONNX)**, language ID ✅ | word timestamps | Sharper word timing, speaker labels |
| Install | `uv pip install faster-whisper` (ctranslate2 ~43 MB, onnxruntime ~24 MB, tokenizers, huggingface-hub, av) | `uv pip install openai-whisper` (+ torch) | heavy (torch, pyannote) |
| Models (Hugging Face cache) | `large-v3` **3.09 GB** · `large-v3-turbo` **1.62 GB** · `small` 0.49 GB ✅ (HF API sizes) | same family | same + alignment model |

**Tamil reality check (🟡 published research, 2026):**
- A paired evaluation of Erode vs common spoken Tamil found Whisper at **≈19% character error rate**, preserving meaning in **only about half** of sentences ([NeurIPS 2026 paper page](https://neurips.cc/virtual/2026/162431)).
- On Sri Lankan Tamil, zero-shot Whisper large-v3 mean WER ranged from **0.67 to 0.90** across districts ([TaLK corpus, LREC 2026](https://aclanthology.org/people/adsajan-thillainathan/)).
- **Consequence:** Tamil transcripts are **drafts, never final captions**. The pipeline uses them for **timing** (where speech is, where words start) and **rough meaning**. In Autonomous Mode ([26](26-video-production-workflow.md)), Claude prefers Tanglish or English caption text it can write confidently. Any Tamil-script text is **flagged in the delivery note for you to check before posting**, as doc 23 §6 requires. Tanglish (code-mixed) speech will be worse still. Compare `large-v3` vs `large-v3-turbo` on 3 of your real clips before choosing ([34 M2](34-tool-integration-plan.md#3-build-milestones)).
- AI4Bharat's Indic-specific ASR models are a possible upgrade for Tamil accuracy. Licences and packaging are **not yet checked**, so this is a research item, not a recommendation.

### 2.6 Spleeter → Demucs
| | Spleeter ❌ | **Demucs** ⚪ optional |
|---|---|---|
| GitHub | https://github.com/deezer/spleeter | https://github.com/adefossez/demucs (the original `facebookresearch/demucs` is **archived** ✅, and the fork says it's "the officially maintained Demucs") |
| License | MIT | **Code MIT. "The license of the weights is not clear"** ✅ (README) |
| Version | 2.4.2 (2025-04-03), **`requires_python <3.12`** ✅, so **it can't install on this machine's Python 3.12** | 4.1.0 (2026-07-11), Python ≥ 3.10 ✅ |
| Engine | TensorFlow | PyTorch (`htdemucs`, `htdemucs_ft`, `htdemucs_6s`) |
| Speed | — | CPU ≈ **1.5× track duration** ✅. GPU needs ≥ 3 GB VRAM (7 GB at defaults) ✅ |
| Use for us | — | Only when your footage has **background music you need removed** (a speaker playing in the room, a song in the car) so we can keep your voice and natural sound and swap the music. Separating a copyrighted song **doesn't grant any rights** to it |

### 2.7 Smaller selected pieces
| Tool | Role | License | Notes |
|---|---|---|---|
| **pyloudnorm** · https://github.com/csteinmetz1/pyloudnorm | ITU-R BS.1770 loudness in Python (QC asserts) | MIT ✅ | 0.2.0 (2026-01-04). FFmpeg `ebur128` remains the reference for final numbers |
| **soundfile** | WAV I/O | BSD-3 ✅ | Pulled in by librosa |
| **Silero VAD** · https://github.com/snakers4/silero-vad | Speech / non-speech segments | MIT ✅ | **Already bundled inside faster-whisper**, so no separate install unless VAD is needed without ASR |
| **MediaPipe Audio Classifier (YAMNet)** · https://ai.google.dev/edge/mediapipe | Labels such as Speech, Music, Laughter, Dog, Bird, Engine for *moment finding* in pet, bike and comedy footage | Apache-2.0 (framework) ✅. Check the model licence when downloading | Optional. Not tested yet |
| **FFmpeg audio filters** | All mixing and processing | via FFmpeg | `amix=normalize=0` · `sidechaincompress` · `adelay` · `afade`/`acrossfade` · `loudnorm` (two-pass) · `alimiter` · `highpass` · `afftdn` · `deesser` · `atempo` / `rubberband` 🧪 ([24 §6.3](24-beat-sync-and-sound-design.md#63-ffmpeg-mixing-recipes--tested-2026-11-07)) |
| ❌ madmom · https://github.com/CPJKU/madmom | Classic beat/downbeat tracker | Code BSD, **models CC BY-NC-SA** ✅ | Last PyPI release 0.16.1 (2018), no wheels, so it's impractical on Py 3.12. Beat This! supersedes it |

---

## 3. How each task is automated

### 3.1 BPM detection
1. Beat This! → beat times → `BPM = 60 / median(diff(beats))`
2. Cross-check with `librosa.feature.tempo(onset_envelope=…)`. If the two disagree by roughly ×2 or ×0.5, flag `tempo_ambiguous: true` and pick the one whose **downbeat spacing equals 4 beats**
3. Report a **local tempo curve** (BPM per 4-bar window). Film BGMs often change tempo, and then a fixed grid is wrong ([24](24-beat-sync-and-sound-design.md) notes the same limit for audio_beats.py)

### 3.2 Beat and downbeat detection
Beat This! beats and downbeats → bars → **phrases** (group of 4 or 8 bars, starting at a downbeat with an energy rise). Output markers in the [24 §3](24-beat-sync-and-sound-design.md#3-marking-the-audio-before-cutting) vocabulary: `H` hook start, `B` build, `D` drop, `S` switch, `A1…An` accents, `E` end/loop.

### 3.3 Music energy analysis
| Feature | Computation | Used for |
|---|---|---|
| Energy curve | `librosa.feature.rms` → dB → 0.25 s smoothing | Matching shot intensity to music intensity |
| Brightness | spectral centroid | "Lift" moments, builds |
| Low-end punch | RMS of < 150 Hz band | Impact points, hero frame |
| **Drop candidate** | Largest rise in 1 s-smoothed RMS, **snapped to the nearest downbeat** (same idea as audio_beats.py, which found the exact drop on test tracks 🧪) | `D` marker |
| Sections | MFCC/chroma recurrence → `librosa.segment.agglomerative` | Intro / verse / hook boundaries → `H`, phrase starts |

### 3.4 Onset detection
`librosa.onset.onset_detect(onset_envelope=…, backtrack=True, units="time")` on the **percussive** part (`librosa.effects.hpss`) → accent candidates `A1…An` ranked by strength. `backtrack=True` moves each onset to the preceding energy minimum, which is the right cut point for "cut 1–2 frames before the hit" ([24 §2](24-beat-sync-and-sound-design.md#2-sync-hierarchy-what-to-align-in-priority-order)).

### 3.5 Dialogue detection (your footage)
1. FFmpeg → 16 kHz mono WAV
2. faster-whisper `transcribe(language="ta" or "en" or auto, vad_filter=True, word_timestamps=True)` → **speech segments + words with start/end + probabilities**
3. Words with low probability are flagged `needs_review`
4. Non-speech, high-energy bursts (laughs, shouts, rabbit thumps, engine revs) come from loudness peaks outside VAD speech, optionally labelled by YAMNet → **reaction-moment candidates** for [32 moments](32-automated-editing-architecture.md#51-moment-proposals-inputs-to-claude-not-decisions)

### 3.6 Music synchronisation
The engine never "eyeballs" sync. It **quantises**:
1. Claude's plan lists intended sync events, e.g. `{"event":"hero_frame", "marker":"D"}`
2. The resolver converts markers to times **relative to the audio start offset** (video 0.0 s = audio start point, per [24 §4](24-beat-sync-and-sound-design.md#4-syncing-to-audio-youll-add-in-app))
3. Each cut snaps to the **frame grid** (`round(t × fps) / fps`), with the optional `−1 frame` early-cut rule
4. QC re-measures cuts in the rendered file and asserts **|cut − marker| ≤ 1 frame** for D and downbeat-tagged cuts ([32 §8](32-automated-editing-architecture.md#8-qc-checks))

### 3.7 Audio mixing
One FFmpeg graph per render:
```
[natural] highpass → afftdn → (deesser, acompressor if speech) ─┐
[sfx_1..n] adelay(event − peak_offset) → volume ────────────────┼─ amix(normalize=0) → loudnorm (2-pass) → alimiter → out
[music bed, only if baked] → sidechaincompress(key=speech) ─────┘
```
Targets come from [24 §6](24-beat-sync-and-sound-design.md#6-mixing-levels): **−14 LUFS** when the music is baked in. **≈ −16 LUFS** for the clean export when library music is added in-app. **True peak ≤ −1 dBTP** always. Two-pass loudnorm: pass 1 measures (`print_format=json`), pass 2 applies `measured_*` values with `linear=true`.

### 3.8 Sound-effect placement
- The SFX library (`assets/sfx/`) has a sidecar `sfx.json` per file: `type` (whoosh, impact, riser, pop, bruh, scratch), `duration`, **`peak_offset_ms`** (measured once with onset detection), `loudness`, `licence`, `source`
- Placement rule: **start = event_time − peak_offset**, so the *peak* lands on the frame ([24 §5.2](24-beat-sync-and-sound-design.md#52-sfx-placement-rules)). **Risers are aligned by their end**
- Variety rule: never use the same file twice within 10 s. Rotate variants
- Density check: SFX per minute is reported in QC against the [24 §5.2](24-beat-sync-and-sound-design.md#52-sfx-placement-rules) range

---

## 4. Licensing summary (audio side)

| Tool | License | Commercial-use risk |
|---|---|---|
| librosa | ISC | None |
| Beat This! (code + weights) | MIT | None |
| faster-whisper + Whisper weights | MIT | None |
| Silero VAD | MIT | None |
| pyloudnorm, soundfile | MIT / BSD | None |
| Demucs | Code MIT, **weights unclear** | Keep to internal processing. Document use |
| Essentia (rejected) | AGPL + **NC models** | Blocks brand-deal use |
| madmom (rejected) | BSD code + **NC models** | Blocks brand-deal use |
| **Music and SFX you use in Reels** | Separate from tools | Governed by [15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific) and [31 §5](31-instagram-audio-research-methods.md#5-getting-the-chosen-audio-into-the-published-reel) |

---

## 5. Open items to verify after installation
- [ ] Beat This! vs librosa vs audio_beats.py on 5 real tracks (2 Tamil mass BGMs, 1 kuthu, 1 melody, 1 English pop): check beat positions against a manual tap-along
- [ ] faster-whisper `large-v3` vs `large-v3-turbo` on 3 of your clips (Tamil, Tanglish, English): word timing error and how much you have to fix
- [ ] CPU timings (transcribe 60 s, beat-track 60 s) logged in [34 §6](34-tool-integration-plan.md#6-performance-log)
- [ ] YAMNet labels on pet and engine audio

**Related:** [29 Video tools](29-video-processing-tool-comparison.md) · [24 Beat sync & sound design](24-beat-sync-and-sound-design.md) · [34 Final stack](34-tool-integration-plan.md#1-final-recommended-stack)
