"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

/* ----------------------------------------------------------------- Modal */
export function Modal({ children, onClose }: { children: React.ReactNode; onClose?: () => void }) {
  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">{children}</div>
    </div>
  );
}

/* ----------------------------------------------------------------- Toasts */
type ToastInput = { icon: string; title: string; text?: string };
type ToastItem = ToastInput & { id: number };
const ToastCtx = createContext<(t: ToastInput) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const push = useCallback((t: ToastInput) => {
    const id = Date.now() + Math.random();
    setItems((cur) => [...cur, { ...t, id }]);
    setTimeout(() => setItems((cur) => cur.filter((x) => x.id !== id)), 4000);
  }, []);
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="toasts" aria-live="polite">
        {items.map((t) => (
          <div className="toast" key={t.id}>
            <div className="t-icon">{t.icon}</div>
            <div><b>{t.title}</b>{t.text && <span>{t.text}</span>}</div>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

/* --------------------------------------------------------------- Confetti */
export function Confetti({ count = 60 }: { count?: number }) {
  const [pieces, setPieces] = useState<React.CSSProperties[]>([]);
  // Random values are generated after mount so server and client HTML match.
  useEffect(() => {
    const colors = ["#58cc02", "#1cb0f6", "#ffc800", "#ff4b4b", "#ce82ff", "#ff9600"];
    setPieces(Array.from({ length: count }, () => ({
      left: `${Math.random() * 100}%`, background: colors[Math.floor(Math.random() * colors.length)],
      animationDuration: `${2.5 + Math.random() * 2.5}s`, animationDelay: `${Math.random() * 1.2}s`,
    })));
  }, [count]);
  return <>{pieces.map((s, i) => <span key={i} className="confetti" style={s} />)}</>;
}

/* ----------------------------------------------------------------- helpers */
export const mmss = (sec: number) => `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, "0")}`;

export function ProgressBar({ value, max, gold, streakGlow }: { value: number; max: number; gold?: boolean; streakGlow?: boolean }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className={`progress ${gold ? "gold" : ""} ${streakGlow ? "glow" : ""}`} role="progressbar" aria-valuenow={value} aria-valuemax={max}>
      <div className="progress-fill" style={{ width: `${pct}%` }} />
    </div>
  );
}
