"use client";
// Screens and modals shown around the lesson player: lesson complete, streak celebration,
// out of hearts, quit confirmation, legendary-failed.
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { CompleteResult, UserState } from "@/lib/types";
import { Bolt, Flame, Gem } from "./Icons";
import Mascot from "./Mascot";
import { Confetti, Modal, mmss, useToast } from "./ui";

const TITLES: Record<string, string> = {
  lesson: "Lesson Complete!", practice: "Practice Complete!", timed: "Time's Up!", legendary: "Legendary!",
};

export function LessonComplete({ result, onContinue }: { result: CompleteResult; onContinue: () => void }) {
  // All numbers come from the server's record of the session.
  const { kind, accuracy, duration_sec: seconds } = result;
  const cards = [
    { head: "Total XP", color: "var(--yellow)", icon: <Bolt size={24} />, val: result.xp_earned },
    { head: accuracy === 100 ? "Amazing" : accuracy >= 80 ? "Great" : "Good", color: "var(--green)", icon: <span>🎯</span>, val: `${accuracy}%` },
    { head: seconds < 120 ? "Speedy" : "Committed", color: "var(--blue)", icon: <span>⏱️</span>, val: mmss(seconds) },
  ];
  return (
    <div className="result">
      <Confetti />
      <div className="result-body">
        <Mascot size={150} mood="cheer" className="float" />
        <h1>{TITLES[kind] ?? "Done!"}</h1>
        <div className="stat-cards">
          {cards.map((c) => (
            <div className="stat-card" key={c.head} style={{ borderColor: c.color }}>
              <div className="head" style={{ background: c.color }}>{c.head}</div>
              <div className="val" style={{ color: c.color }}>{c.icon} {c.val}</div>
            </div>
          ))}
        </div>
        {result.gems_earned > 0 && <p><Gem size={20} /> +{result.gems_earned} gems</p>}
        {result.skill_completed && <p style={{ color: "var(--yellow-d)", fontWeight: 900 }}>⭐ Skill complete!</p>}
        {result.daily_goal_reached && <p style={{ color: "var(--orange)", fontWeight: 900 }}>🎯 Daily goal reached!</p>}
      </div>
      <div className="lesson-footer"><div className="footer-inner"><span />
        <button className="btn btn-primary btn-lg" onClick={onContinue}>Continue</button>
      </div></div>
    </div>
  );
}

export function StreakScreen({ user, onContinue }: { user: UserState; onContinue: () => void }) {
  return (
    <div className="result">
      <Confetti count={40} />
      <div className="result-body">
        <Flame size={120} />
        <div className="big-streak">{user.streak}</div>
        <h1 style={{ color: "var(--orange)" }}>day streak!</h1>
        <p>You&apos;re on fire — keep learning every day.</p>
        <div className="week-strip">
          {user.week.map((d) => (
            <div className="week-day" key={d.date}>
              <div className={`week-dot ${d.active ? "on" : ""}`}>{d.active ? "✓" : ""}</div>{d.label[0]}
            </div>
          ))}
        </div>
      </div>
      <div className="lesson-footer"><div className="footer-inner"><span />
        <button className="btn btn-primary btn-lg" onClick={onContinue}>Continue</button>
      </div></div>
    </div>
  );
}

export function OutOfHeartsModal({ user, onRefilled, onExit }: {
  user: UserState; onRefilled: (u: UserState) => void; onExit: () => void;
}) {
  const router = useRouter();
  const toast = useToast();
  const refill = async () => {
    try { onRefilled(await api.refillHearts()); toast({ icon: "❤️", title: "Hearts refilled!" }); }
    catch (e: any) { toast({ icon: "⚠️", title: e.message }); }
  };
  return (
    <Modal>
      <Mascot size={110} mood="sad" />
      <h2>You ran out of hearts!</h2>
      <p>Practice what you&apos;ve learned to earn a heart back, or refill with gems.</p>
      <button className="btn btn-primary btn-block btn-lg" onClick={() => router.push("/session/practice")}>Practice to earn +1 heart</button>
      <button className="btn btn-blue btn-block btn-lg" onClick={refill} disabled={user.gems < user.refill_cost}>
        Refill for <Gem size={24} /> {user.refill_cost}
      </button>
      <button className="btn btn-ghost btn-block" onClick={onExit}>No thanks</button>
    </Modal>
  );
}

export function QuitModal({ onStay, onQuit }: { onStay: () => void; onQuit: () => void }) {
  return (
    <Modal onClose={onStay}>
      <Mascot size={100} mood="sad" />
      <h2>Wait, don&apos;t go!</h2>
      <p>You&apos;ll lose your progress in this lesson if you quit now.</p>
      <button className="btn btn-primary btn-block btn-lg" onClick={onStay}>Keep learning</button>
      <button className="btn btn-ghost btn-block" style={{ color: "var(--red)" }} onClick={onQuit}>End session</button>
    </Modal>
  );
}

export function FailedModal({ message, onRetry, onExit }: { message: string; onRetry: () => void; onExit: () => void }) {
  return (
    <Modal>
      <Mascot size={110} mood="sad" />
      <h2>Challenge failed</h2>
      <p>{message}</p>
      <button className="btn btn-primary btn-block btn-lg" onClick={onRetry}>Try again</button>
      <button className="btn btn-ghost btn-block" onClick={onExit}>Exit</button>
    </Modal>
  );
}
