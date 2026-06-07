# Resonate Frontend Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a Next.js app at `frontendStuff/resonate-app` with TypeScript types, mock data, API routes, and minimal page shells so Esha can drop in styled components immediately.

**Architecture:** App Router Next.js app with three mock API routes backed by an in-memory job store and a pure adapter function that maps `finance_test_clip_insights.json` to the `ResonateResult` type. Pages are unstyled shells with `data-slot` markers for Esha's components.

**Tech Stack:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, Recharts, Jest + ts-jest

---

## File Map

| File | Responsibility |
|---|---|
| `lib/types.ts` | All exported TypeScript types |
| `lib/job-store.ts` | Shared in-memory Map of active jobs |
| `lib/mock/insights.json` | Copy of `results/finance_test_clip_insights.json` |
| `lib/mock-adapter.ts` | `insightsToResult()` — maps raw JSON → `ResonateResult` |
| `app/api/analyze/route.ts` | POST: creates job, returns `{ jobId }` |
| `app/api/status/[jobId]/route.ts` | GET: simulates 8s processing with rotating messages |
| `app/api/results/[jobId]/route.ts` | GET: returns `ResonateResult` from mock adapter |
| `app/page.tsx` | Upload page shell |
| `app/results/[jobId]/page.tsx` | Results page shell with polling |
| `__tests__/mock-adapter.test.ts` | Unit tests for `insightsToResult` |
| `jest.config.ts` | Jest config with ts-jest and `@/` alias |
| `public/demo-clip.mp4` | Copy of `test_clips/finance_test_clip.mp4` |

---

## Task 1: Create Next.js App

**Files:**
- Create: `frontendStuff/resonate-app/` (entire scaffold)

- [ ] **Step 1: Scaffold the app**

Run from the repo root:
```bash
cd /Users/amisoga/resonate/frontendStuff
npx create-next-app@latest resonate-app \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*" \
  --eslint
```

When prompted for any remaining options, accept defaults.

- [ ] **Step 2: Install additional dependencies**

```bash
cd /Users/amisoga/resonate/frontendStuff/resonate-app
npm install recharts
npm install --save-dev jest @types/jest ts-jest
```

- [ ] **Step 3: Verify dev server starts**

```bash
npm run dev
```

Expected: server starts at `http://localhost:3000`, browser shows default Next.js page. Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app
git commit -m "feat: scaffold Next.js app with Tailwind and Recharts"
```

---

## Task 2: TypeScript Types

**Files:**
- Create: `frontendStuff/resonate-app/lib/types.ts`

- [ ] **Step 1: Create `lib/types.ts`**

```typescript
// frontendStuff/resonate-app/lib/types.ts
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

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/amisoga/resonate/frontendStuff/resonate-app
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/lib/types.ts
git commit -m "feat: add ResonateResult TypeScript types"
```

---

## Task 3: Jest Config + Mock Data

**Files:**
- Create: `frontendStuff/resonate-app/jest.config.ts`
- Create: `frontendStuff/resonate-app/lib/mock/insights.json`
- Create: `frontendStuff/resonate-app/public/demo-clip.mp4`

- [ ] **Step 1: Create `jest.config.ts`**

```typescript
// frontendStuff/resonate-app/jest.config.ts
import type { Config } from "jest";

const config: Config = {
  testEnvironment: "node",
  transform: {
    "^.+\\.tsx?$": ["ts-jest", { tsconfig: { moduleResolution: "node", resolveJsonModule: true } }],
  },
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
};

export default config;
```

- [ ] **Step 2: Copy mock data**

```bash
mkdir -p /Users/amisoga/resonate/frontendStuff/resonate-app/lib/mock
cp /Users/amisoga/resonate/results/finance_test_clip_insights.json \
   /Users/amisoga/resonate/frontendStuff/resonate-app/lib/mock/insights.json
cp /Users/amisoga/resonate/test_clips/finance_test_clip.mp4 \
   /Users/amisoga/resonate/frontendStuff/resonate-app/public/demo-clip.mp4
```

- [ ] **Step 3: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('/Users/amisoga/resonate/frontendStuff/resonate-app/lib/mock/insights.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/jest.config.ts \
        frontendStuff/resonate-app/lib/mock/insights.json \
        frontendStuff/resonate-app/public/demo-clip.mp4
git commit -m "feat: add Jest config and mock data"
```

---

## Task 4: Mock Adapter (TDD)

