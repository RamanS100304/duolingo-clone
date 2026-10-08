"use client";
import { useEffect, useState } from "react";
import { Avatar } from "@/components/Avatar";
import { api } from "@/lib/api";
import type { Leaderboard } from "@/lib/types";

export default function LeaderboardPage() {
  const [lb, setLb] = useState<Leaderboard | null>(null);
  useEffect(() => { api.leaderboard().then(setLb).catch(() => {}); }, []);
  if (!lb) return <div className="loading">Loading…</div>;

  const lastPromo = lb.entries.filter((e) => e.zone === "promotion").length;
  const firstDemo = lb.entries.findIndex((e) => e.zone === "demotion");

  return (
    <div className="page">
      <div className="center" style={{ marginBottom: 20 }}>
        <div className="league-badge" style={{ background: lb.league_color }}>🛡️</div>
        <h1 style={{ fontSize: 28 }}>{lb.league}</h1>
        <p className="muted">Top {lastPromo} advance to the next league · {lb.ends_in_days} days left</p>
      </div>
      <div>
        {lb.entries.map((e, i) => (
          <div key={e.user_id}>
            {i === firstDemo && <div className="zone-label down">▼ Demotion zone ▼</div>}
            <div className={`lb-row ${e.is_me ? "me" : ""}`}>
              <span className="rank">{e.rank <= 3 ? ["🥇", "🥈", "🥉"][e.rank - 1] : e.rank}</span>
              <Avatar name={e.display_name} color={e.avatar_color} />
              <b style={{ flex: 1, color: "var(--heading)" }}>{e.display_name}{e.is_me && " (you)"}</b>
              <span className="xp">{e.xp} XP</span>
            </div>
            {i + 1 === lastPromo && <div className="zone-label up">▲ Promotion zone ▲</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
