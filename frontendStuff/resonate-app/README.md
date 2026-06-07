# Resonate — Frontend

Next.js 16 app (App Router, React 19, Tailwind CSS v4, TypeScript).

## Setup

```bash
cd frontendStuff/resonate-app
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The upload page loads immediately; click **"try the sample clip"** to see the full results dashboard without uploading a video.

> **After every `git pull`, re-run `npm install`** — dependencies may have changed and `node_modules` is not committed.

## 3D Brain Visualization

The brain panel uses Three.js / WebGL. If it shows colored bars instead of a 3D brain:

- **Use Chrome or Firefox** — Safari disables WebGL by default. Enable it via *Develop → Experimental Features → WebGL* or just switch browsers.
- The bars fallback is intentional for when the mock data doesn't include parcel scores. The sample clip mock data (`lib/mock/resonateResult.json`) has full parcel data, so the 3D brain should appear in Chrome/Firefox.

## Project Structure

```
app/
  page.tsx                  # Upload page
  results/[jobId]/page.tsx  # Results dashboard
  api/
    analyze/route.ts        # Accepts video upload, returns jobId
    status/[jobId]/route.ts # Job progress polling
    results/[jobId]/route.ts# Returns analysis result
  globals.css               # Theme (orange palette, custom classes)
  layout.tsx / providers.tsx

components/
  mission-header.tsx        # Diagnosis headline + stat tiles + resonance gauge
  moment-story.tsx          # Phase breakdown + attention event timeline
  brain-visualization.tsx   # 3D Schaefer-200 parcel brain (Three.js)
  attention-timeline.tsx    # Overall attention chart (Recharts)
  modality-tracks.tsx       # Visual/audio/language chart (Recharts)
  cosmic-backdrop.tsx       # Animated canvas backdrop (upload page)
  processing-view.tsx       # Progress bar shown while job runs
  creator-feedback.tsx      # LLM markdown feedback panel
  feature-card.tsx          # Engagement/Payoff/Balance/CTA insight cards
  evidence-drawer.tsx       # Debug accordion with raw data
  video-player.tsx          # HTML5 video with seek sync
  ui/                       # shadcn/ui primitives

lib/
  types.ts                  # ResonateResult type — the backend/frontend contract
  mock/resonateResult.json  # Full mock payload (used by /api/results in dev)
  job-store.ts              # In-memory job store (replace for production)
  utils.ts                  # cn() helper
```

## Connecting the Real Backend

The three API routes currently return mock data. To connect to the Modal backend, update these files:

| File | Current | Replace with |
|------|---------|--------------|
| `app/api/analyze/route.ts` | Stores job in memory | POST video to Modal `run_tribe` endpoint |
| `app/api/status/[jobId]/route.ts` | Returns fake progress | Poll Modal for real job status |
| `app/api/results/[jobId]/route.ts` | Returns `resonateResult.json` | Fetch real result from Modal/storage |

The `ResonateResult` type in `lib/types.ts` is the expected shape — the backend response must match it.