**Files:**
- Create: `frontendStuff/resonate-app/__tests__/mock-adapter.test.ts`
- Create: `frontendStuff/resonate-app/lib/mock-adapter.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// frontendStuff/resonate-app/__tests__/mock-adapter.test.ts
import { insightsToResult } from "@/lib/mock-adapter";
import mockInsights from "@/lib/mock/insights.json";

describe("insightsToResult", () => {
  const result = insightsToResult(mockInsights);

  it("sets videoUrl to /demo-clip.mp4", () => {
    expect(result.videoUrl).toBe("/demo-clip.mp4");
  });

  it("sets duration from last segment end", () => {
    expect(result.duration).toBe(11);
  });

  it("maps segments unchanged", () => {
    expect(result.brain.segments[0]).toEqual({ start: 0, end: 1 });
    expect(result.brain.segments).toHaveLength(11);
  });

  it("maps normalizedTracks to both modality and normalizedTracks", () => {
    expect(result.brain.modality).toEqual(result.brain.normalizedTracks);
    expect(result.brain.modality.visual).toHaveLength(11);
    expect(result.brain.modality.audio).toHaveLength(11);
    expect(result.brain.modality.language).toHaveLength(11);
  });

  it("maps overall track", () => {
    expect(result.brain.overall).toHaveLength(11);
    expect(result.brain.overall[0]).toBeCloseTo(28.4, 1);
  });

  it("maps dips with camelCase fields", () => {
    expect(result.insights.dips.length).toBeGreaterThan(0);
    const dip = result.insights.dips[0];
    expect(dip.overallBefore).toBeCloseTo(28.4, 1);
    expect(dip.overallAfter).toBeCloseTo(10.7, 1);
    expect(dip.overallDelta).toBeCloseTo(-17.7, 1);
    expect(dip.leadModality).toBe("visual");
    expect(dip.modalityDeltas.visual).toBeCloseTo(-27.1, 1);
  });

  it("maps feature cards with camelCase suggestedFix", () => {
    const cards = result.insights.featureCards;
    expect(cards.engagementAutopsy.suggestedFix).toBeDefined();
    expect(cards.payoffTiming.suggestedFix).toBeDefined();
    expect(cards.modalityBalance.suggestedFix).toBeDefined();
    expect(cards.ctaWindow.suggestedFix).toBeDefined();
  });

  it("maps ctaWindow as a Moment (no note field)", () => {
    const cta = result.insights.ctaWindow;
    expect(cta.timestep).toBe(10);
    expect(cta.start).toBe(10);
    expect(cta.end).toBe(11);
    expect((cta as { note?: string }).note).toBeUndefined();
  });

  it("maps modalityBalance", () => {
    expect(result.insights.modalityBalance.dominant).toBe("language");
    expect(result.insights.modalityBalance.shares.visual).toBeCloseTo(13.5, 1);
  });

  it("maps windows", () => {
    expect(result.insights.windows.hook.label).toBe("0-3s hook");
    expect(result.insights.windows.hook.overall).toBeCloseTo(14.0, 1);
  });

  it("sets llmMarkdown to empty string", () => {
    expect(result.insights.llmMarkdown).toBe("");
  });

  it("maps caveats from notes array", () => {
    expect(result.insights.caveats.length).toBeGreaterThan(0);
    expect(typeof result.insights.caveats[0]).toBe("string");
  });
});
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/amisoga/resonate/frontendStuff/resonate-app
npx jest __tests__/mock-adapter.test.ts
```

Expected: FAIL — `Cannot find module '@/lib/mock-adapter'`

- [ ] **Step 3: Implement `lib/mock-adapter.ts`**

