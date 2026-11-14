# 27 — Audio Matching Framework

> **Phase 3** · Created 2026-11-07 · Used in Stage 2 of [26](26-video-production-workflow.md#4-stage-2--audio-research--matching)
> Inputs: footage report ([26 §3](26-video-production-workflow.md#3-stage-1--footage-analysis)), audio log ([account-data/audio-log.md](account-data/audio-log.md)), discovery rules ([22](22-instagram-audio-discovery.md)), role library ([15 §3](15-tamil-music-and-audio-strategy.md#3-audio-role-library-choose-by-the-job-not-the-song))
> **Non-negotiable:** no invented usage counts and no "trending" claim without dated evidence ([22 §4](22-instagram-audio-discovery.md#4-evidence-standard-for-audio-claims)).
> **⚡ Autonomous mode (default since 2026-11-07):** I run this framework internally and **make the final selection myself**. No approval step. The delivery reports the chosen audio, its source and reference, the evidence status, and why it won, plus a one-line note on the runners-up. See [26](26-video-production-workflow.md#-autonomous-mode-the-default-since-2026-11-07).

---

## 1. Process overview

```
Footage report ──► audio roles needed ──► ≥5 candidates ──► gates (pass/fail)
   ──► score (weighted) ──► verification list (screenshots) ──► final scores
   ──► 5 category winners + 1 recommendation + sync map ──► ✋ GATE 1 (you approve)
```

---

## 2. Candidate sourcing (aim for ≥5, mixed)

| Slot | Source | Purpose |
|---|---|---|
| 2–3 | **Audio log**, verified entries matching the needed role | Evidence-backed options |
| 1–2 | **Evergreen Tamil** for the role (iconic BGM or comedy dialogue) | Reliable cultural recognition |
| 1 | **Fresh / possibly trending Tamil** from current film releases or leaderboard screenshots | Trend upside |
| 1 | **Unexpected / creative**: an audio from a contrasting genre (Inflate mode, [23 §1](23-tamil-bgm-editing-guide.md#1-how-tamil-bgm-led-edits-work)) | Surprise |
| 1 | **English** option | Universal concept, or a reach test |

If fewer than 5 suitable candidates exist, I say so rather than padding the list.

---

## 3. Gates (pass/fail before scoring)

| Gate | Fails if… |
|---|---|
| **Availability** | Not findable in Instagram's library for your account type (business accounts have restricted music, [15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific)) |
| **Use type** | The Reel is paid or branded and the audio is a library film song (commercial use not covered, per Zee v. Nykaa) |
| **Cultural safety** | The joke depends on mocking a community, caste, religion or political group, or provokes fan wars ([23 §7](23-tamil-bgm-editing-guide.md#7-cultural--safety-notes-for-tamil-audio-content-)) |
| **Footage fit** | No moment in the footage can carry the audio's key moment (no possible sync) |

---

## 4. Scoring

### 4.1 Criteria & weights (from your brief)
| Criterion | Importance | Weight | Evidence basis |
|---|---|---|---|
| **Relevance to the video** | Very high | **3** | Footage report vs audio role (opinion, reasoned) |
| **Tamil audience appeal** | High | **2** | Cultural recognisability: iconic status, film or composer popularity (opinion + public sources) |
| **Comedy / emotional suitability** | Very high | **3** | Does the audio *create* the joke or emotion with this footage? (opinion) |
| **Current popularity** | High | **2** | **Only from screenshots:** count, ↗, velocity, recent top Reels. Otherwise `?` |
| **Beat synchronisation** | Very high | **3** | Measured (audio_beats.py on a reference) + footage moments: can H/D/S land on real moments? |
| **Trend longevity** | Medium | **1** | Lifecycle stage ([22 §4.1](22-instagram-audio-discovery.md#41-trend-lifecycle-classification-rules-no-invented-thresholds)). Evergreen = high |

### 4.2 Score anchors (1–5)
| Score | Meaning |
|---|---|
| 5 | Exceptional: this audio was made for this clip |
| 4 | Strong fit |
| 3 | Works |
| 2 | Weak, a stretch |
| 1 | Poor |
| ? | **No evidence** (popularity only). Excluded from the total |

### 4.3 Totals
- **Fit score** = weighted sum **excluding popularity** ÷ 60 × 100 → always computable, used for ranking
- **Full score** = weighted sum **including popularity** ÷ 70 × 100 → only when popularity has evidence
- Both are shown. **Missing evidence never inflates a score.**

---

## 5. The five category winners + one recommendation

| Category | Selection rule |
|---|---|
| 🏆 **Best overall** | Highest Fit score (Full score if available) that passes all gates |
| 📈 **Best trending** | Highest **verified** popularity (↗ seen and/or positive velocity) with Fit ≥ 60. If none is verified: "No verified trending option. Screenshots needed" |
| 🤣 **Best comedy** | Highest comedy/emotional score for a comedic use (for an emotional concept, I also name a "best emotional") |
| 🎲 **Best unexpected / creative** | The strongest contrast-based option (Inflate or Break mode) with a clear sync point. Reasoned opinion |
| 🌍 **Best English alternative** | Highest-scoring English candidate |
| ✅ **My recommendation** | One final pick with reasoning. It can differ from "best overall" when strategy calls for it (e.g. a Tamil-vs-English test, or series consistency). **Waits for your approval** |

---

## 6. Required fields per audio (your 7 + mine)

| # | Field | Rule |
|---|---|---|
| 1 | **Audio name** | Exactly as on Instagram (from a screenshot), or "as found in search: …" |
| 2 | **Original source** (film / artist / composer) | From the audio page or a reliable public source. Otherwise "not confirmed" |
| 3 | **Instagram reference** | Audio page link or a Reel link using it (from you or a public page). Otherwise "needs link" |
| 4 | **Usage count** | **Screenshot + date only.** Otherwise `UNVERIFIED` |
| 5 | **Successful example Reels** | From screenshots or links with visible metrics. Otherwise "none verified" |
| 6 | **Growing / declining** | Velocity from two dated counts, or the age of top Reels. Otherwise "direction unknown" |
| 7 | **Why it suits my video** | The specific footage moment ↔ audio moment |
| + | **Role & mode** | e.g. Hero · Inflate |
| + | **Sync points** | H / D / S times in the track |
| + | **Licensing notes** | Library / commercial restrictions |

---

## 7. Sync map (for each shortlisted audio)

| Video moment (clip @ time) | Audio moment (track time) | Marker | Technique |
|---|---|---|---|
| e.g. rabbit turns head (C2 @ 3.40) | the hook phrase's first hit (0:42.10) | H | Open on this frame |
| e.g. bike fails to start (C1 @ 8.20) | right before the drop (0:47.60) | S | BGM switch ([23 §4](23-tamil-bgm-editing-guide.md#4-the-bgm-switch-step-by-step)) |

**The recommended audio's sync map becomes the backbone of the edit plan.**

---

## 8. Report format (what you receive)

```markdown
# Audio Options — P___ · <title>
Evidence date: YYYY-MM-DD · Live Instagram data: <from your screenshots / UNAVAILABLE for: …>

## Roles this footage supports
- …

## Candidates
| # | Audio (name · source) | Lang | Role · mode | Rel ×3 | Tamil ×2 | Com/Emo ×3 | Pop ×2 | Sync ×3 | Long ×1 | Fit % | Full % |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Evidence per audio
### A) <name>
1. Name: … 2. Source: … 3. IG reference: … 4. Usage: … (screenshot, date) / UNVERIFIED
5. Examples: … 6. Direction: … 7. Why it suits: …
Sync points: H … D … S …
Licensing: …

## Winners
🏆 Overall: … · 📈 Trending: … · 🤣 Comedy: … · 🎲 Creative: … · 🌍 English: …

## ✅ Recommendation: <one audio>
Why: … · Sync map: (table) · Risks: …

## Needed from you
- Screenshot the audio pages of: …
- Approve / choose another / ask for more options
```
Template file: [productions/_templates/02-audio-options.md](productions/_templates/02-audio-options.md)

---

## 9. Worked example (structure only, with placeholder audios, not real data)

> Footage (hypothetical): 12 s clip. You walk to the R15 in slow motion, kick or press start, it doesn't start, you stare at the camera.
> Roles needed: Hero (setup) + Comedy (reality) → a **Break**-mode switch.

| # | Audio | Role · mode | Rel | Tamil | Com/Emo | Pop | Sync | Long | Fit % |
|---|---|---|---|---|---|---|---|---|---|
| A | [Mass hero BGM, iconic] | Hero · Break | 5 | 5 | 4 | ? | 5 | 5 | 95 |
| B | [Recent film theme] | Hero · Break | 4 | 4 | 4 | ? | 4 | 3 | 78 |
| C | [Classic comedy dialogue] | Comedy · Fulfil | 4 | 5 | 5 | ? | 3 | 5 | 85 |
| D | [Romantic melody] | Romance · Inflate | 3 | 4 | 4 | ? | 3 | 4 | 70 |
| E | [English dramatic instrumental] | Hero · Break | 4 | 2 | 4 | ? | 4 | 3 | 72 |

How Fit % is computed, for example A: (5×3 Rel + 5×2 Tamil + 4×3 Com + 5×3 Sync + 5×1 Long) = 57 ÷ 60 = **95%**. Popularity (`?`) is excluded until verified.
Popularity is `?` for all of them, so "Best trending" = "No verified trending option. Please screenshot A, B, E audio pages." Recommendation: **A + C as a multitrack switch** ([23 §4](23-tamil-bgm-editing-guide.md#4-the-bgm-switch-step-by-step)), pending your approval.

**Related:** [22](22-instagram-audio-discovery.md) · [23](23-tamil-bgm-editing-guide.md) · [24](24-beat-sync-and-sound-design.md) · [26](26-video-production-workflow.md)
