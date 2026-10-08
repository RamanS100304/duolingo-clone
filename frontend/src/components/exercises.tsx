"use client";
// The five exercise types. Each reports the learner's current answer via onAnswer(string | null)
// (null = nothing chosen yet). The LessonPlayer owns checking and feedback.
import { useEffect, useRef, useState } from "react";
import { play, speak } from "@/lib/sound";
import type { Exercise } from "@/lib/types";
import Mascot from "./Mascot";

export type ExProps = {
  ex: Exercise;
  locked: boolean;                           // true once the answer has been checked
  status: "idle" | "correct" | "wrong";
  correctAnswer: string | null;              // known only after checking
  onAnswer: (answer: string | null) => void;
  onPair?: (leftId: number, rightId: string) => Promise<boolean>;   // match-pairs: server verifies each pair
};

const isEnglish = (s: string | null) => !!s && /^[A-Za-z]/.test(s);

function Speaker({ text }: { text: string }) {
  return <button className="speak-btn" onClick={() => speak(text)} aria-label="Listen" type="button">🔊</button>;
}

/** Keys 1-n pick an option (as on Duolingo). */
function useNumberKeys(options: { text: string }[] | null, pick: (t: string) => void) {
  const pickRef = useRef(pick);
  pickRef.current = pick;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const n = parseInt(e.key, 10);
      if (n >= 1 && options && n <= options.length) pickRef.current(options[n - 1].text);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [options]);
}

/* ------------------------------------------------------- multiple choice */
export function MultipleChoice({ ex, locked, status, correctAnswer, onAnswer }: ExProps) {
  const [sel, setSel] = useState<string | null>(null);
  const pick = (t: string) => { if (locked) return; play("tap"); setSel(t); onAnswer(t); };
  useNumberKeys(ex.options, pick);

  return (
    <div className="exercise">
      <h1>{ex.prompt}</h1>
      <div className="big-word">
        {isEnglish(ex.source_text) && <Speaker text={ex.source_text!} />}
        <span className={isEnglish(ex.source_text) ? "" : "hi"}>{ex.source_text}</span>
      </div>
      {ex.options!.map((o, i) => {
        let cls = sel === o.text ? "selected" : "";
        if (locked && correctAnswer && o.text === correctAnswer) cls = "correct";
        else if (locked && status === "wrong" && sel === o.text) cls = "wrong";
        return (
          <button key={o.id} className={`choice ${cls} ${isEnglish(o.text) ? "" : "hi"}`} onClick={() => pick(o.text)} disabled={locked}>
            <span className="key">{i + 1}</span>{o.text}
          </button>
        );
      })}
    </div>
  );
}

