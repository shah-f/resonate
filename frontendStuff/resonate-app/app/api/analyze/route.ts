import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { jobs } from "@/lib/job-store";

export async function POST() {
  const jobId = randomUUID();
  jobs.set(jobId, { startTime: Date.now() });
  return NextResponse.json({ jobId });
}
