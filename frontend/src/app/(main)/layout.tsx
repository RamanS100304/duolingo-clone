"use client";
import { RightRail, Sidebar, StatsBar } from "@/components/Chrome";
import { useUser } from "@/lib/user-context";

// Shell used by every page except the full-screen lesson player.
export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { error } = useUser();
  return (
    <>
      <Sidebar />
      <div className="shell">
        <main className="shell-main">
          <div className="topbar"><StatsBar /></div>
          {error && <div className="error-banner">{error}</div>}
          {children}
        </main>
        <RightRail />
      </div>
    </>
  );
}
