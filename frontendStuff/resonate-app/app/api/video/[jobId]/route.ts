import { NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;
  try {
    const res = await fetch(`${PYTHON_API_URL}/video/${jobId}`);
    if (!res.ok) return NextResponse.json({ error: "Video not found" }, { status: 404 });
    const blob = await res.blob();
    const contentType = res.headers.get("content-type") ?? "video/mp4";
    return new NextResponse(blob as unknown as BodyInit, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=3600",
      },
    });
  } catch {
    return NextResponse.json({ error: "API server unreachable" }, { status: 503 });
  }
}
