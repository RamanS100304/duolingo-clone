"""Request and response models (they also generate the OpenAPI docs at /docs)."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

SessionKind = Literal["lesson", "practice", "timed", "legendary"]


# ------------------------------------------------------------------- requests
class SettingsIn(BaseModel):
    daily_goal_xp: int | None = Field(default=None, ge=5, le=100)
    display_name: str | None = Field(default=None, min_length=1, max_length=40)
    timezone: str | None = Field(default=None, max_length=64)


class SessionStartIn(BaseModel):
    kind: SessionKind
    lesson_id: int | None = None
    skill_id: int | None = None
    unit_id: int | None = None

    @model_validator(mode="after")
    def _required_ids(self):
        if self.kind == "lesson" and self.lesson_id is None:
            raise ValueError("lesson_id is required for a lesson")
        if self.kind == "legendary" and self.skill_id is None:
            raise ValueError("skill_id is required for a legendary challenge")
        return self


class AnswerIn(BaseModel):
    exercise_id: int
    answer: str = Field(default="", max_length=500)      # "" = skipped


class PairIn(BaseModel):
    exercise_id: int
    left_id: int
    right_id: str = Field(max_length=64)


class DayIn(BaseModel):
    days: int = Field(default=1, ge=1, le=30)


class ResetIn(BaseModel):
    mode: Literal["demo", "empty"] = "demo"


# ------------------------------------------------------------------ responses
class WeekDay(BaseModel):
    date: str
    label: str
    xp: int
    active: bool
    is_today: bool


class CourseOut(BaseModel):
    title: str
    from_language: str
    to_language: str


class UserState(BaseModel):
    id: int
    username: str
    display_name: str
    avatar_color: str
    total_xp: int
    gems: int
    hearts: int
    max_hearts: int
    next_heart_in_sec: int
    streak: int
    longest_streak: int
    streak_active_today: bool
    daily_goal_xp: int
    daily_xp: int
    week: list[WeekDay]
    day_offset: int
    timezone: str
    refill_cost: int
    league: str | None
    dev_tools: bool
    course: CourseOut | None


class PathNode(BaseModel):
    type: Literal["skill", "chest", "trophy"]
    id: int
    title: str
    state: Literal["locked", "available", "completed", "claimed"]
    icon: str | None = None
    lessons_total: int | None = None
    lessons_completed: int | None = None
    legendary: bool = False
    is_current: bool = False
    next_lesson_id: int | None = None
    gems: int | None = None


class UnitOut(BaseModel):
    id: int
    title: str
    description: str
    color: str
    position: int
    nodes: list[PathNode]


class PathOut(BaseModel):
    units: list[UnitOut]


class ChestOut(BaseModel):
    gems_earned: int
    user: UserState


class OptionOut(BaseModel):
    id: str
    text: str


class PairsOut(BaseModel):
    left: list[OptionOut]
    right: list[OptionOut]


class ExerciseOut(BaseModel):
    id: int
    type: str
    prompt: str
    source_text: str | None
    hint: str | None
    options: list[OptionOut] | None
    pairs: PairsOut | None


class SessionOut(BaseModel):
    id: int
    kind: SessionKind
    title: str | None
    lesson_id: int | None
    skill_id: int | None
    unit_id: int | None
    time_limit_sec: int | None
    max_mistakes: int | None
    exercises: list[ExerciseOut]


class SessionState(BaseModel):
    mistakes: int
    correct_count: int
    status: str
    remaining: int
    hearts: int
    next_heart_in_sec: int


class AnswerOut(SessionState):
    correct: bool
    typo: bool
    correct_answer: str | None


class PairOut(SessionState):
    correct: bool
    exercise_solved: bool


class StreakChange(BaseModel):
    before: int
    after: int
    increased: bool


class NewAchievement(BaseModel):
    title: str
    icon: str
    description: str
    gem_reward: int


class CompleteOut(BaseModel):
    kind: SessionKind
    xp_earned: int
    gems_earned: int
    correct_count: int
    mistakes: int
    accuracy: int
    duration_sec: int
    perfect: bool
    skill_completed: bool
    streak: StreakChange
    daily_goal_reached: bool
    new_achievements: list[NewAchievement]
    user: UserState


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    display_name: str
    avatar_color: str
    xp: int
    is_me: bool
    zone: Literal["promotion", "safe", "demotion"]


class LeaderboardOut(BaseModel):
    league: str
    league_color: str
    ends_in_days: int
    entries: list[LeaderboardEntry]


class Badge(BaseModel):
    id: int
    code: str
    title: str
    description: str
    icon: str
    gem_reward: int
    threshold: int
    progress: int
    unlocked: bool
    unlocked_at: str | None


class ProfileOut(BaseModel):
    user: UserState
    joined: str
    accuracy: int
    stats: dict[str, int]
    achievements: list[Badge]


class Quest(BaseModel):
    id: str
    icon: str
    title: str
    progress: int
    target: int
    done: bool


class QuestsOut(BaseModel):
    quests: list[Quest]


class ErrorOut(BaseModel):
    detail: str
    code: str