```typescript
// frontendStuff/resonate-app/lib/mock-adapter.ts
import type { ResonateResult, Moment, Dip, WindowSummary, FeatureCard } from "@/lib/types";

type InsightsDip = {
  timestep: number; start: number; end: number;
  overall_before: number; overall_after: number; overall_delta: number;
  lead_modality: "visual" | "audio" | "language";
  modality_deltas: { visual: number; audio: number; language: number };
};

type InsightsMoment = {
  timestep: number; start: number; end: number; overall: number;
  modalities: { visual: number; audio: number; language: number };
  note?: string;
};

type InsightsFeatureCard = {
  headline: string; evidence: unknown; suggested_fix: string;
};

type InsightsWindow = {
  label: string; indices: number[];
  overall: number | null;
  modalities: { visual: number | null; audio: number | null; language: number | null };
};

type InsightsJSON = {
  source: string;
  n_timesteps: number;
  segments: Array<{ start: number; end: number }>;
  normalized_tracks: { visual: number[]; audio: number[]; language: number[] };
  overall: number[];
  windows: { hook: InsightsWindow; middle: InsightsWindow; close: InsightsWindow };
  ranked_moments: { strongest: InsightsMoment[]; weakest: InsightsMoment[] };
  dips: InsightsDip[];
  cta_window: InsightsMoment;
  modality_balance: {
    shares: { visual: number; audio: number; language: number };
    dominant: "visual" | "audio" | "language";
    verdict: string;
  };
  feature_cards: {
    engagement_autopsy: InsightsFeatureCard;
    payoff_timing: InsightsFeatureCard;
    modality_balance: InsightsFeatureCard;
    cta_window: InsightsFeatureCard;
  };
  notes: string[];
};

function toMoment(m: InsightsMoment): Moment {
  return { timestep: m.timestep, start: m.start, end: m.end, overall: m.overall, modalities: m.modalities };
}

function toDip(d: InsightsDip): Dip {
  return {
    timestep: d.timestep, start: d.start, end: d.end,
    overallBefore: d.overall_before,
    overallAfter: d.overall_after,
    overallDelta: d.overall_delta,
    leadModality: d.lead_modality,
    modalityDeltas: d.modality_deltas,
  };
}

function toFeatureCard(fc: InsightsFeatureCard): FeatureCard {
  return { headline: fc.headline, evidence: fc.evidence, suggestedFix: fc.suggested_fix };
}

function toWindow(w: InsightsWindow): WindowSummary {
  return { label: w.label, indices: w.indices, overall: w.overall, modalities: w.modalities };
}

export function insightsToResult(raw: unknown): ResonateResult {
  const d = raw as InsightsJSON;
  const lastSeg = d.segments[d.segments.length - 1];
  const duration = lastSeg ? lastSeg.end : 10.5;

  return {
    videoUrl: "/demo-clip.mp4",
    filename: d.source.split("/").pop(),
    duration,
    brain: {
      segments: d.segments,
      modality: d.normalized_tracks,
      normalizedTracks: d.normalized_tracks,
      overall: d.overall,
    },
    insights: {
      windows: {
        hook: toWindow(d.windows.hook),
        middle: toWindow(d.windows.middle),
        close: toWindow(d.windows.close),
      },
      rankedMoments: {
        strongest: d.ranked_moments.strongest.map(toMoment),
        weakest: d.ranked_moments.weakest.map(toMoment),
      },
      dips: d.dips.map(toDip),
      ctaWindow: toMoment(d.cta_window),
      modalityBalance: d.modality_balance,
      featureCards: {
        engagementAutopsy: toFeatureCard(d.feature_cards.engagement_autopsy),
        payoffTiming: toFeatureCard(d.feature_cards.payoff_timing),
        modalityBalance: toFeatureCard(d.feature_cards.modality_balance),
        ctaWindow: toFeatureCard(d.feature_cards.cta_window),
      },
      llmMarkdown: "",
      caveats: d.notes,
    },
  };
}
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/amisoga/resonate/frontendStuff/resonate-app
npx jest __tests__/mock-adapter.test.ts
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/__tests__/mock-adapter.test.ts \
        frontendStuff/resonate-app/lib/mock-adapter.ts
git commit -m "feat: add mock adapter with tests (insightsToResult)"
```

---

## Task 5: Job Store + POST /api/analyze

**Files:**
- Create: `frontendStuff/resonate-app/lib/job-store.ts`
- Create: `frontendStuff/resonate-app/app/api/analyze/route.ts`

- [ ] **Step 1: Create `lib/job-store.ts`**

```typescript
// frontendStuff/resonate-app/lib/job-store.ts
export const jobs = new Map<string, { startTime: number }>();
```

- [ ] **Step 2: Create `app/api/analyze/route.ts`**

```typescript
// frontendStuff/resonate-app/app/api/analyze/route.ts
import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { jobs } from "@/lib/job-store";

export async function POST() {
  const jobId = randomUUID();
  jobs.set(jobId, { startTime: Date.now() });
  return NextResponse.json({ jobId });
}
```

- [ ] **Step 3: Start dev server and verify route**

```bash
cd /Users/amisoga/resonate/frontendStuff/resonate-app
npm run dev &
sleep 3
curl -s -X POST http://localhost:3000/api/analyze | python3 -m json.tool
```

Expected output shape:
```json
{
  "jobId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/lib/job-store.ts \
        frontendStuff/resonate-app/app/api/analyze/route.ts
git commit -m "feat: add job store and POST /api/analyze"
```

