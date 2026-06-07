# Resonate Frontend Plan

Audience: frontend teammates building the demo UI.

Backend owners: Julia / Foram  
Frontend owners: Esha / Ami

This plan describes what the frontend should build and what form each feature should take. Treat `PLAN.md` as the product scope, and treat this file as the practical frontend implementation guide.

## Product Goal

Resonate should feel like a working creator analysis tool, not a generic dashboard. The user uploads a short video, waits while the brain-response model runs, then sees a timeline-based diagnosis with clear edit suggestions.

The core promise:

> Show where predicted brain response rises, falls, and shifts across visual, audio, and language signals, then turn that into concrete creator advice.

## Current Backend Shape

The backend pipeline is moving toward:

1. Modal runs Tribe v2 on an uploaded video.
2. Backend maps raw 20,484 surface vertices into 200 Schaefer parcels.
3. Backend computes visual/audio/language modality tracks.
4. Deterministic analyzer creates structured insights JSON.
5. LLM turns structured insights into creator-facing markdown.

Frontend should assume the final result can include:

```ts
type ResonateResult = {
  videoUrl: string;
  filename?: string;
  duration: number;

  brain: {
    segments: Array<{ start: number; end: number }>;
    modality: {
      visual: number[];
      audio: number[];
      language: number[];
    };
    normalizedTracks?: {
      visual: number[];
      audio: number[];
      language: number[];
    };
    overall: number[];
    parcels?: number[][];
    parcelNames?: string[];
    modalityIndices?: {
      visual: number[];
      audio: number[];
      language: number[];
    };
  };

  insights: {
    windows: {
      hook: WindowSummary;
      middle: WindowSummary;
      close: WindowSummary;
    };
    rankedMoments: {
      strongest: Moment[];
      weakest: Moment[];
    };
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

type WindowSummary = {
  label: string;
  indices: number[];
  overall: number | null;
  modalities: { visual: number | null; audio: number | null; language: number | null };
};

type Moment = {
  timestep: number;
  start: number;
  end: number;
  overall: number;
  modalities: { visual: number; audio: number; language: number };
};

type Dip = {
  timestep: number;
  start: number;
  end: number;
  overallBefore: number;
  overallAfter: number;
  overallDelta: number;
  leadModality: "visual" | "audio" | "language";
  modalityDeltas: { visual: number; audio: number; language: number };
};

type FeatureCard = {
  headline: string;
  evidence: unknown;
  suggestedFix: string;
};
```

Use mock data in this shape until the API exists.

## MVP User Flow

### 1. Upload Page

Route: `/`

Form:

- Large drag-and-drop upload area.
- Accept `.mp4`, `.mov`, `.webm`.
- Show selected filename, size, and a video thumbnail/preview.
- Button: `Analyze Video`.
- On submit, POST video as `FormData` to `/api/analyze`.
- Redirect to `/results/[jobId]`.

User-facing text should be minimal and direct:

- App name: `Resonate`
- Subtitle: `Find the moments your video loses the brain.`
- Upload helper: `Short vertical clips work best for the demo.`

### 2. Processing Page

Route: `/results/[jobId]` while status is pending, or `loading.tsx`.

Form:

- Full-screen processing state.
- Animated brain or signal visualization.
- Rotating status messages:
  - `Running Tribe v2...`
  - `Mapping cortical vertices...`
  - `Applying Schaefer-200 atlas...`
  - `Finding attention dips...`
  - `Generating creator feedback...`
- Poll `/api/status/[jobId]` every 2-3 seconds.
- When complete, fetch `/api/results/[jobId]`.

### 3. Results Page

Route: `/results/[jobId]`

Desktop layout:

- Left: video + timeline.
- Right: diagnosis cards + brain/modality panel.
- Below: LLM creator analysis and detailed evidence.

Mobile layout:

- Stack vertically:
  1. Video
  2. Main takeaway
  3. Timeline
  4. Feature cards
  5. Creator feedback
  6. Brain/modality view

## Results Page Components

### A. Video Player

- Native `<video controls>`.
- Keep current playback time in state.
- Expose `seekTo(time)` to timeline/cards.
- Display current segment/timestep subtly under the player.

Every insight should be clickable back to the video moment.

### B. Main Takeaway Panel

- Compact top panel, not a giant marketing hero.
- Show:
  - one-sentence LLM summary if available
  - strongest moment
  - weakest moment
  - dominant modality

Example:

```text
The payoff lands late: the strongest predicted response is at 10.0-11.0s, while the hook stays low.
```

### C. Attention Timeline

- Recharts area/line chart.
- X-axis: time.
- Y-axis: normalized `overall`.
- Overlay:
  - red/orange dip markers
  - blue strongest moment marker
  - white playhead line
