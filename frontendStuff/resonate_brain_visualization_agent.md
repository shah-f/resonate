# Brain Visualization Agent — 200-Parcel Frontend Plan

## What You Are

You are the Brain Visualization Agent. Your job is to build the frontend brain visualization for Resonate alongside a human teammate. The backend is separate. Your component should be able to run against mock data first, then plug into the real Tribe v2 analysis response when the backend is ready.

The product goal is:

> Show creators where predicted brain activation rises, falls, and shifts across a video — clearly enough to understand, but with enough neuroscience depth to prove this is not a generic analytics dashboard.

---

## Core Visualization Strategy

Build two layers:

1. **Modality View for clarity**
   - Visual / Audio / Language activation over time.
   - Easy for judges and creators to understand in seconds.
   - This is the default view if the 200-parcel view is visually noisy or incomplete.

2. **200-Parcel View for credibility**
   - Uses Schaefer-200 parcel scores from the backend.
   - Shows named brain-region activity at each video timestep.
   - This is the target visualization. Aim to make it demo-ready.

Do **not** attempt raw 20,484-vertex visualization for the hackathon frontend. Raw vertex data is useful for backend/debugging, but the user-facing visualization should use 200 atlas parcels plus modality groupings.

---

## Backend Inputs

The backend should provide an analysis result with this shape:

```ts
type AnalysisResult = {
  videoUrl: string;
  filename?: string;
  duration: number;

  brain: {
    segments: BrainSegment[];

    modality: {
      visual: number[];
      audio: number[];
      language: number[];
    };

    parcels: number[][];
    parcelNames: string[];

    modalityIndices: {
      visual: number[];
      audio: number[];
      language: number[];
    };
  };

  insights?: {
    dips: BrainDip[];
  };
};

type BrainSegment = {
  start: number;
  end: number;
};

type BrainDip = {
  timestamp: number;
  modality?: "visual" | "audio" | "language";
  parcelIndex?: number;
  regionName?: string;
  severity: "low" | "medium" | "high";
  explanation?: string;
};
```

### Required for MVP

```ts
duration
brain.segments
brain.modality.visual
brain.modality.audio
brain.modality.language
brain.parcels
brain.parcelNames
brain.modalityIndices
```

### Nice to Have

```ts
insights.dips
filename
videoUrl
```

The component must also work with mock data before the backend route exists.

---

## Important Data Notes

Tribe v2 gives raw cortical surface predictions:

```ts
predictions: number[][];
// shape: [timesteps, 20484]
```

The backend maps those raw vertices into Schaefer-200 parcels:

```ts
parcels: number[][];
// shape: [timesteps, 200]
```

Then the backend computes modality averages:

```ts
modality.visual: number[];
modality.audio: number[];
modality.language: number[];
```

The frontend should treat `parcels` as the main neuroscience data and `modality` as the readable summary layer.

---

## Time Mapping

Do not assume one Tribe timestep equals one video second.

Map `currentTime` from the video player to the closest segment:

```ts
function getTimestepIndex(currentTime: number, segments: BrainSegment[]) {
  const direct = segments.findIndex(
    (s) => currentTime >= s.start && currentTime <= s.end
  );
  if (direct >= 0) return direct;

  return segments.reduce((bestIndex, segment, index) => {
    const bestCenter = (segments[bestIndex].start + segments[bestIndex].end) / 2;
    const center = (segment.start + segment.end) / 2;
    return Math.abs(center - currentTime) < Math.abs(bestCenter - currentTime)
      ? index
      : bestIndex;
  }, 0);
}
```

Fallback if `segments` is missing or malformed:

```ts
index = Math.round((currentTime / duration) * (seriesLength - 1));
```

---

## Normalization

Raw activation values may not be in `0..1`. Normalize values on the frontend for display.

For each parcel:

```ts
normalizedParcelValue =
  (parcels[t][parcelIndex] - minAcrossTimeForParcel) /
  (maxAcrossTimeForParcel - minAcrossTimeForParcel);
```

For each modality:

```ts
normalizedModalityValue =
  (modality[track][t] - minAcrossTimeForTrack) /
  (maxAcrossTimeForTrack - minAcrossTimeForTrack);
```

Clamp final display values to `0..1`. If max equals min, use `0.5` so the region remains visible.

---

## Component API

Build a reusable component:

```tsx
type BrainVisualizationProps = {
  currentTime: number;
  duration: number;
  segments: BrainSegment[];

  modality: {
    visual: number[];
    audio: number[];
    language: number[];
  };

  parcels: number[][];
  parcelNames: string[];

  modalityIndices: {
    visual: number[];
    audio: number[];
    language: number[];
  };

  dips?: BrainDip[];

  viewMode?: "modality" | "parcels";
  selectedParcelIndex?: number | null;
  selectedModality?: "visual" | "audio" | "language" | null;

  onSelectTimestamp?: (time: number) => void;
  onSelectParcel?: (parcelIndex: number | null) => void;
  onSelectModality?: (modality: "visual" | "audio" | "language" | null) => void;
};
```

---

## Recommended File Structure

```txt
src/components/brain/
  BrainVisualization.tsx
  BrainScene.tsx
  BrainModel.tsx
  ParcelCloud.tsx
  ParcelPoint.tsx
  ModalityZones.tsx
  BrainLegend.tsx
  BrainReadout.tsx
  brainTypes.ts
  brainUtils.ts
  mockBrainData.ts
```

