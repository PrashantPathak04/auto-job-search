import { NextResponse } from "next/server";

export function GET() {
  if (!process.env.LINKEDIN_CLIENT_ID) {
    return NextResponse.redirect("/login?error=linkedin_unconfigured");
  }
  return NextResponse.redirect("/api/auth/signin/linkedin");
}

