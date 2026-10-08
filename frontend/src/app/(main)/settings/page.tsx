"use client";
import { useEffect, useState } from "react";
import { useToast } from "@/components/ui";
import { api } from "@/lib/api";
import { useUser } from "@/lib/user-context";

const GOALS = [{ xp: 10, name: "Casual" }, { xp: 20, name: "Regular" }, { xp: 30, name: "Serious" }, { xp: 50, name: "Intense" }];

export default function SettingsPage() {
  const { user, setUser } = useUser();
  const toast = useToast();
  const [dark, setDark] = useState(false);
  const [sound, setSound] = useState(true);
  const [name, setName] = useState("");

  useEffect(() => {
    setDark(document.documentElement.dataset.theme === "dark");
    try { setSound(localStorage.getItem("sound") !== "off"); } catch { /* storage blocked */ }
  }, []);
  useEffect(() => { if (user) setName(user.display_name); }, [user?.display_name]); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
    try { localStorage.setItem("theme", next ? "dark" : "light"); } catch { /* ignore */ }
  };
  const toggleSound = () => {
    setSound(!sound);
    try { localStorage.setItem("sound", sound ? "off" : "on"); } catch { /* ignore */ }
  };
  const setGoal = async (xp: number) => { setUser(await api.updateSettings({ daily_goal_xp: xp })); toast({ icon: "🎯", title: `Daily goal set to ${xp} XP` }); };
  const saveName = async () => {
    if (!name.trim()) return;
    setUser(await api.updateSettings({ display_name: name }));
    toast({ icon: "✏️", title: "Name updated" });
  };
  const nextDay = async () => { const u = await api.advanceDay(1); setUser(u); toast({ icon: "📅", title: "Simulated a new day", text: `Streak is now ${u.streak}. Do a lesson to continue it!` }); };
  const reset = async (mode: "demo" | "empty") => {
    setUser(await api.reset(mode));
    toast({ icon: "♻️", title: mode === "demo" ? "Demo learner restored" : "Progress cleared" });
  };
  const soon = (what: string) => toast({ icon: "🚧", title: what, text: "Coming soon!" });

  if (!user) return <div className="loading">Loading…</div>;

  return (
    <div className="page">
      <h1 className="page-title">Settings</h1>

      <h2 className="section-title" style={{ marginTop: 0 }}>Account</h2>
      <div className="settings-row">
        <div><div>Time zone</div><span className="muted" style={{ fontSize: 14 }}>Your streak and daily goal reset at midnight here</span></div>
        <b style={{ color: "var(--heading)" }}>{user.timezone}</b>
      </div>
      <div className="settings-row">
        <label htmlFor="dn">Display name</label>
        <div className="row">
          <input id="dn" value={name} onChange={(e) => setName(e.target.value)} maxLength={40}
            style={{ padding: "10px 12px", border: "2px solid var(--border)", borderRadius: 12, background: "var(--hover)", fontWeight: 700 }} />
          <button className="btn btn-secondary" style={{ minWidth: 0 }} onClick={saveName}>Save</button>
        </div>
      </div>
      <div className="settings-row">
        <div><div>Daily goal</div><span className="muted" style={{ fontSize: 14 }}>Currently {user.daily_goal_xp} XP per day</span></div>
        <div className="seg">
          {GOALS.map((g) => <button key={g.xp} className={user.daily_goal_xp === g.xp ? "on" : ""} onClick={() => setGoal(g.xp)}>{g.xp} XP · {g.name}</button>)}
        </div>
      </div>

      <h2 className="section-title">Preferences</h2>
      <div className="settings-row"><span>Dark mode</span><button className={`switch ${dark ? "on" : ""}`} onClick={toggleTheme} aria-label="Dark mode" /></div>
      <div className="settings-row"><span>Sound effects</span><button className={`switch ${sound ? "on" : ""}`} onClick={toggleSound} aria-label="Sound effects" /></div>
      <div className="settings-row"><span>Speaking exercises <span className="soon">Soon</span></span><button className="switch" onClick={() => soon("Speaking exercises")} aria-label="Speaking" /></div>

      <h2 className="section-title">Coming soon</h2>
      {["Super subscription", "Friends & social", "Change course", "Notifications"].map((x) => (
        <div className="settings-row" key={x}><span>{x} <span className="soon">Soon</span></span>
          <button className="btn btn-secondary" style={{ minWidth: 0 }} onClick={() => soon(x)}>Open</button></div>
      ))}

      {user.dev_tools && (
        <>
          <h2 className="section-title">Testing tools</h2>
          <p className="muted" style={{ marginBottom: 8, fontSize: 15 }}>Handy for reviewers: simulate the passing of time and reset the demo learner.</p>
          <div className="settings-row">
            <div><div>Simulate next day</div><span className="muted" style={{ fontSize: 14 }}>Skip a day (day offset: +{user.day_offset}). Skip two without a lesson to lose the streak.</span></div>
            <button className="btn btn-orange" style={{ minWidth: 0 }} onClick={nextDay}>+1 day</button>
          </div>
          <div className="settings-row">
            <div><div>Restore demo learner</div><span className="muted" style={{ fontSize: 14 }}>Back to the sample progress (2 skills done, 4-day streak), dated from today.</span></div>
            <button className="btn btn-blue" style={{ minWidth: 0 }} onClick={() => reset("demo")}>Restore</button>
          </div>
          <div className="settings-row">
            <div><div>Start from scratch</div><span className="muted" style={{ fontSize: 14 }}>Wipes XP, streak, hearts, badges and skills for this learner.</span></div>
            <button className="btn btn-danger" style={{ minWidth: 0 }} onClick={() => reset("empty")}>Reset</button>
          </div>
        </>
      )}
    </div>
  );
}
