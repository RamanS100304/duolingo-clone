"use client";
// Page chrome: left Sidebar, StatsBar (course / streak / XP / gems / hearts) and the right rail.
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Quest } from "@/lib/types";
import { useUser } from "@/lib/user-context";
import {
  Bolt, Flag, Flame, Gem, Heart, NavLearn, NavLeaderboard, NavMore, NavPractice, NavProfile, NavQuests, NavShop,
} from "./Icons";
import Mascot from "./Mascot";
import { ProgressBar, mmss, useToast } from "./ui";

const NAV = [
  { href: "/learn", Icon: NavLearn, label: "Learn" },
  { href: "/practice", Icon: NavPractice, label: "Practice" },
  { href: "/leaderboard", Icon: NavLeaderboard, label: "Leaderboards" },
  { href: "/quests", Icon: NavQuests, label: "Quests" },
  { href: "/shop", Icon: NavShop, label: "Shop" },
  { href: "/profile", Icon: NavProfile, label: "Profile" },
  { href: "/settings", Icon: NavMore, label: "More" },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <nav className="sidebar">
      <Link href="/learn" className="logo"><Mascot size={36} /> lingua</Link>
      {NAV.map(({ href, Icon, label }) => (
        <Link key={href} href={href} className={`nav-item ${path.startsWith(href) ? "active" : ""}`}>
          <span className="nav-icon"><Icon /></span><span className="nav-label">{label}</span>
        </Link>
      ))}
    </nav>
  );
}