---

## Task 6: GET /api/status/[jobId]

**Files:**
- Create: `frontendStuff/resonate-app/app/api/status/[jobId]/route.ts`

- [ ] **Step 1: Create the route**

```typescript
// frontendStuff/resonate-app/app/api/status/[jobId]/route.ts
import { NextResponse } from "next/server";
import { jobs } from "@/lib/job-store";

const MESSAGES = [
  "Running Tribe v2...",
  "Mapping cortical vertices...",
  "Applying Schaefer-200 atlas...",
  "Finding attention dips...",
  "Generating creator feedback...",
];

const TOTAL_MS = 8000;
const SLOT_MS = TOTAL_MS / MESSAGES.length;

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;
  const job = jobs.get(jobId);
  if (!job) {
    return NextResponse.json({ status: "error", message: "Job not found" }, { status: 404 });
  }
  const elapsed = Date.now() - job.startTime;
  if (elapsed >= TOTAL_MS) {
    return NextResponse.json({ status: "complete" });
  }
  const msgIndex = Math.min(Math.floor(elapsed / SLOT_MS), MESSAGES.length - 1);
  return NextResponse.json({ status: "processing", message: MESSAGES[msgIndex] });
}
```

- [ ] **Step 2: Test the route with a real jobId**

First POST to get a jobId, then poll status immediately (should be processing) and after 9 seconds (should be complete):

```bash
# Get a jobId
JOB=$(curl -s -X POST http://localhost:3000/api/analyze | python3 -c "import sys,json; print(json.load(sys.stdin)['jobId'])")
echo "jobId: $JOB"

# Poll immediately — expect processing
curl -s "http://localhost:3000/api/status/$JOB" | python3 -m json.tool

# Wait 9s, poll again — expect complete
sleep 9
curl -s "http://localhost:3000/api/status/$JOB" | python3 -m json.tool
```

Expected first response:
```json
{"status": "processing", "message": "Running Tribe v2..."}
```

Expected second response:
```json
{"status": "complete"}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/app/api/status
git commit -m "feat: add GET /api/status/[jobId] with 8s simulation"
```

---

## Task 7: GET /api/results/[jobId]

**Files:**
- Create: `frontendStuff/resonate-app/app/api/results/[jobId]/route.ts`

- [ ] **Step 1: Create the route**

```typescript
// frontendStuff/resonate-app/app/api/results/[jobId]/route.ts
import { NextResponse } from "next/server";
import { insightsToResult } from "@/lib/mock-adapter";
import mockInsights from "@/lib/mock/insights.json";

export async function GET() {
  const result = insightsToResult(mockInsights);
  return NextResponse.json(result);
}
```

- [ ] **Step 2: Verify the route returns a valid ResonateResult**

```bash
curl -s "http://localhost:3000/api/results/any-id" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('videoUrl:', d['videoUrl'])
print('duration:', d['duration'])
print('brain.overall length:', len(d['brain']['overall']))
print('dips count:', len(d['insights']['dips']))
print('featureCards keys:', list(d['insights']['featureCards'].keys()))
print('llmMarkdown:', repr(d['insights']['llmMarkdown'][:30]))
"
```

Expected output:
```
videoUrl: /demo-clip.mp4
duration: 11
brain.overall length: 11
dips count: <number>
featureCards keys: ['engagementAutopsy', 'payoffTiming', 'modalityBalance', 'ctaWindow']
llmMarkdown: ''
```

- [ ] **Step 3: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/app/api/results
git commit -m "feat: add GET /api/results/[jobId] returning ResonateResult"
```

---

## Task 8: Upload Page Shell

**Files:**
- Modify: `frontendStuff/resonate-app/app/page.tsx`

- [ ] **Step 1: Replace default page with upload shell**

```tsx
// frontendStuff/resonate-app/app/page.tsx
"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const data = new FormData(e.currentTarget);
    const res = await fetch("/api/analyze", { method: "POST", body: data });
    const { jobId } = await res.json();
    router.push(`/results/${jobId}`);
  }

  return (
    /* Esha: replace this entire <main> with your upload component */
    <main className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold">Resonate</h1>
      <p className="text-gray-400">Find the moments your video loses the brain.</p>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <input
          name="video"
          type="file"
          accept=".mp4,.mov,.webm"
          required
          className="block"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 rounded disabled:opacity-50"
        >
          {loading ? "Uploading..." : "Analyze Video"}
        </button>
      </form>
    </main>
  );
}
```

- [ ] **Step 2: Verify in browser**

Navigate to `http://localhost:3000`. You should see a file input and "Analyze Video" button. Select a `.mp4` file and submit — browser should navigate to `/results/<uuid>`.

