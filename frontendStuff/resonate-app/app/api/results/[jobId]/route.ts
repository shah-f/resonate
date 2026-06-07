import { NextResponse } from "next/server";
import resonateResult from "@/lib/mock/resonateResult.json";

export async function GET() {
  return NextResponse.json(resonateResult);
}
