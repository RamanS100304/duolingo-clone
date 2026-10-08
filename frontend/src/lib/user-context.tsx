"use client";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { UserState } from "./types";

type Ctx = {
  user: UserState | null;
  error: string | null;
  refresh: () => Promise<void>;
  setUser: (u: UserState) => void;     // push a fresh snapshot returned by a mutating API call
};
const UserContext = createContext<Ctx>({ user: null, error: null, refresh: async () => {}, setUser: () => {} });

const browserTimezone = () => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone; } catch { return null; } };

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const tzSynced = useRef(false);

  const refresh = useCallback(async () => {
    try {
      let me = await api.me();
      // Streaks and the daily goal follow the learner's own midnight, so tell the server our time zone once.
      const tz = browserTimezone();
      if (!tzSynced.current && tz && tz !== me.timezone) me = await api.updateSettings({ timezone: tz });
      tzSynced.current = true;
      setUser(me); setError(null);
    } catch {
      setError("Waking up the server… this can take a few seconds.");
    }
  }, []);

  // First load, retrying while a sleeping backend boots up.
  useEffect(() => {
    let cancelled = false, delay = 1500;
    const attempt = async () => {
      await refresh();
      if (!cancelled && !tzSynced.current) { setTimeout(attempt, delay); delay = Math.min(delay * 2, 10000); }
    };
    attempt();
    return () => { cancelled = true; };
  }, [refresh]);

  // Re-poll once a minute so the heart-regeneration timer stays accurate.
  useEffect(() => {
    const t = setInterval(refresh, 60_000);
    return () => clearInterval(t);
  }, [refresh]);

  return <UserContext.Provider value={{ user, error, refresh, setUser }}>{children}</UserContext.Provider>;
}

export const useUser = () => useContext(UserContext);
