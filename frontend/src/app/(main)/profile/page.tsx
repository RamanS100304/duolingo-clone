"use client";
import { useEffect, useState } from "react";
import { Avatar } from "@/components/Avatar";
import { Bolt, Flame, Gem } from "@/components/Icons";
import { ProgressBar } from "@/components/ui";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function ProfilePage() {
  const [p, setP] = useState<Profile | null>(null);
  useEffect(() => { api.profile().then(setP).catch(() => {}); }, []);
  if (!p) return <div className="loading">Loading…</div>;

  const u = p.user;
  const tiles = [
    { icon: <Flame />, value: u.streak, label: "Day streak" },
    { icon: <Bolt />, value: u.total_xp, label: "Total XP" },
    { icon: <span style={{ fontSize: 26 }}>🏅</span>, value: p.stats.skills_completed, label: "Skills completed" },
    { icon: <span style={{ fontSize: 26 }}>🎯</span>, value: `${p.accuracy}%`, label: "Accuracy" },
    { icon: <Gem />, value: u.gems, label: "Gems" },
    { icon: <span style={{ fontSize: 26 }}>📚</span>, value: p.stats.lessons_completed, label: "Lessons done" },
  ];
  const unlocked = p.achievements.filter((a) => a.unlocked).length;

  return (
    <div className="page">
      <div className="profile-head">
        <Avatar name={u.display_name} color={u.avatar_color} size="xl" />
        <div>
          <h1 style={{ fontSize: 28 }}>{u.display_name}</h1>
          <p className="muted">@{u.username} · Joined {new Date(p.joined).toLocaleDateString(undefined, { month: "long", year: "numeric" })}</p>
          <p className="muted">Longest streak: {u.longest_streak} days</p>
        </div>
      </div>

      <h2 className="section-title" style={{ marginTop: 0 }}>Statistics</h2>
      <div className="stat-grid">
        {tiles.map((t) => (
          <div className="stat-tile" key={t.label}>{t.icon}<div><b>{t.value}</b><span>{t.label}</span></div></div>
        ))}
      </div>

      <h2 className="section-title">Achievements <span className="muted" style={{ fontSize: 16 }}>({unlocked}/{p.achievements.length})</span></h2>
      <div className="card" style={{ padding: 0 }}>
        {p.achievements.map((a) => (
          <div className={`badge-row ${a.unlocked ? "" : "locked"}`} key={a.id}>
            <div className="badge-icon">{a.icon}</div>
            <div style={{ flex: 1 }}>
              <b style={{ color: "var(--heading)", fontSize: 18 }}>{a.title}</b>
              <p className="muted" style={{ fontSize: 14, marginBottom: 6 }}>{a.description}</p>
              {a.unlocked
                ? <span style={{ color: "var(--green-d)", fontSize: 14 }}>✓ Unlocked · +{a.gem_reward} gems</span>
                : <><ProgressBar value={a.progress} max={a.threshold} /><span className="muted" style={{ fontSize: 13 }}>{a.progress} / {a.threshold}</span></>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
