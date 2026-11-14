# tools/

| Tool | Job | Status |
|---|---|---|
| `analyze_reel.py` | Measure a clip or render (specs, loudness, cuts, frames, safe zone, sync) | 🧪 tested |
| `audio_beats.py` | Tempo, beat grid, hits and drop of a reference audio | 🧪 tested |
| `reel_render.py` | **Render a finished Reel from an EDL** (one encode from originals) | 🧪 tested |
| `make_sfx_kit.sh` | Generate the original SFX kit in `assets/sfx/` | 🧪 tested |

---

## reel_render.py — render a finished Reel from an EDL

```bash
python3 -I tools/reel_render.py productions/P001_x/build/edl.json            # final (x264 preset slow, CRF 17)
python3 -I tools/reel_render.py productions/P001_x/build/edl.json --draft    # quick preview
```
The EDL format is documented at the top of the script. It supports, per segment: trim in/out, speed (atempo-matched audio), optional motion-interpolated slow-mo, **crop** or **blur-background** fit to 1080×1920 with a focus point, grade presets (`moviemode`, `reality`) or raw ffmpeg filters, linear zoom, **zoom punches** (eased in over 0.1 s), **shakes**, freeze-frame hold, automatic HDR→SDR tone-mapping, keep or mute natural audio, and `xfade` transitions in. Global: animated **ASS text** (Tamil supported), **SFX** at exact times, optional music with sidechain ducking, and **two-pass loudness normalisation** (default −16 LUFS / −1 dBTP). It writes `render_cmd.txt` next to the EDL for transparency.

**Tested 2026-11-07** on a mixed edit: vertical 30 fps + horizontal 60 fps sources, 3 segments, 50% slow-mo from 60 fps, punch + shake, freeze, crossfade, blur fit, both grades, Tamil and name-card text, 3 SFX. Output 1080×1920 / 30 fps, duration within 1 frame of plan (6.07 vs 6.05 s), −16 LUFS ±0.3, all spec checks PASS. Bugs found and fixed during testing: SFX mixing dropped 0.2 s of audio (fixed by padding SFX to full length), and `-shortest` cut 4 frames in the mux (removed).

**Memory-safe mode (default since 2026-11-07, P001):** 4K HDR iPhone sources ran out of memory (exit 137) when all segments were decoded in one filtergraph. Each segment is now rendered alone to a near-lossless 1080×1920 intermediate (x264 CRF 8), then assembled in the final pass. Peak RAM was 2.8 GB on P001. `--onepass` restores the old behaviour. Other P001 additions: input-level seeking per segment, `reframe: [x, y, s]` (crop from the 4K source before scaling), `tonemap` choice (default `mobius`), grades `cozy` / `cozy_lift`, loudnorm TP −1.5, exact-length mux, `loudness_lufs: null` (peak-limit only, for SFX-only versions).

## make_sfx_kit.sh — original SFX kit

`bash tools/make_sfx_kit.sh` → `assets/sfx/`: whoosh_short/long/airy, impact_hit, sub_drop, punch, pop, click, ding, riser_2s, scratch_stop, tape_stop, shutter. All are synthesised (no samples, no licences needed) and peak-normalised to −3 dBFS. Basic quality, chosen for being clean and original. Better SFX can be added to `assets/sfx/` at any time (keep licence proof in `licenses/`).

---

## analyze_reel.py — objective Reel measurements

Measures facts about a video file. It produces no opinions. Its output goes into **Part A (Verified observations)** of each Reel audit.

```bash
# one Reel
python3 -I tools/analyze_reel.py account-data/reels/R01_2026-11-04.mp4 13-reel-audits/measurements/R01

# all Reels in the folder
for f in account-data/reels/*.mp4; do
  id=$(basename "$f" | cut -d_ -f1)
  python3 -I tools/analyze_reel.py "$f" "13-reel-audits/measurements/$id"
done
```

**Outputs** (in the output folder):
| File | What it is |
|---|---|
| `metrics.md` / `metrics.json` | Format, resolution, fps, duration, bitrate, loudness (LUFS / true peak), audio start time, black frames at the start, detected cuts, shot lengths, cut-to-audio sync ratio, spec checks |
| `frames/hook_*.jpg` | Frames at 0.0, 0.5 … 3.0 s, for analysing the first-3-second hook |
| `frames/hook_*_safezone.jpg` | The same frames with Instagram UI zones shaded (red = top and bottom UI, orange = right-side buttons) |
| `contact_sheet.jpg` | One frame per detected shot, showing the visual flow at a glance |
| `transitions/cut_*.jpg` | 7 frames (0.1 s apart) around each cut, for judging transitions and text animation |

**Limits (always state these in audits):**
- Scene-cut detection is approximate. Fast motion or flashes can add false cuts, and slow dissolves can be missed.
- Audio-sync ratio = cuts within ±100 ms of a detected energy jump. It's a proxy: dialogue onsets count too, and smooth music has few onsets.
- It can't identify songs or transcribe Tamil speech. Song names come from you. Transcription would need an extra tool (ask first).
- Frames are samples, not playback. Motion feel, timing comedy and lip-sync accuracy still need your description or a judgement call, labelled as opinion.

Tested 2026-11-07 on synthetic videos (known cuts, black lead-in, beep-synced cuts): every value was measured correctly.

---

## audio_beats.py — tempo, beat grid, hits and drop (for sync planning)

```bash
python3 -I tools/audio_beats.py <audio_or_video> --fps 30 [--start 12.5 --dur 20]
```
Prints: estimated BPM, frames per beat, the beat grid (seconds + frame numbers), the strongest hits (candidate cut and impact points), the **candidate drop** (largest 1-second energy rise), and an energy curve every 0.5 s.

**Accuracy (tested 2026-11-07 on synthetic click tracks at 90, 120, 128 and 145 BPM):** tempo within 0.5 BPM, beat grid within **18 ms** of true beats over 15–24 beats (under 1 frame at 30 fps), and drop detected at the exact time.
**Limits:** real music is messier than clicks. Tempo may come out at half or double the felt tempo. Rubato or tempo changes (common in film BGM) break a fixed grid. Dialogue has no beat grid, so use the hits list instead. **Confirm by ear before final cuts.**
**Audio source for analysis:** a local reference copy you provide (for example a screen recording of the Instagram audio page playing, or your own file). Used only for timing, never baked into the export ([23 §4](../23-tamil-bgm-editing-guide.md#4-the-bgm-switch-step-by-step)).
