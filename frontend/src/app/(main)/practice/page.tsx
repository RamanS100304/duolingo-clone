"use client";
// Practice hub: free practice (earns a heart) and the timed challenge.
import Link from "next/link";
import { useToast } from "@/components/ui";
import { useUser } from "@/lib/user-context";

export default function PracticePage() {
  const { user } = useUser();
  const toast = useToast();
  const cards = [
    { href: "/session/practice", icon: "💪", title: "Practice", text: "Review words from finished lessons. No hearts lost — and you earn one back.", color: "var(--green)" },
    { href: "/session/timed", icon: "⏱️", title: "Timed challenge", text: "Two minutes on the clock. Answer as many as you can for up to 40 XP.", color: "var(--orange)" },
  ];
  return (
    <div className="page">
      <h1 className="page-title">Practice Hub</h1>
      <div className="hub-grid">
        {cards.map((c) => (
          <Link key={c.href} href={c.href} className="hub-card" style={{ ["--accent" as string]: c.color }}>
            <span className="hub-icon">{c.icon}</span>
            <div><b>{c.title}</b><p className="muted">{c.text}</p></div>
          </Link>
        ))}
        <button className="hub-card" style={{ ["--accent" as string]: "var(--purple)" }}
          onClick={() => toast({ icon: "🎙️", title: "Speaking practice", text: "Coming soon!" })}>
          <span className="hub-icon">🎙️</span>
          <div><b>Speaking <span className="soon">Soon</span></b><p className="muted">Pronunciation practice with speech recognition.</p></div>
        </button>
      </div>
      {user && user.hearts < user.max_hearts && (
        <p className="muted center" style={{ marginTop: 20 }}>You have {user.hearts} of {user.max_hearts} hearts — a practice session earns one back.</p>
      )}
    </div>
  );
}
