import { NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;
  try {
    const res = await fetch(`${PYTHON_API_URL}/status/${jobId}`);
    if (!res.ok) {
      return NextResponse.json({ status: "error", message: "Job not found" }, { status: 404 });
    }
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ status: "error", message: "API server unreachable" }, { status: 503 });
  }
}
