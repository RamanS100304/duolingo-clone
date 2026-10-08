// "Kero" - our own original frog mascot (not a copy of any existing character).
type Mood = "happy" | "sad" | "cheer";

export default function Mascot({ size = 120, mood = "happy", className = "" }: { size?: number; mood?: Mood; className?: string }) {
  const mouth =
    mood === "sad"
      ? <path d="M44 80 Q60 68 76 80" stroke="#2b6b00" strokeWidth="4" fill="none" strokeLinecap="round" />
      : <path d="M42 74 Q60 94 78 74 Q60 80 42 74z" fill="#2b6b00" stroke="#2b6b00" strokeWidth="3" strokeLinejoin="round" />;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" className={className} role="img" aria-label="Kero the frog">
      {mood === "cheer" && (
        <g stroke="#58a700" strokeWidth="9" strokeLinecap="round">
          <line x1="22" y1="70" x2="8" y2="36" /><line x1="98" y1="70" x2="112" y2="36" />
        </g>
      )}
      <ellipse cx="60" cy="72" rx="42" ry="36" fill="#58cc02" stroke="#58a700" strokeWidth="4" />
      <ellipse cx="60" cy="84" rx="26" ry="20" fill="#b5ee7a" />
      <circle cx="38" cy="38" r="17" fill="#58cc02" stroke="#58a700" strokeWidth="4" />
      <circle cx="82" cy="38" r="17" fill="#58cc02" stroke="#58a700" strokeWidth="4" />
      <circle cx="38" cy="38" r="12" fill="#fff" /><circle cx="82" cy="38" r="12" fill="#fff" />
      <circle cx={mood === "sad" ? 38 : 40} cy={mood === "sad" ? 42 : 39} r="6" fill="#1f2937" />
      <circle cx={mood === "sad" ? 82 : 84} cy={mood === "sad" ? 42 : 39} r="6" fill="#1f2937" />
      <circle cx="42" cy="36" r="2" fill="#fff" /><circle cx="86" cy="36" r="2" fill="#fff" />
      {mood === "sad" && <path d="M30 22 L46 28 M90 22 L74 28" stroke="#58a700" strokeWidth="3.500" strokeLinecap="round" />}
      <circle cx="30" cy="68" r="6" fill="#ff8fa3" opacity=".6" /><circle cx="90" cy="68" r="6" fill="#ff8fa3" opacity=".6" />
      {mouth}
      {mood === "sad" && <path d="M92 52 q4 8 0 12 q-4 -4 0 -12z" fill="#84d8ff" />}
    </svg>
  );
}
