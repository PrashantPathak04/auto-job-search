import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-semibold mb-4">Dashboard</h1>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 border rounded">
          <h2 className="text-lg font-medium">Saved Jobs</h2>
          <p className="text-2xl mt-2">0</p>
        </div>

        <div className="p-4 border rounded">
          <h2 className="text-lg font-medium">Applications</h2>
          <p className="text-2xl mt-2">0</p>
        </div>

        <div className="p-4 border rounded">
          <h2 className="text-lg font-medium">Profile</h2>
          <p className="mt-2">No profile connected</p>
        </div>
      </section>

      <div className="mt-6 flex gap-3">
        <Link href="/login" className="px-4 py-2 bg-blue-600 text-white rounded">Login</Link>
        <Link href="/register" className="px-4 py-2 border rounded">Register</Link>
      </div>
    </main>
  );
}
