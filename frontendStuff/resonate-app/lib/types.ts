export type Modality = "visual" | "audio" | "language";

export type Segment = { start: number; end: number };

export type ModalityValues = { visual: number; audio: number; language: number };

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
  modalities: ModalityValues;
};

export type Dip = {
  timestep: number;
  start: number;
  end: number;
  overallBefore: number;
  overallAfter: number;
  overallDelta: number;
  leadModality: Modality;
  modalityDeltas: ModalityValues;
};

export type FeatureCard = {
  headline: string;
  evidence: unknown;
  suggestedFix: string;
};

export type ResonateResult = {
  videoUrl: string;
  filename?: string;
  duration: number;

  brain: {
    segments: Segment[];
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
    /** parcels[parcelIndex][timestep], normalized 0..1 */
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
      shares: ModalityValues;
      dominant: Modality;
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

export type JobStatus = {
  status: "queued" | "processing" | "complete" | "error";
  progress?: number;
  message?: string;
};

export const MODALITY_COLORS: Record<Modality | "overall" | "dip" | "strong", string> = {
  overall: "#e5edff",
  visual: "#3b82f6",
  audio: "#22c55e",
  language: "#f43f5e",
  dip: "#ef4444",
  strong: "#a78bfa",
};
