import { NextResponse } from "next/server";
import { LIBRARY } from "@/lib/library";
import complaint_tiktok from "@/lib/library/complaint_tiktok.json";
import finance_test_clip from "@/lib/library/finance_test_clip.json";
import grwm from "@/lib/library/grwm.json";
import walk_in_park from "@/lib/library/walk_in_park.json";
import flow_state_zetamac from "@/lib/library/flow_state_zetamac.json";

const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000";

const LIBRARY_RESULTS: Record<string, unknown> = {
  complaint_tiktok,
  finance_test_clip,
  grwm,
  walk_in_park,
  flow_state_zetamac,
};

const LIBRARY_SLUGS = new Set(LIBRARY.map((e) => e.slug));

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;

  if (LIBRARY_SLUGS.has(jobId)) {
    return NextResponse.json(LIBRARY_RESULTS[jobId]);
  }

  try {
    const res = await fetch(`${PYTHON_API_URL}/results/${jobId}`);
    if (!res.ok) {
      return NextResponse.json({ error: "Results not available" }, { status: res.status });
    }
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ error: "API server unreachable" }, { status: 503 });
  }
}
