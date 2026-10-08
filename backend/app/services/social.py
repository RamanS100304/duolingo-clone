"""Leaderboard, profile and daily quests (all derived from completed sessions)."""
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Achievement, StudySession, User, UserAchievement
from .achievements import achievement_out, metrics_for_user
from .clock import effective_today, xp_today
from .users import user_state

PROMOTION_SLOTS = 5
DEMOTION_SLOTS = 3


def leaderboard(db: Session, user: User) -> dict:
    """Weekly XP ranking of everyone in the learner's league (Monday to Sunday)."""
    today = effective_today(user)
    week_start = today - timedelta(days=today.weekday())
    xp_sum = func.coalesce(func.sum(StudySession.xp_earned), 0)
    rows = db.execute(
        select(User, xp_sum.label("xp"))
        .outerjoin(StudySession, (StudySession.user_id == User.id) & (StudySession.status == "completed")
                   & (StudySession.activity_date >= week_start) & (StudySession.activity_date <= today))
        .where(User.league_id == user.league_id)
        .group_by(User.id).order_by(xp_sum.desc(), User.display_name)).all()
    n = len(rows)
    entries = []
    for i, (u, xp) in enumerate(rows, start=1):
        zone = "promotion" if i <= PROMOTION_SLOTS else ("demotion" if i > n - DEMOTION_SLOTS else "safe")
        entries.append({"rank": i, "user_id": u.id, "display_name": u.display_name,
                        "avatar_color": u.avatar_color, "xp": int(xp), "is_me": u.id == user.id, "zone": zone})
    league = user.league
    return {"league": league.name if league else "League", "league_color": league.color if league else "#cd7f32",
            "ends_in_days": 7 - today.weekday(), "entries": entries}


def profile(db: Session, user: User) -> dict:
    metrics = metrics_for_user(db, user)
    unlocked = dict(db.execute(select(UserAchievement.achievement_id, UserAchievement.unlocked_at)
                               .where(UserAchievement.user_id == user.id)).all())
    badges = [achievement_out(a, metrics, unlocked.get(a.id))
              for a in db.scalars(select(Achievement).order_by(Achievement.id))]
    correct, mistakes = db.execute(
        select(func.coalesce(func.sum(StudySession.correct_count), 0), func.coalesce(func.sum(StudySession.mistakes), 0))
        .where(StudySession.user_id == user.id, StudySession.status == "completed")).one()
    answered = correct + mistakes
    return {"user": user_state(db, user), "joined": user.created_at.date().isoformat(),
            "accuracy": round(100 * correct / answered) if answered else 0,
            "stats": metrics, "achievements": badges}


def daily_quests(db: Session, user: User) -> dict:
    """Three quests that reset every day, computed from today's completed sessions."""
    today = effective_today(user)
    todays = list(db.scalars(select(StudySession).where(
        StudySession.user_id == user.id, StudySession.status == "completed", StudySession.activity_date == today)))
    lessons = [s for s in todays if s.kind == "lesson"]
    quests = [
        ("goal", "⚡", f"Earn {user.daily_goal_xp} XP", xp_today(db, user), user.daily_goal_xp),
        ("lessons", "📚", "Complete 2 lessons", len(lessons), 2),
        ("perfect", "🎯", "Finish a lesson with no mistakes", sum(1 for s in lessons if s.mistakes == 0), 1),
    ]
    return {"quests": [{"id": q, "icon": icon, "title": title, "progress": min(p, target), "target": target,
                        "done": p >= target} for q, icon, title, p, target in quests]}