/* -------------------------------------------------------- translate (word bank) */
export function Translate({ ex, locked, onAnswer }: ExProps) {
  const [picked, setPicked] = useState<number[]>([]);   // indexes into ex.options, in tap order
  const opts = ex.options!;
  const update = (next: number[]) => {
    setPicked(next);
    onAnswer(next.length ? next.map((i) => opts[i].text).join(" ") : null);
  };
  const add = (i: number) => { if (!locked && !picked.includes(i)) { play("tap"); update([...picked, i]); } };
  const remove = (i: number) => { if (!locked) update(picked.filter((p) => p !== i)); };

  return (
    <div className="exercise">
      <h1>{ex.prompt}</h1>
      <div className="bubble-row">
        <Mascot size={86} />
        <div className="bubble hi"><span className="hint-word">{ex.source_text}</span></div>
      </div>
      <div className="answer-line">
        {picked.map((i) => <button key={i} className="tile" onClick={() => remove(i)}>{opts[i].text}</button>)}
      </div>
      <div className="bank">
        {opts.map((o, i) => (
          <button key={o.id} className={`tile ${picked.includes(i) ? "ghost" : ""}`} onClick={() => add(i)}>{o.text}</button>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------- match pairs */
export function MatchPairs({ ex, locked, onAnswer, onPair }: ExProps) {
  const { left, right } = ex.pairs!;
  const [selL, setSelL] = useState<string | null>(null);
  const [selR, setSelR] = useState<string | null>(null);
  const [matched, setMatched] = useState<string[]>([]);          // ids of matched tiles (both sides)
  const [bad, setBad] = useState<{ l: string; r: string } | null>(null);
  const busy = useRef(false);

  useEffect(() => { onAnswer(null); }, []);   // eslint-disable-line react-hooks/exhaustive-deps

  const tryPair = async (l: string, r: string) => {
    busy.current = true;
    try {
      const ok = onPair ? await onPair(Number(l), r) : false;
      if (ok) { play("correct"); setMatched((m) => [...m, l, r]); }
      else { play("wrong"); setBad({ l, r }); setTimeout(() => setBad(null), 600); }
    } finally { busy.current = false; setSelL(null); setSelR(null); }
  };

  const clickL = (id: string) => {
    if (locked || busy.current || matched.includes(id)) return;
    play("tap"); speakLeft(id); setSelL(id);
    if (selR !== null) tryPair(id, selR);
  };
  const clickR = (id: string) => {
    if (locked || busy.current || matched.includes(id)) return;
    play("tap"); setSelR(id);
    if (selL !== null) tryPair(selL, id);
  };
  const speakLeft = (id: string) => { const t = left.find((x) => x.id === id)?.text; if (t) speak(t); };

  // keys 1-5 pick a left tile, 6-9 and 0 a right tile (same numbering as the tile badges)
  const keyRef = useRef<(n: number) => void>(() => {});
  keyRef.current = (n) => {
    if (n >= 1 && n <= left.length) clickL(left[n - 1].id);
    else if (n > left.length && n <= left.length + right.length) clickR(right[n - left.length - 1].id);
  };
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!/^[0-9]$/.test(e.key)) return;
      keyRef.current(e.key === "0" ? 10 : Number(e.key));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const cls = (side: "l" | "r", id: string) => {
    if (matched.includes(id)) return "matched";
    if (bad && ((side === "l" && bad.l === id) || (side === "r" && bad.r === id))) return "error";
    if ((side === "l" ? selL : selR) === id) return "selected";
    return "";
  };

  return (
    <div className="exercise">
      <h1>{ex.prompt}</h1>
      <div className="match-grid">
        {left.map((l, i) => {
          const r = right[i];
          return [
            <button key={`l${l.id}`} className={`tile ${cls("l", l.id)}`} onClick={() => clickL(l.id)}>
              <span className="tile-key">{i + 1}</span>{l.text}</button>,
            <button key={`r${r.id}`} className={`tile hi ${cls("r", r.id)}`} onClick={() => clickR(r.id)}>
              <span className="tile-key">{i + 1 + left.length}</span>{r.text}</button>,
          ];
        })}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------- fill blank */
export function FillBlank({ ex, locked, status, correctAnswer, onAnswer }: ExProps) {
  const [sel, setSel] = useState<string | null>(null);
  const pick = (t: string) => { if (locked) return; play("tap"); setSel(t); onAnswer(t); };
  useNumberKeys(ex.options, pick);
  const [before, after] = (ex.source_text || "").split("____");
  return (
    <div className="exercise">
      <h1>{ex.prompt}</h1>
      {ex.hint && <p className="hi muted" style={{ fontSize: 18 }}>{ex.hint}</p>}
      <div className="fill-sentence">
        {before}<span className="blank-slot">{sel ?? " "}</span>{after}
      </div>
      {ex.options!.map((o, i) => {
        let cls = sel === o.text ? "selected" : "";
        if (locked && correctAnswer && o.text === correctAnswer) cls = "correct";
        else if (locked && status === "wrong" && sel === o.text) cls = "wrong";
        return (
          <button key={o.id} className={`choice ${cls}`} onClick={() => pick(o.text)} disabled={locked}>
            <span className="key">{i + 1}</span>{o.text}
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------ type answer */
export function TypeAnswer({ ex, locked, onAnswer }: ExProps) {
  const [val, setVal] = useState("");
  return (
    <div className="exercise">
      <h1>{ex.prompt}</h1>
      <div className="bubble-row">
        <Mascot size={86} />
        <div className="bubble hi"><span className="hint-word">{ex.source_text}</span></div>
      </div>
      <textarea className="type-input" autoFocus placeholder="अंग्रेज़ी में लिखें…" value={val} disabled={locked}
        onChange={(e) => { setVal(e.target.value); onAnswer(e.target.value.trim() || null); }}
        autoCapitalize="off" autoCorrect="off" spellCheck={false} />
    </div>
  );
}

export function ExerciseView(props: ExProps) {
  switch (props.ex.type) {
    case "multiple_choice": return <MultipleChoice {...props} />;
    case "translate": return <Translate {...props} />;
    case "match_pairs": return <MatchPairs {...props} />;
    case "fill_blank": return <FillBlank {...props} />;
    case "type_answer": return <TypeAnswer {...props} />;
  }
}
