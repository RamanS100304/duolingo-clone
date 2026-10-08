"use client";
// One stop on the learning path: a skill (with progress ring + crowns), a treasure chest or a unit trophy.
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import type { ChestNodeData, PathNodeData, SkillNodeData, TrophyNodeData } from "@/lib/types";
import { useUser } from "@/lib/user-context";
import { ChestIcon, TrophyIcon } from "./Icons";
import Mascot from "./Mascot";
import { useToast } from "./ui";

const R = 50;                       // ring radius
const CIRC = 2 * Math.PI * R;

function darken(hex: string) {      // darker shade for the 3D button edge
  const n = parseInt(hex.slice(1), 16);
  const f = (v: number) => Math.max(0, Math.floor(v * 0.78));
  return `rgb(${f(n >> 16)}, ${f((n >> 8) & 255)}, ${f(n & 255)})`;
}

type Common = { color: string; unitId: number; offset: number; open: boolean; onToggle: () => void; onClose: () => void; onChanged: () => void };

export default function PathNode({ node, ...rest }: Common & { node: PathNodeData }) {
  const style = { ["--off" as string]: `${rest.offset}px`, ["--node" as string]: rest.color, ["--node-d" as string]: darken(rest.color) };
  const current = node.type === "skill" && node.is_current;
  return (
    <div className={`node-wrap ${node.type} ${current ? "current" : ""}`} style={style}>
      {node.type === "skill" && <SkillNode node={node} {...rest} />}
      {node.type === "chest" && <ChestNode node={node} {...rest} />}
      {node.type === "trophy" && <TrophyNode node={node} {...rest} />}
    </div>
  );
}

/* ---------------------------------------------------------------- skill */
function SkillNode({ node: skill, color, open, onToggle, onClose }: Common & { node: SkillNodeData }) {
  const router = useRouter();
  const { state, lessons_completed: done, lessons_total: total } = skill;
  const completed = state === "completed";
  const fraction = completed ? 1 : done / total;
  const go = (url: string) => { onClose(); router.push(url); };

  return (
    <>
      {state !== "locked" && (
        <svg className="node-ring" viewBox="0 0 110 110" aria-hidden>
          <circle cx="55" cy="55" r={R} fill="none" stroke="var(--border)" strokeWidth="8" />
          <circle cx="55" cy="55" r={R} fill="none" strokeWidth="8" strokeLinecap="round"
            stroke={completed ? "var(--yellow)" : color}
            strokeDasharray={`${CIRC * fraction} ${CIRC}`} transform="rotate(-90 55 55)" />
        </svg>
      )}

      {skill.is_current && !open && <div className="start-bubble">{done > 0 ? "CONTINUE" : "START"}</div>}
      {skill.is_current && (
        <div className="path-mascot float" style={{ left: -96, top: 14 }}><Mascot size={78} mood="happy" /></div>
      )}

      <button className={`skill-btn ${state === "locked" ? "locked" : completed ? "done" : "available"}`}
        onClick={onToggle} aria-label={`${skill.title} (${state})`}>
        {state === "locked" ? "🔒" : completed ? (skill.legendary ? "👑" : "⭐") : skill.icon}
        {state !== "locked" && <span className="crown-badge">👑 {completed ? total : done}</span>}
      </button>

      {open && (
        <div className={`node-popover ${state === "locked" ? "locked" : ""}`}
          style={state === "locked" ? undefined : { background: completed ? "var(--yellow-d)" : color }}>
          <h3>{skill.title}</h3>
          {state === "locked" && <p>Complete all levels above to unlock this!</p>}
          {state === "available" && (
            <>
              <p>Lesson {done + 1} of {total}</p>
              <button className="btn" style={{ color }} onClick={() => go(`/lesson/${skill.next_lesson_id}`)}>
                Start +10 XP
              </button>
            </>
          )}
          {completed && (
            <>
              <p>Skill complete — all {total} lessons done!</p>
              <button className="btn" style={{ color: "var(--yellow-d)" }} onClick={() => go(`/session/practice?skill=${skill.id}`)}>
                Practice +5 XP
              </button>
              {skill.legendary
                ? <p style={{ margin: "10px 0 0", textAlign: "center" }}>👑 Legendary achieved</p>
                : <button className="btn" style={{ color: "var(--purple-d)" }} onClick={() => go(`/session/legendary?skill=${skill.id}`)}>
                    👑 Legendary +40 XP
                  </button>}
            </>
          )}
        </div>
      )}
    </>
  );
}

/* ---------------------------------------------------------------- chest */
function ChestNode({ node, unitId, onChanged }: Common & { node: ChestNodeData }) {
  const { setUser } = useUser();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const open = async () => {
    if (node.state === "locked") { toast({ icon: "🔒", title: "Treasure chest", text: "Keep going! Finish the skill above to open it." }); return; }
    if (node.state === "claimed" || busy) return;
    setBusy(true);
    try {
      const r = await api.openChest(unitId);
      setUser(r.user);
      toast({ icon: "💎", title: `+${r.gems_earned} gems!`, text: "You opened a treasure chest." });
      onChanged();
    } catch (e) { toast({ icon: "⚠️", title: (e as Error).message }); }
    finally { setBusy(false); }
  };
  return (
    <button className={`chest-btn ${node.state}`} onClick={open} aria-label={`Treasure chest (${node.state})`}>
      <ChestIcon size={84} grey={node.state === "locked"} open={node.state === "claimed"} />
    </button>
  );
}

/* --------------------------------------------------------------- trophy */
function TrophyNode({ node, unitId, open, onToggle, onClose }: Common & { node: TrophyNodeData }) {
  const router = useRouter();
  const done = node.state === "completed";
  return (
    <>
      <button className={`chest-btn trophy ${node.state}`} onClick={onToggle} aria-label={`${node.title} (${node.state})`}>
        <TrophyIcon size={80} grey={!done} />
      </button>
      {open && (
        <div className={`node-popover ${done ? "" : "locked"}`} style={done ? { background: "var(--yellow-d)" } : undefined}>
          <h3>{node.title}</h3>
          {done ? (
            <>
              <p>Unit complete! Review it to keep it fresh.</p>
              <button className="btn" style={{ color: "var(--yellow-d)" }} onClick={() => { onClose(); router.push(`/session/practice?unit=${unitId}`); }}>
                Review +5 XP
              </button>
            </>
          ) : <p>Complete every skill in this unit to earn the trophy.</p>}
        </div>
      )}
    </>
  );
}
