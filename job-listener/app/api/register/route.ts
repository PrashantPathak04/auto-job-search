import { NextResponse } from "next/server";
import { createUser } from "../../../../lib/users";

export async function POST(req: Request) {
  try {
    const { userId, email, password } = await req.json();
    if (!userId || !email || !password) {
      return NextResponse.json({ message: "Missing fields" }, { status: 400 });
    }

    const ok = createUser({ userId, email, password });
    if (!ok) return NextResponse.json({ message: "User already exists" }, { status: 409 });

    return NextResponse.json({ ok: true }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ message: "Bad Request" }, { status: 400 });
  }
}
