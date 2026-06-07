import { NextResponse } from "next/server";
import { insightsToResult } from "@/lib/mock-adapter";
import mockInsights from "@/lib/mock/insights.json";

export async function GET() {
  const result = insightsToResult(mockInsights);
  return NextResponse.json(result);
}