- [ ] **Step 3: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/app/page.tsx
git commit -m "feat: add upload page shell"
```

---

## Task 9: Results Page Shell

**Files:**
- Create: `frontendStuff/resonate-app/app/results/[jobId]/page.tsx`

- [ ] **Step 1: Create the results page**

```tsx
// frontendStuff/resonate-app/app/results/[jobId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { ResonateResult } from "@/lib/types";

type StatusResponse = {
  status: "queued" | "processing" | "complete" | "error";
  message?: string;
};

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [status, setStatus] = useState<StatusResponse>({ status: "queued" });
  const [result, setResult] = useState<ResonateResult | null>(null);

  useEffect(() => {
    if (status.status === "complete" || status.status === "error") return;

    const interval = setInterval(async () => {
      const res = await fetch(`/api/status/${jobId}`);
      const data: StatusResponse = await res.json();
      setStatus(data);

      if (data.status === "complete") {
        clearInterval(interval);
        const r = await fetch(`/api/results/${jobId}`);
        setResult(await r.json());
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, status.status]);

  if (!result) {
    return (
      /* Esha: replace with your processing/loading component */
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-gray-300 animate-pulse">
          {status.message ?? "Initializing..."}
        </p>
      </main>
    );
  }

  return (
    /* Esha: replace each section with your styled components */
    <main className="min-h-screen p-6 flex flex-col gap-6">

      {/* Video Player — props: src={result.videoUrl} */}
      <section data-slot="video-player">
        <video src={result.videoUrl} controls className="w-full max-w-md" />
      </section>

      {/* Main Takeaway — props: rankedMoments={result.insights.rankedMoments}, modalityBalance={result.insights.modalityBalance} */}
      <section data-slot="main-takeaway" />

      {/* Attention Timeline — props: overall={result.brain.overall}, segments={result.brain.segments}, dips={result.insights.dips} */}
      <section data-slot="attention-timeline" />

      {/* Modality Tracks — props: modality={result.brain.modality} */}
      <section data-slot="modality-tracks" />

      {/* Feature Cards — props: featureCards={result.insights.featureCards} */}
      <section data-slot="feature-cards" />

      {/* LLM Analysis — props: markdown={result.insights.llmMarkdown} */}
      <section data-slot="llm-analysis" />

      {/* Brain/Modality Panel — props: modalityBalance={result.insights.modalityBalance} */}
      <section data-slot="modality-panel" />

      {/* Evidence Drawer — collapsible debug panel for judges */}
      <details className="text-xs text-gray-500">
        <summary className="cursor-pointer">Evidence</summary>
        <pre className="mt-2 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
      </details>

    </main>
  );
}
```

- [ ] **Step 2: End-to-end smoke test in browser**

1. Go to `http://localhost:3000`
2. Select any `.mp4` file and click "Analyze Video"
3. You should land on `/results/<uuid>` and see "Running Tribe v2..." (or similar rotating message)
4. After 8 seconds the loading message should stop and you should see a `<video>` element and the evidence drawer
5. Expand the evidence drawer — confirm the JSON shows `videoUrl: "/demo-clip.mp4"`, 11 timesteps, and camelCase `featureCards` keys

- [ ] **Step 3: Commit**

```bash
cd /Users/amisoga/resonate
git add frontendStuff/resonate-app/app/results
git commit -m "feat: add results page shell with polling and data-slot markers"
```

---

## Self-Review

**Spec coverage:**
- ✅ `frontendStuff/resonate-app` location
- ✅ All TypeScript types from FRONTEND_PLAN.md
- ✅ Mock data copied from `results/` and `test_clips/`
- ✅ `insightsToResult` adapter with all snake_case → camelCase mappings
- ✅ POST /api/analyze → `{ jobId }`
- ✅ GET /api/status/[jobId] → 8s simulation with rotating messages
- ✅ GET /api/results/[jobId] → `ResonateResult`
- ✅ Upload page shell
- ✅ Results page shell with 2s polling
- ✅ All swap points documented in spec

**Placeholder scan:** None found.

**Type consistency:** `insightsToResult` returns `ResonateResult`. All `Moment`, `Dip`, `FeatureCard`, `WindowSummary` usages match the definitions in `lib/types.ts`. `data-slot` comments on results page reference correct field paths from `ResonateResult`.
