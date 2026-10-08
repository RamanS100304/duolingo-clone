"use client";
// Mock shop: gems are a pretend currency. Only the heart refill does something.
import { Gem, Heart } from "@/components/Icons";
import { useToast } from "@/components/ui";
import { api } from "@/lib/api";
import { useUser } from "@/lib/user-context";

export default function ShopPage() {
  const { user, setUser } = useUser();
  const toast = useToast();
  if (!user) return <div className="loading">Loading…</div>;
  const full = user.hearts >= user.max_hearts;
  const refill = async () => {
    try { setUser(await api.refillHearts()); toast({ icon: "❤️", title: "Hearts refilled!" }); }
    catch (e) { toast({ icon: "⚠️", title: (e as Error).message }); }
  };
  const soon = (what: string) => toast({ icon: "🚧", title: what, text: "Coming soon!" });
  return (
    <div className="page">
      <div className="row" style={{ justifyContent: "space-between", marginBottom: 8 }}>
        <h1 className="page-title" style={{ margin: 0 }}>Shop</h1>
        <span className="stat" style={{ color: "var(--blue)", cursor: "default" }}><Gem /> {user.gems}</span>
      </div>

      <h2 className="section-title">Hearts</h2>
      <div className="shop-row">
        <Heart size={56} />
        <div style={{ flex: 1 }}><b>Refill Hearts</b><p className="muted">Get full hearts so you can worry less about making mistakes in a lesson.</p></div>
        <button className="btn btn-secondary shop-btn" onClick={refill} disabled={full || user.gems < user.refill_cost}>
          {full ? "Full" : <><Gem size={22} /> {user.refill_cost}</>}
        </button>
      </div>

      <h2 className="section-title">Power-ups</h2>
      <div className="shop-row">
        <span style={{ fontSize: 50 }}>🧊</span>
        <div style={{ flex: 1 }}><b>Streak Freeze <span className="soon">Soon</span></b><p className="muted">Keeps your streak in place for one full day of inactivity.</p></div>
        <button className="btn btn-secondary shop-btn" onClick={() => soon("Streak Freeze")}><Gem size={22} /> 200</button>
      </div>

      <h2 className="section-title">Super</h2>
      <div className="shop-row super">
        <span style={{ fontSize: 50 }}>🚀</span>
        <div style={{ flex: 1 }}><b>Try Super for free <span className="soon">Soon</span></b><p>Unlimited hearts, no ads and personalised practice.</p></div>
        <button className="btn btn-secondary shop-btn" onClick={() => soon("Super subscription")}>Learn more</button>
      </div>
    </div>
  );
}