---

## Visual Design

The visualization should feel like a serious creative analytics tool, not a toy.

- Dark background.
- Transparent or subtly shaded 3D brain silhouette.
- 200 parcel points or small surface markers distributed across left/right hemisphere.
- Color parcels by modality group when possible:
  - Visual: blue
  - Audio: green
  - Language: rose/red
  - Other parcels: dim neutral gray
- Brightness and scale represent current activation.
- Biggest drops can flash or outline in amber/red.
- Hovering a parcel shows name and activation.

Use a stylized brain model if a true cortical mesh is not ready. Be honest in labels: call it a "Schaefer-200 parcel visualization," not an exact surgical map.

---

## 200-Parcel View

This is the target.

Render all 200 parcels as points or small glowing patches.

Each parcel needs:

```ts
{
  parcelIndex: number;
  name: string;
  value: number;
  normalizedValue: number;
  modalityGroup?: "visual" | "audio" | "language" | "other";
  isDip?: boolean;
}
```

Since the backend currently provides parcel names and modality indices, the frontend can group parcels like this:

```ts
function getParcelGroup(index, modalityIndices) {
  if (modalityIndices.visual.includes(index)) return "visual";
  if (modalityIndices.audio.includes(index)) return "audio";
  if (modalityIndices.language.includes(index)) return "language";
  return "other";
}
```

### Parcel Placement

For hackathon speed, use deterministic approximate placement:

- First 100 parcels = left hemisphere.
- Next 100 parcels = right hemisphere.
- Place each hemisphere as an ellipsoid point cloud.
- Spread points by parcel index using spherical coordinates or a deterministic spiral.
- Put visual parcels toward the back, audio/language more lateral/front when possible.

This is acceptable for a demo as long as the UI says "parcel visualization" and does not claim exact anatomical coordinates.

Later, replace approximate positions with a true fsaverage5/Schaefer surface mapping.

---

## Modality View

This is the clarity layer and fallback.

Render three large zones:

- Visual system: rear/occipital area, blue.
- Audio system: side/temporal area, green.
- Language system: frontal/temporal area, rose/red.

Intensity comes from:

```ts
modality.visual[t]
modality.audio[t]
modality.language[t]
```

Use this view when:

- the user needs a fast explanation,
- the 200-parcel view is too noisy,
- the backend only returns modality data,
- the demo needs a clean first impression.

---

## Readout Panel

Next to or below the 3D scene, show a compact readout:

```txt
Current time: 0:04.5
Strongest system: Language

Visual    72%
Audio     31%
Language 84%

Top active parcels
1. 7Networks_LH_Vis_6        91%
2. 7Networks_RH_Default_Temp 88%
3. 7Networks_LH_SomMot_4     82%

Biggest drops
1. 7Networks_RH_Cont_PFCl_1  -42%
2. 7Networks_LH_Default_Temp -37%
3. 7Networks_RH_Vis_3        -31%
```

Do not over-explain in the visualization component. Larger narrative explanations belong in the results/insights panel.

---

## Interaction Requirements

MVP:

- Brain updates as video plays.
- Toggle between `Modality` and `200 Parcels`.
- Hover parcel to show parcel name and activation.
- Click parcel to pin it in the readout.
- Click modality legend item to highlight that group.

If time:

- Click dip marker to jump video to timestamp.
- Animate current largest drop.
- Show top active parcels and biggest movers for each timestep.

---

## Implementation Milestones

### Milestone 1 — Mock Data Shell

- Create TypeScript types.
- Create mock data with 10-20 timesteps and 200 parcels.
- Render panel with current timestep index and normalized modality values.

### Milestone 2 — Modality View

- Build 3D scene.
- Render three large modality zones.
- Update zone intensity based on `currentTime`.
- Add legend and readout.

### Milestone 3 — 200-Parcel View

- Render all 200 parcels as deterministic point cloud.
- Color by `modalityIndices`.
- Scale/brightness by normalized parcel activation.
- Add hover and click selection.

### Milestone 4 — Video Sync

- Connect to the parent video player's `currentTime`.
- Verify brain state changes while the video plays.
- Add fallback time mapping if segment data is missing.

### Milestone 5 — Insight Integration

- Accept `dips`.
- Highlight parcels/modalities involved in current or nearest dip.
- Enable timestamp selection callback.

---

## Human + Agent Collaboration

The human teammate should own:

- final visual taste,
- where the component sits in the results layout,
- whether the demo defaults to Modality View or 200-Parcel View,
- copy around what the visualization means.

The agent should own:

- component implementation,
- data normalization,
- mock data,
- 3D scene structure,
- parcel grouping and interactions,
- keeping the component resilient to partial backend data.

When uncertain, prefer a working 200-parcel point-cloud view over a more anatomically ambitious but unfinished cortical mesh.

---

## Acceptance Criteria

- Component runs with mock data without backend.
- Component accepts real backend-shaped data.
- Modality View shows visual/audio/language activation clearly.
- 200-Parcel View renders all 200 parcels.
- Parcels are colored by modality group when available.
- Parcel intensity changes as `currentTime` changes.
- Hovering/clicking parcels reveals parcel names and values.
- The UI does not claim exact medical localization unless true anatomical coordinates are implemented.

