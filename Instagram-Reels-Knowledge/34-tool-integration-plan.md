# 34 — Tool Integration Plan & Final Technical Stack

> **Phase 3b · Technical infrastructure** · Created 2026-11-07 · Plan only. Execution starts after you approve [33 §11](33-environment-setup-guide.md#11-approval-checklist-reply-with-what-you-approve)
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · 🧪 Tested here
> Brings together [29 video](29-video-processing-tool-comparison.md) · [30 audio](30-audio-analysis-tool-comparison.md) · [31 Instagram audio](31-instagram-audio-research-methods.md) · [32 architecture](32-automated-editing-architecture.md) · [33 setup](33-environment-setup-guide.md). Builds on the working v0 tools (`tools/analyze_reel.py`, `audio_beats.py`, `reel_render.py`) and the Autonomous Mode SOP in [26](26-video-production-workflow.md).

---

## 1. Final recommended stack

| Layer | Tool | Version (2026-11-07) | License | Role | Status |
|---|---|---|---|---|---|
| Render + probe | **FFmpeg / ffprobe** (system) | 6.1.1 (Ubuntu) | GPL-2.0+ build | All cutting, speed, reframing, transitions, text (libass), grading, mixing, loudness, encoding | ✅ Installed 🧪 |
| Captions / titles | **libass** (in FFmpeg) + generated ASS | 0.17.1 | ISC | Animated captions, name cards, **Tamil shaping** | ✅ Installed 🧪 |
| Renderer core | **tools/reel_render.py** (v0) → `engine/render` (v1) | — | ours | EDL → single-pass FFmpeg graph | ✅ v0 working 🧪 |
| Env manager | **uv** | 0.13.x | Apache-2.0 / MIT | venv + lockfile + CPU-torch pinning without sudo | T0 |
| Language | **Python** (system) | 3.12.3 | PSF | Engine code | ✅ Installed |
| Frame decoding | **PyAV** | 19.x | BSD-3 | Exact-PTS frames for analysis | T1 |
| Vision maths | **OpenCV** (`opencv-python`) + **YuNet** model | 5.0.x | Apache-2.0 / MIT | Motion, sharpness, exposure, faces, subject paths, QC overlays | T1 |
| Shot detection | **PySceneDetect** | 0.7.2 | BSD-3 | Scene boundaries | T1 |
| Music features | **librosa** | 1.0.x | ISC | Energy, onsets, sections, tempo cross-check | T1 |
| Loudness checks | **pyloudnorm** (+ FFmpeg `ebur128`) | 0.2.x | MIT | QC asserts | T1 |
| Contracts | **pydantic** | 2.x | MIT | EDL schema (`edl/1` + `edl/2`) and validation | T1 |
| Beats + downbeats | **Beat This!** (on CPU PyTorch 2.11) | 1.1.x | MIT (code + weights) | Beat grid, downbeats, phrases. audio_beats.py stays as fallback | T2 |
| Speech | **faster-whisper** (+ bundled Silero VAD) · `large-v3-turbo` (A/B vs `large-v3`) | 1.2.x | MIT | Speech segments, word timings, draft transcripts | T2 |
| Hand-off | OpenTimelineIO | 0.18.x | Apache-2.0 | EDL → Resolve/Kdenlive (doc 26 Path B/C) | Optional |
| Subject fallback | MediaPipe | 1.2.x | Apache-2.0 | Person/pose tracking, YAMNet audio labels | Optional |
| Separation | Demucs (adefossez) | 4.1.x | MIT code, weights unclear | Remove background music from your footage | Optional |
| Silence pre-cut | Auto-Editor (binary) | latest release | Unlicense | Long talking footage | Optional |
| Interpolation | Practical-RIFE | — | MIT | Smooth slow-mo from 30 fps (needs GPU) | Optional, after GPU |
| Orchestrator | **Claude Code** in the KB folder | — | — | Runs the CLI, reads JSON, views evidence images, writes EDLs | ✅ Available |
| **Rejected** | MoviePy (slow, duplicate FFmpeg) · Essentia (AGPL + non-commercial models, stale cp312 wheel) · Spleeter (Python < 3.12) · madmom (2018, non-commercial models) · Audacity (GUI-bound) · openai-whisper (slower than faster-whisper) · YOLO/Ultralytics (AGPL) · scraper APIs (policy) | | | | — |

**Cost: ₹0.** No subscriptions. Everything runs locally. The only network calls are one-time model downloads and, optionally, the official Meta and YouTube APIs ([31 §6](31-instagram-audio-research-methods.md#6-instagram-audio-api-setup-optional-not-yet-approved)).

---

## 2. Integration map (adapters and their contracts)

Each adapter is the **only** module that imports its tool. Everything downstream consumes plain JSON in the production folder ([32 §4](32-automated-editing-architecture.md#4-code-and-folder-layout)).

| Module | Imports | Function (sketch) | Output (in `productions/P###/`) |
|---|---|---|---|
| `ffmpeg.py` | subprocess | `run(args, log) → Result` · `probe(path) → dict` | — |
| `ingest.py` | ffmpeg.py | `ingest(src) → SourceInfo` (hash, VFR/HDR/rotation flags, proxy, 48 kHz WAV) | `source/sources.json`, `analysis/proxy_*.mp4` |
| `analysis/scenes.py` | scenedetect | `detect(proxy) → [Scene]` (`AdaptiveDetector`, `backend="pyav"`) | `analysis/scenes.json` |
| `analysis/visual.py` | av, cv2, numpy | `features(proxy, hz=5) → {t, motion, sharpness, luma, shake}` | `analysis/visual.json` |
| `analysis/subject.py` | cv2 (YuNet), [mediapipe] | `track(proxy, mode)` → `smooth(path, deadzone, max_speed)` | `analysis/subject_*.json` |
| `analysis/speech.py` | faster_whisper | `transcribe(wav, lang, model) → segments + words(start, end, prob)` | `analysis/speech.json` |
| `analysis/sounds.py` | numpy, [mediapipe] | `events(wav, speech) → non-speech peaks (+labels)` | `analysis/sounds.json` |
| `analysis/music.py` | beat_this, librosa (fallback: tools/audio_beats.py) | `analyse(ref_wav, start, dur) → bpm, beats, downbeats, energy, sections, markers` | `audio/music.json`, `audio/beats_plot.png` |
| `moments.py` | numpy | `propose(prod) → ranked windows + reasons` | `analysis/moments.json` + sheet |
| `edl/*` | pydantic | `load → resolve (markers, sync, macros) → validate` | `build/edl.resolved.vN.json` |
| `render/*` | ffmpeg.py | Wraps, then absorbs, `tools/reel_render.py`, adding smooth ramps, track fit, text items and macros | `renders/vN_*.mp4`, `build/graph_vN.txt` |
| `qc/*` | ffmpeg.py, cv2, pyloudnorm + tools/analyze_reel.py | `run(render, edl) → findings` | `build/qc_vN.json` + evidence |
| `package.py` | — | fills `productions/_templates/04-publish-package.md` | `publish/` |

**Config sourced from the KB** (so documents and code can't drift apart):

| Setting | Source doc |
|---|---|
| Safe zones | [07 §2](07-instagram-seo-and-optimization.md#2-safe-zones) |
| Export spec | [28 §1](28-reels-export-and-publishing.md#1-export-settings-by-tool) |
| Loudness targets | [24 §6](24-beat-sync-and-sound-design.md#6-mixing-levels) |
| Brand styles, signatures S1–S6, formats | [16](16-editing-identity-and-reel-formats.md) |
| Caption styles | [21 §6](21-professional-reels-editing.md#6-text--subtitle-production-standard) |
| Grades | [25 §5.2](25-cinematic-and-comedy-editing.md#52-your-two-signature-looks-s5--starting-values) and reel_render.py `GRADES` |
| Audio evidence rules | [22](22-instagram-audio-discovery.md) / [31 §4](31-instagram-audio-research-methods.md#4-the-audio-record-machine-readable-used-by-the-engine) |

`config.py` carries a comment with each doc reference.

---

## 3. Build milestones

Additive: **v0 keeps working at every step.** Each milestone ends with a demo and passing tests.

| # | Milestone | Deliverables | Acceptance test |
|---|---|---|---|
| **M0** | Install T0 + T1, smoke test | `engine/` with pyproject + uv.lock, YuNet (+ fonts if approved) | [33 §8](33-environment-setup-guide.md#8-verification-smoke-test) core checks pass |
| **M1** | Skeleton + state + QC v1 | `reel ingest/qc/doctor`, `production.json`, QC rules as pass/fail over analyze_reel.py metrics | Ingest 3 real clips correctly (fps, rotation, HDR flag). QC verdicts on an existing render match a manual review |
| **M2** | Analysis (install T2 here) | scenes, visual, subject, speech, sounds, music, moments | Fixtures within tolerance. **A/B reports written here:** Whisper turbo vs large-v3 (Tamil, Tanglish, English) and Beat This! vs librosa vs audio_beats.py on 5 real tracks |
| **M3** | EDL v2 | Schema for `edl/1` + `edl/2`, resolver, validator, macros | Every existing v0 EDL validates unchanged. The [32 §6.1](32-automated-editing-architecture.md#61-example-edl2) example resolves to D = 7.520 s and E = 15.000 s. Bad plans give readable errors |
| **M4** | Renderer upgrades | Smooth ramps, track fit, text items → ASS, macros S1–S6, `graph_vN.txt` | v0 EDLs render identically (frame hash). Golden render per macro. Cuts within ±1 frame of plan. Loudness on target |
| **M5** | QC loop | All [32 §8](32-automated-editing-architecture.md#8-qc-checks) rules, sync plot, auto-fixes, versioned revisions | Deliberately broken EDLs (unsafe text, loud mix, sync off by 3 frames) are caught. Auto-fixes converge in ≤ 1 round |
| **M6** | Packaging + logs | `publish/04-publish-package.md` generation, audio record ↔ [audio-log](account-data/audio-log.md), wall times → §6 | The package can be followed in Edits without questions |
| **M7** | First production on v1 | One real clip from `productions/inbox/` end to end in Autonomous Mode | You judge it on your phone. Lessons go into [26](26-video-production-workflow.md) and here |

---

## 4. Version and dependency policy
- `uv.lock` is kept. Upgrades are deliberate: `uv lock --upgrade-package X` → re-run fixtures and golden renders → record it in §8.
- Pin **major** versions (OpenCV 5, PySceneDetect 0.7, librosa 1.0, PyAV 19, torch 2.11), because each recently shipped breaking releases ✅.
- System FFmpeg stays at the Ubuntu version. A newer static FFmpeg is only added if a needed filter is missing (none is today 🧪).
- Monthly check (the same cadence as the KB's re-verification): new releases, deprecations, and Meta API changelog entries affecting [31](31-instagram-audio-research-methods.md).

## 5. Licence register (`assets/LICENSES/README.md`, plus `licenses/` per production)
| Category | Rule |
|---|---|
| Software | Permissive (MIT/BSD/ISC/Apache) preferred. GPL FFmpeg is fine (used locally, not distributed). **No AGPL and no non-commercial model weights in the core**, so brand-deal Reels stay possible |
| Fonts | OFL files stored in `assets/LICENSES/` |
| SFX | v0 kit is synthesised in-house (no licence issue). Any added SFX gets `licence` + `source` in `sfx.json` and proof in `assets/LICENSES/` |
| Instagram library audio | **Never in upload outputs.** The reference copy is for timing only ([31 §5](31-instagram-audio-research-methods.md#5-getting-the-chosen-audio-into-the-published-reel)) |

## 6. Performance log
*(No numbers are recorded until they're measured)*

| Date | Operation | Input | Settings | Wall time | Notes |
|---|---|---|---|---|---|
| 2026-11-07 | FFmpeg PoC render (blur-fill, speed, xfade, ASS, loudnorm) | 2 × synthetic 1080p, output 6.6 s 1080×1920 | libx264 medium CRF 18, CPU | 4.7 s | 🧪 [29 §2.1](29-video-processing-tool-comparison.md#21-proof-of-concept-render-) |
| — | faster-whisper turbo, 60 s Tamil | — | CPU int8 | *to measure* | M2 |
| — | Beat This! final0, 60 s | — | CPU | *to measure* | M2 |
| — | Full draft render, 30 s Reel | — | draft preset | *to measure* | M4 |

## 7. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Tamil transcription is often wrong (≈ 19% CER in published research 🟡) | Transcripts used for timing. Tanglish/English captions preferred. **Tamil-script text flagged for your check** before posting |
| New major versions (OpenCV 5, PySceneDetect 0.7, librosa 1.0) have untested combinations | Smoke test + fixtures at M0/M2. Pinned majors. Single OpenCV variant |
| Breaking the working v0 renderer | v0 EDL frame-hash regression tests at M3/M4. v0 scripts stay stdlib and runnable |
| Pet and vehicle footage has no faces, so reframing fails | Motion/saliency path, MediaPipe person fallback, blur-fill, manual `focus_x` |
| In-app audio start can't be set precisely → sync drift | Edits waveform alignment + the publish package's sync-check frame ([24 §4](24-beat-sync-and-sound-design.md#4-syncing-to-audio-youll-add-in-app)) |
| Claude can't *watch* motion or comedic timing | Your phone review of the delivered Reel. Claude labels those judgements as opinion |
| RAM pressure (15 GiB) with large Whisper + renders | Sequential stages. turbo or small model. Proxies for analysis |
| Meta API terms or changes | Path A needs no API. API use is optional and checked monthly |
| Drift into an "automation bot" | The engine **never publishes or engages**. You post (your no-bots rule) |

## 8. Changelog
| Date | Change |
|---|---|
| 2026-11-07 | Stack selected. Plan written, re-based on the v0 tools and Autonomous Mode (doc 26). Nothing installed (awaiting [33 §11](33-environment-setup-guide.md#11-approval-checklist-reply-with-what-you-approve)) |

---

## 9. Decisions needed from you
1. **Approve installation tiers** T0, T1, T2 ([33 §11](33-environment-setup-guide.md#11-approval-checklist-reply-with-what-you-approve)), and say yes or no to the optional brand fonts.
2. **Engine location:** `Instagram-Reels-Knowledge/engine/` (recommended: it shares `tools/`, `assets/` and `productions/`), or a separate `crazy_projects/reel-engine/`?
3. **GPU:** stay CPU-only for now (recommended), or schedule the NVIDIA driver install ([33 §9](33-environment-setup-guide.md#9-optional-gpu-enablement-decide-later))?
4. **Meta developer app for the Audio API:** later (recommended) or now ([31 §6](31-instagram-audio-research-methods.md#6-instagram-audio-api-setup-optional-not-yet-approved))?
5. **Account goal** (fun vs brand deals) is still open from [13](13-my-instagram-account-analysis.md). The stack works either way. It only changes which music path (A/B/C) each Reel may use.
