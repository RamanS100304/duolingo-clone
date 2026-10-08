"use client";
import { useCallback, useEffect, useState } from "react";
import PathNode from "@/components/PathNode";
import { useToast } from "@/components/ui";
import { api } from "@/lib/api";
import type { UnitData } from "@/lib/types";
import { useUser } from "@/lib/user-context";

// Horizontal wiggle (px) that gives the path its winding look.
const OFFSETS = [0, -44, -70, -44, 0, 44, 70, 44];

export default function LearnPage() {
  const [units, setUnits] = useState<UnitData[] | null>(null);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const { refresh, user } = useUser();
  const toast = useToast();

  const load = useCallback(() => api.path().then((p) => setUnits(p.units)), []);

  useEffect(() => {
    load().catch(() => setUnits(null));
    refresh();   // pick up streak/hearts changed elsewhere
  }, [load, refresh, user?.id]);

  if (!units) return <div className="loading">Loading your path…</div>;

  return (
    <div className="page" onClick={() => setOpenKey(null)}>
      {units.map((unit) => (
        <section key={unit.id}>
          <div className="unit-banner" style={{ background: unit.color }}>
            <div>
              <div className="kicker">Section 1, Unit {unit.position}</div>
              <h2>{unit.title}</h2>
              <p className="hi">{unit.description}</p>
            </div>
            <button className="banner-btn" onClick={(e) => { e.stopPropagation(); toast({ icon: "📖", title: "Guidebook", text: "Coming soon!" }); }}>
              📖 Guidebook
            </button>
          </div>
          <div className="path">
            {unit.nodes.map((node, i) => {
              const key = `${node.type}-${node.id}`;
              return (
                // stop propagation so clicking a node doesn't immediately close its own popover.
                // An open node sits above the sticky unit banners (z-index 5) but below the phone top bar (10).
                <div key={key} onClick={(e) => e.stopPropagation()} style={{ position: "relative", zIndex: openKey === key ? 8 : 1 }}>
                  <PathNode node={node} color={unit.color} unitId={unit.id} offset={OFFSETS[i % OFFSETS.length]}
                    open={openKey === key}
                    onToggle={() => setOpenKey(openKey === key ? null : key)}
                    onClose={() => setOpenKey(null)}
                    onChanged={() => { load(); }} />
                </div>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
