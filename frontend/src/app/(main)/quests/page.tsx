"use client";
import { useEffect, useState } from "react";
import { QuestList } from "@/components/Chrome";
import Mascot from "@/components/Mascot";
import { api } from "@/lib/api";
import type { Quest } from "@/lib/types";
import { useUser } from "@/lib/user-context";

export default function QuestsPage() {
  const { user } = useUser();
  const [quests, setQuests] = useState<Quest[] | null>(null);
  useEffect(() => { api.quests().then((r) => setQuests(r.quests)).catch(() => setQuests([])); }, [user?.daily_xp]);
  if (!quests) return <div className="loading">Loading…</div>;
  const done = quests.filter((q) => q.done).length;
  return (
    <div className="page">
      <div className="quest-hero">
        <div>
          <h1>Daily Quests</h1>
          <p>Complete quests to keep your learning on track. New quests every day!</p>
        </div>
        <Mascot size={110} mood={done === quests.length ? "cheer" : "happy"} />
      </div>
      <div className="card" style={{ padding: "4px 16px" }}><QuestList quests={quests} /></div>
      <p className="muted center" style={{ marginTop: 16 }}>{done} of {quests.length} done today · Friends quests coming soon</p>
    </div>
  );
}
