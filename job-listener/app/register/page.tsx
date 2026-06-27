"use client";
import * as React from "react";
const useState: any = (React as any).useState || ((init: any) => [init, () => {}]);
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [userId, setUserId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleSubmit(e: any) {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, email, password }),
      });

      if (res.ok) {
        router.push("/login");
      } else {
        const data = await res.json();
        setError(data?.message || "Registration failed");
      }
    } catch (err) {
      setError("Network error");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="max-w-md w-full bg-white shadow p-6 rounded">
        <h1 className="text-2xl mb-4">Register</h1>
        {error && <p className="text-red-600 mb-2">{error}</p>}

        <label className="block mb-2">
          <span className="text-sm">User ID</span>
          <input
            type="text"
            value={userId}
            onChange={(e: any) => setUserId(e.target.value)}
            required
            className="mt-1 block w-full border rounded px-3 py-2"
          />
        </label>

        <label className="block mb-2">
          <span className="text-sm">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e: any) => setEmail(e.target.value)}
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

        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded">Create account</button>

        <p className="mt-4 text-sm text-center">
          Already have an account? <a href="/login" className="text-blue-600">Sign in</a>
        </p>
      </form>
    </div>
  );
}
