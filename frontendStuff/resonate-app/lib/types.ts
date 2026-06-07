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
