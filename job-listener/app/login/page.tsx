"use client";
import * as React from "react";
const useState: any = (React as any).useState || ((init: any) => [init, () => {}]);
import { useRouter, useSearchParams } from "next/navigation";

export default function LoginPage() {
  const [identifier, setIdentifier] = useState("");
  const [useUserId, setUseUserId] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();
  const oauthError = searchParams?.get("error") || null;

  async function handleSubmit(e: any) {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, type: useUserId ? "userId" : "email", password }),
      });

      if (res.ok) {
        router.push("/");
      } else {
        const data = await res.json();
        setError(data?.message || "Login failed");
      }
    } catch (err) {
      setError("Network error");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="max-w-md w-full bg-white shadow p-6 rounded">
        <h1 className="text-2xl mb-4">Sign in</h1>
        {error && <p className="text-red-600 mb-2">{error}</p>}
        {oauthError === "linkedin_unconfigured" && (
          <p className="text-yellow-700 mb-2">LinkedIn login not configured. Set LINKEDIN_CLIENT_ID.</p>
        )}
        {oauthError === "invalid_oauth_state" && (
          <p className="text-red-600 mb-2">OAuth state mismatch. Please try again.</p>
        )}

        <label className="flex items-center gap-2 mb-3">
          <input type="checkbox" checked={useUserId} onChange={(e: any) => setUseUserId(e.target.checked)} />
          <span className="text-sm">Use User ID (instead of email)</span>
        </label>

        <label className="block mb-2">
          <span className="text-sm">{useUserId ? "User ID" : "Email"}</span>
          <input
            type={useUserId ? "text" : "email"}
            value={identifier}
            onChange={(e: any) => setIdentifier(e.target.value)}
            required
            className="mt-1 block w-full border rounded px-3 py-2"
          />
        </label>

        <label className="block mb-4">
          <span className="text-sm">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e: any) => setPassword(e.target.value)}
            required
            className="mt-1 block w-full border rounded px-3 py-2"
          />
        </label>

        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded mb-3">Sign in</button>

        <div className="flex gap-2">
          <a href="/api/auth/signin/linkedin" className="flex-1 text-center border rounded py-2">Sign in with LinkedIn</a>
        </div>

        <p className="mt-4 text-sm text-center">
          Don't have an account? <a href="/register" className="text-blue-600">Register</a>
        </p>
      </form>
    </div>
  );
}
