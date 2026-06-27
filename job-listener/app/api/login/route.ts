import { NextResponse } from "next/server";
import { validateUser } from "../../../lib/users";

export async function POST(req: Request) {
  try {
    const { identifier, type, password } = await req.json();

    if (!identifier || !type || !password) {
      return NextResponse.json({ message: "Missing fields" }, { status: 400 });
    }

    const ok = validateUser(identifier, type, password);
    if (ok) return NextResponse.json({ ok: true }, { status: 200 });

    return NextResponse.json({ message: "Invalid credentials" }, { status: 401 });
  } catch (err) {
    return NextResponse.json({ message: "Bad Request" }, { status: 400 });
  }
}
