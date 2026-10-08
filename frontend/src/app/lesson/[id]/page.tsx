"use client";
import LessonPlayer from "@/components/LessonPlayer";

export default function LessonPage({ params }: { params: { id: string } }) {
  return <LessonPlayer start={{ kind: "lesson", lesson_id: Number(params.id) }} />;
}
