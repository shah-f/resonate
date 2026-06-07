import type { JobStatus, ResonateResult } from "./types";
import rawResult from "../mock/resonateResult.json";

const PROCESSING_MESSAGES = [
  "Running Tribe v2...",
  "Mapping cortical vertices...",
  "Applying Schaefer-200 atlas...",
  "Computing modality tracks...",
  "Finding attention dips...",
  "Generating creator feedback...",
];

type Job = {
  id: string;
  createdAt: number;
  filename: string;
  objectUrl?: string;
};

const jobs = new Map<string, Job>();

function resolveAsset(file: string): string {
  if (/^https?:|^blob:/.test(file)) return file;
  return `${import.meta.env.BASE_URL}${file.replace(/^\//, "")}`;
}

/** Simulated POST /api/analyze */
export async function analyzeVideo(file: File): Promise<{ jobId: string }> {
  await delay(600);
  const jobId = `job_${Math.random().toString(36).slice(2, 10)}`;
  jobs.set(jobId, {
    id: jobId,
    createdAt: Date.now(),
    filename: file.name,
    objectUrl: URL.createObjectURL(file),
  });
  return { jobId };
}

/** Simulated GET /api/status/[jobId] */
export async function getStatus(jobId: string): Promise<JobStatus> {
  await delay(250);
  const job = jobs.get(jobId);
  // Total simulated processing time ~9s.
  const elapsed = job ? Date.now() - job.createdAt : 9999;
  const total = 9000;
  const progress = Math.min(1, elapsed / total);
  if (progress >= 1) {
    return { status: "complete", progress: 1, message: "Analysis complete" };
  }
  const stage = Math.min(
    PROCESSING_MESSAGES.length - 1,
    Math.floor(progress * PROCESSING_MESSAGES.length),
  );
  return {
    status: progress < 0.05 ? "queued" : "processing",
    progress,
    message: PROCESSING_MESSAGES[stage],
  };
}

/** Simulated GET /api/results/[jobId] */
export async function getResult(jobId: string): Promise<ResonateResult> {
  await delay(400);
  const job = jobs.get(jobId);
  const base = rawResult as ResonateResult;
  return {
    ...base,
    filename: job?.filename ?? base.filename,
    // Prefer the user's uploaded clip; fall back to the bundled sample.
    videoUrl: job?.objectUrl ?? resolveAsset(base.videoUrl),
  };
}

/** Load the bundled sample result directly (no upload). */
export function getSampleResult(): ResonateResult {
  const base = rawResult as ResonateResult;
  return { ...base, videoUrl: resolveAsset(base.videoUrl) };
}

export const PROCESSING_STAGES = PROCESSING_MESSAGES;

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}