function useCountdown(seconds: number) {
  const [left, setLeft] = useState(seconds);
  useEffect(() => {
    setLeft(seconds);
    const t = setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [seconds]);
  return left;
}

function StreakPopover() {
  const { user } = useUser();
  if (!user) return null;
  return (
    <div className="popover">
      <h3>{user.streak} day streak</h3>
      <p className="muted" style={{ margin: "6px 0 12px" }}>
        {user.streak_active_today ? "You practised today. Come back tomorrow to keep it going!" : "Do a lesson today to extend your streak!"}
      </p>
      <div className="week-strip">
        {user.week.map((d) => (
          <div className="week-day" key={d.date}>
            <div className={`week-dot ${d.active ? "on" : ""}`}>{d.active ? "✓" : ""}</div>{d.label[0]}
          </div>
        ))}
      </div>
    </div>
  );
}

function HeartsPopover({ close }: { close: () => void }) {
  const { user, setUser } = useUser();
  const toast = useToast();
  const router = useRouter();
  const left = useCountdown(user?.next_heart_in_sec ?? 0);
  if (!user) return null;
  const full = user.hearts >= user.max_hearts;
  const refill = async () => {
    try { setUser(await api.refillHearts()); toast({ icon: "❤️", title: "Hearts refilled!" }); close(); }
    catch (e) { toast({ icon: "⚠️", title: (e as Error).message }); }
  };
  return (
    <div className="popover">
      <div className="hearts-row">{Array.from({ length: user.max_hearts }, (_, i) => <Heart key={i} size={30} grey={i >= user.hearts} />)}</div>
      <h3>{full ? "You have full hearts" : `${user.hearts} of ${user.max_hearts} hearts`}</h3>
      <p className="muted" style={{ margin: "6px 0 14px" }}>
        {full ? "Keep on learning! Mistakes in lessons cost a heart." : `Next heart in ${mmss(left)}`}
      </p>
      {!full && (
        <>
          <button className="btn btn-blue btn-block" onClick={refill} disabled={user.gems < user.refill_cost}>
            Refill <Gem size={22} /> {user.refill_cost}
          </button>
          <button className="btn btn-secondary btn-block" style={{ marginTop: 10 }}
            onClick={() => { close(); router.push("/session/practice"); }}>Practice to earn +1</button>
        </>
      )}
    </div>
  );
}

export function StatsBar() {
  const { user } = useUser();
  const [open, setOpen] = useState<null | "streak" | "hearts">(null);
  if (!user) return <div className="stats-row" style={{ minHeight: 40 }} />;
  const toggle = (k: "streak" | "hearts") => setOpen(open === k ? null : k);
  return (
    <div className="stats-row" style={{ position: "relative" }}>
      <div className="course-chip" title={user.course ? `${user.course.title} for ${user.course.from_language} speakers` : ""}>
        <Flag />
      </div>
      {/* the flame stays grey until today's streak is extended, like Duolingo */}
      <button className="stat" onClick={() => toggle("streak")} style={{ color: user.streak_active_today ? "var(--orange)" : "var(--muted)" }}>
        <Flame grey={!user.streak_active_today} /> {user.streak}
      </button>
      <span className="stat" style={{ color: "var(--yellow-d)", cursor: "default" }} title="Total XP"><Bolt /> {user.total_xp}</span>
      <Link className="stat" style={{ color: "var(--blue)" }} title="Gems" href="/shop"><Gem /> {user.gems}</Link>
      <button className="stat" onClick={() => toggle("hearts")} style={{ color: user.hearts === 0 ? "var(--muted)" : "var(--red)" }}>
        <Heart grey={user.hearts === 0} /> {user.hearts}
      </button>
      {open === "streak" && <StreakPopover />}
      {open === "hearts" && <HeartsPopover close={() => setOpen(null)} />}
    </div>
  );
}

export function DailyGoalCard() {
  const { user } = useUser();
  if (!user) return null;
  const done = user.daily_xp >= user.daily_goal_xp;
  return (
    <div className="card goal-card">
      <div className="row" style={{ justifyContent: "space-between", marginBottom: 12 }}>
        <h3 style={{ margin: 0 }}>Daily Goal</h3>
        <Link href="/settings" className="link-btn">Edit goal</Link>
      </div>
      <div className="row" style={{ gap: 12 }}>
        <span style={{ fontSize: 30 }}>{done ? "🏆" : "🎯"}</span>
        <div style={{ flex: 1 }}>
          <b style={{ color: "var(--heading)" }}>{done ? "Goal reached!" : `Earn ${user.daily_goal_xp} XP`}</b>
          <div style={{ margin: "6px 0 4px" }}><ProgressBar value={user.daily_xp} max={user.daily_goal_xp} gold={done} /></div>
          <span className="muted" style={{ fontSize: 14 }}>{Math.min(user.daily_xp, user.daily_goal_xp)} / {user.daily_goal_xp} XP</span>
        </div>
      </div>
    </div>
  );
}

export function QuestList({ quests }: { quests: Quest[] }) {
  return (
    <>
      {quests.map((q) => (
        <div className="quest-row" key={q.id}>
          <span className="quest-icon">{q.icon}</span>
          <div style={{ flex: 1 }}>
            <b>{q.title}</b>
            <div className="row" style={{ gap: 8, marginTop: 6 }}>
              <div style={{ flex: 1 }}><ProgressBar value={q.progress} max={q.target} gold={q.done} /></div>
              <span className="muted" style={{ fontSize: 13, minWidth: 40, textAlign: "right" }}>{q.progress}/{q.target}</span>
            </div>
          </div>
          <span className="quest-chest">{q.done ? "✅" : "🎁"}</span>
        </div>
      ))}
    </>
  );
}

function QuestsCard() {
  const { user } = useUser();
  const [quests, setQuests] = useState<Quest[]>([]);
  useEffect(() => { if (user) api.quests().then((r) => setQuests(r.quests)).catch(() => {}); }, [user]);
  if (!user || !quests.length) return null;
  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}>
        <h3 style={{ fontSize: 18 }}>Daily Quests</h3>
        <Link href="/quests" className="link-btn">View all</Link>
      </div>
      <QuestList quests={quests} />
    </div>
  );
}

export function RightRail() {
  const { user } = useUser();
  return (
    <aside className="shell-rail">
      <StatsBar />
      <Link href="/leaderboard" className="card timed-card">
        <span style={{ fontSize: 34 }}>🏆</span>
        <div><b style={{ color: "var(--heading)" }}>{user?.league ?? "Bronze League"}</b><p className="muted" style={{ fontSize: 14 }}>See where you rank this week</p></div>
      </Link>
      <DailyGoalCard />
      <QuestsCard />
    </aside>
  );
}
