GitHub Copilot — using GPT-5 mini.

Step-by-step instructions + created documentation file.

Step-by-step (summary)

Create a LinkedIn App (https://www.linkedin.com/developers/apps). Note client ID / client secret.
Add OAuth 2.0 redirect URI: <BASE_URL>/api/auth/linkedin/callback (e.g. http://localhost:3000/api/auth/linkedin/callback).
Add env vars to .env (project root):
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
NEXT_PUBLIC_BASE_URL=http://localhost:3000
Add route to start auth: app/api/auth/linkedin/route.ts (redirect to LinkedIn auth URL).
Add callback route: app/api/auth/linkedin/callback/route.ts (exchange code→access_token, fetch /me and email, create/find user, set session cookie, redirect to /dashboard).
Add or update server-side user store helper (lib/users.ts) to create/find user from LinkedIn profile.
Ensure login page links to /api/auth/linkedin (already present).
Test: run npm run dev, visit /login → Sign in with LinkedIn → authorize → should redirect to /dashboard with a session cookie.
(Optional) Replace in-memory users + cookie with DB and secure signed JWT or NextAuth.
Created docs file with full steps and example code:

# LinkedIn OAuth setup — job-listener

## Overview
This document records steps to add "Sign in with LinkedIn" to the Next.js app (app directory).

## 1. Create LinkedIn App
1. Visit https://www.linkedin.com/developers/apps and create a new app.
2. Note `Client ID` and `Client Secret`.
3. Under "Auth" or "OAuth 2.0", add redirect URI:
   - `https://<your-domain>/api/auth/linkedin/callback`
   - For local dev: `http://localhost:3000/api/auth/linkedin/callback`

## 2. Environment variables
Create `.env` in project root (do not commit secrets):
```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## 3. Start auth route
Create `app/api/auth/linkedin/route.ts` to redirect to LinkedIn:
```typescript
// filepath: c:\Users\patha\code\auto-job-search\job-listener\app\api\auth\linkedin\route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const clientId = process.env.LINKEDIN_CLIENT_ID;
  const base = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000";
  const redirectUri = `${base}/api/auth/linkedin/callback`;
  const scope = encodeURIComponent("r_liteprofile r_emailaddress");
  const url = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(
    redirectUri
  )}&scope=${scope}`;
  return NextResponse.redirect(url);
}
```

## 4. Callback route (exchange code, fetch profile & email)
Create `app/api/auth/linkedin/callback/route.ts`:
```typescript
// filepath: c:\Users\patha\code\auto-job-search\job-listener\app\api\auth\linkedin\callback\route.ts
import { NextResponse } from "next/server";
import { findOrCreateFromLinkedIn } from "../../../../lib/users";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  if (!code) return NextResponse.redirect("/login?error=missing_code");

  const base = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000";
  const tokenRes = await fetch("https://www.linkedin.com/oauth/v2/accessToken", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: `${base}/api/auth/linkedin/callback`,
      client_id: process.env.LINKEDIN_CLIENT_ID || "",
      client_secret: process.env.LINKEDIN_CLIENT_SECRET || "",
    }),
  });
  const tokenData = await tokenRes.json();
  const accessToken = tokenData?.access_token;
  if (!accessToken) return NextResponse.redirect("/login?error=token");

  const profileRes = await fetch("https://api.linkedin.com/v2/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const profile = await profileRes.json();

  const emailRes = await fetch(
    "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  const emailData = await emailRes.json();
  const email = emailData?.elements?.[0]?.["handle~"]?.emailAddress;

  // create/find user
  const user = findOrCreateFromLinkedIn(profile, email);

  // set a simple session cookie (replace with secure session/JWT in prod)
  const sessionToken = `sess_${user.id}_${Date.now()}`;
  const headers = new Headers({ Location: "/dashboard" });
  headers.append(
    "Set-Cookie",
    `session=${sessionToken}; Path=/; HttpOnly; SameSite=Lax; Secure`
  );
  return new Response(null, { status: 302, headers });
}
```

## 5. Server helper (simple in-memory store)
Create `lib/users.ts`:
```typescript
// filepath: c:\Users\patha\code\auto-job-search\job-listener\lib\users.ts
type User = { id: string; email?: string; name?: string; linkedInId?: string };
const users: User[] = [];

export function findOrCreateFromLinkedIn(profile: any, email?: string) {
  let user = users.find(
    (u) => u.linkedInId === profile.id || (email && u.email === email)
  );
  if (!user) {
    user = {
      id: String(users.length + 1),
      email,
      name: `${profile.localizedFirstName || ""} ${profile.localizedLastName || ""}`.trim(),
      linkedInId: profile.id,
    };
    users.push(user);
  }
  return user;
}
```

## 6. Login page
Ensure `app/login/page.tsx` has a link to start flow:
```tsx
<a href="/api/auth/linkedin" className="...">Sign in with LinkedIn</a>
```

## 7. Test
1. npm run dev
2. Visit `/login` → click "Sign in with LinkedIn"
3. Authorize app → should redirect to `/dashboard` and set cookie

## 8. Next steps / Security
- Use a persistent DB for users.
- Replace cookie with signed JWT or NextAuth.
- Secure cookies (SameSite, Secure, expiration) and CSRF protections.


If you want, I can add the route and lib files into the repo now and run the dev server locally. Which do you prefer?

GPT-5 mini • 1x