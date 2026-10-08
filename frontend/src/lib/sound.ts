// Tiny WebAudio sound effects (no audio files needed). Can be muted in Settings.
let ctx: AudioContext | null = null;

export const soundEnabled = () => {
  try { return localStorage.getItem("sound") !== "off"; } catch { return true; }
};

function tone(freq: number, start: number, dur: number, type: OscillatorType = "sine", vol = 0.12) {
  if (!ctx) return;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type; osc.frequency.value = freq;
  gain.gain.setValueAtTime(vol, ctx.currentTime + start);
  gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + start + dur);
  osc.connect(gain).connect(ctx.destination);
  osc.start(ctx.currentTime + start); osc.stop(ctx.currentTime + start + dur);
}

export function play(kind: "correct" | "wrong" | "finish" | "tap") {
  if (typeof window === "undefined" || !soundEnabled()) return;
  try {
    ctx = ctx ?? new (window.AudioContext || (window as any).webkitAudioContext)();
    if (kind === "correct") { tone(660, 0, 0.12); tone(880, 0.1, 0.2); }
    if (kind === "wrong") { tone(220, 0, 0.18, "sawtooth", 0.08); tone(160, 0.15, 0.25, "sawtooth", 0.08); }
    if (kind === "finish") [523, 659, 784, 1046].forEach((f, i) => tone(f, i * 0.12, 0.25, "triangle"));
    if (kind === "tap") tone(440, 0, 0.05, "sine", 0.06);
  } catch { /* audio blocked by the browser: ignore */ }
}

/** Read an English phrase aloud with the browser's built-in text-to-speech. */
export function speak(text: string) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US"; u.rate = 0.9;
  window.speechSynthesis.speak(u);
}
