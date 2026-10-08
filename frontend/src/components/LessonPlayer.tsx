"use client";
// The lesson loop. One component drives every mode; the server tracks the session and decides
// correctness, hearts, mistakes, XP and unlocks:
//   lesson     - wrong answers cost hearts and are repeated at the end
//   practice   - no hearts lost, earns one heart back
//   timed      - 2 minute countdown, answer as many as you can (one try each)
//   legendary  - hard challenge on a finished skill: at most one mistake
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, api, type StartParams } from "@/lib/api";
import { play } from "@/lib/sound";
import type { AnswerResult, CompleteResult, Exercise, SessionData, SessionState } from "@/lib/types";
import { useUser } from "@/lib/user-context";
import { ExerciseView } from "./exercises";
import { Heart } from "./Icons";
import { FailedModal, LessonComplete, OutOfHeartsModal, QuitModal, StreakScreen } from "./LessonEnd";
import { ProgressBar, mmss, useToast } from "./ui";

type Status = "idle" | "correct" | "wrong";
type Phase = "loading" | "error" | "blocked" | "playing" | "result" | "streak";
const PRAISE = ["Amazing!", "Correct!", "Great job!", "Awesome!", "Nice one!", "Perfect!"];

export default function LessonPlayer({ start }: { start: StartParams }) {
  const router = useRouter();
  const toast = useToast();
  const { user, setUser, refresh } = useUser();
  const kind = start.kind;
  const requeueWrong = kind === "lesson" || kind === "practice";   // wrong answers come back at the end

  const [attempt, setAttempt] = useState(0);                 // bump to restart (retry / after a refill)
  const [phase, setPhase] = useState<Phase>("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [session, setSession] = useState<SessionData | null>(null);
  const [queue, setQueue] = useState<Exercise[]>([]);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);
  const [typo, setTypo] = useState(false);
  const [combo, setCombo] = useState(0);
  const [server, setServer] = useState<Pick<SessionState, "mistakes" | "correct_count" | "status">>(
    { mistakes: 0, correct_count: 0, status: "active" });
  const [answered, setAnswered] = useState(0);
  const [hearts, setHearts] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const [modal, setModal] = useState<null | "quit" | "hearts" | "failed">(null);
  const [result, setResult] = useState<CompleteResult | null>(null);
  const finishing = useRef(false);

  /* ---------------------------------------------------------------- load */
  useEffect(() => {
    let cancelled = false;
    setPhase("loading"); setIdx(0); setAnswer(null); setStatus("idle"); setCombo(0); setAnswered(0);
    setServer({ mistakes: 0, correct_count: 0, status: "active" }); setModal(null); finishing.current = false;
    api.startSession(start).then((s) => {
      if (cancelled) return;
      setSession(s); setQueue(s.exercises); setTimeLeft(s.time_limit_sec); setPhase("playing");
    }).catch((e: ApiError) => {
      if (cancelled) return;
      if (e.code === "out_of_hearts") { setHearts(0); setPhase("blocked"); setModal("hearts"); return; }
      setErrorMsg(e.message || "Could not load the lesson"); setPhase("error");
    });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt, kind, start.lesson_id, start.skill_id, start.unit_id]);

  useEffect(() => { if (user && hearts === null) setHearts(user.hearts); }, [user, hearts]);

  /* ------------------------------------------------------------- finishing */
  const finish = useCallback(async () => {
    if (finishing.current || !session) return;
    finishing.current = true;
    try {
      const res = await api.completeSession(session.id);
      setUser(res.user);
      setResult(res); setPhase("result"); play("finish");
      res.new_achievements.forEach((a) => toast({ icon: a.icon, title: `Achievement: ${a.title}`, text: `${a.description} · +${a.gem_reward} gems` }));
    } catch (e) {
      const err = e as ApiError;
      if (err.code === "challenge_failed") { setModal("failed"); return; }
      toast({ icon: "⚠️", title: "Could not save progress", text: err.message });
      router.push("/learn");
    }
  }, [session, setUser, toast, router]);

  // timed mode countdown
  useEffect(() => {
    if (phase !== "playing" || timeLeft === null || modal === "quit") return;
    if (timeLeft <= 0) { finish(); return; }
    const t = setTimeout(() => setTimeLeft((s) => (s === null ? s : s - 1)), 1000);
    return () => clearTimeout(t);
  }, [phase, timeLeft, finish, modal]);

  /* --------------------------------------------------------------- answers */
  const ex = queue[idx];

  const sync = (s: SessionState) => {
    setServer({ mistakes: s.mistakes, correct_count: s.correct_count, status: s.status });
    setHearts(s.hearts);
  };

  const showResult = (correct: boolean, res: Partial<AnswerResult>) => {
    setStatus(correct ? "correct" : "wrong");
    setCorrectAnswer(res.correct_answer ?? null);
    setTypo(!!res.typo);
    setAnswered((n) => n + 1);
    play(correct ? "correct" : "wrong");
    setCombo((c) => (correct ? c + 1 : 0));
    if (!correct && requeueWrong) setQueue((q) => [...q, ex]);
  };

  const handleError = (e: unknown) => {
    const err = e as ApiError;
    if (err.code === "out_of_hearts") { setHearts(0); setModal("hearts"); return; }
    if (err.code === "time_up") { finish(); return; }
    if (err.code === "challenge_failed") { setModal("failed"); return; }
    toast({ icon: "⚠️", title: "Connection problem", text: "Please try again." });
  };

  const check = async (forced?: string) => {
    if (!ex || !session || status !== "idle" || busy || (ex.type === "match_pairs" && forced === undefined)) return;
    const given = forced ?? answer;
    if (given === null) return;
    setBusy(true);
    try {
      const res = await api.answer(session.id, ex.id, given);
      sync(res);
      showResult(res.correct, res);
    } catch (e) { handleError(e); }
    finally { setBusy(false); }
  };

  // Match-pairs: each pair is verified by the server; the exercise counts once every pair is matched.
  const checkPair = async (leftId: number, rightId: string): Promise<boolean> => {
    if (!ex || !session) return false;
    try {
      const res = await api.pair(session.id, ex.id, leftId, rightId);
      sync(res);
      if (res.status === "failed") { play("wrong"); setModal("failed"); return false; }
      if (res.exercise_solved) showResult(true, {});
      return res.correct;
    } catch (e) { handleError(e); return false; }
  };

  const advance = () => {
    if (idx + 1 >= queue.length) { finish(); return; }
    setIdx(idx + 1); setAnswer(null); setStatus("idle"); setCorrectAnswer(null); setTypo(false);
  };

  const next = () => {
    if (status === "idle") return;
    if (server.status === "failed") { setModal("failed"); return; }
    if (kind === "lesson" && status === "wrong" && hearts === 0) { setModal("hearts"); return; }
    advance();
  };

  // Enter = Check / Continue
  const keyRef = useRef<() => void>(() => {});
  keyRef.current = () => (status === "idle" ? check() : next());
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Enter" || modal || phase !== "playing") return;
      e.preventDefault();
      keyRef.current();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [modal, phase]);

  const exit = () => { refresh(); router.push("/learn"); };
  const quit = () => { if (session && phase === "playing") api.abandonSession(session.id).catch(() => {}); exit(); };

  /* ---------------------------------------------------------------- render */
  if (phase === "loading") return <div className="lesson-shell"><div className="loading" style={{ flex: 1 }}>Loading…</div></div>;
  if (phase === "error") {
    return (
      <div className="lesson-shell"><div className="loading" style={{ flex: 1, textAlign: "center", gap: 16 }}>
        <div><p style={{ marginBottom: 16 }}>{errorMsg}</p><button className="btn btn-primary" onClick={exit}>Back to learn</button></div>
      </div></div>
    );
  }
  if (phase === "result" && result) {
    return <LessonComplete result={result} onContinue={() => (result.streak.increased ? setPhase("streak") : exit())} />;
  }
  if (phase === "streak" && result) return <StreakScreen user={result.user} onContinue={exit} />;

  const total = session?.exercises.length ?? 0;
  const progress = requeueWrong ? server.correct_count : answered;
  const lives = session?.max_mistakes != null ? session.max_mistakes + 1 - server.mistakes : 0;
  const canCheck = answer !== null && !busy;
  const praise = combo >= 3 ? `${combo} in a row!` : PRAISE[idx % PRAISE.length];

  return (
    <div className="lesson-shell">
      <div className="lesson-top">
        <button className="icon-btn" aria-label="Quit" onClick={() => setModal("quit")}>✕</button>
        <ProgressBar value={progress} max={total} streakGlow={combo >= 3} />
        {kind === "lesson" && <div className="hearts-chip"><Heart size={26} grey={hearts === 0} /> {hearts ?? "-"}</div>}
        {kind === "practice" && <div className="hearts-chip" title="No hearts are lost in practice"><Heart size={26} /> ∞</div>}
        {kind === "timed" && timeLeft !== null && <div className={`timer-chip ${timeLeft <= 15 ? "low" : ""}`}>⏱️ {mmss(Math.max(0, timeLeft))}</div>}
        {kind === "legendary" && <div className="timer-chip" style={{ color: "var(--purple-d)" }}>👑 ×{Math.max(0, lives)}</div>}
      </div>

      <div className="lesson-body">
        {ex && session && (
          <ExerciseView key={`${ex.id}-${idx}`} ex={ex} locked={status !== "idle"} status={status} correctAnswer={correctAnswer}
            onAnswer={setAnswer} onPair={checkPair} />
        )}
      </div>

      <div className={`lesson-footer ${status === "idle" ? "" : status}`}>
        <div className="footer-inner">
          {status === "idle" && (
            <>
              <button className="btn btn-secondary skip-btn" onClick={() => check("")} disabled={busy || !ex || phase !== "playing"}>Skip</button>
              <button className="btn btn-primary btn-lg check-btn" disabled={!canCheck} onClick={() => check()}>Check</button>
            </>
          )}
          {status === "correct" && (
            <>
              <div className="feedback">
                <div className="feedback-icon ok" aria-hidden>✓</div>
                <div>
                  <h3>{typo ? "You have a typo." : praise}</h3>
                  {typo && correctAnswer && <p>Correct answer: <b>{correctAnswer}</b></p>}
                </div>
              </div>
              <button className="btn btn-primary btn-lg check-btn" onClick={next}>Continue</button>
            </>
          )}
          {status === "wrong" && (
            <>
              <div className="feedback">
                <div className="feedback-icon bad" aria-hidden>✕</div>
                <div>
                  <h3>{correctAnswer ? "Correct solution:" : "Not quite!"}</h3>
                  <p>{correctAnswer ?? "Keep practising — you'll get it."}</p>
                </div>
              </div>
              <button className="btn btn-danger btn-lg check-btn" onClick={next}>Continue</button>
            </>
          )}
        </div>
      </div>

      {modal === "quit" && <QuitModal onStay={() => setModal(null)} onQuit={quit} />}
      {modal === "hearts" && user && (
        <OutOfHeartsModal user={user} onExit={quit}
          onRefilled={(u) => {
            setUser(u); setHearts(u.hearts); setModal(null);
            if (phase === "blocked") setAttempt((a) => a + 1);
            else if (status !== "idle") advance();
          }} />
      )}
      {modal === "failed" && (
        <FailedModal
          message={kind === "legendary" ? "Too many mistakes. Legendary challenges allow only one slip." : "Something went wrong."}
          onRetry={() => setAttempt((a) => a + 1)} onExit={exit} />
      )}
    </div>
  );
}
