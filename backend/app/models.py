"""Database schema (SQLite via SQLAlchemy 2).

Content tree     courses -> units -> skills -> lessons -> exercises -> exercise_options
                                                              \\-> exercise_answers (accepted answers)
Learner          users (-> leagues), user_skill_progress, chest_claims, user_achievements
Play             study_sessions -> session_exercises, session_answers
Reference        leagues, achievements

A study_session row covers one run of the lesson player from start to finish. The server
creates it, checks every answer against it, and only a finished session awards XP. Daily XP,
the daily goal, the weekly leaderboard and the streak calendar are all derived from completed
sessions. users.total_xp / gems / hearts / streak are kept as fast counters.
"""
from datetime import date, datetime

from sqlalchemy import (Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import DEFAULT_TIMEZONE
from .database import Base, utcnow

EXERCISE_TYPES = ("multiple_choice", "translate", "match_pairs", "fill_blank", "type_answer")
SESSION_KINDS = ("lesson", "practice", "timed", "legendary")
SESSION_STATUSES = ("active", "completed", "failed", "abandoned")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


# ------------------------------------------------------------------- content
class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    from_language: Mapped[str] = mapped_column(String(50))   # learner speaks
    to_language: Mapped[str] = mapped_column(String(50))     # learner learns
    units: Mapped[list["Unit"]] = relationship(back_populates="course", order_by="Unit.position")


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (UniqueConstraint("course_id", "position"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(200))
    color: Mapped[str] = mapped_column(String(20))           # banner colour on the path
    course: Mapped[Course] = relationship(back_populates="units")
    skills: Mapped[list["Skill"]] = relationship(back_populates="unit", order_by="Skill.position")


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("unit_id", "position"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(10))            # emoji shown on the node
    unit: Mapped[Unit] = relationship(back_populates="skills")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="skill", order_by="Lesson.position")


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("skill_id", "position"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    skill: Mapped[Skill] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(back_populates="lesson", order_by="Exercise.position")


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (UniqueConstraint("lesson_id", "position"),
                      CheckConstraint(_in("type", EXERCISE_TYPES), name="type"))
    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(20))
    prompt: Mapped[str] = mapped_column(String(200))                              # instruction line
    source_text: Mapped[str | None] = mapped_column(String(300), nullable=True)   # sentence shown to the learner
    hint: Mapped[str | None] = mapped_column(String(300), nullable=True)          # e.g. Hindi translation for fill-blank
    lesson: Mapped[Lesson] = relationship(back_populates="exercises")
    options: Mapped[list["ExerciseOption"]] = relationship(
        back_populates="exercise", order_by="ExerciseOption.position", cascade="all, delete-orphan")
    answers: Mapped[list["ExerciseAnswer"]] = relationship(
        back_populates="exercise", order_by="ExerciseAnswer.id", cascade="all, delete-orphan")

    @property
    def primary_answer(self) -> str | None:
        """The canonical answer shown as the 'Correct solution'."""
        return next((a.text for a in self.answers if a.is_primary), None)


class ExerciseAnswer(Base):
    """Accepted answers of an exercise: one primary (shown to the learner) plus alternatives."""
    __tablename__ = "exercise_answers"
    __table_args__ = (UniqueConstraint("exercise_id", "text"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(300))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    exercise: Mapped[Exercise] = relationship(back_populates="answers")


class ExerciseOption(Base):
    """Choices for multiple-choice / fill-blank, word-bank tiles for translate,
    and (text, pair_text) rows for match-pairs."""
    __tablename__ = "exercise_options"
    __table_args__ = (UniqueConstraint("exercise_id", "position"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(100))
    pair_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    exercise: Mapped[Exercise] = relationship(back_populates="options")


# ----------------------------------------------------------------- reference
class League(Base):
    __tablename__ = "leagues"
    id: Mapped[int] = mapped_column(primary_key=True)
    tier: Mapped[int] = mapped_column(Integer, unique=True)   # 1 = Bronze, 2 = Silver, ...
    name: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str] = mapped_column(String(20))


class Achievement(Base):
    __tablename__ = "achievements"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(200))
    icon: Mapped[str] = mapped_column(String(10))
    metric: Mapped[str] = mapped_column(String(30))          # key in services.achievements.metrics_for_user()
    threshold: Mapped[int] = mapped_column(Integer)
    gem_reward: Mapped[int] = mapped_column(Integer, default=10)


# ------------------------------------------------------------------- learner
class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("hearts BETWEEN 0 AND 5", name="hearts_range"),
                      CheckConstraint("gems >= 0", name="gems_non_negative"),
                      CheckConstraint("total_xp >= 0", name="xp_non_negative"))
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_color: Mapped[str] = mapped_column(String(20), default="#1cb0f6")
    league_id: Mapped[int | None] = mapped_column(ForeignKey("leagues.id"), index=True, nullable=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    gems: Mapped[int] = mapped_column(Integer, default=500)
    hearts: Mapped[int] = mapped_column(Integer, default=5)
    hearts_updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_goal_xp: Mapped[int] = mapped_column(Integer, default=20)
    timezone: Mapped[str] = mapped_column(String(64), default=DEFAULT_TIMEZONE)   # IANA name; defines "today"
    # Lets us *simulate* future days to test streak logic without waiting.
    day_offset: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    league: Mapped[League | None] = relationship()


class UserSkillProgress(Base):
    __tablename__ = "user_skill_progress"
    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    legendary: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class ChestClaim(Base):
    """A treasure chest on the path, opened once per learner per unit."""
    __tablename__ = "chest_claims"
    __table_args__ = (UniqueConstraint("user_id", "unit_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    gems: Mapped[int] = mapped_column(Integer)
    claimed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id", ondelete="CASCADE"), index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ---------------------------------------------------------------------- play
class StudySession(Base):
    """One run of the lesson player (lesson / practice / timed / legendary)."""
    __tablename__ = "study_sessions"
    __table_args__ = (CheckConstraint(_in("kind", SESSION_KINDS), name="kind"),
                      CheckConstraint(_in("status", SESSION_STATUSES), name="status"),
                      Index("ix_study_sessions_user_date", "user_id", "activity_date"))
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True, nullable=True)
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), index=True, nullable=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id", ondelete="SET NULL"), nullable=True)  # unit review
    time_limit_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)   # timed mode
    max_mistakes: Mapped[int | None] = mapped_column(Integer, nullable=True)     # legendary mode
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    mistakes: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    gems_earned: Mapped[int] = mapped_column(Integer, default=0)
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # The learner's *local* date when the session was completed (see User.timezone / day_offset).
    activity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    items: Mapped[list["SessionExercise"]] = relationship(
        back_populates="session", order_by="SessionExercise.position", cascade="all, delete-orphan")


class SessionExercise(Base):
    """The exercises dealt into a session, and whether each has been answered / solved."""
    __tablename__ = "session_exercises"
    __table_args__ = (UniqueConstraint("session_id", "exercise_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    answered: Mapped[bool] = mapped_column(Boolean, default=False)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    session: Mapped[StudySession] = relationship(back_populates="items")
    exercise: Mapped[Exercise] = relationship()


class SessionAnswer(Base):
    """Every answer submitted in a session (audit log; also tracks matched pairs)."""
    __tablename__ = "session_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