- Click chart to seek video.
- Hover tooltip:
  - timestamp
  - overall
  - visual/audio/language values
  - dip label if present

Data:

- `brain.overall`
- `brain.segments`
- `insights.dips`
- `insights.rankedMoments`

### D. Modality Tracks

- Three stacked mini-lines or one combined multi-line chart.
- Colors:
  - Visual: blue
  - Audio: green
  - Language: red/pink
- Highlight the lead modality for selected dip.

Purpose:

- Make it obvious whether a dip is visual, audio, or language-driven.

### E. Feature Cards

Render four cards from `insights.featureCards`:

1. Engagement Autopsy
2. Payoff Timing
3. Modality Balance
4. CTA Window

Each card form:

- Icon
- Headline
- Evidence row
- Suggested fix
- Timestamp button if applicable

Example:

```text
Engagement Autopsy
Predicted engagement drops around 1.0s.
Fix: Strengthen the visual cue at this moment.
[Jump to 1.0s]
```

### F. Creator Feedback / LLM Analysis

- Render markdown from `insights.llmMarkdown`.
- Keep it readable and editorial.
- Sections may vary depending on data richness.

Expected sections for rich results:

- Executive Takeaway
- Timeline Diagnosis
- What Caused Each Dip
- Modality Breakdown
- Best Payoff / CTA Window
- Concrete Edit Plan
- Confidence + Caveats

For sparse/old results, it may resemble:

- What The Data Says
- Human-Facing Insights
- Suggested Creator Feedback
- Demo Cards
- Caveat

Frontend should not assume exact headings. Render markdown generically.

### G. Brain / Modality Visualization

MVP form:

- Start with a modality view:
  - three glowing zones or bars for Visual / Audio / Language
  - update values based on current video time
  - clicking a modality filters/highlights related cards/timeline

Stretch form:

- 200-parcel view using `parcels`, `parcelNames`, and `modalityIndices`.
- Show parcel dots or simplified hemispheres.
- Hover/click parcel to show:
  - parcel index
  - parcel name
  - value at current timestep
  - modality group if assigned

Important:

- Do not render raw 20,484 vertices.
- Do not turn Schaefer labels into polished brain-region claims unless backend supplies a translation layer.

### H. Evidence Drawer

- Collapsible debug/evidence panel.
- For demo, this proves depth without cluttering the main UI.
- Show:
  - normalized tracks
  - segment timings
  - top rising/falling parcels
  - event dataframe availability
  - caveats

This is useful for judges and for our own debugging.

## API Endpoints To Mock

### `POST /api/analyze`

Input:

- `FormData` with `video`.

Output:

```ts
{ jobId: string }
```

### `GET /api/status/[jobId]`

Output:

```ts
{
  status: "queued" | "processing" | "complete" | "error";
  progress?: number;
  message?: string;
}
```

### `GET /api/results/[jobId]`

Output:

- `ResonateResult`

While backend is not wired, use static mock data loaded from a local JSON file.

## Visual Design

Use a dark product UI, not a landing page.

Guidelines:

- Background: near-black.
- Cards: restrained, dense, scan-friendly.
- Use clear charts and timestamps over decorative effects.
- Use glow sparingly for the brain/signal moments.
- Avoid large marketing hero blocks on the results page.
- Make all important timestamps clickable.

Suggested colors:

- Overall: white / blue
- Visual: `#3b82f6`
- Audio: `#22c55e`
- Language: `#f43f5e`
- Dips: `#ef4444`
- Strong moments: `#a78bfa`

## Build Priority

### Must Have

1. Upload page
2. Processing state
3. Results shell
4. Video player with seek support
5. Attention timeline with dips and playhead
6. Feature cards
7. Markdown LLM analysis renderer
8. Modality balance/tracks

### Should Have

1. Modality visualization panel
2. Evidence drawer
3. Strongest/weakest moment cards
4. Responsive mobile layout

### Nice To Have

1. 200-parcel brain visualization
2. Sound-off comparison UI
3. Blueprint/reference comparison UI
4. Scene-cut/pacing markers

## Mock Data Strategy

Use the existing generated file as a backend-like mock:

```text
results/finance_test_clip_insights.json
```

Frontend can adapt it into the `ResonateResult` shape. For video preview, use:

```text
test_clips/finance_test_clip.mp4
```

Once backend API exists, swap the static mock loader for `/api/results/[jobId]`.

## Caveats To Preserve In UI

Always include a small caveat somewhere near the analysis:

- These are predicted brain-response signals, not measured viewer retention.
- Scores are normalized within the clip.
- Schaefer parcel labels are atlas labels, not polished named brain regions.

This protects the demo from overclaiming while still showing the technical depth.
