import { NextResponse } from "next/server";
import { createUser, findUserByEmail } from "../../../../../lib/users";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");

  // Validate state cookie set by the initial redirect
  const cookieHeader = req.headers.get("cookie") || "";
  const match = cookieHeader.match(/(?:^|; )li_oauth_state=([^;]+)/);
  const savedState = match ? decodeURIComponent(match[1]) : null;

  if (state && savedState && state !== savedState) {
    const baseFail = process.env.NEXT_PUBLIC_BASE_URL || process.env.BASE_URL || new URL(req.url).origin;
    return NextResponse.redirect(`${baseFail}/login?error=invalid_oauth_state`);
  }

  if (!code) {
    return NextResponse.json({ message: "Missing code" }, { status: 400 });
  }

  const clientId = process.env.LINKEDIN_CLIENT_ID;
  const clientSecret = process.env.LINKEDIN_CLIENT_SECRET;
  const base = process.env.NEXT_PUBLIC_BASE_URL || process.env.BASE_URL || "http://localhost:3000";
  const redirectUri = `${base}/api/auth/linkedin/callback`;

  if (!clientId || !clientSecret) {
    // Dev stub: no secrets configured — fake success and redirect back to dashboard
    const res = NextResponse.redirect(`${base}/dashboard?linkedin=stub-success`);
    // create a stub session value
    res.cookies.set("session", "linkedin-stub", { httpOnly: true, path: "/", maxAge: 60 * 60 * 24 * 7 });
    return res;
  }

  try {
    const tokenRes = await fetch("https://www.linkedin.com/oauth/v2/accessToken", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code: code,
        redirect_uri: redirectUri,
        client_id: clientId,
        client_secret: clientSecret,
      }),
    });

    if (!tokenRes.ok) {
      const errText = await tokenRes.text();
      return NextResponse.json({ message: "Token exchange failed", details: errText }, { status: 500 });
    }

    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    // Fetch basic profile
    const profileRes = await fetch("https://api.linkedin.com/v2/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const profile = await profileRes.json();
    const linkedinId = profile.id;

    // Fetch primary email
    const emailRes = await fetch(
      "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    const emailData = await emailRes.json();
    const primaryEmail = emailData?.elements?.[0]?.['handle~']?.emailAddress;

    if (!linkedinId || !primaryEmail) {
      return NextResponse.json({ message: "Failed to obtain user info from LinkedIn" }, { status: 500 });
    }

    // Create or find user in our in-memory store
    const userId = `li_${linkedinId}`;
    const created = createUser({ userId, email: primaryEmail, password: Math.random().toString(36) });
    let finalUserId = userId;
    if (!created) {
      // user already exists (maybe registered by email) — find by email
      const existing = findUserByEmail(primaryEmail);
      if (existing) finalUserId = existing.userId;
    }

    // Set a session cookie and redirect to dashboard
    const res = NextResponse.redirect(`${base}/dashboard`);
    res.cookies.set("session", finalUserId, { httpOnly: true, path: "/", maxAge: 60 * 60 * 24 * 7 });
    return res;
  } catch (err) {
    return NextResponse.json({ message: "OAuth exchange failed" }, { status: 500 });
  }
}
