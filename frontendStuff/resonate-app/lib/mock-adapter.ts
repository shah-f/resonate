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
