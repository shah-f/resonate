# Blue Agent — Reference Corpus & Blueprint Builder

## What You Are
You are Blue Agent. Your job is to find, download, and pre-score the reference video corpus for Resonate — a hackathon project that uses Meta's Tribe v2 fMRI brain encoding model to predict viewer attention in short-form videos. The output of your work becomes the pre-built Blueprints users can benchmark against inside the app.

## Context
Resonate compares a creator's video against a curated set of top-performing videos in their niche. Those reference videos need to be:
1. Found (right niche, right format, proven high performance)
2. Downloaded as local video files
3. Run through Tribe v2 on Modal to get fMRI predictions
4. Cached in a Modal Volume so the app never recomputes them

You are building 3 Blueprint packs: **Finance**, **Tech**, and **Beauty (GRWM)**.

---

## Step 1 — Find the Videos

You need 8-10 videos per niche. Search YouTube manually or via YouTube Data API. Criteria for every video:
- YouTube Shorts format (vertical, under 60 seconds)
- 500k+ views minimum
- Consistent format within the niche (see specs below)
- NOT sponsored content or compilations

### Finance — "Money Mistakes in Your 20s"
- Format: talking head, numbered list structure, hook-driven, fast cuts
- NOT crypto, investing, or stock picks — stick to budgeting/spending habits/savings
- Search terms: `money mistakes 20s #shorts`, `personal finance tips #shorts`
- Creators to check: @AyoJay, @humphreytalks, @JarradMorrow

### Tech — "Hidden iPhone/App Features"
- Format: screen recording with voiceover, rapid cuts, each tip shown in 2-3 seconds
- NOT reviews or unboxings — tips/tricks only
- Search terms: `hidden iphone features #shorts`, `apps you didn't know existed #shorts`
- Creators to check: @zohd, @iReviews, @mkbhd

### Beauty — GRWM (Get Ready With Me)
- Format: mirror setup, products visible, creator talking while applying makeup
- 30-60 seconds, one continuous scene (not fast cuts)
- Search terms: `grwm #shorts`
- Creators to check: @glamzilla, @hindash, @NikkieTutorials

Save all URLs in a file at `/Users/foramshah/brain/reference_urls.txt` formatted like:
```
# FINANCE
https://youtube.com/shorts/...
https://youtube.com/shorts/...

# TECH
https://youtube.com/shorts/...
https://youtube.com/shorts/...

# BEAUTY
https://youtube.com/shorts/...
https://youtube.com/shorts/...
```

---

## Step 2 — Download the Videos

Use yt-dlp (already installed). Download each niche into its own folder:

```bash
mkdir -p /Users/foramshah/brain/reference_videos/finance
mkdir -p /Users/foramshah/brain/reference_videos/tech
mkdir -p /Users/foramshah/brain/reference_videos/beauty

# Finance
yt-dlp -o "/Users/foramshah/brain/reference_videos/finance/%(title)s.%(ext)s" \
  "URL1" "URL2" "URL3" ...

# Tech
yt-dlp -o "/Users/foramshah/brain/reference_videos/tech/%(title)s.%(ext)s" \
  "URL1" "URL2" ...

# Beauty
yt-dlp -o "/Users/foramshah/brain/reference_videos/beauty/%(title)s.%(ext)s" \
  "URL1" "URL2" ...
```

Verify all files downloaded correctly — check file sizes (each should be >1MB) and confirm they play.

---

## Step 3 — Run Tribe v2 on Each Video

Use the Modal script at `/Users/foramshah/brain/resonate_tribe_modal.py`.

Every video returns **three modality tracks** — visual, audio, and language — not a single score. The Blueprint average is computed separately per modality so comparisons remain meaningful even when a video is strong in one dimension but weak in another.

Create a new script at `/Users/foramshah/brain/resonate_score_corpus.py`:

