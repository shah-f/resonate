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
