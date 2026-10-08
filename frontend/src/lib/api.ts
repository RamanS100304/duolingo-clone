// Typed client for the FastAPI backend. Every rule (answers, hearts, XP, unlocks) is decided there.
import type {
  AnswerResult, CompleteResult, Leaderboard, PairResult, Profile, Quest, SessionData, SessionKind, UnitData, UserState,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, message: string, public code: string | null = null) { super(message); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(0, "Can't reach the server", "network");
  }
  if (!res.ok) {
    let detail: unknown = res.statusText;
    let code: string | null = null;
    try { const body = await res.json(); detail = body.detail ?? detail; code = body.code ?? null; } catch { /* non-JSON body */ }
    throw new ApiError(res.status, typeof detail === "string" ? detail : "Request failed", code);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

const send = <T,>(method: string, path: string, body?: unknown) =>
  request<T>(path, { method, body: body === undefined ? undefined : JSON.stringify(body) });

export type StartParams = { kind: SessionKind; lesson_id?: number; skill_id?: number; unit_id?: number };

export const api = {
  me: () => request<UserState>("/me"),
  updateSettings: (b: { daily_goal_xp?: number; display_name?: string; timezone?: string }) => send<UserState>("PATCH", "/me", b),
  refillHearts: () => send<UserState>("POST", "/hearts/refill"),

  path: () => request<{ units: UnitData[] }>("/path"),
  openChest: (unitId: number) => send<{ gems_earned: number; user: UserState }>("POST", `/units/${unitId}/chest`),

  startSession: (p: StartParams) => send<SessionData>("POST", "/sessions", p),
  answer: (sessionId: number, exercise_id: number, answer: string) =>
    send<AnswerResult>("POST", `/sessions/${sessionId}/answers`, { exercise_id, answer }),
  pair: (sessionId: number, exercise_id: number, left_id: number, right_id: string) =>
    send<PairResult>("POST", `/sessions/${sessionId}/pairs`, { exercise_id, left_id, right_id }),
  completeSession: (sessionId: number) => send<CompleteResult>("POST", `/sessions/${sessionId}/complete`),
  abandonSession: (sessionId: number) => send<void>("POST", `/sessions/${sessionId}/abandon`),

  leaderboard: () => request<Leaderboard>("/leaderboard"),
  profile: () => request<Profile>("/profile"),
  quests: () => request<{ quests: Quest[] }>("/quests"),

  advanceDay: (days = 1) => send<UserState>("POST", "/dev/advance-day", { days }),
  reset: (mode: "demo" | "empty") => send<UserState>("POST", "/dev/reset", { mode }),
};
