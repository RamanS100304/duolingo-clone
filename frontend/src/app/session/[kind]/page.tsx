"use client";
// /session/practice[?skill=ID | ?unit=ID] | /session/timed | /session/legendary?skill=ID
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import LessonPlayer from "@/components/LessonPlayer";

const KINDS = ["practice", "timed", "legendary"] as const;

function Inner({ kind }: { kind: string }) {
  const params = useSearchParams();
  const num = (k: string) => (params.get(k) ? Number(params.get(k)) : undefined);
  const k = (KINDS as readonly string[]).includes(kind) ? (kind as (typeof KINDS)[number]) : "practice";
  return <LessonPlayer start={{ kind: k, skill_id: num("skill"), unit_id: num("unit") }} />;
}

export default function SessionPage({ params }: { params: { kind: string } }) {
  return <Suspense fallback={null}><Inner kind={params.kind} /></Suspense>;
}
