type User = {
  userId: string;
  email: string;
  password: string;
};

const users = new Map<string, User>();

export function createUser({ userId, email, password }: User) {
  if (users.has(userId) || Array.from(users.values()).some((u) => u.email === email)) {
    return false;
  }
  users.set(userId, { userId, email, password });
  return true;
}

export function findUserByEmail(email: string) {
  return Array.from(users.values()).find((u) => u.email === email) || null;
}

export function findUserById(userId: string) {
  return users.get(userId) || null;
}

export function validateUser(identifier: string, type: "email" | "userId", password: string) {
  const user = type === "email" ? findUserByEmail(identifier) : findUserById(identifier);
  if (!user) return false;
  return user.password === password;
}
