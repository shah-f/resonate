# Resonate — Hackathon Plan

**Event:** NYTW Intern Hackathon, Jun 7 (12 hours)
**Team:** 2 people
**One-liner:** Know exactly where your video loses viewers — and what your brain is missing compared to the top creators in your niche.

---

## The Idea

Upload a video. Resonate runs it through **Tribe v2** (Meta's fMRI brain encoding model) to predict second-by-second cortical activation across ~20,000 brain vertices. Those vertices are mapped to named brain regions using the **Schaefer-200 brain atlas** so outputs say "visual cortex" and "anterior insula" — not raw numbers. It then compares activation patterns against a pre-scored reference pack of top-performing creator videos in your niche. GPT-4o translates the neuroscience delta into plain-language suggestions a creator can actually act on.

**Why this wins:**
- Genuinely novel — no existing tool uses predicted brain response for content optimization
- Technically hard (Tribe v2 + brain atlas mapping + fMRI signal processing + LLM pipeline)
- Jaw-dropping demo (named brain regions lighting up over a video timeline)
- Targets content creators — 50M+ who have no access to neuroscience tools today, unlike ad agencies that already have Kantar/Nielsen/Ace Metrix

---

## New feature idea

I would position it less as a "brain map" and more as a Brain Network Timeline.

The problem with lighting up 200 Schaefer regions is that judges won't know what they're looking at. The moment you aggregate into interpretable networks, the feature becomes understandable.

Feature: Brain Network Timeline

Description

Visualize how different cognitive systems are engaged throughout a video. Rather than displaying raw cortical regions, Resonate groups Schaefer-200 activations into color-coded brain networks and shows how they rise and fall over time.

Each second of the video is mapped to the dominant cognitive systems being activated:

Network	Color	What it represents
Visual Network	Blue	Processing imagery, motion, scene changes
Auditory Network	Green	Processing sound, music, voice
Language Network	Red	Processing words, captions, narration
Attention Network	Yellow	Sustained focus and engagement
Salience Network	Orange	Novelty, surprise, emotionally important moments
Executive Control Network	Purple	Higher-order reasoning and decision making
User Experience

As the video plays:

0:03
🟦 Visual spikes
→ Fast scene change

0:08
🟨 Attention drops
→ Viewer likely begins disengaging

0:11
🟧 Salience spike
→ Unexpected event captures attention

0:18
🟥 Language dominates
→ Heavy information density

The brain visualization lights up regions on a cortical map, while the timeline below shows which networks are responsible.

Why This Is Valuable

Instead of saying:

"Parcel 137 activation decreased by 23%"

Resonate can say:

"Your Attention Network collapses 5 seconds before your CTA."

or

"Top-performing videos in this niche maintain stronger Salience Network activation during the first 8 seconds."

That's a much stronger creator insight.

Demo Pitch

Brain Network Timeline shows which cognitive systems are active at every moment of a video. By color-coding Schaefer-200 brain regions into interpretable networks like Visual, Language, Attention, and Salience, creators can see not only where engagement drops, but why it drops.

I would honestly make Attention Network and Salience Network the stars of the show. Most competitors can tell creators where viewers leave. Resonate can claim to show which cognitive systems stopped engaging the viewer before they left. That's the differentiator.

---

## Per-Modality Breakdown — Default Everywhere

Every score, dip, comparison, and Blueprint similarity in Resonate is broken down into **three modality tracks**:

| Modality | Brain Regions | What it measures |
|---|---|---|
| **Visual** | Occipital cortex, visual association areas | How hard the brain is working to process what it *sees* |
| **Audio** | Superior temporal gyrus, auditory cortex | How hard the brain is working to process what it *hears* |
| **Language** | Broca's area, Wernicke's area, angular gyrus | How hard the brain is working to process *words and meaning* |

A single overall score is never shown alone — it always appears alongside the three modality breakdowns. This prevents a video with great audio but weak visuals from appearing "equal" to one with great visuals but weak audio.

**Example output format used everywhere:**
```
Overall: 71%
  Visual:   89% ✅
  Audio:    45% ⚠
  Language: 68%
```

---

## Core Features

### 1. Engagement Autopsy
- Full-video scan, attention dips flagged on a timeline
- All meaningful engagement dips flagged, not just the worst one
- Each dip labeled by **which modality dropped** — e.g. "Visual attention fell here (-42%)" or "Audio engagement dropped (-31%)"
- Hook zone (first 3–8s) highlighted separately with per-modality breakdown
- Use Tribe's event dataframe and parsed segment timings to align dips with the exact extracted video/audio/text event rows that produced them
- GPT-4o "why + fix" explanation at each dip, informed by which modality caused it

### 2. Sound-Off Score
- Run Tribe twice: once on full video, once muted (video-only)
- Gap shown **per modality**: visual stays flat (expected), audio drops (expected), language drops (shows how much meaning was carried by voice)
- Overall muted score + per-modality delta
- **Why:** ~75–85% of social video is watched muted first; creators can't pre-test silent performance today

### 3. Modality Balance
- Run Tribe with full video → compare visual vs audio vs language activation per timestep
- **Balance bar** — three-way split: Visual | Audio | Language (e.g. 28% / 20% / 52%)
- **One-line verdict** — e.g. *"Language-heavy — meaning is carried by words, not visuals or sound"*
- **Timeline strip** — three-color second-by-second chart (blue=visual, green=audio, red=language); click a spike to jump to that moment
- Back each spike with saved event metadata, so the UI can explain whether the moment came from visual frames, audio/voice, text/language extraction, or timing overlap
- **vs Blueprint/niche** — your three-way split vs reference pack average
- GPT-4o structural fix suggestion — no re-run needed
- **Fix + proof (optional)** — suggested structural edit (shorten copy, delay VO, add b-roll) with before/after balance shift if there is time to support a simulated rerun
- **Note:** computed from the same Tribe run, no extra GPU cost

### 4. CTA Window Finder
- Finds the optimal timestamp to place the CTA (click/subscribe/buy)
- Shows **per-modality attention** at the optimal moment — e.g. "Visual: 84%, Audio: 71%, Language: 90% at 0:18"
- Flags when CTA lands after any modality has already significantly dropped
- Uses parsed segment start/end times, not just array index, so CTA recommendations map cleanly back onto the video player
- **Why:** CTA too early = annoying; too late = they've scrolled — creators guess today with no data

### 5. Pacing Alert
- Detects long stretches with no visual change and correlates them with Tribe engagement dips
- Uses **PySceneDetect** (Python, CPU-only) for scene-cut detection — no extra ML model needed
- Cross-checks scene-cut timing against Tribe event rows and segment metadata so "held too long" warnings can distinguish edit pacing from weak language/audio content
- Flags moments where the edit holds too long while predicted attention falls
- **Why:** Short-form editors already know "don't hold a shot too long" — this validates that instinct with predicted brain response

### 6. Full Signal Capture
- Every paid Modal inference should preserve all useful model-side context, not only the final score arrays
- Save raw predictions, parsed segments, Tribe event dataframe records/columns, video metadata, model/cache metadata, atlas parcel names, modality indices, and modality keywords
- **Why:** lets us debug, create richer explanations, re-score with improved analysis logic, and interpret old parcel arrays without spending Modal credits again
- JSON remains the full-fidelity artifact; compressed NPZ stores the major numeric arrays plus object metadata for quick analysis

---

## Brain Atlas Mapping (technical depth layer)

Tribe v2 outputs raw predictions across ~20,000 cortical vertices on the fsaverage5 mesh. To make these human-readable:

- Load the **Schaefer-200 parcellation** (200 named cortical regions mapped to fsaverage5)
- Average vertex-level activation within each parcel → 200 region-level scores per timestep
- Map regions to plain-English functions: e.g. region 14 → "primary visual cortex", region 87 → "language processing"
- Save parcel names and modality indices with every new inference result, and keep the global mapping artifact at `results/schaefer200_modality_mapping.json`
- This layer runs inside the Modal function — no extra service needed

**Why this matters for judges:** This is real neuroscience, not a black box. A neuroscientist in the audience will recognize the atlas and know this isn't faked. It's the detail that separates serious ML work from a GPT wrapper.

---

## Reference Corpus

- **8–12 top-performing YouTube Shorts per niche**: Finance (money mistakes), Tech (hidden iPhone features), Beauty (GRWM)
- Source: proven high-retention Shorts — validated by view count and engagement
- Manually curated and format-consistent; avoid scraped random reels, compilations, and sponsored outliers
- **Pre-score with Tribe + atlas mapping the night before via Blue Agent** (`resonate_blue_agent.md`)
- Stored per modality: `blueprint_visual.npy`, `blueprint_audio.npy`, `blueprint_language.npy` per niche
- At inference time: compare user's per-modality scores against niche Blueprint, compute delta per modality per timestep

**Category-pack note:** The early plan framed this as Beauty / Fitness / DTC ad packs. For the hackathon, the active corpus is Finance / Tech / Beauty because those niches are easier to source quickly from YouTube Shorts while keeping formats consistent. The same system can later support ad-specific packs like Beauty, Fitness, and DTC.

---

## Engines

- **Tribe v2** — brain response sensor
- **Schaefer-200 Atlas Mapper** — converts raw surface vertices into named brain-region and modality scores
- **Semantic Collision** — explains why dips happen when modality load, content, or timing fight each other
- **Retention Translator** — converts Tribe/modality signals into creator-friendly predicted retention language
- **Edit Simulator** — optional structural fixes with re-prediction proof when time allows
- **PySceneDetect** — scene cuts for Pacing Alert; lightweight CPU helper, not another ML dependency

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | **Next.js** | One repo, built-in API routes, Vercel deploy in one command |
| GPU inference | **Modal** | Serverless, $30 free credits, 20-line deploy, scales to zero |
| API layer | **Next.js API routes** | Calls Modal + OpenAI directly — no second service to manage |
| Brain atlas | **Schaefer-200 + nilearn** | Real neuroscience parcellation, runs inside Modal |
| Pacing helper | **PySceneDetect** | CPU-only scene-cut detection for Pacing Alert |
| LLM | **GPT-4o** (Claude fallback) | Fast, reliable; both API keys in .env |
| Reference storage | **JSON/numpy files** | Pre-computed atlas scores, served statically — no DB needed for demo |

### Architecture
```
[Next.js frontend]
  → upload video
  → [Next.js API route]
      → [Modal endpoint]
            → Tribe v2 inference → 20k vertex fMRI predictions
            → capture Tribe event dataframe + parsed segment timing + run metadata
            → Schaefer-200 atlas → 200 named region scores × timesteps
            → dip detection + Sound-Off delta + CTA window + pacing alerts
      → [OpenAI GPT-4o] → plain-language suggestions per region/dip
  → render timeline + named brain region heatmap + suggestions
```

---

## Inference Performance

For a **15-second video** on a pre-warmed Modal container:
- Tribe v2 inference: ~15–30s
- Atlas mapping (nilearn parcel averaging): ~2–3s
- GPT-4o suggestions: ~5–10s
- **Total: ~30–45 seconds end-to-end**

**Demo strategy:** Pre-warm Modal before judges arrive. Use a 15-second clip. Show a "mapping brain response..." loading state with brain region names appearing — judges lean in, not out.

---

## Team Split

| Person 1 (ML/Backend) | Person 2 (Frontend/UI) |
|---|---|
| Tribe v2 on Modal | Next.js app + video upload |
| Schaefer-200 atlas mapping in Modal | Retention curve + timeline UI |
| Curate + pre-score reference corpus | Brain region heatmap visualization |
| Dip detection + Sound-Off delta + CTA logic | Sound-Off + CTA UI components |
| PySceneDetect pacing pipeline | Pacing Alert timeline markers |
| GPT-4o prompt engineering + API routes | Pitch deck + backup demo video |

---

## Hackathon Build Order

**Before hackathon (night of Jun 6):**
- [ ] **Run Atlas Agent first** (`resonate_atlas_agent.md`) — verifies and corrects the Schaefer-200 region indices for visual/audio/language modalities in `resonate_tribe_modal.py`.
  - ⚠️ **MUST run Atlas Agent before Blue Agent.** Blue Agent scores the entire reference corpus using these indices. If the indices are wrong when Blue Agent runs, all Blueprint averages will be incorrect and you'll have to re-score everything from scratch (2+ hours wasted).
- [ ] **Run Blue Agent second** (`resonate_blue_agent.md`) — only after Atlas Agent confirms indices are correct. — finds, downloads, and pre-scores all reference videos for Finance, Tech, and Beauty niches. Uploads Blueprint averages to Modal Volume. Budget 2 hours for this — start it first, let it run in the background.

- [ ] Set up Modal account, deploy Tribe v2 endpoint, confirm it returns predictions
- [ ] Install Schaefer-200 atlas via nilearn, confirm parcel averaging works on Tribe output
- [ ] Curate 8–12 reference videos per niche via YouTube Data API, pre-score with Tribe + atlas, store as numpy arrays
- [ ] Scaffold Next.js app, confirm video upload → API route works end-to-end
- [ ] Install PySceneDetect and confirm scene-cut detection on one demo clip

**Hour 0–3 (foundation):**
- [ ] Modal endpoint: Tribe v2 + atlas mapping → returning named region scores
- [ ] Next.js API route wired to Modal + OpenAI
- [ ] Video upload → inference → raw region scores working

**Hour 3–7 (features):**
- [ ] Engagement Autopsy: dip detection per region + GPT-4o explanations
- [ ] Sound-Off Score: muted vs full delta by brain region
- [ ] CTA Window Finder: optimal timestamp from attention curve
- [ ] Reference pack comparison: user scores vs niche average per region
- [ ] Pacing Alert: scene-cut timestamps + long-hold warnings aligned to engagement dips

**Hour 7–10 (UI polish):**
- [ ] Named brain region heatmap on video timeline
- [ ] Retention curve chart with dip markers
- [ ] Benchmark overlay, modality balance, sound-off gap, and pacing markers
- [ ] Clean, polished frontend — this is what judges see

**Hour 10–12 (demo prep):**
- [ ] Pre-cache 3–4 demo videos (include 1 sound-off + 1 CTA timing + 1 pacing example)
- [ ] Pre-warm Modal container
- [ ] Record backup demo video in case of live failure
- [ ] Pitch rehearsal

---

### 5. Blueprint
- Creator uploads 3 "inspiration" videos they want to emulate
- Tribe v2 runs on each → Schaefer-200 atlas applied → **per-modality averages** computed (visual, audio, language separately)
- User uploads their own video → compared against Blueprint per modality → three similarity scores + per-modality gap analysis
- GPT-4o translates gaps into plain-language suggestions: *"Your visual score is 40% below your Blueprint — add more motion or scene cuts. Your audio is on par."*
- **Blueprint Analysis button** — shows the Blueprint's per-modality profile on its own (what brain activation pattern the 3 inspiration videos collectively produce), without needing to upload a new video

**Similarity output format:**
```
Blueprint Match
───────────────────────
Overall:   71%
Visual:    89% ✅
Audio:     45% ⚠  — biggest gap
Language:  68%
```

**Caching (critical — avoids recomputing Tribe on the same videos):**
- Cache key: SHA-256 hash of the 3 uploaded video files
- Store results in Modal Volume at `/cache/blueprints/{hash}/`
  - `video1_{modality}.npy`, `video2_{modality}.npy`, `video3_{modality}.npy` — per modality
  - `blueprint_visual.npy`, `blueprint_audio.npy`, `blueprint_language.npy` — averaged per modality
  - `metadata.json` — filenames, timestamps, per-modality mean scores
- On Blueprint load: check if hash exists in Volume → return cached instantly, skip Tribe recomputation
- Blueprints are per-user for now (no sharing)

---

## Add If Time Permits

- **YouTube Retention Curve Correlation** — connect creator's YouTube account via OAuth, pull actual retention curve for an existing video, overlay it against Tribe's predicted brain activation curve for the same video. The mic drop demo moment: Tribe predicts attention drops at 8s and 23s, you reveal the real retention curve — and the drops match. Validates the entire premise live in front of judges.
  - **MUST pre-test tomorrow before building** — Tribe won't perfectly match every retention curve (real retention is also affected by thumbnail clickbait, audience mismatch, algorithm distribution). Run it on 3-4 real videos, plot both curves, confirm the correlation is visually compelling. If it holds → build it as the centerpiece. If it's noisy → cut it, you've lost nothing.
  - Requires: YouTube OAuth + YouTube Analytics API (separate from Data API)

- **Predicted Retention Curve** — train a simple regression on pre-scored reference corpus (Tribe brain scores → actual YouTube retention %) to output a predicted retention curve for new uploads. Real ML work, no OAuth needed, bridges neuroscience to a metric creators already understand. Requires good corpus coverage tomorrow to be meaningful.

- **Script input in frontend shell** — show the future Script-First workflow as a disabled or lightweight panel if it helps the pitch, but do not build the full scoring pipeline during the hackathon.

---

## Cut for Hackathon
- Vector similarity search (cool tech, weak user value)
- Script-First Mode (different pipeline — post-hackathon)
- Hook Shootout (too slow per variant — post-hackathon)
- Auth, billing, auto mood boards, competitor snapshot

---

## Post-Hackathon Roadmap
- Hook Shootout — upload 2–5 hook variants, rank by predicted retention
  - **Why later:** Not technically hard, but each hook requires a full Tribe GPU run. Five variants can mean 10–25 minutes of inference, plus comparison UI and pre-caching.
- Script-First Mode — paste script or upload scratch VO → Tribe scores before you shoot
  - **Why:** Production is expensive ($500–5K+ per ad); testing copy first avoids wasted shoots.
- Expand niche reference packs (auto-updated via YouTube Data API)
- Auto-pull trending content per category from legal sources
- Auto mood board from creator preferences
- Custom reference sets (creator uploads their own top-performing videos as baseline)
- **Instagram Reels support** — use Apify Instagram Reels scraper to build reference corpus and accept Reel URLs as input (no official API needed); yt-dlp for free video downloads, Apify for engagement metrics to validate top performers
