import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const res = await fetch(`${PYTHON_API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
