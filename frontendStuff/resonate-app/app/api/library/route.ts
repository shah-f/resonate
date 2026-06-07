import { NextResponse } from "next/server";
import { LIBRARY } from "@/lib/library";

export async function GET() {
  return NextResponse.json(LIBRARY);
}
