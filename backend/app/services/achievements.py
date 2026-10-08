"""Badges: each achievements row is 'metric >= threshold'. Adding a badge = inserting one row."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Achievement, StudySession, User, UserAchievement
from .clock import daily_xp_by_date
from .path import is_complete, ordered_skills, progress_map


def metrics_for_user(db: Session, user: User) -> dict[str, int]:
    done = (StudySession.user_id == user.id, StudySession.status == "completed")
    count = lambda *cond: db.scalar(select(func.count()).select_from(StudySession).where(*done, *cond)) or 0  # noqa: E731
    prog = progress_map(db, user)
    return {
        "lessons_completed": count(StudySession.kind == "lesson"),
        "perfect_lessons": count(StudySession.kind == "lesson", StudySession.mistakes == 0),
        "total_xp": user.total_xp,
        "streak": max(user.streak, user.longest_streak),
        "skills_completed": sum(1 for s in ordered_skills(db) if is_complete(s, prog)),
        "legendary_count": sum(1 for p in prog.values() if p.legendary),
        "best_timed_correct": db.scalar(select(func.max(StudySession.correct_count))
                                        .where(*done, StudySession.kind == "timed")) or 0,
        "goal_days": sum(1 for x in daily_xp_by_date(db, user).values() if x >= user.daily_goal_xp),
    }


def check_achievements(db: Session, user: User) -> list[Achievement]:
    """Unlock every badge whose threshold is now met; rewards gems."""
    db.flush()
    metrics = metrics_for_user(db, user)
    owned = set(db.scalars(select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)))
    unlocked = []
    for a in db.scalars(select(Achievement).order_by(Achievement.id)):
        if a.id not in owned and metrics.get(a.metric, 0) >= a.threshold:
            db.add(UserAchievement(user_id=user.id, achievement_id=a.id))
            user.gems += a.gem_reward
            unlocked.append(a)
    return unlocked


def achievement_out(a: Achievement, metrics: dict, unlocked_at: datetime | None = None) -> dict:
    return {"id": a.id, "code": a.code, "title": a.title, "description": a.description, "icon": a.icon,
            "gem_reward": a.gem_reward, "threshold": a.threshold,
            "progress": min(metrics.get(a.metric, 0), a.threshold),
            "unlocked": unlocked_at is not None, "unlocked_at": unlocked_at.isoformat() if unlocked_at else None}


def new_badges_out(badges: list[Achievement]) -> list[dict]:
    return [{"title": a.title, "icon": a.icon, "description": a.description, "gem_reward": a.gem_reward}
            for a in badges]
