# 29 — Video Processing Tool Comparison

> **Phase 3b · Technical infrastructure** · Created 2026-11-07 · **Research only. Nothing has been installed.**
> Evidence tags: ✅ Official (project docs, PyPI metadata, GitHub API) · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 **Tested here** (run on this machine on 2026-11-07)
> Part of the infrastructure set: **29 video** · [30 audio](30-audio-analysis-tool-comparison.md) · [31 Instagram audio research](31-instagram-audio-research-methods.md) · [32 architecture](32-automated-editing-architecture.md) · [33 setup](33-environment-setup-guide.md) · [34 integration plan](34-tool-integration-plan.md)
> Editing craft lives in [21](21-professional-reels-editing.md), [23](23-tamil-bgm-editing-guide.md) and [24](24-beat-sync-and-sound-design.md). This document covers only *which software does the work*.

---

## 1. Verdict

**FFmpeg renders everything.** Python tools *analyse* the footage and *generate* FFmpeg instructions, but they never push video frames through Python on the final render.

| Task | Best tool | Runner-up | Avoid |
|---|---|---|---|
| Metadata extraction | **ffprobe** (JSON output) | PyAV | MoviePy (wraps ffmpeg anyway) |
| Frame extraction (stills, contact sheets) | **FFmpeg** (`-ss` + `select`) | PyAV (exact frames into NumPy) | — |
| Frame access for analysis (motion, faces, sharpness) | **PyAV** decode → **OpenCV** maths | OpenCV `VideoCapture` | MoviePy |
| Scene / shot detection | **PySceneDetect** (`AdaptiveDetector`) | FFmpeg `scdet` (already used by [tools/analyze_reel.py](tools/README.md)) | — |
| Trimming (frame-accurate) | **FFmpeg** `trim`/`atrim` inside one filtergraph (re-encode) | `-ss`/`-to` with re-encode | `-c copy` (cuts only on keyframes) |
| Cutting + merging | **FFmpeg** filtergraph (`concat` / `xfade`) | concat demuxer for identical intermediates | MoviePy |
| Vertical 9:16 conversion | **FFmpeg** `crop`/`scale` driven by an **OpenCV subject track**. Blur-fill fallback | Kdenlive/Resolve by hand | Blind centre crop |
| Speed ramping | **FFmpeg** `setpts` with a closed-form ramp expression 🧪 | Stepped segments | MoviePy `time_transform` (slow) |
| Slow motion | **High-fps source + `setpts`**. Interpolation: FFmpeg `minterpolate` (CPU) or **RIFE** (optional, GPU) | Resolve Optical Flow (manual) | Slowing 30 fps footage without interpolation (stutter) |
| Transitions | **FFmpeg** `xfade` (58 built-in types + custom expressions) 🧪 | Zoom/whip built from `crop`/`scale` expressions | — |
| Text overlays and captions | **ASS subtitles via libass** (`ass`/`subtitles` filter) 🧪 | `drawtext` for simple labels 🧪 | MoviePy `TextClip` (ImageMagick/Pillow, no Tamil shaping guarantees) |
| Rendering / encoding | **FFmpeg + libx264** (final), any fast preset for drafts | `h264_qsv`/`h264_vaapi` (Intel iGPU) for drafts, untested | — |
| Silence/dead-air pre-cut (talking footage) | Our own VAD-based cut list ([30](30-audio-analysis-tool-comparison.md)) | **Auto-Editor** binary | — |

---

## 2. What's already on this machine (🧪 checked 2026-11-07)

