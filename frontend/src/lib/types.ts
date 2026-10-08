// Mirrors the backend response models (backend/app/schemas.py).

export type WeekDay = { date: string; label: string; xp: number; active: boolean; is_today: boolean };

export type UserState = {
  id: number; username: string; display_name: string; avatar_color: string;
  total_xp: number; gems: number; hearts: number; max_hearts: number; next_heart_in_sec: number;
  streak: number; longest_streak: number; streak_active_today: boolean;
  daily_goal_xp: number; daily_xp: number; week: WeekDay[]; day_offset: number; timezone: string;
  refill_cost: number; league: string | null; dev_tools: boolean;
  course: { title: string; from_language: string; to_language: string } | null;
};

export type NodeState = "locked" | "available" | "completed" | "claimed";
export type SkillNodeData = {
  type: "skill"; id: number; title: string; icon: string; state: NodeState;
  lessons_total: number; lessons_completed: number; legendary: boolean; is_current: boolean;
  next_lesson_id: number | null;
};
export type ChestNodeData = { type: "chest"; id: number; title: string; state: NodeState; gems: number };
export type TrophyNodeData = { type: "trophy"; id: number; title: string; state: NodeState };
export type PathNodeData = SkillNodeData | ChestNodeData | TrophyNodeData;
export type UnitData = { id: number; title: string; description: string; color: string; position: number; nodes: PathNodeData[] };

export type ExerciseType = "multiple_choice" | "translate" | "match_pairs" | "fill_blank" | "type_answer";
export type Option = { id: string; text: string };
export type Exercise = {
  id: number; type: ExerciseType; prompt: string; source_text: string | null; hint: string | null;
  options: Option[] | null; pairs: { left: Option[]; right: Option[] } | null;
};

export type SessionKind = "lesson" | "practice" | "timed" | "legendary";
export type SessionData = {
  id: number; kind: SessionKind; title: string | null; lesson_id: number | null; skill_id: number | null;
  unit_id: number | null; time_limit_sec: number | null; max_mistakes: number | null; exercises: Exercise[];
};
export type SessionState = {
  mistakes: number; correct_count: number; status: "active" | "completed" | "failed" | "abandoned";
  remaining: number; hearts: number; next_heart_in_sec: number;
};
export type AnswerResult = SessionState & { correct: boolean; typo: boolean; correct_answer: string | null };
export type PairResult = SessionState & { correct: boolean; exercise_solved: boolean };

export type NewAchievement = { title: string; icon: string; description: string; gem_reward: number };
export type CompleteResult = {
  kind: SessionKind; xp_earned: number; gems_earned: number; correct_count: number; mistakes: number;
  accuracy: number; duration_sec: number; perfect: boolean; skill_completed: boolean;
  streak: { before: number; after: number; increased: boolean };
  daily_goal_reached: boolean; new_achievements: NewAchievement[]; user: UserState;
};

export type LeaderboardEntry = {
  rank: number; user_id: number; display_name: string; avatar_color: string; xp: number;
  is_me: boolean; zone: "promotion" | "demotion" | "safe";
};
export type Leaderboard = { league: string; league_color: string; ends_in_days: number; entries: LeaderboardEntry[] };

export type Badge = {
  id: number; code: string; title: string; description: string; icon: string; gem_reward: number;
  threshold: number; progress: number; unlocked: boolean; unlocked_at: string | null;
};
export type Profile = { user: UserState; joined: string; accuracy: number; achievements: Badge[]; stats: Record<string, number> };

export type Quest = { id: string; icon: string; title: string; progress: number; target: number; done: boolean };
