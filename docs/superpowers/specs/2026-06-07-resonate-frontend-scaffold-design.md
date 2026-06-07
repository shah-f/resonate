# Resonate Frontend Scaffold — Design Spec

**Date:** 2026-06-07
**Author:** Ami (frontend)
**Scope:** Plumbing-only scaffold. No UI components — Esha's Lovable/Figma design plugs in.

---

## Context

Hackathon day. Esha is building the visual design in Lovable/Figma. Ami builds the data layer so Esha can drop components into a working skeleton. Backend mock data is already available at `results/finance_test_clip_insights.json`.

---

## Location

`frontendStuff/resonate-app`

---

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (installed, used by Esha's chart components)

---

## File Structure

```
frontendStuff/resonate-app/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                        # Upload page (/)
│   ├── results/[jobId]/
│   │   └── page.tsx                    # Results page shell
│   └── api/
│       ├── analyze/
│       │   └── route.ts               # POST → { jobId: string }
│       ├── status/[jobId]/
│       │   └── route.ts               # GET → { status, message? }
│       └── results/[jobId]/
│           └── route.ts               # GET → ResonateResult
├── lib/
│   ├── types.ts                        # All TypeScript types
│   ├── mock-adapter.ts                 # insights JSON → ResonateResult
│   └── mock/
│       └── insights.json              # copy of finance_test_clip_insights.json
└── public/
    └── demo-clip.mp4                  # copy of test_clips/finance_test_clip.mp4
```

---

## TypeScript Types (`lib/types.ts`)

Sourced from `frontendStuff/FRONTEND_PLAN.md`. All types must be exported.

```ts
export type ResonateResult = {
  videoUrl: string;
  filename?: string;
  duration: number;
  brain: {
    segments: Array<{ start: number; end: number }>;
    modality: { visual: number[]; audio: number[]; language: number[] };
    normalizedTracks?: { visual: number[]; audio: number[]; language: number[] };
    overall: number[];
    parcels?: number[][];
    parcelNames?: string[];
    modalityIndices?: { visual: number[]; audio: number[]; language: number[] };
  };
  insights: {
    windows: { hook: WindowSummary; middle: WindowSummary; close: WindowSummary };
    rankedMoments: { strongest: Moment[]; weakest: Moment[] };
    dips: Dip[];
    ctaWindow: Moment;
    modalityBalance: {
      shares: { visual: number; audio: number; language: number };
      dominant: "visual" | "audio" | "language";
      verdict: string;
    };
    featureCards: {
      engagementAutopsy: FeatureCard;
      payoffTiming: FeatureCard;
      modalityBalance: FeatureCard;
      ctaWindow: FeatureCard;
    };
    llmMarkdown: string;
    caveats: string[];
  };
};

export type WindowSummary = {
  label: string;
  indices: number[];
  overall: number | null;
  modalities: { visual: number | null; audio: number | null; language: number | null };
};

export type Moment = {
  timestep: number;
  start: number;
  end: number;
  overall: number;
  modalities: { visual: number; audio: number; language: number };
};

export type Dip = {
  timestep: number;
  start: number;
  end: number;
  overallBefore: number;
  overallAfter: number;
  overallDelta: number;
  leadModality: "visual" | "audio" | "language";
  modalityDeltas: { visual: number; audio: number; language: number };
};

export type FeatureCard = {
  headline: string;
  evidence: unknown;
  suggestedFix: string;
};
```

---

## Mock Data

### `lib/mock/insights.json`

Copy of `results/finance_test_clip_insights.json` (first-run finance clip). This file is the source of all mock API responses.

### `public/demo-clip.mp4`

Copy of `test_clips/finance_test_clip.mp4`. Served at `/demo-clip.mp4` so the results page can play it without any backend dependency.

---

## Mock Adapter (`lib/mock-adapter.ts`)

A single function: `insightsToResult(insights: unknown): ResonateResult`

Responsibilities:
- Maps the raw `finance_test_clip_insights.json` structure to `ResonateResult`
- Sets `videoUrl` to `/demo-clip.mp4`
- Derives `duration` from `brain.segments` last end time, or falls back to `10.5`
- Maps `brain.modality.*` normalized tracks to both `modality` and `normalizedTracks`
- Maps `insights.dips`, `insights.windows`, `insights.rankedMoments`, `insights.ctaWindow`, `insights.modalityBalance`, `insights.featureCards`
- Sets `llmMarkdown` to empty string `""` if not present (LLM analysis not yet generated)
- Sets `caveats` from insights or to a default array

When the real Modal + analysis API exists, delete this file and point the results route at the real endpoint.

---

## API Routes

### `POST /api/analyze/route.ts`

- Accepts `FormData` with a `video` field (ignored in mock mode)
- Generates a UUID `jobId`
- Stores `{ jobId, startTime: Date.now() }` in a server-side module-level `Map<string, { startTime: number }>`
- Returns `{ jobId }`

### `GET /api/status/[jobId]/route.ts`

Rotating messages (cycle by elapsed time):
1. `"Running Tribe v2..."`
2. `"Mapping cortical vertices..."`
3. `"Applying Schaefer-200 atlas..."`
4. `"Finding attention dips..."`
5. `"Generating creator feedback..."`

Logic:
- If jobId not in store → return `{ status: "error", message: "Job not found" }`
- If elapsed < 8000ms → return `{ status: "processing", message: <rotating message based on elapsed> }`
- If elapsed >= 8000ms → return `{ status: "complete" }`

Message rotation: divide 8000ms into 5 equal slots (~1600ms each), pick message by `Math.floor(elapsed / 1600)`.

### `GET /api/results/[jobId]/route.ts`

- Reads `lib/mock/insights.json`
- Passes through `insightsToResult()`
- Returns the `ResonateResult` as JSON
- Always returns mock result regardless of jobId (the in-memory Map is not checked here — hot reload wipes it and would break the results page mid-demo)

---

## Page Shells

### `app/page.tsx` — Upload page

Minimal functional form:
- `<form>` with `encType="multipart/form-data"`
- `<input type="file" accept=".mp4,.mov,.webm">`
- Submit button
- On submit: POST to `/api/analyze`, redirect to `/results/[jobId]`
- No styling — placeholder `<div>` with a comment marking where Esha's upload component goes

### `app/results/[jobId]/page.tsx` — Results page

- On mount: poll `/api/status/[jobId]` every 2s
- While `status === "processing"`: show rotating message from status response
- When `status === "complete"`: fetch `/api/results/[jobId]`, store in state
- Render: `<pre>{JSON.stringify(result, null, 2)}</pre>` as placeholder
- Comments mark where each component slot goes: video player, timeline, feature cards, modality tracks, LLM markdown

---

## Swap Points (When Real Backend Is Ready)

1. **`lib/mock-adapter.ts`** — delete when real API returns `ResonateResult` directly
2. **`/api/analyze/route.ts`** — replace mock jobId with real Modal job submission
3. **`/api/status/[jobId]/route.ts`** — replace in-memory Map with real Modal job status polling
4. **`/api/results/[jobId]/route.ts`** — replace mock read with real Modal result fetch + analysis pipeline call

---

## What This Does NOT Include

- Any styled UI components (Esha's responsibility)
- Sound-Off score (second Modal run — post-scaffold)
- Blueprint comparison UI
- Blue Agent reference corpus integration
- Auth, file storage, or any persistence beyond in-memory job Map