| Item | Finding | Impact |
|---|---|---|
| OS | Ubuntu 24.04.5 LTS, x86_64 | Target platform |
| CPU / RAM / disk | i7-12700H (20 threads) · 15 GiB RAM · ~800 GB free | Comfortable for 1080×1920 CPU renders of Reels-length clips |
| GPU | Intel Iris Xe (driver loaded, `/dev/dri/renderD128` present) + **NVIDIA RTX 3050 Mobile with the driver *not* loaded** (`nvidia-smi` fails) | CUDA, NVENC and GPU ML aren't usable until a driver is installed. That's an optional, separate decision ([33 §9](33-environment-setup-guide.md#9-optional-gpu-enablement-decide-later)) |
| FFmpeg | **6.1.1** (Ubuntu build), GPL build with `libx264 libx265 libass libfreetype libfribidi libharfbuzz libfontconfig librubberband libsoxr libzimg libvpx libsvtav1 libopus libmp3lame frei0r` | Covers everything in this document. **No upgrade needed** |
| FFmpeg filters present | `xfade drawtext(text_shaping) ass subtitles zoompan sendcmd minterpolate vidstabdetect/transform lut3d zscale scdet blackdetect freezedetect silencedetect ebur128 loudnorm atempo rubberband sidechaincompress` | Every rendering technique in §4 is available |
| Encoders | `libx264`, `libx265`, `aac`. Also `h264_nvenc` (needs the NVIDIA driver), `h264_qsv`/`h264_vaapi` (Intel, untested) | libx264 for finals |
| Python | 3.12.3, **no pip, no ensurepip** | Needs `uv` or `python3.12-venv` ([33](33-environment-setup-guide.md)) |
| Python libs | Only Pillow 10.2, PyYAML, jsonschema. No NumPy, OpenCV, etc. | Everything in Python is a fresh install in a project venv |
| Fonts | **Noto Sans Tamil** (full family) and **Noto Sans Condensed Black** (v0's name-card font, [26 §1](26-video-production-workflow.md#1-what-i-can-render-here-capability-check-2026-11-07)) installed. Anton, Bebas Neue, Montserrat and Poppins ([16 brand kit](16-editing-identity-and-reel-formats.md)) are **not** installed | Optional: download the brand fonts into `assets/fonts/` (OFL licence). No system change |

### 2.1 Proof-of-concept render (🧪)
One FFmpeg command on two synthetic 16:9 sources did all of the following:
- 9:16 **blur-fill** for clip 1
- a 9:16 **centre crop** of clip 2 at **0.5× speed** (`setpts` + `atempo`)
- a **`zoomin` xfade** transition
- **Tamil + English ASS captions** with a coloured punch word
- a `drawtext` series tag
- an audio crossfade
- **`loudnorm` to −14 LUFS**

| Check | Expected | Measured |
|---|---|---|
| Output | 1080×1920, H.264, 30 fps | 1080×1920, h264, 30/1 ✅ |
| Duration | 3 s + (2 s × 2) − 0.4 s overlap = 6.6 s | **6.600 s** ✅ |
| Loudness | −14 LUFS | **−13.9 LUFS** ✅ |
| Tamil shaping | "என்ன டா இது?" with correct conjuncts | Rendered correctly (frame inspected) ✅ |
| Render time | — | **4.7 s wall-clock** for 6.6 s of 1080×1920 (`-preset medium`, CPU) |

Further tests (§4.6, §4.3): a **smooth speed ramp** came out at 3.700 s against a theoretical 3.697 s, and **subject-tracked crops** worked via both `sendcmd` and per-frame `x` expressions.

---

## 3. Tool cards

### 3.1 FFmpeg (+ ffprobe): ✅ **SELECTED (core renderer)**
| Field | Detail |
|---|---|
| Website | https://ffmpeg.org · filter docs https://ffmpeg.org/ffmpeg-filters.html |
| Source | https://git.ffmpeg.org/ffmpeg.git (GitHub mirror https://github.com/FFmpeg/FFmpeg) |
| License | **LGPL-2.1-or-later**, or **GPL-2.0-or-later** when built with `--enable-gpl` (the Ubuntu build is GPL because it includes x264/x265) ✅. Licences cover the *software*, not the videos you make with it |
| Version here | 6.1.1 (Ubuntu 24.04 package `ffmpeg 7:6.1.1-3ubuntu5`) 🧪 |
| Install | Already installed. (`sudo apt install ffmpeg` on a fresh machine) |
| Dependencies | System libraries managed by apt |
| Capabilities | Decode practically every phone format (HEVC, HDR HLG/PQ, VFR), filtergraphs (trim, speed, crop, scale, xfade, overlay, ASS text, LUTs, stabilisation, interpolation), audio mixing and loudness, precise encoding |
| Limitations | Filtergraph syntax is unforgiving (we generate it from code, never by hand). No AI segmentation or tracking. `minterpolate` is slow and can smear on complex motion. Error messages are cryptic, so always keep the generated graph file for debugging |
| Integration | `subprocess` with argument lists (never shell strings), filtergraphs written to a file and passed with `-filter_complex_script` (FFmpeg 6.1; `-/filter_complex` in FFmpeg 7+), progress via `-progress pipe:1`. Python wrappers (`ffmpeg-python`, last release 2019; `typed-ffmpeg` 4.6, MIT) are **optional**. A small in-house graph builder is simpler to debug |

### 3.2 PyAV: ✅ **SELECTED (frame-accurate decoding for analysis)**
| Field | Detail |
|---|---|
| Website | https://pyav.basswood-io.com (docs) |
| GitHub | https://github.com/PyAV-Org/PyAV |
| License | BSD-3-Clause ✅. Wheels bundle their own FFmpeg libraries (LGPL build) |
| Version | **19.0.2** (2026-10-21). **Requires Python ≥ 3.12** ✅. This machine has 3.12.3 ✅ |
| Install | `uv pip install av` (wheel ~35 MB, FFmpeg bundled, no system FFmpeg needed) |
| Dependencies | None beyond the wheel |
| Capabilities | Decode exact frames with exact PTS into NumPy, seek, read side data (rotation, HDR), read and write audio, remux |
| Limitations | Low-level, so you manage time bases yourself. Its bundled FFmpeg differs from the system FFmpeg, so codec support can differ slightly. The project's own advice is that if a plain `ffmpeg` command does the job, PyAV is more hindrance than help ✅ |
| Integration | Analysis stage only: frame iterator → OpenCV (motion, sharpness, faces) at reduced resolution and sample rate. Also used by `faster-whisper` for audio decoding and as an optional PySceneDetect backend |

### 3.3 OpenCV: ✅ **SELECTED (vision maths)**
| Field | Detail |
|---|---|
| Website | https://opencv.org · docs https://docs.opencv.org |
| GitHub | https://github.com/opencv/opencv · Python wheels https://github.com/opencv/opencv-python |
| License | **Apache-2.0** ✅ |
| Version | **5.0.0.93** on PyPI (2026-07-02). Wheels are `abi3`, so they work on Python 3.12 ✅. **OpenCV 5 is a new major version**, so test the APIs we use in the smoke test ([33 §8](33-environment-setup-guide.md#8-verification-smoke-test)) |
| Install | `uv pip install opencv-python` (~71 MB). **Install only one OpenCV variant.** PySceneDetect 0.7 depends on `opencv-python`, so don't add `opencv-python-headless` as well, or the two `cv2` modules will conflict |
| Dependencies | NumPy |
| Capabilities | Frame differencing and optical flow (motion energy), Laplacian variance (blur and focus), histograms (exposure), **face detection with YuNet** (`cv2.FaceDetectorYN`, small ONNX model from the OpenCV Zoo), saliency, template matching, drawing overlays for QC images |
| Limitations | `VideoCapture` timestamps are unreliable on VFR phone video (that's why PyAV decodes). Face detectors don't find **rabbits, birds or bikes**, so pet and vehicle Reels need motion or saliency-based framing or manual crop keyframes |
| Integration | Pure functions over NumPy frames → JSON features (`visual.json`, `subject_track.json`) |

### 3.4 PySceneDetect: ✅ **SELECTED (shot boundaries)**
| Field | Detail |
|---|---|
| Website | https://www.scenedetect.com · changelog https://www.scenedetect.com/changelog/ |
| GitHub | https://github.com/Breakthrough/PySceneDetect |
| License | BSD-3-Clause ✅ |
| Version | **0.7.2** (2026-10-11). Requires Python ≥ 3.10 ✅. **0.7 is a breaking release**: timestamps were rebuilt for VFR, `video_manager` was removed, and `framerate` became `frame_rate` ✅. 0.7.2 changed the default thresholds for the hist and hash detectors ✅ |
| Install | `uv pip install scenedetect` (pulls `opencv-python`, click, platformdirs, tqdm). Optional extra: `scenedetect[pyav]` |
| Capabilities | Detectors: `ContentDetector`, **`AdaptiveDetector`** (best for handheld phone footage), `ThresholdDetector` (fades), `HistogramDetector`, `HashDetector`. Output scene lists as CSV, EDL, **OTIO** or FCP. `detect(path, backend="pyav")` (0.7.1+) ✅ |
| Limitations | Handheld whip pans and flashes cause false cuts. Slow dissolves get missed. Most user footage will be a few long takes, so "scenes" matter less than *moments inside a take* (that's the motion and audio analysis in [32](32-automated-editing-architecture.md)) |
| Integration | `scenedetect.detect(proxy_path, AdaptiveDetector())` → `scenes.json`. Runs on a 540p proxy for speed |

### 3.5 MoviePy: ❌ **NOT SELECTED** (prototyping only)
| Field | Detail |
|---|---|
| Website | https://zulko.github.io/moviepy/ |
| GitHub | https://github.com/Zulko/moviepy |
| License | MIT ✅ |
| Version | **2.2.1** (2025-05-21, no release since). **v2 broke the v1 API** (for example `subclip` → `subclipped`, `set_*` → `with_*`), so most online tutorials are v1 and won't run ✅/🔵 |
| Install | `uv pip install moviepy` (pulls imageio-ffmpeg, which downloads its *own* FFmpeg binary; pins `pillow<12`) |
| Capabilities | Friendly Python compositing: clips, text, effects, audio |
| Limitations | Every frame goes through NumPy in Python, so it's **much slower** than a native filtergraph at 1080×1920 🔵. Text relies on Pillow (no guaranteed complex-script shaping for Tamil). Its own FFmpeg copy duplicates the system one. The v1/v2 split means unreliable examples |
| Why rejected | Our renders are filtergraphs. MoviePy adds speed cost and a second FFmpeg, and provides nothing FFmpeg + libass can't already do |

### 3.6 Auto-Editor: ⚪ **OPTIONAL** (silence pre-cut only, not in core)
| Field | Detail |
|---|---|
| Website | https://auto-editor.com |
| GitHub | https://github.com/WyattBlue/auto-editor |
| License | **Unlicense (public domain)** ✅ |
| Version / language | **Rewritten in Nim.** The site says "the auto-editor cli is no longer being published on pip" ✅. PyPI still lists a stale 29.3.1 (2025-11-04). Install the **binary from GitHub Releases** |
| Install | Download the Linux binary → `chmod +x` → put it in `~/.local/bin` (no sudo) |
| Capabilities | Cuts "dead space" by audio loudness or motion. Margins (`--margin 0.2s`). Exports to Premiere, Resolve, Final Cut Pro, Shotcut, **Kdenlive**, clip sequence ✅ |
| Limitations | It's a *first-pass silence cutter*, not a creative editor. Loudness thresholds misfire on noisy footage (engine, fans, pets). A separate binary outside the venv |
| Why optional | Our VAD + loudness analysis ([30](30-audio-analysis-tool-comparison.md)) produces the same cut list *inside* the timeline JSON. Add Auto-Editor later only for long talking-head footage, if needed |

### 3.7 Supporting tools (recommended additions)
| Tool | Role | License | Status |
|---|---|---|---|
| **libass** (inside FFmpeg) · https://github.com/libass/libass | Styled, animated captions and name cards (ASS format: karaoke `\k`, `\move`, `\t` transforms), HarfBuzz shaping for **Tamil** | ISC ✅ | ✅ Already compiled into FFmpeg 🧪 |
| **OpenTimelineIO** · https://opentimeline.io · https://github.com/AcademySoftwareFoundation/OpenTimelineIO | Export our timeline for **hand-finishing in Resolve or Kdenlive** (doc 21's "give you a frame-exact timeline" path) | Apache-2.0 ✅ | Optional (v0.18.1, has cp312 wheels) |
| **MediaPipe** · https://ai.google.dev/edge/mediapipe · https://github.com/google-ai-edge/mediapipe | Person and pose detection for reframing when faces aren't visible (back to camera, helmet on the R15) | Apache-2.0 ✅ | Optional (1.2.2, manylinux wheel). Needs `.tflite` model downloads |
| **Practical-RIFE** · https://github.com/hzwer/Practical-RIFE | AI frame interpolation for smoother slow-mo from 30/60 fps footage | MIT ✅ | Optional. PyTorch, realistically needs a GPU. Manual git clone + weights |
| **vid.stab** (inside FFmpeg) | Two-pass stabilisation for shaky handheld | GPL (via FFmpeg) | ✅ Compiled in |
| ❌ Ultralytics YOLO | Object/pet detection | **AGPL-3.0** | **Avoid**: the licence is restrictive if this ever becomes a service or brand-deal workflow. Prefer motion and saliency for pets |

---

## 4. Task recipes (how each job is done)

All recipes run inside **one generated filtergraph** per render, from the **original files** (doc 21 principle 5: render once).

### 4.1 Metadata
`ffprobe -v error -print_format json -show_format -show_streams IN` → container, codecs, w×h, **rotation side data**, `r_frame_rate` vs `avg_frame_rate` (if they differ, the file is **VFR**: normalise with `fps=30` or `fps=60`), colour transfer (`arib-std-b67` = HLG, `smpte2084` = PQ → **HDR, tone-map it**), audio rate and channels. The existing [tools/analyze_reel.py](tools/README.md) already does this for audits.

### 4.2 Frames
- Stills at times: `ffmpeg -ss T -i IN -frames:v 1 out.jpg` (fast seek, accurate on re-encode)
- Contact sheet: `select='gt(scene,0.3)'` or explicit timestamps + `tile=4x4`
- Analysis stream: PyAV decode of a **540p CFR proxy** at 5–10 samples/s → NumPy

### 4.3 9:16 vertical conversion
| Mode | When | Filter chain |
|---|---|---|
| **Native vertical** | Phone shot vertical (most of your footage) | `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920` |
| **Tracked crop** 🧪 | Landscape with one subject | `crop=w=ih*9/16:h=ih:x='<expr>':y=0,scale=1080:1920`. `x` is evaluated **per frame**. Feed it a smoothed subject path either as a piecewise-linear expression or via `sendcmd` (both tested) |
| **Blur-fill** 🧪 | Landscape where the whole frame matters (wide road shots, two subjects) | `split → [bg] scale+crop+boxblur → [fg] scale=1080:-2 → overlay centred` |
| **Fit + design** | Landscape screen recordings | Letterbox on a brand background + title in the empty space |

Subject path = OpenCV/YuNet face centre (or MediaPipe person, or motion centroid for pets) → median filter → **dead-zone + max-pan-speed smoothing**, so the "camera" doesn't jitter → crop x(t).

### 4.4 Trim, cut, merge
- `trim=start=S:end=E,setpts=PTS-STARTPTS` + `atrim`/`asetpts` per clip, then `concat=n=N:v=1:a=1`, or chained `xfade`/`acrossfade` where transitions exist.
- **Before `concat`/`xfade`, normalise every input** to the same size, `fps`, `format=yuv420p`, `setsar=1` and audio `aresample=48000`. Otherwise `xfade` fails.
- `xfade` offset maths: `offset_k = (sum of durations of clips 0..k) − (sum of transition durations 0..k)`. The engine computes this; never do it by hand.

### 4.5 Transitions (🧪 `xfade` types available here)
`fade fadeblack fadewhite dissolve wipeleft/right/up/down slideleft/right/up/down smoothleft/right/up/down circleopen/close circlecrop rectcrop radial pixelize zoomin hblur squeezeh/v cover*/reveal* wind* slices diag*` + `custom` (expression). **Doc 21 rule applies:** hard cuts by default. A *whip* is only used when a whip was filmed. A zoom punch is `scale`/`crop` keyframes, not an xfade.

### 4.6 Speed ramp (🧪 smooth, not stepped)
A linear speed change from `s0` to `s1` over source span `L` maps output time as
`τ(t) = L/(s1−s0) · ln(1 + (s1−s0)·t/(L·s0))`, which goes straight into `setpts`:
```
setpts='(2/(-0.75))*log(1+(-0.75)*T/2)/TB',fps=30     # 1.0x → 0.25x over 2 s of 120 fps source
```
🧪 Output 3.700 s vs theoretical 3.697 s. This **updates [21 §3](21-professional-reels-editing.md#3-tool-capability-matrix-nov-2026), [25 §3.3](25-cinematic-and-comedy-editing.md#33-tool-steps) and [26 §1](26-video-production-workflow.md#1-what-i-can-render-here-capability-check-2026-11-07)**, which list FFmpeg ramps as a "stepped approximation": smooth ramps are possible when generated as expressions. Adding this to `tools/reel_render.py` (`"speed": {"ramp": [from, to]}`) is part of [32 §6](32-automated-editing-architecture.md#6-the-edl-contract-backward-compatible-extension-of-v0). Multi-segment ramps are a piecewise `if(lt(T,a),…,…)` chain generated by the engine. Audio on ramped spans is normally muted or replaced (music/SFX). For constant-speed spans, use `atempo` (range 0.5–100, chainable) or `rubberband` (better pitch quality, compiled in).

### 4.7 Slow motion
1. **Best:** shoot at 60/120/240 fps and conform with `setpts=N*PTS` → real frames, no artefacts.
2. **30 fps source:** `minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1` (CPU, slow, can warp edges), then `setpts`. Claude checks the transition strips for smearing ([32 QC](32-automated-editing-architecture.md#8-qc-checks)).
3. **Optional upgrade:** RIFE interpolation (GPU), then FFmpeg conform.

### 4.8 Text overlays
- **ASS (default)** 🧪: the engine writes `captions.ass` (styles from the brand kit: Tamil = Noto Sans Tamil, display = Anton/Bebas from `assets/fonts` via `subtitles=captions.ass:fontsdir=assets/fonts`). Supports pop-in scale, karaoke word highlight, moves, fades and per-word colour. Safe-zone margins come from [07 §2](07-instagram-seo-and-optimization.md#2-safe-zones).
- **`drawtext`** 🧪 for simple static labels (series tag `BRUH MOMENT #07`). `text_shaping=1` (default) uses HarfBuzz.
- **PNG overlays** (Pillow-generated or designed) for logos and stickers: `overlay=x:y:enable='between(t,a,b)'`.

### 4.9 Colour and look
`lut3d=file.cube` (MovieMode LUT from the Phase 3 kit), `eq`, `curves`, `colorbalance`, `vignette`, `noise` (grain). **HDR iPhone or Android footage:** `zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p` (libzimg is compiled in).

### 4.10 Rendering presets
| Preset | Use | Settings |
|---|---|---|
| `draft` | Iteration and Claude review | 540×960, `libx264 -preset veryfast -crf 26`, AAC 128k |
| `final` | Upload | 1080×1920, CFR 30 (or 60 for action), `libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -maxrate 20M -bufsize 40M`, BT.709 tags, **AAC 48 kHz 256k stereo**, `-movflags +faststart` (matches [07 §1](07-instagram-seo-and-optimization.md)) |
| `clean` | Final without music (for in-app library audio) | Same as `final`, mixed to **≈ −16 LUFS** per [24 §6.1](24-beat-sync-and-sound-design.md#61-when-library-music-is-added-in-app-the-default-workflow) |
| `sync_guide` | Your review only, **never uploaded** | `final` + the reference music track at its planned offset |

---

## 5. Licensing summary (video side)

| Tool | License | Obligation for us |
|---|---|---|
| FFmpeg (Ubuntu GPL build) | GPL-2.0+ | None for personal use or for the videos produced. Only matters if we *distribute* the software |
| PyAV | BSD-3 (bundled FFmpeg LGPL) | None for local use |
| OpenCV | Apache-2.0 | None |
| PySceneDetect | BSD-3 | None |
| OpenTimelineIO / MediaPipe | Apache-2.0 | None |
| RIFE | MIT | None |
| Fonts: Noto Sans Tamil, Anton, Bebas Neue, Montserrat, Poppins | SIL OFL 1.1 | Fine to use in videos, including commercial ones. Keep the licence files with the fonts |
| Auto-Editor | Unlicense | None |

No tool in the selected stack restricts commercial use of the **videos**, so brand-deal Reels stay open. Music licensing is a separate matter ([15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific)).

---

## 6. Open items to verify after installation
- [ ] OpenCV 5.0 with PySceneDetect 0.7.2 (smoke test, [33 §8](33-environment-setup-guide.md#8-verification-smoke-test))
- [ ] YuNet face detection on your real footage (helmets, side profiles, low light)
- [ ] `h264_qsv`/`h264_vaapi` draft encodes on Iris Xe (needs `intel-media-va-driver-non-free`, untested)
- [ ] `minterpolate` quality on one real 30 fps clip before relying on it

**Related:** [30 Audio tools](30-audio-analysis-tool-comparison.md) · [32 Architecture](32-automated-editing-architecture.md) · [34 Final stack](34-tool-integration-plan.md#1-final-recommended-stack)
