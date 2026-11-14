# 09 — Instagram Analytics & Growth Measurement

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory
> Last researched: 2026-11-07

---

## 1. Access & setup

- ✅ Insights require a **professional account** (Creator or Business). Switching is free. Data may take up to a day to populate.
- ✅ Access: Profile → **Professional dashboard**, or on any Reel → **View insights**.
- 🟡 **April 2026 redesign:** Insights split into **three tabs, Overview, Engagement and Audience**, and added **Skip rate**, **Share rate**, **Views over time** and a **retention chart** for videos. At rollout, collab posts, Trial Reels, cross-posted and boosted content still used the older layout ([Inro](https://www.inro.social/blog/instagram-insights-update)).

---

## 2. Metric glossary (Reels)

| Metric | Definition | Tag | What it tells you |
|---|---|---|---|
| **Views** | Number of times the Reel started playing, including replays. Instagram's primary cross-format metric since 2024–25 | ✅ | Total distribution |
| **Accounts reached** | Unique accounts that saw the Reel | ✅ | True audience size |
| **Followers vs non-followers** (reach split) | Share of reach from each | ✅ | Whether you're being recommended. Instagram tells creators to monitor this |
| **Skip rate** | Share of viewers who swipe away almost immediately (sources say ~first 3 s; exact definition unconfirmed) | 🟡 | **Hook strength**. Lower is better |
| **Watch time** | Total time watched, including replays | ✅ | Overall consumption |
| **Average watch time** | Watch time ÷ initial views (replays add to watch time but not to the divisor, so a looping Reel can exceed its own length) | ✅/🟡 | Retention. Compare with Reel length |
| **Retention chart** | % of viewers still watching at each second | 🟡 | **Exactly where people drop off** |
| **Likes, comments, saves** | Raw counts | ✅ | Engagement types |
| **Shares / Sends** | Shares to Stories, DMs or off-platform | ✅ | **Sendability**, a top signal for non-follower reach 🟡 |
| **Share rate** | Shares ÷ views or reach (new 2026) | 🟡 | Sendability, normalised |
| **Profile activity** | Profile visits, follows, link taps from this Reel | ✅ | **Conversion** |
| **Views over time** | Long-tail distribution chart | 🟡 | Evergreen vs one-day spike |
| **Audience demographics / most active times** | Age, gender, top locations, active hours | ✅ | Targeting and timing |

---

## 3. The key ratios (compute these yourself)

🔵 Raw counts scale with reach. **Ratios show quality** and let you compare a 500-view Reel with a 50,000-view one. Mosseri's advice points the same way ✅/🟡: track sends per reach, likes per reach and watch time.

| Ratio | Formula | 🔵 Rough health signal* | Stage |
|---|---|---|---|
| **Non-follower share** | non-follower reach ÷ total reach | >50% means it's being recommended | Reach |
| **Skip rate** | (shown in app) | Lower is better. Track your trend | Hook |
| **Avg % watched** | avg watch time ÷ Reel length | >50% good for 30–60 s. >80–100% strong for short Reels (loops push it above 100%) | Retain |
| **Replay factor** | views ÷ accounts reached | >1.2 means people rewatch | Retain |
| **Sends per reach** | shares ÷ accounts reached | Top Reels often sit well above your median | React |
| **Saves per reach** | saves ÷ accounts reached | Key for educational content | React |
| **Likes per reach** | likes ÷ accounts reached | Mosseri lists it among the top three | React |
| **Comments per reach** | comments ÷ accounts reached | Community / debate | React |
| **Follows per reach** (follow conversion) | follows from Reel ÷ accounts reached | Shows whether reach builds the account | Convert |
| **Profile visit → follow rate** | follows ÷ profile visits | Low means your profile isn't convincing | Convert |

\* ⚠️ **No reliable universal benchmarks exist.** Niche, length and account size vary too much ([Metricool](https://metricool.com/instagram-reel-analytics/)). **Benchmark against your own median.** Label each Reel as above or below your trailing 10-Reel median.

---

## 4. Diagnosis tree

```
Is non-follower reach ~0?
 ├─ YES → Eligibility problem → Account Status, watermark, >3 min, guidelines (see 01 §4)
 └─ NO ↓
Is skip rate higher than your median?
 ├─ YES → HOOK problem → rework frame 1, text hook, spoken hook (05 §2–3)
 └─ NO ↓
Is avg % watched below median? (check retention chart for the drop point)
 ├─ YES → BODY problem → cut slow parts, add re-hook before drop, move payoff later (03 §5, 05 §5)
 └─ NO ↓
Are sends/saves per reach below median?
 ├─ YES → VALUE problem → content watchable but not worth passing on; make it more useful/relatable/specific
 └─ NO ↓
Are follows per reach below median?
 ├─ YES → CONVERSION problem → profile, niche consistency, series, CTA (02 §7)
 └─ NO → It's working. Make more like it; test one variable at a time.
```

### Reading the retention chart (🔵)
| Shape | Meaning | Fix |
|---|---|---|
| Steep drop at 0–3 s | Hook fails | New first frame and hook |
| Steady slow decline | Normal. Aim for a flatter slope | Tighten pacing |
| Sudden cliff mid-video | A boring section, a confusing moment, or the payoff came early | Cut or rework that exact second |
| Bump or spike up | Rewatched moment, highly engaging | Do more of this. Consider opening with it |
| Drop right before the end | Viewers sensed it was over (an outro or CTA dragged) | End sooner. Loop the ending |

---

## 5. Analysing successful creators (teardown method)

🔵 Study 5–10 creators in your niche (similar size **and** larger). For each of their **top 5 Reels** (sort by views), record:

```markdown
## Teardown: @creator — <Reel topic>  (views: __, posted: __)
- Format: (tutorial / POV / listicle / storytime / before-after ...)
- Length: __ s
- Frame 1: what's on screen?
- Text hook (exact words):
- Spoken hook (exact words):
- Time to first payoff: __ s
- Cuts per 10 s: __
- Caption style: (font/placement/animation)
- Audio: (trending / original / library) — music under speech?
- SFX usage: (none / light / heavy)
- Colour look:
- Ending: (loop / CTA / payoff / abrupt)
- CTA:
- Caption first line + hashtags:
- Why I think it worked (sendability? relatability? utility?):
- What I'll borrow (structure, NOT content):
```

**Pattern extraction:** After 20–30 teardowns, tally what recurs: formats, lengths, hook types, ending styles. Those are your niche's proven patterns. ✅ **Borrow structures, never content.** Copying content breaks the originality rules and won't be recommended.

---

## 6. Your tracking sheet (start in Phase 5)

🔵 Instagram shows per-post data but doesn't show trends across posts well. Keep a simple spreadsheet:

| Column | |
|---|---|
| Date / time posted | |
| Reel title / link | |
| Pillar · format · length (s) | |
| Hook type · hook text | |
| Trial Reel? (Y/N) | |
| Views · reach · % non-follower | |
| Skip rate · avg watch time · avg % watched | |
| Likes · comments · saves · shares · follows | |
| *Computed:* sends/reach · saves/reach · follows/reach · replay factor | |
| vs. median (↑/↓) | |
| Lesson learned (1 line) | |

**Review cadence:**
- **48–72 h after posting:** initial read (the Trial Reel decision point is 72 h ✅).
- **Day 7:** final numbers for the log.
- **Monthly:** sort by each ratio. What do the top 20% share? What do the bottom 20% share? Update [02](02-reels-growth-strategy.md) pillars and formats accordingly.

---

## 7. Experiment design (🔵)

1. **One variable per test:** hook text, first frame, length, cover, caption, format, or posting time.
2. **Control for timing:** compare posts at the same age (for example 72 h) and similar posting times.
3. **Repeat:** one test is noise. Look for the pattern across 3+ tests.
4. **Use Trial Reels** ✅ to A/B hooks on non-followers without affecting followers.
5. **Document** every result in the tracking sheet, including failures.

---

## 8. Third-party analytics tools (optional)

🔵 Useful when you want cross-post trends, competitor tracking or exports: **Metricool**, **Later**, **Sprout Social**, **Hootsuite**, **Iconosquare**, **Buffer**, **Sociality.io**. They pull from Instagram's API, so some metrics (skip rate, the retention chart) may only exist in the app. **Instagram's native Insights is the source of truth.**

**Related:** [01 Algorithm](01-instagram-algorithm.md) · [02 Growth Strategy](02-reels-growth-strategy.md) · [05 Hooks](05-hooks-and-storytelling.md)
