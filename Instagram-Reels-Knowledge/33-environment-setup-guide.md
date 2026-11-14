# 33 — Environment Setup Guide (Installation Plan, Awaiting Approval)

> **Phase 3b · Technical infrastructure** · Created 2026-11-07
> ⛔ **NOTHING IN THIS DOCUMENT HAS BEEN RUN.** It's the plan I'll execute **only after you approve it**, tier by tier. Everything checked so far was read-only (versions, hardware, URLs) plus throwaway FFmpeg test renders in a temporary scratch folder.
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · 🧪 Tested here
> Tool choices are justified in [29](29-video-processing-tool-comparison.md) and [30](30-audio-analysis-tool-comparison.md). The final stack table is in [34 §1](34-tool-integration-plan.md#1-final-recommended-stack).

---

## 1. Summary of changes I'm asking permission for

| Tier | What | Where it goes | Needs sudo? | Download (measured wheel and model sizes) |
|---|---|---|---|---|
| **T0** | `uv` (Python package and venv manager), a single binary | `~/.local/bin/uv`, `~/.local/bin/uvx` | ❌ No | ~20 MB |
| **T1 core** | Project venv + NumPy, OpenCV, PySceneDetect, PyAV, librosa, soundfile, pyloudnorm, pydantic | `Instagram-Reels-Knowledge/engine/.venv/` | ❌ | ≈ 0.25 GB |
| **T1 assets** | YuNet face model (MIT) + *optional* brand fonts (Anton, Bebas Neue, Montserrat, Poppins, OFL). v0 already uses the installed Noto Sans Condensed Black for name cards | `Instagram-Reels-Knowledge/assets/` | ❌ | < 5 MB |
| **T2 ML** | PyTorch **CPU** 2.11 + torchaudio, Beat This!, faster-whisper | `Instagram-Reels-Knowledge/engine/.venv/` | ❌ | ≈ 0.3 GB packages |
| **T2 models** | Whisper `large-v3-turbo` (1.62 GB) **or** `large-v3` (3.09 GB) + `small` (0.49 GB) for quick runs · Beat This! checkpoint (~78 MB) | `~/.cache/huggingface/`, `~/.cache/torch/` | ❌ | 1.7–3.6 GB |
| **T3 optional** | Demucs, OpenTimelineIO, MediaPipe, Auto-Editor binary, RIFE | venv / `~/.local/bin` | ❌ | on demand, asked separately |
| **Sys optional** | `intel-media-va-driver-non-free vainfo` (Intel GPU draft encodes) · `audacity` (manual listening tool) · NVIDIA driver (§9) | system | ✅ Yes | asked separately |

**Nothing in T0–T2 touches system Python, apt, or any file outside `~/.local/bin`, `~/.cache/` and the new `Instagram-Reels-Knowledge/engine/` and `assets/` subfolders.** The v0 scripts in `tools/` aren't changed and keep running without the venv. Rollback is in §10.

---

## 2. Verified starting point (🧪 2026-11-07)

| Item | Value | Consequence |
|---|---|---|
| OS | Ubuntu 24.04.5 LTS x86_64 | — |
| Python | 3.12.3 at `/usr/bin/python3`. **No `pip`, no `ensurepip`** (the `python3.12-venv` package isn't installed) | Use **uv**, which creates venvs without ensurepip. The alternative is §3 Option B (sudo) |
| FFmpeg | 6.1.1 with libass, HarfBuzz, x264, zimg, rubberband, vid.stab | **No install needed** ([29 §2](29-video-processing-tool-comparison.md#2-whats-already-on-this-machine--checked-2026-11-07)) |
| Fonts | Noto Sans Tamil ✅ and Noto Sans Condensed Black ✅ (the current v0 name-card font, [26 §1](26-video-production-workflow.md#1-what-i-can-render-here-capability-check-2026-11-07)) are installed | The [16](16-editing-identity-and-reel-formats.md) brand fonts are optional and go in `assets/fonts/` only |
| GPU | Iris Xe active. RTX 3050 Mobile present, **NVIDIA driver not loaded**. Secure Boot **disabled**. Ubuntu recommends `nvidia-driver-595-open` | Plan is **CPU-only**. GPU is a separate decision (§9) |
| RAM / disk | 15 GiB (≈ 7 GiB available at check time) / ~800 GB free | Fine. Avoid running large-v3 Whisper and a final render at the same time |

---

## 3. Step T0: install uv (no sudo)

uv is Astral's package and project manager (https://docs.astral.sh/uv/ · https://github.com/astral-sh/uv · Apache-2.0 or MIT). Latest release at time of writing: **0.13.7** (2026-11-03).

**Option A (recommended): verified release tarball, no shell-profile edits**
```bash
cd /tmp && V=0.13.7
curl -LO https://github.com/astral-sh/uv/releases/download/$V/uv-x86_64-unknown-linux-gnu.tar.gz
curl -LO https://github.com/astral-sh/uv/releases/download/$V/uv-x86_64-unknown-linux-gnu.tar.gz.sha256
sha256sum -c uv-x86_64-unknown-linux-gnu.tar.gz.sha256
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
mkdir -p ~/.local/bin && install -m 755 uv-x86_64-unknown-linux-gnu/uv uv-x86_64-unknown-linux-gnu/uvx ~/.local/bin/
uv --version
```
(Ubuntu's default `~/.profile` adds `~/.local/bin` to PATH when the folder exists. You may need to open a new terminal once.)

**Option A2:** the official installer `curl -LsSf https://astral.sh/uv/install.sh | sh` does the same, but **edits your shell rc files**. Add `UV_NO_MODIFY_PATH=1` before `sh` to prevent that.

**Option B (sudo, no uv):** `sudo apt install python3.12-venv python3-pip`, then use `python3 -m venv .venv` and pip. It works, but gives no lockfile and no easy CPU-only torch pinning, so it isn't preferred.

---

## 4. Step T1: project and core packages

```bash
mkdir -p /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge/engine && cd $_
uv init --app --name reel-engine --python /usr/bin/python3.12   # uses system 3.12, no download
```
`pyproject.toml` (the part relevant to installation):
```toml
[project]
name = "reel-engine"
requires-python = ">=3.12,<3.13"
dependencies = [
  "numpy>=2.1",
  "opencv-python>=5.0,<6",        # ONE OpenCV variant only (PySceneDetect depends on opencv-python)
  "scenedetect>=0.7.2,<0.8",
  "av>=19,<20",
  "librosa>=1.0,<1.1",
  "soundfile>=0.13",
  "pyloudnorm>=0.2",
  "pydantic>=2.10,<3",
]

[project.optional-dependencies]
ml = [
  "torch==2.11.*",                # CPU wheels via the index below (≈190 MB instead of multi-GB CUDA)
  "torchaudio==2.11.*",           # matched pair with torch
  "beat-this>=1.1",
  "faster-whisper>=1.2",
]
extras = ["opentimelineio>=0.18", "mediapipe>=1.2", "demucs>=4.1"]

[tool.uv.sources]
torch = [{ index = "pytorch-cpu" }]
torchaudio = [{ index = "pytorch-cpu" }]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```
```bash
uv sync                    # T1 only → creates .venv + uv.lock
```
**Why these pins:**
- **librosa 1.0** and **PyAV 19** require Python ≥ 3.12 ✅
- **OpenCV 5** and **PySceneDetect 0.7** are new major versions, so the smoke test (§8) confirms they work together
- **torch from PyPI on Linux pulls CUDA 13 libraries** (`nvidia-cudnn-cu13` etc.) ✅. The `explicit` CPU index avoids gigabytes of unusable GPU libraries while the NVIDIA driver is off
- torchaudio 2.11 declares only `torch>=2.11` ✅, so pinning the **same minor version** of both avoids an ABI mismatch with a newer torch

---

## 5. Step T1 assets: face model (+ optional brand fonts), KB `assets/` folder only

```bash
cd /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge && mkdir -p assets/fonts assets/models assets/LICENSES
# --- optional brand fonts (only if you say yes; v0 works with the installed Noto fonts) ---
G=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -L -o assets/fonts/Anton-Regular.ttf        $G/anton/Anton-Regular.ttf
curl -L -o assets/fonts/BebasNeue-Regular.ttf    $G/bebasneue/BebasNeue-Regular.ttf
curl -L -o assets/fonts/Poppins-Bold.ttf         $G/poppins/Poppins-Bold.ttf
curl -L -o assets/fonts/Poppins-ExtraBold.ttf    $G/poppins/Poppins-ExtraBold.ttf
curl -L -o assets/fonts/Montserrat-ExtraBold.ttf https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-ExtraBold.ttf
for f in anton bebasneue poppins; do curl -L -o assets/LICENSES/OFL-$f.txt $G/$f/OFL.txt; done
# --- face model (needed for subject-tracked 9:16 reframing) ---
curl -L -o assets/models/face_detection_yunet_2023mar.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
curl -L -o assets/LICENSES/YuNet-LICENSE.txt \
  https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/face_detection_yunet/LICENSE
```
- Static Montserrat ExtraBold comes from the upstream repo, because Google Fonts ships it as a variable font and libass may only use its default weight. Save that repo's OFL licence file into `assets/LICENSES/` as well.
- Fonts are used through `subtitles=…:fontsdir=assets/fonts`, so **nothing is installed system-wide**.
- All URLs verified to respond on 2026-11-07 🧪.

---

## 6. Step T2: ML packages and models (CPU)

```bash
uv sync --extra ml
# models download on first use. Pre-fetch so the first edit isn't slow:
uv run python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"
uv run python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
uv run python -c "from beat_this.inference import File2Beats; File2Beats(checkpoint_path='final0', device='cpu')"
```
- faster-whisper resolves `large-v3-turbo` to `mobiuslabsgmbh/faster-whisper-large-v3-turbo` (now served as `dropbox-dash/faster-whisper-large-v3-turbo`, MIT, 1.62 GB) ✅. `large-v3` = `Systran/faster-whisper-large-v3` (3.09 GB, MIT) ✅
- **Decision deferred:** turbo vs large-v3 for Tamil. Start with turbo and run the A/B in [30 §5](30-audio-analysis-tool-comparison.md#5-open-items-to-verify-after-installation). Download large-v3 only if turbo is clearly worse on your speech
- Hugging Face downloads need no account for these models

---

## 7. Step T3: optional tools (each asked for separately, when needed)

| Tool | Install | Trigger to install |
|---|---|---|
| OpenTimelineIO | `uv sync --extra extras` (or just that package) | When you want to hand-finish an edit in Resolve or Kdenlive |
| MediaPipe | same | When YuNet misses subjects (helmet, back to camera) in real footage |
| Demucs | same (uses the CPU torch already installed) | When a clip has background music that must be removed |
| Auto-Editor | GitHub Release binary → `~/.local/bin/auto-editor` (no longer published on pip ✅) | Long talking-head footage |
| Practical-RIFE | `git clone` into `engine/vendor/` + weights per its README | Only after GPU enablement, for 30 fps slow-mo |
| VA-API (sudo) | `sudo apt install intel-media-va-driver-non-free vainfo` | If CPU draft renders feel slow |
| Audacity (sudo or Flatpak) | `sudo apt install audacity` | For your own listening and recording, not the pipeline |

---

## 8. Verification (smoke test)

Run right after T1 (and again after T2). Every line must pass before any engine code is written:
```bash
cd /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge/engine
uv run python - <<'EOF'
import sys, numpy, cv2, av, scenedetect, librosa, soundfile, pyloudnorm, pydantic
print("python", sys.version.split()[0])
for m in (numpy, cv2, av, scenedetect, librosa, pydantic): print(m.__name__, m.__version__)
assert sys.version_info[:2] == (3, 12)
assert hasattr(cv2, "FaceDetectorYN"), "YuNet API missing"
print("OK core imports")
EOF
ffmpeg -hide_banner -filters | grep -wE "xfade|ass|subtitles|drawtext|loudnorm|scdet|zscale|minterpolate" | wc -l   # expect 8
```
Functional checks (synthetic fixtures with known answers, as used for analyze_reel.py 🧪):

| Test | Pass criterion |
|---|---|
| PySceneDetect 0.7 + OpenCV 5 on a clip with cuts at known frames | All cuts found within ±1 frame |
| PyAV decode of a VFR phone clip | Timestamps monotonic. Frame count matches ffprobe |
| librosa on a 120 BPM click track | Tempo 120 ± 1 |
| Beat This! on the same click track (T2) | Beats within ±20 ms (audio_beats.py baseline: 18 ms 🧪) |
| faster-whisper on one of your clips (T2) | Runs. Real-time factor recorded in [34 §6](34-tool-integration-plan.md#6-performance-log) |
| ASS render with `fontsdir` | Anton, Poppins and Noto Sans Tamil all appear in a test frame (Claude inspects the image) |
| Smooth ramp + tracked crop + blur-fill render | Durations match theory (already passed with system FFmpeg 🧪) |

---

## 9. Optional: GPU enablement (decide later)

**Recommendation: stay on CPU for now.** Reels are short. FFmpeg renders 1080×1920 faster than real time on this CPU 🧪, and faster-whisper int8 and Beat This! both run on CPU. Revisit the GPU if transcription or RIFE becomes a bottleneck.

If you approve it later:
1. `sudo ubuntu-drivers install` (installs the recommended `nvidia-driver-595-open`). Secure Boot is disabled, so no MOK enrolment is needed. **Reboot.**
2. Check with `nvidia-smi` (record the VRAM: Demucs needs ≥ 3 GB ✅, so verify before relying on it).
3. Switch the torch index to a matching CUDA build (`https://download.pytorch.org/whl/cu1xx`) in `pyproject.toml` → `uv sync --extra ml`.
4. faster-whisper on GPU needs the NVIDIA cuBLAS and cuDNN runtime libraries matching its CTranslate2 build. Follow the faster-whisper README at that time.
5. Risks: hybrid-graphics power and suspend quirks on laptops, plus kernel-update rebuilds (DKMS). Keep the ability to boot with the Intel GPU only.

---

## 10. Rollback (complete removal)

```bash
rm -rf /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge/engine/.venv   # packages (delete engine/ entirely to remove the code too)
rm -rf ~/.cache/uv ~/.cache/huggingface/hub/models--*whisper* ~/.cache/torch/hub/checkpoints   # caches and models
rm -f ~/.local/bin/uv ~/.local/bin/uvx                                # uv itself
```
No system packages, PATH files or system Python are changed by T0–T2.

---

## 11. Approval checklist (reply with what you approve)

- [ ] **T0** uv via verified tarball (Option A)
- [ ] **T1** `Instagram-Reels-Knowledge/engine/` + core packages + YuNet (+ brand fonts: yes / no)
- [ ] **T2** CPU torch + Beat This! + faster-whisper + Whisper `large-v3-turbo` and `small`
- [ ] T3 / system / GPU items: **not now** (asked when needed)

**Related:** [34 Integration plan](34-tool-integration-plan.md) · [32 Architecture](32-automated-editing-architecture.md)