```python
import modal
import numpy as np
import json
from pathlib import Path
from resonate_tribe_modal import run_tribe

NICHES = ["finance", "tech", "beauty"]
BASE_PATH = Path("/Users/foramshah/brain/reference_videos")
OUTPUT_PATH = Path("/Users/foramshah/brain/reference_scores")
MODALITIES = ["visual", "audio", "language"]

OUTPUT_PATH.mkdir(exist_ok=True)
for niche in NICHES:
    (OUTPUT_PATH / niche).mkdir(exist_ok=True)

for niche in NICHES:
    video_dir = BASE_PATH / niche
    videos = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.webm"))

    print(f"\nProcessing {niche} — {len(videos)} videos")

    # Store per-modality time series for each video
    modality_series = {m: [] for m in MODALITIES}
    parcel_series = []
    metadata = []

    for video_path in videos:
        print(f"  Running Tribe on {video_path.name}...")
        video_bytes = video_path.read_bytes()
        result = run_tribe.remote(video_bytes, video_path.name)

        # Save raw predictions
        preds = np.array(result["predictions"])
        np.save(OUTPUT_PATH / niche / f"{video_path.stem}_raw.npy", preds)

        # Save per-modality time series
        for m in MODALITIES:
            series = np.array(result["modality"][m])  # (n_timesteps,)
            np.save(OUTPUT_PATH / niche / f"{video_path.stem}_{m}.npy", series)
            modality_series[m].append(series)

        # Save parcel scores (200 regions x timesteps)
        parcels = np.array(result["parcels"])
        np.save(OUTPUT_PATH / niche / f"{video_path.stem}_parcels.npy", parcels)
        parcel_series.append(parcels)

        metadata.append({
            "filename": video_path.name,
            "shape": result["shape"],
            "segments": result["segments"],
            "mean_scores": {
                m: float(np.array(result["modality"][m]).mean())
                for m in MODALITIES
            },
        })
        print(f"  ✓ {video_path.name} — visual: {metadata[-1]['mean_scores']['visual']:.3f} | audio: {metadata[-1]['mean_scores']['audio']:.3f} | language: {metadata[-1]['mean_scores']['language']:.3f}")

    # Blueprint average: computed per modality separately
    # Trim to shortest series before averaging
    blueprint = {}
    for m in MODALITIES:
        min_len = min(s.shape[0] for s in modality_series[m])
        trimmed = [s[:min_len] for s in modality_series[m]]
        blueprint[m] = np.mean(trimmed, axis=0)  # (n_timesteps,)
        np.save(OUTPUT_PATH / niche / f"blueprint_{m}.npy", blueprint[m])

    # Blueprint parcel average (for 3D brain viz)
    min_len = min(p.shape[0] for p in parcel_series)
    trimmed_parcels = [p[:min_len] for p in parcel_series]
    blueprint_parcels = np.mean(trimmed_parcels, axis=0)
    np.save(OUTPUT_PATH / niche / "blueprint_parcels.npy", blueprint_parcels)

    # Save metadata + blueprint summary
    blueprint_summary = {
        m: float(blueprint[m].mean()) for m in MODALITIES
    }
    with open(OUTPUT_PATH / niche / "metadata.json", "w") as f:
        json.dump({"videos": metadata, "blueprint": blueprint_summary}, f, indent=2)

    print(f"\n  ✅ {niche} Blueprint:")
    for m in MODALITIES:
        print(f"     {m}: {blueprint_summary[m]:.3f}")

print("\n✅ All niches scored. Reference corpus ready.")
```

Run it:
```bash
cd /Users/foramshah/brain
python3 resonate_score_corpus.py
```

**Note:** Each video = one full Tribe v2 GPU run (~2-5 min). With 24-30 videos total, budget 1.5-2 hours. Start it and let it run in the background.

---

## Step 4 — Verify Outputs

After the script finishes, confirm the output structure looks like this:

```
reference_scores/
  finance/
    video1.npy
    video2.npy
    ...
    blueprint_average.npy
    metadata.json
  tech/
    ...
    blueprint_average.npy
    metadata.json
  beauty/
    ...
    blueprint_average.npy
    metadata.json
```

Spot-check one niche:
```python
import numpy as np, json

# Check per-modality Blueprint averages
for m in ["visual", "audio", "language"]:
    arr = np.load(f"reference_scores/finance/blueprint_{m}.npy")
    print(f"{m}: shape={arr.shape}, mean={arr.mean():.3f}, min={arr.min():.3f}, max={arr.max():.3f}")

# Check parcel Blueprint
parcels = np.load("reference_scores/finance/blueprint_parcels.npy")
print(f"parcels: shape={parcels.shape}")  # Should be (n_timesteps, 200)

# Check metadata summary
with open("reference_scores/finance/metadata.json") as f:
    meta = json.load(f)
print("Blueprint summary:", meta["blueprint"])
# Expected: {"visual": 0.xxx, "audio": 0.xxx, "language": 0.xxx}
```

If all three modality arrays are non-zero and parcel shape is (n_timesteps, 200) — Blue Agent is done.

---

## Step 5 — Upload to Modal Volume

Once scores are confirmed, upload the blueprint averages to the Modal Volume so the app can access them at inference time:

```python
import modal
import numpy as np
from pathlib import Path

volume = modal.Volume.from_name("tribe-model-cache")

# Upload blueprint averages for each niche
niches = ["finance", "tech", "beauty"]
base = Path("/Users/foramshah/brain/reference_scores")

with volume.batch_upload() as batch:
    for niche in niches:
        avg_path = base / niche / "blueprint_average.npy"
        batch.put_file(avg_path, f"/blueprints/{niche}/blueprint_average.npy")
        
        meta_path = base / niche / "metadata.json"
        batch.put_file(meta_path, f"/blueprints/{niche}/metadata.json")

print("✅ Blueprints uploaded to Modal Volume.")
```

---

## Done
When all steps are complete, the reference corpus is ready. The app can load any Blueprint by reading `/blueprints/{niche}/blueprint_average.npy` from the Modal Volume — no recomputation needed.

Report back: how many videos per niche were scored, any errors encountered, and the shape of the blueprint_average.npy files.
